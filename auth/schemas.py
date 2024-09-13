from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class UserLogin(BaseModel):
    username: str
    password: str
