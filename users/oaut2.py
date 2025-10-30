from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import token
from . schemas import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(data: str = Depends(oauth2_scheme))-> TokenData :
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = token.verify_access_token(data, credentials_exception)
    return user

def get_admin_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    if not current_user.isadmin :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


