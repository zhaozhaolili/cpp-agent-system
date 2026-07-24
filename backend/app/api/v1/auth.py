from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, Token, UserResponse, ProfileUpdate, ForgotPasswordRequest, ResetPasswordRequest
from app.core.security import verify_password, get_password_hash, create_access_token, create_reset_token, verify_reset_token
from app.core.config import settings
from app.api.v1.deps import get_current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        password_hash=hashed_password,
        role=user_data.role,
        full_name=user_data.full_name,
        email=getattr(user_data, 'email', None)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        email=new_user.email,
        full_name=new_user.full_name,
        created_at=new_user.created_at.isoformat()
    )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: User = Depends(get_current_active_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at.isoformat()
    )


@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新个人信息（用户名/密码/姓名）"""
    # 如果改密码，需要验证当前密码
    if data.new_password:
        if not data.current_password:
            raise HTTPException(400, "请提供当前密码")
        if not verify_password(data.current_password, current_user.password_hash):
            raise HTTPException(400, "当前密码错误")
        current_user.password_hash = get_password_hash(data.new_password)

    # 如果改用户名，检查是否重复
    if data.username and data.username != current_user.username:
        exists = db.query(User).filter(User.username == data.username).first()
        if exists:
            raise HTTPException(400, "用户名已被使用")
        current_user.username = data.username

    if data.full_name is not None:
        current_user.full_name = data.full_name

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """忘记密码 - 发送重置链接（开发模式下返回 token）"""
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        token = create_reset_token(user.username)
        reset_link = f"http://localhost:3000/reset-password?token={token}"
        print(f"[RESET PASSWORD] Reset link for {user.username} ({data.email}): {reset_link}")
        return {
            "message": "If the email exists, reset instructions have been sent",
            "reset_token": token,  # dev/testing only
        }
    # 不管用户存不存在，都返回同样的消息（防止邮箱枚举）
    return {"message": "If the email exists, reset instructions have been sent"}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """重置密码"""
    username = verify_reset_token(data.token)
    if username is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password reset successfully"}