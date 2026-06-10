import json
import copy
import os
import random

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Callable
from uuid import uuid4

from src.engine.models.pokemon import Pokemon
from src.engine.models.entrenador import Entrenador
from src.engine.models.movimientos import Movimiento
from src.engine.models.battle import Battle
from src.engine.logic.heuristic import (
    choose_best_move,
    chose_random_move,
    elegir_movimiento_nivel2,
    elegir_movimiento_nivel3,
    elegir_accion_nivel4,
)
from src.engine.logic.damage_calc import calculate_damage
from src.engine.logic.status_effects import (
    pre_move_check,
    try_apply_move_status,
    end_of_turn_residuals,
)
from src.api.services.storage import (
    add_user_battle,
    get_battle_state as load_battle_state,
    get_user,
    save_battle_state,
)

DATA_DIR = Path(__file__).resolve().parents[3] / "data"

with open(DATA_DIR / "moves-data.json") as f:
    MOVES_DB: Dict[str, dict] = json.load(f)

with open(DATA_DIR / "pokedex_con_moves.json") as f:
    POKEDEX_DB: Dict[str, dict] = json.load(f)

_PESOS_DEFAULT    = [1.0, 1.0, 0.5, 1.0]
_PESOS_N4_DEFAULT = [1.0, 1.0, 0.5, 1.0, 1.0]


def _cargar_pesos() -> list:
    """Load GA weights for minimax3 (4-weight vector)."""
    path = DATA_DIR / "best_weights.json"
    try:
        with open(path) as f:
            data = json.load(f)
        pesos = data["pesos"] if isinstance(data, dict) else data
        if isinstance(pesos, list) and len(pesos) == 4:
            return [float(x) for x in pesos]
    except Exception:
        pass
    return list(_PESOS_DEFAULT)


def _cargar_pesos_nivel4() -> list:
    """Load GA weights for minimax4 (5-weight vector from best_weights_n4.json)."""
    path = DATA_DIR / "best_weights_n4.json"
    try:
        with open(path) as f:
            data = json.load(f)
        pesos = data["pesos"] if isinstance(data, dict) else data
        if isinstance(pesos, list) and len(pesos) == 5:
            return [float(x) for x in pesos]
    except Exception:
        pass
    return list(_PESOS_N4_DEFAULT)

def _random_team(size: int = 4) -> List[str]:
    """Elige `size` pokémon al azar del pokedex."""
    available = list(POKEDEX_DB.keys())
    return random.sample(available, size)

# ── helpers ──────────────────────────────────────────────────────────────────

def _normalize(name: str) -> str:
    return name.strip().lower().replace(" ", "").replace("-", "")


def _get_pokemon(name: str) -> Pokemon:
    pid = _normalize(name)
    if pid not in POKEDEX_DB:
        raise KeyError(pid)
    data = POKEDEX_DB[pid]
    return Pokemon(data.get("name", pid), data, MOVES_DB)


def _get_move_obj(name: str) -> Movimiento:
    mid = _normalize(name)
    if mid not in MOVES_DB:
        raise KeyError(mid)
    return Movimiento(data=MOVES_DB[mid])


def _find_move(pokemon: Pokemon, move_name: str) -> Movimiento:
    mid = _normalize(move_name)
    for move in pokemon.moves:
        if _normalize(move.name) == mid:
            return move
    raise ValueError(f"Movimiento inválido: {move_name}")


def _max_pp_for(m) -> int:
    """Return the max PP for a move from MOVES_DB, falling back to m.pp if unknown."""
    key = _normalize(m.name)
    if key in MOVES_DB and "pp" in MOVES_DB[key]:
        return int(MOVES_DB[key]["pp"])
    return int(m.pp)


