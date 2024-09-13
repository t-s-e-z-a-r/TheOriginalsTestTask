from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from decouple import config
from pydantic import BaseModel

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from database.models import User


class TokenData(BaseModel):
    user_id: int
    role: int


SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))
CREDENTIAL_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_token(user: User, duration: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.utcnow() + timedelta(minutes=duration)
    to_encode = {"user_id": user.id, "role": user.role, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise CREDENTIAL_EXCEPTION
    except JWTError:
        raise CREDENTIAL_EXCEPTION

    return TokenData(user_id=user_id, role=role)


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    return verify_token(token)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(unhashed_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(unhashed_password, hashed_password)


# Alternative for middleware

# class RoleChecker:
#     def __init__(self, allowed_roles: List[UserRole]):
#         self.allowed_roles = allowed_roles

#     def __call__(self, user: Annotated[User, Depends(get_current_user)]):
#         if user.role not in self.allowed_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="You don't have enough permissions",
#             )
#         return True
