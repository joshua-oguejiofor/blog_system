
import logging

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from middleware.rate_limiter import limiter
from models.user import User
from schemas import user
from service.auth import AuthService
from utility.dependency import current_user, get_auth_service

logger= logging.getLogger(__name__)


load_dotenv()

router= APIRouter()

 


#done
@router.post('/register', status_code= 201)
@limiter.limit("5/minute")
async def register(
    request: Request, 
    data: user.UserSchema, 
    service: AuthService= Depends(get_auth_service)):
    
    await service.register(data=data)
    return {"msg": "Check your email to continue verification process."}


@router.post('/register/resend-email', status_code=200)
@limiter.limit("5/minute")
async def resend_email(
    request: Request, 
    data: user.EmailVerification,
    service: AuthService= Depends(get_auth_service)):
    
    return await service.resend_email(email= data.email)
    



#User clicks the verification link which is eqivallent to a get request on the browser
#This is set to a get request to prevent "405 method not allowed"
#done
@router.get('/verify-email')
@limiter.limit("5/minute")
async def verify_token(
    request: Request, 
    token: str, 
    service: AuthService= Depends(get_auth_service)):
    
    return await service.email_verify_token(token)


#done
@router.post("/login", response_model=user.TokenResponse, status_code=200)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: user.UserSchema,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(data)

#done  
@router.post('/refresh-token', response_model= user.TokenResponse, status_code= 200)
@limiter.limit("5/minute")
async def refresh_token(
    request: Request, 
    credentials: HTTPAuthorizationCredentials= Depends(HTTPBearer()), 
    service: AuthService= Depends(get_auth_service)):
    
    token= credentials.credentials
    return await service.refresh_token(token)
    

#done
@router.patch('/password', status_code= 200)
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    data: user.ChangePassword,
    current_user: User= Depends(current_user), 
    service: AuthService= Depends(get_auth_service)):
    await service.change_password(data.old_password, data.new_password, user= current_user)
    return {"msg":"Password update successfull"}


#done
@router.post('/password-forget', status_code= 200)
@limiter.limit("5/minute")
async def forget_password(
    request: Request, 
    data: user.EmailVerification, 
    service: AuthService= Depends(get_auth_service)):
     
    
    await service.forget_password(data.email)
    
    return {"msg": "If the account exists, an OTP has been sent"}


@router.post('/password-forget/resend-otp', status_code= 200)
@limiter.limit("5/minute")
async def resend_otp(
    request: Request, 
    data: user.EmailVerification, 
    service: AuthService= Depends(get_auth_service)):
     
    
    await service.forget_password(data.email)
    
    return {"msg": "If the account exists, an OTP has been sent"}



#done
@router.post('/verify-otp', status_code=200)
@limiter.limit("5/minute")
async def verify_otp(
    request: Request, 
    data: user.OTPVerify,
    service: AuthService= Depends(get_auth_service)):
    
    return await service.verify_otp(email= data.email, otp= data.otp)
    


    
#done
@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(
    request: Request, 
    data: user.PasswordReset, 
    service: AuthService= Depends(get_auth_service)):

    await service.reset_password(reset_token= data.reset_token, new_password= data.new_password)
    
    return {"msg": "Password reset successfully"}



#done
@router.post('/logout', status_code=200)
@limiter.limit("5/minute")
async def logout(
    request: Request, 
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), # Extracted safely from header
    service: AuthService = Depends(get_auth_service)
):
    access_token= credentials.credentials
    
    await service.logout(access_token)

    return {"msg":"Logout successfully"}