def _serialize_pokemon(p: Pokemon) -> dict:
    return {
        "name": p.name,
        "hp": p.hp,
        "max_hp": p.max_hp,
        "types": list(p.types),
        "moves": [
            {
                "name": m.name,
                "pp": m.pp,
                "max_pp": _max_pp_for(m),
                "available": m.available,
            }
            for m in p.moves
        ],
        "is_fainted": p.hp <= 0,
        "status": p.status,
        "volatile_status": p.volatile_status,
        # Contadores internos — necesarios para restaurar batallas; los
        # response models de Pydantic los ignoran (extra fields)
        "status_turns": p.status_turns,
        "volatile_turns": p.volatile_turns,
    }


# ── estado de batalla ────────────────────────────────────────────────────────

@dataclass
class BattleState:
    battle_id: str
    user_id: str
    entrenador_player: Entrenador
    entrenador_enemy: Entrenador
    # Dual-mode fields (REQ-1.7)
    player_mode: str = "human"    # "human" | BattleMode value
    enemy_mode: str = "random"    # BattleMode value
    # Legacy mirror — kept for any serialized state still using `mode`
    mode: str = "random"
    logs: List[str] = field(default_factory=list)
    finished: bool = False
    winner: Optional[str] = None
    first_turn: Optional[str] = None
    needs_switch: bool = False   # jugador debe elegir pokémon

    @property
    def player(self) -> Pokemon:
        return self.entrenador_player.get_current_pokemon()

    @property
    def enemy(self) -> Pokemon:
        return self.entrenador_enemy.get_current_pokemon()

    @property
    def player_index(self) -> int:
        return self.entrenador_player.current_pokemon_index

    @property
    def enemy_index(self) -> int:
        return self.entrenador_enemy.current_pokemon_index


BATTLES: Dict[str, BattleState] = {}


def _build_state(battle: BattleState) -> dict:
    return {
        "battle_id": battle.battle_id,
        "user_id": battle.user_id,
        "player": _serialize_pokemon(battle.player),
        "enemy": _serialize_pokemon(battle.enemy),
        "player_team": [_serialize_pokemon(p) for p in battle.entrenador_player.pokemones],
        "enemy_team": [_serialize_pokemon(p) for p in battle.entrenador_enemy.pokemones],
        "player_index": battle.player_index,
        "enemy_index": battle.enemy_index,
        "logs": list(battle.logs),
        "finished": battle.finished,
        "winner": battle.winner,
        "first_turn": battle.first_turn,
        "needs_switch": battle.needs_switch,
        # Dual-mode fields (REQ-1.7)
        "player_mode": battle.player_mode,
        "enemy_mode": battle.enemy_mode,
        # Legacy mirror
        "mode": battle.enemy_mode,
    }


# ── estrategias de la IA ─────────────────────────────────────────────────────

def _resolve_strategy(mode) -> Callable:
    """
    Map a BattleMode (or its string value) to a callable (actor, opp) -> Movimiento|int|None.

    REQ-2.3: random is its OWN explicit branch; unknown mode raises (no silent fallback).
    REQ-2.4: 'human' must never reach here — also raises.
    """
    from src.api.schemas.battle import BattleMode
    # Normalize to string value for comparison
    mode_val = mode.value if isinstance(mode, BattleMode) else str(mode)

    if mode_val == BattleMode.random.value:
        return lambda actor, opp: chose_random_move(actor.get_current_pokemon())
    if mode_val == BattleMode.heuristic.value:
        return lambda actor, opp: choose_best_move(
            actor.get_current_pokemon(), opp.get_current_pokemon()
        )
    if mode_val == BattleMode.minimax2.value:
        return elegir_movimiento_nivel2
    if mode_val == BattleMode.minimax3.value:
        pesos = _cargar_pesos()
        return lambda actor, opp: elegir_movimiento_nivel3(actor, opp, pesos)
    if mode_val == BattleMode.minimax4.value:
        pesos = _cargar_pesos_nivel4()
        return lambda actor, opp: elegir_accion_nivel4(actor, opp, pesos)
    # No silent catch-all: any unrecognized / 'human' value raises
    raise ValueError(f"Modo de IA no reconocido: {mode_val!r}")


