from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import src.utils
from jose import jwt
from pydantic import ValidationError
from src.schemas import TokenPayload, SystemAccount
# TODO: Revisar que esté bien que lo añada yo:
from functools import lru_cache
from typing_extensions import Annotated
from src.utils import Settings
import src.repository as repository
import src.main as main



@lru_cache()
def get_settings():
    return src.utils.Settings()

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)
# TODO: Revisar que he cambiado config.Settings a Settings importándolo directamente de utils
async def get_current_user(settings: Annotated[Settings, Depends(get_settings)], token: str = Depends(reuseable_oauth)) -> SystemAccount:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.algorithm]
        )
        token_data = TokenPayload(**payload)
        
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = token_data.sub
    # get database
    db = main.get_db() # TODO: Revisar si está bien que haga esto aquí y luego use next(db)
    # get user from database
    db_user = repository.get_account_by_username(next(db), username)
    # if user does not exist, raise an exception
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn't found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return user Schema with password hashed
    user = { 'password': db_user.password,
             'username': db_user.username,
             'is_admin': db_user.is_admin,
             'available_money': db_user.available_money
    }
    return SystemAccount(**user)

