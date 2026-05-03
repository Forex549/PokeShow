from typing import List

from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: str
    username: str
    battles: List[str]
    created_at: str