# Legacy alias kept for any code not yet migrated
def _get_enemy_strategy(mode: str) -> Callable:
    return _resolve_strategy(mode)


def _resolve_ai_action(
    actor_entrenador,
    opp_entrenador,
    mode,
) -> tuple:
    """
    Resolve one AI action for a single side.

    Returns:
      ('move', Movimiento)  — side attacks with this move
      ('switch', int)       — side voluntarily switches to this index
      ('none', None)        — side skips (no available moves, or strategy returned None)

    NOTE: isinstance(action, int) MUST be checked BEFORE truthiness so that
    index 0 (falsy) is correctly interpreted as a switch, not as None/no-action.
    """
    strategy = _resolve_strategy(mode)
    action = strategy(actor_entrenador, opp_entrenador)
    if isinstance(action, int):          # int (or bool, which is int subclass) → switch
        return ("switch", action)
    if action is None:
        return ("none", None)
    return ("move", action)


# ── ejecución de turno ───────────────────────────────────────────────────────

def _try_switch(entrenador, idx: int, logs: List[str], side_label: str) -> bool:
    """
    Attempt a voluntary AI switch to `idx`.
    Returns True if switch was performed, False if it was illegal.
    REQ-5.4: illegal = out of range, already active, or target is fainted.
    """
    team = entrenador.pokemones
    if not (0 <= idx < len(team)):
        return False
    target = team[idx]
    if target.hp <= 0 or idx == entrenador.current_pokemon_index:
        return False
    entrenador.switch_pokemon(idx)
    logs.append(f"¡La IA envió a {entrenador.get_current_pokemon().name}!")
    return True


def _execute_turn(
    battle: BattleState,
    player_move: Optional[Movimiento],  # None when player_mode != human
    player_mode: str,
    enemy_mode: str,
) -> tuple[List[str], str]:
    logs: List[str] = []

    # Auto-switch enemy if its current Pokémon has already fainted
    if battle.enemy.hp <= 0:
        _auto_switch_enemy(battle)
        return logs, "enemy"

    # ── Resolve enemy action ──────────────────────────────────────────────
    enemy_tag, enemy_action = _resolve_ai_action(
        battle.entrenador_enemy, battle.entrenador_player, enemy_mode
    )
    enemy_move: Optional[Movimiento] = None

    if enemy_tag == "switch":
        _try_switch(battle.entrenador_enemy, enemy_action, logs, "enemy")
        # enemy action consumed; no attack this turn
    elif enemy_tag == "move":
        enemy_move = enemy_action
    # else "none": enemy skips

    # ── Resolve player action ─────────────────────────────────────────────
    if player_mode == "human":
        # player_move was validated by play_turn; use as-is
        p_move = player_move
    else:
        # IA-vs-IA: auto-resolve player side
        p_tag, p_action = _resolve_ai_action(
            battle.entrenador_player, battle.entrenador_enemy, player_mode
        )
        p_move = None
        if p_tag == "switch":
            # Player-side AI switches
            team = battle.entrenador_player.pokemones
            idx = p_action
            if (isinstance(idx, int) and 0 <= idx < len(team)
                    and team[idx].hp > 0
                    and idx != battle.player_index):
                battle.entrenador_player.switch_pokemon(idx)
                logs.append(f"¡El jugador IA envió a {battle.player.name}!")
        elif p_tag == "move":
            p_move = p_action
        # else "none": player side skips

    # ── Speed ordering ────────────────────────────────────────────────────
    player = battle.player
    enemy  = battle.enemy

    player_first = player.spe >= enemy.spe
    first_turn   = "player" if player_first else "enemy"

    if player_first:
        logs.append(f"{player.name} es más rápido.")
        order = [
            (player, p_move,     enemy,  "player"),
            (enemy,  enemy_move, player, "enemy"),
        ]
    else:
        logs.append(f"{enemy.name} es más rápido.")
        order = [
            (enemy,  enemy_move, player, "enemy"),
            (player, p_move,     enemy,  "player"),
        ]

    # ── Execute attacks ───────────────────────────────────────────────────
    for attacker, move, defender, _side in order:
        if attacker.hp <= 0 or move is None:
            continue

        # Estados previos al ataque: sueño/congelación/parálisis/confusión
        can_act, status_logs = pre_move_check(attacker)
        logs.extend(status_logs)
        if attacker.hp <= 0:  # autogolpe de confusión puede debilitar
            logs.append(f"{attacker.name} se debilitó.")
            break
        if not can_act:
            continue

        damage, crit = calculate_damage(attacker, defender, move)
        defender.hp = max(0, defender.hp - damage)
        # REQ-4.1: decrease PP after successful use
        move.decrease_pp()
        if move.category in ("Physical", "Special"):
            msg = f"{attacker.name} usó {move.name}. Hizo {damage} de daño."
            if crit:
                msg += " ¡Golpe crítico!"
        else:
            msg = f"{attacker.name} usó {move.name}."
        logs.append(msg)

        # Efectos de estado del movimiento (directos y secundarios)
        logs.extend(try_apply_move_status(defender, move))

        if defender.hp <= 0:
            logs.append(f"{defender.name} se debilitó.")
            break

    # ── Residuales de fin de turno (quemadura / veneno) ───────────────────
    for p in (battle.player, battle.enemy):
        if p.hp > 0:
            logs.extend(end_of_turn_residuals(p))
            if p.hp <= 0:
                logs.append(f"{p.name} se debilitó.")

    return logs, first_turn


