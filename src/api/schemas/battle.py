from typing import List, Optional

from pydantic import BaseModel


class StartBattleRequest(BaseModel):
    player_pokemon: str
    enemy_pokemon: Optional[str] = None


class TurnRequest(BaseModel):
    battle_id: str
    player_move: str


class BattlePokemonState(BaseModel):
    name: str
    hp: int
    max_hp: int
    types: List[str]
    moves: List[str]


class BattleStateResponse(BaseModel):
    battle_id: str
    player: BattlePokemonState
    enemy: BattlePokemonState
    logs: List[str]
    finished: bool
    winner: Optional[str]
