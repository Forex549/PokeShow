from fastapi import APIRouter, HTTPException

from src.api.schemas.battle import BattleStateResponse, StartBattleRequest, TurnRequest
from src.api.services.battle_service import get_battle_state, play_turn, start_battle

router = APIRouter()


@router.post("/start", response_model=BattleStateResponse, status_code=201)
def start_battle_endpoint(payload: StartBattleRequest) -> BattleStateResponse:
    try:
        state = start_battle(payload.user_id, payload.player_pokemon, payload.enemy_pokemon)
        return BattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Usuario o Pokemon no encontrado: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/turn", response_model=BattleStateResponse, status_code=200)
def turn_endpoint(payload: TurnRequest) -> BattleStateResponse:
    try:
        state = play_turn(payload.battle_id, payload.player_move)
        return BattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Batalla no encontrada: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{battle_id}", response_model=BattleStateResponse, status_code=200)
def resume_battle_endpoint(battle_id: str) -> BattleStateResponse:
    try:
        state = get_battle_state(battle_id)
        return BattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Batalla no encontrada: {exc}") from exc