def _auto_switch_enemy(battle: BattleState):
    """La IA cambia automáticamente al siguiente pokémon vivo."""
    team = battle.entrenador_enemy.pokemones
    for i, p in enumerate(team):
        if p.hp > 0 and i != battle.enemy_index:
            battle.entrenador_enemy.switch_pokemon(i)
            battle.logs.append(f"¡La IA envió a {battle.enemy.name}!")
            return


def _auto_switch_player(battle: BattleState):
    """En IA-vs-IA el lado jugador también repone automáticamente al caer."""
    team = battle.entrenador_player.pokemones
    for i, p in enumerate(team):
        if p.hp > 0 and i != battle.player_index:
            battle.entrenador_player.switch_pokemon(i)
            battle.logs.append(f"¡El jugador IA envió a {battle.player.name}!")
            return


def _check_battle_over(battle: BattleState):
    player_alive = any(p.hp > 0 for p in battle.entrenador_player.pokemones)
    enemy_alive  = any(p.hp > 0 for p in battle.entrenador_enemy.pokemones)

    if not player_alive and not enemy_alive:
        battle.finished = True
        battle.winner = "Empate"
    elif not player_alive:
        battle.finished = True
        battle.winner = battle.entrenador_enemy.name
    elif not enemy_alive:
        battle.finished = True
        battle.winner = battle.entrenador_player.name


# ── endpoints públicos ────────────────────────────────────────────────────────

