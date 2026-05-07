import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from src.engine.logic.damage_calc import calculate_damage
from src.engine.logic.heuristic import choose_best_move
from src.engine.models.movimientos import Movimiento
from src.engine.models.pokemon import Pokemon
from src.api.services.storage import (
    add_user_battle,
    get_battle_state as load_battle_state,
    get_user,
    save_battle_state,
)


DATA_DIR = Path(__file__).resolve().parents[3] / "data"

with open(DATA_DIR / "moves-data.json") as file:
    MOVES_DB: Dict[str, dict] = json.load(file)

with open(DATA_DIR / "pokedex_con_moves.json") as file:
    POKEDEX_DB: Dict[str, dict] = json.load(file)


@dataclass
class BattleState:
    battle_id: str
    user_id: str
    player: Pokemon
    enemy: Pokemon
    logs: List[str]
    finished: bool
    winner: Optional[str]
    first_turn: Optional[str]


BATTLES: Dict[str, BattleState] = {}


def _normalize_id(name: str) -> str:
    return name.strip().lower().replace(" ", "").replace("-", "")


def _get_pokemon(name: str) -> Pokemon:
    poke_id = _normalize_id(name)
    if poke_id not in POKEDEX_DB:
        raise KeyError(poke_id)
    data = POKEDEX_DB[poke_id]
    return Pokemon(data.get("name", poke_id), data, MOVES_DB)


def _get_move_obj(name: str) -> Movimiento:
    move_id = _normalize_id(name)
    if move_id not in MOVES_DB:
        raise KeyError(move_id)
    return Movimiento(data=MOVES_DB[move_id])


def _find_move(pokemon: Pokemon, move_name: str) -> Movimiento:
    move_id = _normalize_id(move_name)
    for move in pokemon.moves:
        if _normalize_id(move.name) == move_id:
            return move
    raise ValueError("Movimiento invalido")


def _execute_turn(player: Pokemon, enemy: Pokemon, player_move: Movimiento, enemy_move: Movimiento) -> List[str]:
    logs: List[str] = []

    player_first = player.spe >= enemy.spe

    if player_first:
        logs.append(f"{player.name} es más rápido.")
        
        order = [
            (player, player_move, enemy),
            (enemy, enemy_move, player)
        ]
    else:
        logs.append(f"{enemy.name} es más rápido.")

        order = [
            (enemy, enemy_move, player),
            (player, player_move, enemy)
        ]
    for attacker, move, defender in order:
        if attacker.hp <= 0:
            continue

        damage, crit = calculate_damage(attacker, defender, move)
        defender.hp = max(0, defender.hp - damage)
        
        message = f"{attacker.name} uso {move.name}. Hizo {damage} de dano."
        
        if crit:
            message += " ¡Golpe critico!"

        logs.append(message)

        if defender.hp <= 0:
            logs.append(f"{defender.name} se debilito.")
            break

    return logs, "player" if player_first else "enemy"


def _build_state(battle: BattleState) -> Dict[str, object]:
    return {
        "battle_id": battle.battle_id,
        "user_id": battle.user_id,
        "player": {
            "name": battle.player.name,
            "hp": battle.player.hp,
            "max_hp": battle.player.max_hp,
            "types": list(battle.player.types),
            "moves": [move.name for move in battle.player.moves],
        },
        "enemy": {
            "name": battle.enemy.name,
            "hp": battle.enemy.hp,
            "max_hp": battle.player.max_hp,
            "types": list(battle.enemy.types),
            "moves": [move.name for move in battle.enemy.moves],
        },
        "logs": list(battle.logs),
        "finished": battle.finished,
        "winner": battle.winner,
        "first_turn": battle.first_turn,
    }


def _pokemon_from_state(state: Dict[str, object]) -> Pokemon:
    name = str(state.get("name", ""))
    pokemon = _get_pokemon(name)
    pokemon.hp = int(state.get("hp", pokemon.hp))
    stored_moves = list(state.get("moves", []))
    if stored_moves:
        pokemon.moves = [_get_move_obj(move_name) for move_name in stored_moves]
    pokemon.types = list(state.get("types", pokemon.types))
    return pokemon


def _restore_battle(battle_id: str) -> BattleState:
    stored = load_battle_state(battle_id)
    state = stored.get("state", {})
    player_state = state.get("player", {})
    enemy_state = state.get("enemy", {})

    battle = BattleState(
        battle_id=battle_id,
        user_id=str(stored.get("user_id", "")),
        player=_pokemon_from_state(player_state),
        enemy=_pokemon_from_state(enemy_state),
        logs=list(state.get("logs", [])),
        finished=bool(state.get("finished", False)),
        winner=state.get("winner"),
    )
    BATTLES[battle_id] = battle
    return battle


def start_battle(user_id: str, player_name: str, enemy_name: Optional[str]) -> Dict[str, object]:
    get_user(user_id)
    player = _get_pokemon(player_name)
    enemy = _get_pokemon(enemy_name) if enemy_name else _get_pokemon("mewtwo")

    battle_id = str(uuid4())
    battle = BattleState(
        battle_id=battle_id,
        user_id=user_id,
        player=player,
        enemy=enemy,
        logs=[f"Inicia {player.name} vs {enemy.name}"],
        finished=False,
        winner=None,
        first_turn=None,
    )
    BATTLES[battle_id] = battle
    state = _build_state(battle)
    save_battle_state(battle_id, user_id, state)
    add_user_battle(user_id, battle_id)
    return state


def play_turn(battle_id: str, player_move: str) -> Dict[str, object]:
    battle = BATTLES.get(battle_id)
    if battle is None:
        battle = _restore_battle(battle_id)

    if battle.finished:
        battle.logs.append("La batalla ya termino.")
        state = _build_state(battle)
        save_battle_state(battle_id, battle.user_id, state)
        return state

    player_move_obj = _find_move(battle.player, player_move)
    enemy_move_obj = choose_best_move(battle.enemy, battle.player)
    turn_logs, first_turn = _execute_turn(battle.player, battle.enemy, player_move_obj, enemy_move_obj)
    battle.logs.extend(turn_logs)
    battle.first_turn = first_turn

    if battle.player.hp <= 0 or battle.enemy.hp <= 0:
        battle.finished = True
        if battle.player.hp > 0:
            battle.winner = battle.player.name
        elif battle.enemy.hp > 0:
            battle.winner = battle.enemy.name
        else:
            battle.winner = "Empate"

    state = _build_state(battle)
    save_battle_state(battle_id, battle.user_id, state)
    return state


def get_battle_state(battle_id: str) -> Dict[str, object]:
    battle = BATTLES.get(battle_id)
    if battle is None:
        battle = _restore_battle(battle_id)
    return _build_state(battle)
