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
)
from src.engine.logic.damage_calc import calculate_damage
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

_PESOS_DEFAULT = [1.0, 1.0, 0.5, 1.0]

def _cargar_pesos() -> list:
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


def _serialize_pokemon(p: Pokemon) -> dict:
    return {
        "name": p.name,
        "hp": p.hp,
        "max_hp": p.max_hp,
        "types": list(p.types),
        "moves": [m.name for m in p.moves],
        "is_fainted": p.hp <= 0,
    }


# ── estado de batalla ────────────────────────────────────────────────────────

@dataclass
class BattleState:
    battle_id: str
    user_id: str
    entrenador_player: Entrenador
    entrenador_enemy: Entrenador
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
    }


# ── estrategias de la IA ─────────────────────────────────────────────────────

def _get_enemy_strategy(mode: str) -> Callable:
    if mode == "heuristic":
        return lambda e, r: choose_best_move(e.get_current_pokemon(), r.get_current_pokemon())
    elif mode == "minimax2":
        return elegir_movimiento_nivel2
    elif mode == "minimax3":
        pesos = _cargar_pesos()
        return lambda e, r: elegir_movimiento_nivel3(e, r, pesos)
    else:  # random
        return lambda e, r: chose_random_move(e.get_current_pokemon())


# ── ejecución de turno ───────────────────────────────────────────────────────

def _execute_turn(
    battle: BattleState,
    player_move: Movimiento,
) -> tuple[List[str], str]:
    logs: List[str] = []

    # la IA cambia automáticamente si su pokémon cayó
    if battle.enemy.hp <= 0:
        _auto_switch_enemy(battle)
        return logs, "enemy"

    # la IA elige movimiento según su estrategia
    strategy = _get_enemy_strategy(battle.mode)
    enemy_move = strategy(battle.entrenador_enemy, battle.entrenador_player)

    player = battle.player
    enemy  = battle.enemy

    player_first = player.spe >= enemy.spe
    first_turn   = "player" if player_first else "enemy"

    if player_first:
        logs.append(f"{player.name} es más rápido.")
        order = [(player, player_move, enemy), (enemy, enemy_move, player)]
    else:
        logs.append(f"{enemy.name} es más rápido.")
        order = [(enemy, enemy_move, player), (player, player_move, enemy)]

    for attacker, move, defender in order:
        if attacker.hp <= 0 or move is None:
            continue
        damage, crit = calculate_damage(attacker, defender, move)
        defender.hp = max(0, defender.hp - damage)
        msg = f"{attacker.name} usó {move.name}. Hizo {damage} de daño."
        if crit:
            msg += " ¡Golpe crítico!"
        logs.append(msg)
        if defender.hp <= 0:
            logs.append(f"{defender.name} se debilitó.")
            break

    return logs, first_turn


def _auto_switch_enemy(battle: BattleState):
    """La IA cambia automáticamente al siguiente pokémon vivo."""
    team = battle.entrenador_enemy.pokemones
    for i, p in enumerate(team):
        if p.hp > 0 and i != battle.enemy_index:
            battle.entrenador_enemy.switch_pokemon(i)
            battle.logs.append(f"¡La IA envió a {battle.enemy.name}!")
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
    mode: str = "random",
) -> dict:
    get_user(user_id)
    
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
        mode=mode,
        logs=[f"¡Inicia la batalla! {entrenador_player.pokemones[0].name} vs {entrenador_enemy.pokemones[0].name}"],
    )
    BATTLES[battle_id] = battle
    state = _build_state(battle)
    save_battle_state(battle_id, user_id, state)
    add_user_battle(user_id, battle_id)
    return state


def play_turn(battle_id: str, player_move_name: str) -> dict:
    battle = BATTLES.get(battle_id) or _restore_battle(battle_id)

    if battle.finished:
        battle.logs.append("La batalla ya terminó.")
        return _build_state(battle)

    if battle.needs_switch:
        raise ValueError("El jugador debe cambiar de Pokémon antes de continuar")

    player_move = _find_move(battle.player, player_move_name)
    turn_logs, first_turn = _execute_turn(battle, player_move)
    battle.logs.extend(turn_logs)
    battle.first_turn = first_turn

    # IA cambia automáticamente si cayó
    if battle.enemy.hp <= 0:
        _auto_switch_enemy(battle)

    # Si el pokémon del jugador cayó, marcamos needs_switch
    if battle.player.hp <= 0:
        battle.needs_switch = True
        battle.logs.append(f"¡{battle.player.name} se debilitó! Elige tu siguiente Pokémon.")

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

    # Si es voluntario, la IA igual ataca ese turno
    if voluntary:
        strategy = _get_enemy_strategy(battle.mode)
        enemy_move = strategy(battle.entrenador_enemy, battle.entrenador_player)
        if enemy_move is not None:
            damage, crit = calculate_damage(battle.enemy, battle.player, enemy_move)
            battle.player.hp = max(0, battle.player.hp - damage)
            msg = f"{battle.enemy.name} usó {enemy_move.name}. Hizo {damage} de daño."
            if crit:
                msg += " ¡Golpe crítico!"
            battle.logs.append(msg)
            if battle.player.hp <= 0:
                battle.logs.append(f"{battle.player.name} se debilitó.")
                battle.needs_switch = True

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
        p.moves = [_get_move_obj(m) for m in moves]
    p.types = list(s.get("types", p.types))
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

    battle = BattleState(
        battle_id=battle_id,
        user_id=str(stored.get("user_id", "")),
        entrenador_player=entrenador_player,
        entrenador_enemy=entrenador_enemy,
        mode=state.get("mode", "random"),
        logs=list(state.get("logs", [])),
        finished=bool(state.get("finished", False)),
        winner=state.get("winner"),
        needs_switch=bool(state.get("needs_switch", False)),
    )
    BATTLES[battle_id] = battle
    return battle