def start_battle(
    user_id: str,
    player_names: List[str],
    enemy_names: Optional[List[str]] = None,
    mode: str = "random",           # legacy param (kept for old call sites)
    player_mode: str = "human",
    enemy_mode: str = "random",
) -> dict:
    get_user(user_id)

    # Legacy support: if only `mode` was supplied (old call sites), use it as enemy_mode
    # The explicit enemy_mode param overrides the legacy mode param.
    resolved_enemy_mode = enemy_mode if enemy_mode != "random" or mode == "random" else mode
    # Simpler: explicit enemy_mode wins; fallback to legacy `mode`
    # "random" is the default for enemy_mode; if the caller passed a non-default
    # enemy_mode we use it. If enemy_mode is still "random" but mode is something
    # else (old callers), use mode.
    if enemy_mode == "random" and mode != "random":
        resolved_enemy_mode = mode

    if not enemy_names:
        enemy_names = _random_team()

    entrenador_player = Entrenador("Jugador", [_get_pokemon(n) for n in player_names])
    entrenador_enemy  = Entrenador("IA",      [_get_pokemon(n) for n in enemy_names])

    battle_id = str(uuid4())
    battle = BattleState(
        battle_id=battle_id,
        user_id=user_id,
        entrenador_player=entrenador_player,
        entrenador_enemy=entrenador_enemy,
        player_mode=player_mode,
        enemy_mode=resolved_enemy_mode,
        mode=resolved_enemy_mode,
        logs=[f"¡Inicia la batalla! {entrenador_player.pokemones[0].name} vs {entrenador_enemy.pokemones[0].name}"],
    )
    BATTLES[battle_id] = battle
    state = _build_state(battle)
    save_battle_state(battle_id, user_id, state)
    add_user_battle(user_id, battle_id)
    return state


def play_turn(battle_id: str, player_move_name: Optional[str]) -> dict:
    battle = BATTLES.get(battle_id) or _restore_battle(battle_id)

    if battle.finished:
        battle.logs.append("La batalla ya terminó.")
        return _build_state(battle)

    if battle.needs_switch:
        raise ValueError("El jugador debe cambiar de Pokémon antes de continuar")

    # ── Resolve player's move object ──────────────────────────────────────
    if battle.player_mode == "human":
        if not player_move_name:
            raise ValueError("Falta el movimiento del jugador")
        player_move = _find_move(battle.player, player_move_name)
        # REQ-4.5a: reject a move whose available is False
        if not player_move.available:
            raise ValueError(f"Movimiento sin PP o deshabilitado: {player_move_name}")
    else:
        # IA-vs-IA: player side is auto-resolved inside _execute_turn
        player_move = None

    turn_logs, first_turn = _execute_turn(
        battle, player_move, battle.player_mode, battle.enemy_mode
    )
    battle.logs.extend(turn_logs)
    battle.first_turn = first_turn

    # IA cambia automáticamente si cayó
    if battle.enemy.hp <= 0:
        _auto_switch_enemy(battle)

    # Si el pokémon del jugador cayó: humano elige, IA repone automáticamente
    if battle.player.hp <= 0:
        if battle.player_mode == "human":
            battle.needs_switch = True
            battle.logs.append(f"¡{battle.player.name} se debilitó! Elige tu siguiente Pokémon.")
        else:
            _auto_switch_player(battle)

    _check_battle_over(battle)
    if battle.finished:
        battle.needs_switch = False

    state = _build_state(battle)
    save_battle_state(battle_id, battle.user_id, state)
    return state


