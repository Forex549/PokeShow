from typing import List, Optional
from pydantic import BaseModel, model_validator


class StartBattleRequest(BaseModel):
    user_id: str
    player_team: List[str]          # lista de 4 nombres
    enemy_team: List[str]           # lista de 4 nombres
    mode: Optional[str] = "random"  # "random" | "heuristic" | "minimax2" | "minimax3"

    @model_validator(mode="after")
    def validate_teams(self):
        if len(self.player_team) != 4:
            raise ValueError("El equipo del jugador debe tener exactamente 4 Pokémon")
        if len(self.enemy_team) != 4:
            raise ValueError("El equipo de la IA debe tener exactamente 4 Pokémon")
        return self


class SwitchRequest(BaseModel):
    battle_id: str
    pokemon_index: int   # 0-3


class TurnRequest(BaseModel):
    battle_id: str
    player_move: str


class BattlePokemonState(BaseModel):
    name: str
    hp: int
    max_hp: int
    types: List[str]
    moves: List[str]
    is_fainted: bool


class BattleStateResponse(BaseModel):
    battle_id: str
    user_id: str
    player: BattlePokemonState        # pokémon activo del jugador
    enemy: BattlePokemonState         # pokémon activo de la IA
    player_team: List[BattlePokemonState]   # equipo completo
    enemy_team: List[BattlePokemonState]
    player_index: int                 # índice activo del jugador
    enemy_index: int
    logs: List[str]
    finished: bool
    winner: Optional[str] = None
    first_turn: Optional[str] = None
    needs_switch: bool = False        # True cuando el pokémon del jugador cayó