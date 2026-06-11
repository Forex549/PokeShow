from enum import Enum
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Canonical AI mode enum (single source of truth)
# ---------------------------------------------------------------------------

class BattleMode(str, Enum):
    """The 5 valid AI strategy identifiers. 'human' is NOT in this enum."""
    random    = "random"
    heuristic = "heuristic"
    minimax2  = "minimax2"
    minimax3  = "minimax3"
    minimax4  = "minimax4"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class StartBattleRequest(BaseModel):
    user_id: str
    player_team: Annotated[List[str], Field()]
    enemy_team: Optional[List[str]] = None

    # New explicit fields. player_mode="human" → Jugador vs IA.
    player_mode: str = "human"            # "human" | one of BattleMode
    enemy_mode: BattleMode = BattleMode.random
    # Legacy alias: old clients send `mode`. Map it to enemy_mode.
    mode: Optional[str] = None

    @model_validator(mode="after")
    def _resolve_and_validate(self) -> "StartBattleRequest":
        # Validate team length
        if len(self.player_team) != 4:
            raise ValueError("El equipo del jugador debe tener exactamente 4 Pokémon")

        # Legacy alias: if `mode` is provided AND enemy_mode is still the
        # default (i.e. was not explicitly set), honor the legacy `mode`.
        # NOTE: Pydantic processes fields in declaration order; if enemy_mode
        # was explicitly set to something non-default we keep it.
        # We detect "explicitly set" by checking model_fields_set.
        if self.mode is not None and "enemy_mode" not in self.model_fields_set:
            if self.mode in BattleMode._value2member_map_:
                self.enemy_mode = BattleMode(self.mode)
            # else: unknown legacy string → keep default (random), don't crash

        # player_mode must be "human" or a valid BattleMode value
        if (
            self.player_mode != "human"
            and self.player_mode not in BattleMode._value2member_map_
        ):
            raise ValueError(f"player_mode inválido: {self.player_mode}")

        return self


class SwitchRequest(BaseModel):
    battle_id: str
    pokemon_index: int
    voluntary: bool = False


class TurnRequest(BaseModel):
    battle_id: str
    # Optional in IA-vs-IA (auto-resolved); required for human player
    player_move: Optional[str] = None


# ---------------------------------------------------------------------------
# Move payload: object form exposing PP
# ---------------------------------------------------------------------------

class MovePP(BaseModel):
    name: str
    pp: int
    max_pp: int
    available: bool


# ---------------------------------------------------------------------------
# Internal full pokemon state (player active, player bench, enemy active)
# ---------------------------------------------------------------------------

class BattlePokemonState(BaseModel):
    name: str
    hp: int
    max_hp: int
    types: List[str]
    moves: List[MovePP]
    is_fainted: bool
    status: str = "No State"            # brn | par | psn | slp | frz | "No State"
    volatile_status: str = "No State"   # confusion | "No State"


# ---------------------------------------------------------------------------
# PUBLIC masked enemy bench entry: name + fainted ONLY
# No hp, no max_hp, no types, no moves — they simply do not exist on this model.
# ---------------------------------------------------------------------------

class PublicEnemyPokemonState(BaseModel):
    name: str
    is_fainted: bool


# ---------------------------------------------------------------------------
# Active on-field enemy Pokémon: visible stats but NO per-move PP (REQ-4.4)
# Moves exposed as plain strings (names only) — PP is private to the AI.
# ---------------------------------------------------------------------------

class PublicActiveEnemyState(BaseModel):
    name: str
    hp: int
    max_hp: int
    types: List[str]
    moves: List[str]    # names only — no PP exposed (REQ-4.4)
    is_fainted: bool
    status: str = "No State"            # visible on-field condition (like the real games)
    volatile_status: str = "No State"

    @model_validator(mode="before")
    @classmethod
    def _extract_move_names(cls, data):
        """Coerce moves from List[dict|str] → List[str] (extract 'name' from dicts)."""
        if isinstance(data, dict) and "moves" in data:
            raw_moves = data.get("moves", [])
            data = dict(data)
            data["moves"] = [
                m["name"] if isinstance(m, dict) else str(m)
                for m in raw_moves
            ]
        return data


# ---------------------------------------------------------------------------
# PUBLIC battle state — declared response_model for every state-returning endpoint
# ---------------------------------------------------------------------------

class PublicBattleStateResponse(BaseModel):
    battle_id: str
    user_id: str
    player: BattlePokemonState                  # full own active (with PP)
    enemy: PublicActiveEnemyState               # on-field enemy — HP/types/move NAMES, no PP
    player_team: List[BattlePokemonState]       # full own bench
    enemy_team: List[PublicEnemyPokemonState]   # MASKED bench
    player_index: int
    enemy_index: int
    logs: List[str]
    finished: bool
    winner: Optional[str] = None
    first_turn: Optional[str] = None
    needs_switch: bool = False
    # Surfaces IA-vs-IA so the FE knows the player side is auto-driven
    player_mode: str = "human"
    enemy_mode: str = "random"


# ---------------------------------------------------------------------------
# Backward-compat alias for any existing code that still imports BattleStateResponse
# ---------------------------------------------------------------------------
BattleStateResponse = PublicBattleStateResponse
