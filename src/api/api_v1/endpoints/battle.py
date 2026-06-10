from fastapi import APIRouter, HTTPException
from src.api.schemas.battle import (
    PublicBattleStateResponse,
    StartBattleRequest,
    TurnRequest,
    SwitchRequest,
)
from src.api.services.battle_service import (
    get_battle_state,
    play_turn,
    start_battle,
    switch_pokemon,
)

router = APIRouter()


@router.post("/start", response_model=PublicBattleStateResponse, status_code=201)
def start_battle_endpoint(payload: StartBattleRequest):
    try:
        state = start_battle(
            user_id=payload.user_id,
            player_names=payload.player_team,
            enemy_names=payload.enemy_team,
            player_mode=payload.player_mode,
            enemy_mode=payload.enemy_mode.value,
        )
        return PublicBattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(404, detail=f"Pokémon no encontrado: {exc}")
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc))


@router.post("/turn", response_model=PublicBattleStateResponse, status_code=200)
def turn_endpoint(payload: TurnRequest):
    try:
        state = play_turn(payload.battle_id, payload.player_move)
        return PublicBattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(404, detail=f"Batalla no encontrada: {exc}")
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc))


@router.post("/switch", response_model=PublicBattleStateResponse, status_code=200)
def switch_endpoint(payload: SwitchRequest):
    try:
        state = switch_pokemon(
            payload.battle_id,
            payload.pokemon_index,
            payload.voluntary,   # BUG FIX: was previously dropped
        )
        return PublicBattleStateResponse(**state)
    except (KeyError, ValueError) as exc:
        raise HTTPException(400, detail=str(exc))


@router.get("/{battle_id}", response_model=PublicBattleStateResponse, status_code=200)
def resume_battle_endpoint(battle_id: str):
    try:
        state = get_battle_state(battle_id)
        return PublicBattleStateResponse(**state)
    except KeyError as exc:
        raise HTTPException(404, detail=f"Batalla no encontrada: {exc}")
