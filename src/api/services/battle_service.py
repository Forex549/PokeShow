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


BATTLES: Dict[str, BattleState] = {}


def _normalize_id(name: str) -> str:
    return name.strip().lower().replace(" ", "").replace("-", "")


def _get_pokemon(name: str) -> Pokemon:
    poke_id = _normalize_id(name)
    if poke_id not in POKEDEX_DB:
        raise KeyError(poke_id)
    data = POKEDEX_DB[poke_id]
    return Pokemon(data.get("name", poke_id), data)


def _get_move_obj(name: str) -> Movimiento:
    move_id = _normalize_id(name)
    if move_id not in MOVES_DB:
        raise KeyError(move_id)
    return Movimiento(move_id, MOVES_DB[move_id])


def _execute_turn(player: Pokemon, enemy: Pokemon, player_move_name: str, enemy_move_name: str) -> List[str]:
    logs: List[str] = []

    player_move = _get_move_obj(player_move_name)
    enemy_move = _get_move_obj(enemy_move_name)

    if player.spe >= enemy.spe:
        order = [(player, player_move, enemy), (enemy, enemy_move, player)]
    else:
        order = [(enemy, enemy_move, player), (player, player_move, enemy)]

    for attacker, move, defender in order:
        if attacker.hp <= 0:
            continue

        damage = calculate_damage(attacker, defender, move)
        defender.hp -= damage
        logs.append(f"{attacker.name} uso {move.name}. Hizo {damage} de dano.")

        if defender.hp <= 0:
            logs.append(f"{defender.name} se debilito.")
            break

    return logs


def _build_state(battle: BattleState) -> Dict[str, object]:
    return {
        "battle_id": battle.battle_id,
        "user_id": battle.user_id,
        "player": {
            "name": battle.player.name,
            "hp": battle.player.hp,
            "max_hp": battle.player.max_hp,
            "types": list(battle.player.types),
            "moves": list(battle.player.moves),
        },
        "enemy": {
            "name": battle.enemy.name,
            "hp": battle.enemy.hp,
            "max_hp": battle.enemy.max_hp,
            "types": list(battle.enemy.types),
            "moves": list(battle.enemy.moves),
        },
        "logs": list(battle.logs),
        "finished": battle.finished,
        "winner": battle.winner,
    }


def _pokemon_from_state(state: Dict[str, object]) -> Pokemon:
    name = str(state.get("name", ""))
    pokemon = _get_pokemon(name)
    pokemon.hp = int(state.get("hp", pokemon.hp))
    pokemon.max_hp = int(state.get("max_hp", pokemon.max_hp))
    pokemon.moves = list(state.get("moves", pokemon.moves))
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

    if player_move not in battle.player.moves:
        raise ValueError("Movimiento invalido")

    enemy_move = choose_best_move(battle.enemy, battle.player, MOVES_DB)
    battle.logs.extend(_execute_turn(battle.player, battle.enemy, player_move, enemy_move))

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
