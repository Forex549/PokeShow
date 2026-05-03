from fastapi import APIRouter, HTTPException

from src.api.schemas.battle import BattleStateResponse, StartBattleRequest, TurnRequest
from src.api.services.battle_service import play_turn, start_battle

router = APIRouter()


@router.post("/start", response_model=BattleStateResponse, status_code=201)
def start_battle_endpoint(payload: StartBattleRequest) -> BattleStateResponse:
    try:
        state = start_battle(payload.player_pokemon, payload.enemy_pokemon)
        return BattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Pokemon no encontrado: {exc}") from exc


@router.post("/turn", response_model=BattleStateResponse, status_code=200)
def turn_endpoint(payload: TurnRequest) -> BattleStateResponse:
    try:
        state = play_turn(payload.battle_id, payload.player_move)
        return BattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Batalla no encontrada: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
