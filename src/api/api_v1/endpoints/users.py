from fastapi import APIRouter, HTTPException

from src.api.schemas.users import CreateUserRequest, UserResponse
from src.api.services.storage import create_user, get_user, list_user_battles

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=201)
def create_user_endpoint(payload: CreateUserRequest) -> UserResponse:
    user = create_user(payload.username)
    return UserResponse(**user)


@router.get("/{user_id}", response_model=UserResponse, status_code=200)
def get_user_endpoint(user_id: str) -> UserResponse:
    try:
        user = get_user(user_id)
        return UserResponse(**user)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Usuario no encontrado: {exc}") from exc


@router.get("/{user_id}/battles", response_model=list[str], status_code=200)
def list_battles_endpoint(user_id: str) -> list[str]:
    try:
        return list_user_battles(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Usuario no encontrado: {exc}") from exc
