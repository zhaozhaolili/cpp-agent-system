from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    role: str = payload.get("role")
    if username is None or role is None:
        raise credentials_exception
    token_data = TokenData(username=username, role=role)
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    # 可添加激活状态检查，暂不实现
    return current_user

def get_current_teacher(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Not enough permissions (teacher required)")
    return current_user

def get_current_student(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not enough permissions (student required)")
    return current_user