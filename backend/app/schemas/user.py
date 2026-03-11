from pydantic import BaseModel


class UserCreate(BaseModel):
    nickname: str
    email: str | None = None
    password: str


class UserLogin(BaseModel):
    nickname: str
    password: str


class UserResponse(BaseModel):
    id: str
    nickname: str
    email: str | None = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
