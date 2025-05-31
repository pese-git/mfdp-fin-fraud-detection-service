from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from database.database import get_session
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from models.user import TokenResponse, User
from services.crud import user as UserService
from typing import List

user_route = APIRouter(tags=['User'])
hash_password = HashPassword()

@user_route.post("/signup")
async def sign_new_user(user: User, session=Depends(get_session)) -> dict: 
    user_exist = UserService.get_user_by_email(user.email, session)
    
    if user_exist:
        raise HTTPException( 
        status_code=status.HTTP_409_CONFLICT, 
        detail="User with email provided exists already.")
    
    hashed_password = hash_password.create_hash(user.password)
    user.password = hashed_password 
    UserService.create_user(user, session)
    
    return {"message": "User created successfully"}

@user_route.post("/signin", response_model=TokenResponse)
async def sign_user_in(user: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)) -> dict: 
    user_exist = UserService.get_user_by_email(user.username, session)
    
    if user_exist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    if hash_password.verify_hash(user.password, user_exist.password):
        access_token = create_access_token(user_exist.email)
        return {"access_token": access_token, "token_type": "Bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )