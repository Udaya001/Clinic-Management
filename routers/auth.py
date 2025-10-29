from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from datetime import timedelta
from models import User
from schemas import RegisterRequest, LoginRequest, StandardResponse, Token
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from database import get_db
from utils import generate_unique_id
from auth import get_password_hash
from config import settings

router = APIRouter()

@router.post("/login", response_model=StandardResponse)
async def login(login_request: LoginRequest):
    user = await authenticate_user(login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return StandardResponse(
        success=True,
        message="Login successful",
        data={"access_token": access_token, "token_type": "bearer"}
    )

@router.post("/register", response_model=StandardResponse)
async def register(register_request: RegisterRequest, db=Depends(get_db)):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": register_request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate user ID
    user_id = generate_unique_id("USR")
    
    user = User(
        user_id=user_id,
        user_name=register_request.user_name,
        email=register_request.email,
        phone=register_request.phone,
        role="admin",  # You might want to change this to a default role like "user"
        password=get_password_hash(register_request.password)
    )
    
    result = await db.users.insert_one(user.dict(by_alias=True))
    
    # Return user info without password
    user_dict = user.dict()
    if 'password' in user_dict:
        del user_dict['password']
    
    return StandardResponse(
        success=True,
        message="User registered successfully",
        data=user_dict
    )

# Example protected route
@router.get("/me", response_model=StandardResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    user_dict = current_user.dict()
    if 'password' in user_dict:
        del user_dict['password']
    
    return StandardResponse(
        success=True,
        message="User info retrieved successfully",
        data=user_dict
    )