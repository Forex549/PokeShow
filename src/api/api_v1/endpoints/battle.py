from fastapi import APIRouter, HTTPException
from src.api.schemas.battle import (
    BattleStateResponse, StartBattleRequest,
    TurnRequest, SwitchRequest
)
from src.api.services.battle_service import (
    get_battle_state, play_turn, start_battle, switch_pokemon
)

router = APIRouter()


@router.post("/start", response_model=BattleStateResponse, status_code=201)
def start_battle_endpoint(payload: StartBattleRequest):
    try:
        state = start_battle(
            payload.user_id,
            payload.player_team,
            payload.enemy_team,
            payload.mode,
        )
        return BattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(404, detail=f"Pokémon no encontrado: {exc}")
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc))


@router.post("/turn", response_model=BattleStateResponse, status_code=200)
def turn_endpoint(payload: TurnRequest):
    try:
        state = play_turn(payload.battle_id, payload.player_move)
        return BattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(404, detail=f"Batalla no encontrada: {exc}")
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc))


@router.post("/switch", response_model=BattleStateResponse, status_code=200)
def switch_endpoint(payload: SwitchRequest):
    try:
        state = switch_pokemon(payload.battle_id, payload.pokemon_index)
        return BattleStateResponse(**state)
    except (KeyError, ValueError) as exc:
        raise HTTPException(400, detail=str(exc))


@router.get("/{battle_id}", response_model=BattleStateResponse, status_code=200)
def resume_battle_endpoint(battle_id: str):
    try:
        state = get_battle_state(battle_id)
        return BattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(404, detail=f"Batalla no encontrada: {exc}")