def switch_pokemon(battle_id: str, pokemon_index: int, voluntary: bool = False) -> dict:
    battle = BATTLES.get(battle_id) or _restore_battle(battle_id)

    if battle.finished:
        raise ValueError("La batalla ya terminó")

    team = battle.entrenador_player.pokemones
    if not (0 <= pokemon_index < len(team)):
        raise ValueError("Índice fuera de rango")
    if team[pokemon_index].hp <= 0:
        raise ValueError("Ese Pokémon está debilitado")
    if pokemon_index == battle.player_index:
        raise ValueError("Ese Pokémon ya está en batalla")

    battle.entrenador_player.switch_pokemon(pokemon_index)
    battle.logs.append(f"¡Enviaste a {battle.player.name}!")
    battle.needs_switch = False

    # Si es voluntario, la IA igual actúa ese turno (REQ-5.3, A6, design 4.5)
    if voluntary:
        e_tag, e_action = _resolve_ai_action(
            battle.entrenador_enemy, battle.entrenador_player, battle.enemy_mode
        )

        if e_tag == "move":
            enemy_move = e_action
            can_act, status_logs = pre_move_check(battle.enemy)
            battle.logs.extend(status_logs)
            if can_act and battle.enemy.hp > 0:
                damage, crit = calculate_damage(battle.enemy, battle.player, enemy_move)
                battle.player.hp = max(0, battle.player.hp - damage)
                # REQ-4.1: decrement enemy move PP on use
                enemy_move.decrease_pp()
                if enemy_move.category in ("Physical", "Special"):
                    msg = f"{battle.enemy.name} usó {enemy_move.name}. Hizo {damage} de daño."
                    if crit:
                        msg += " ¡Golpe crítico!"
                else:
                    msg = f"{battle.enemy.name} usó {enemy_move.name}."
                battle.logs.append(msg)
                battle.logs.extend(try_apply_move_status(battle.player, enemy_move))
            if battle.player.hp <= 0:
                battle.logs.append(f"{battle.player.name} se debilitó.")
                battle.needs_switch = True

        elif e_tag == "switch":
            # Enemy also switches (rare double-switch turn) — no damage
            _try_switch(battle.entrenador_enemy, e_action, battle.logs, "enemy")

        # e_tag == "none": enemy skips, no action

        # Residuales del turno (quemadura/veneno) para ambos lados
        for p in (battle.player, battle.enemy):
            if p.hp > 0:
                battle.logs.extend(end_of_turn_residuals(p))
                if p.hp <= 0:
                    battle.logs.append(f"{p.name} se debilitó.")
                    if p is battle.player:
                        battle.needs_switch = True

        if battle.enemy.hp <= 0:
            _auto_switch_enemy(battle)

        _check_battle_over(battle)

    state = _build_state(battle)
    save_battle_state(battle_id, battle.user_id, state)
    return state

def get_battle_state(battle_id: str) -> dict:
    battle = BATTLES.get(battle_id) or _restore_battle(battle_id)
    return _build_state(battle)


# ── restaurar desde storage ──────────────────────────────────────────────────

def _pokemon_from_state(s: dict) -> Pokemon:
    p = _get_pokemon(s["name"])
    p.hp = int(s.get("hp", p.hp))
    moves = s.get("moves", [])
    if moves:
        # Moves may be stored as strings (old format) or dicts (new format)
        move_names = [
            m["name"] if isinstance(m, dict) else m
            for m in moves
        ]
        p.moves = [_get_move_obj(n) for n in move_names]
    p.types = list(s.get("types", p.types))
    p.status = s.get("status", "No State")
    p.volatile_status = s.get("volatile_status", "No State")
    p.status_turns = s.get("status_turns", 0)
    p.volatile_turns = s.get("volatile_turns", 0)
    return p


def _restore_battle(battle_id: str) -> BattleState:
    stored = load_battle_state(battle_id)
    state  = stored.get("state", {})

    player_team = [_pokemon_from_state(p) for p in state.get("player_team", [])]
    enemy_team  = [_pokemon_from_state(p) for p in state.get("enemy_team",  [])]

    entrenador_player = Entrenador("Jugador", player_team)
    entrenador_enemy  = Entrenador("IA",      enemy_team)
    entrenador_player.current_pokemon_index = state.get("player_index", 0)
    entrenador_enemy.current_pokemon_index  = state.get("enemy_index",  0)

    # Backward compat: if stored state only has legacy `mode`, use it as enemy_mode
    legacy_mode   = state.get("mode", "random")
    enemy_mode    = state.get("enemy_mode",  legacy_mode)
    player_mode   = state.get("player_mode", "human")

    battle = BattleState(
        battle_id=battle_id,
        user_id=str(stored.get("user_id", "")),
        entrenador_player=entrenador_player,
        entrenador_enemy=entrenador_enemy,
        player_mode=player_mode,
        enemy_mode=enemy_mode,
        mode=enemy_mode,
        logs=list(state.get("logs", [])),
        finished=bool(state.get("finished", False)),
        winner=state.get("winner"),
        needs_switch=bool(state.get("needs_switch", False)),
    )
    BATTLES[battle_id] = battle
    return battle