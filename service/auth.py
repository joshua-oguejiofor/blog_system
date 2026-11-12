"""
This auth_service handles validation for authentication and use repository methods to 
execute the corresponding database operation there-by 
following the "single responsibility principles"

all method will be async to support concurrency

"""

import logging
import time

from fastapi import HTTPException
from fastapi.responses import RedirectResponse

from celery_tasks import celery_tasks
from core import redis_setup, security
from core.config import settings
from models.user import User
from repositories import auth_repository
from schemas import base, user
from service import audit

logger= logging.getLogger(__name__)


    

class AuthService:
    def __init__(self, auth_repo: auth_repository.AuthRepository, audit_service: audit.AuditService= None):
        self.auth_repo= auth_repo 
        self.audit_service= audit_service
    
    async def register(self, data: user.UserSchema) -> bool:
        

        # databese consistency for unique constraint[email]
        if await self.auth_repo.get_by_email(data.email):
            raise HTTPException(status_code=409, detail="Email already exist")
        
        added_user = await self.auth_repo.create_object({
            "email": data.email,
            "hashed_password": security.hash_password(data.password),
            "role": base.UserRole.READER,
            "acct_status": base.AccountStatus.PENDING,
            "is_verified": False
        })

        await self.audit_service.create_auditlog({
            "user_id": added_user.id,
            "action": f"{added_user.email} registered",
            "entity": "User",
            "entity_id": added_user.id
        })
        
        token= security.create_email_verification_token({"sub": str(added_user.id)})
        celery_tasks.email_verify_token_task.delay(added_user.email, token)
        return True
    
        
    async def email_verify_token(self, token: str) -> RedirectResponse:
        
        if await redis_setup.is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Session expired.")
        
        try:
            payload= security.decode_token(token)
        except ValueError as e:
            return RedirectResponse(
            url= f"{settings.FRONTEND_URL}/error?msg={str(e)}", status_code= 302
        ) 
        
        if payload.get("type") != "verify_email":
            return RedirectResponse(
            url= f"{settings.FRONTEND_URL}/error?msg=invalid-token-type", status_code= 302
        )
              
        user_id= int(payload.get("sub"))
        db_user= await self.auth_repo.get_by_model_id(user_id)
        if not db_user:
            return RedirectResponse(
            url= f"{settings.FRONTEND_URL}/error?msg=user-not-found", status_code= 302
        )
            
        if db_user.is_verified:
            return RedirectResponse(url= f"{settings.FRONTEND_URL}/error?msg=user-already-verified", status_code=302)
        
        remaining_time= max(payload.get("exp") - int(time.time()), 1)
    
        db_user.is_verified= True
        db_user.acct_status=  base.AccountStatus.ACTIVE
        
        await self.auth_repo.update_object(db_user)
        await self.audit_service.create_auditlog({
                "user_id": db_user.id,
                "action": f"{db_user.email} verified",
                "entity": "User",
                "entity_id": db_user.id
            })
       
        
        await redis_setup.invalidate_token(token, remaining_time)
        logger.info(f"Email verified successfully for user {db_user.id}")   
        return RedirectResponse( url= f"{settings.FRONTEND_URL}/verified?status=success", status_code= 302)
        
    
    async def login(self, data: user.UserSchema) -> user.TokenResponse:
        
        db_user= await self.auth_repo.get_by_email(data.email)
            
        if not db_user or not security.verify_password(data.password, db_user.hashed_password):            
            raise HTTPException(status_code= 401, detail= "Invalid credentials for password and email.")

        if db_user.acct_status == base.AccountStatus.DELETED:
            raise HTTPException(status_code=404, detail="User of such dose not exist")
        
        if not db_user.is_verified:
            raise HTTPException(status_code=401, detail="Please verify your email before logging in.")

        if db_user.acct_status.value != base.AccountStatus.ACTIVE:
            raise HTTPException(status_code=401, detail=f"Your account has been {db_user.acct_status.value}. Contact support.")
        
        access_token = security.create_access_token({"sub": str(db_user.id), "role": db_user.role})
        refresh_token= security.create_refresh_token({"sub": str(db_user.id)})
        
        exp= settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60    #calculated in seconds to complete 7 days
        username = db_user.username if db_user.username else db_user.email
        await redis_setup.set_refresh_token(db_user.id, exp, refresh_token)
        celery_tasks.login_notification_task.delay(db_user.email, username)

        return user.TokenResponse(access_token= access_token, refresh_token= refresh_token)



    async def refresh_token(self, refresh_token: str) -> user.TokenResponse:
        
        try:
            payload= security.decode_token(refresh_token)
            
        except ValueError as e:
            raise HTTPException(status_code=401, detail=f"{str(e)}")
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id= payload.get("sub")
 
        stored_refresh_token= await redis_setup.get_refresh_token(user_id)
        if stored_refresh_token != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        await redis_setup.delete_cache(f"refresh:{user_id}")
        
        new_access_token = security.create_access_token({"sub": str(user_id), "role": payload.get("role")})
        new_refresh_token = security.create_refresh_token({"sub": str(user_id)})
        exp= settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60    #calculated in seconds to complete 7 days
        
        await redis_setup.set_refresh_token(user_id, exp, new_refresh_token)
        
        return user.TokenResponse(access_token= new_access_token, refresh_token= new_refresh_token)


    async def change_password(self, old_password: str, new_password: str, user: User)-> bool:
       
        user= await self.auth_repo.get_by_model_id(user.id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not security.verify_password(old_password, user.hashed_password):
            raise HTTPException(status_code= 400, detail= "Old password is invalid")    
        
        user.hashed_password= security.hash_password(new_password)
        await self.auth_repo.update_object(user)
        
        await self.audit_service.create_auditlog({
            "user_id": user.id,
            "action": f"{user.username} changed password",
            "entity": "User",
            "entity_id": user.id
        })
        return True


    async def forget_password(self, email: str) -> bool:

        user= await self.auth_repo.get_by_email(email)  
        # This message tricks an invalid user
        if not user:
            return {"msg": "If the account exists, an OTP has been sent"}
        
        otp= security.generate_otp()
        await redis_setup.set_otp(email, 10, otp)#set to expire 10 minutes
        celery_tasks.password_reset_code_task.delay(email, otp)
        
        return True
    
    
    async def verify_otp(self, email: str, otp: str):
        
        stored_otp= await redis_setup.get_otp(email)
        if not stored_otp:
            raise HTTPException(status_code=401, detail="OTP expired")
        
        if stored_otp != otp:
            raise HTTPException(status_code=401, detail="Invalid OTP")
                
        reset_token= security.create_password_reset_token({"sub": email})
        await redis_setup.delete_cache(f"otp:{email}")

        return {"reset_token": reset_token}


    async def reset_password(self, reset_token: str, new_password: str) -> bool:
        
        if await redis_setup.is_token_blacklisted(reset_token):
            raise HTTPException(status_code=401, detail="Expired reset token")
        try:

                payload = security.decode_token(reset_token)
        except ValueError as e:
            raise HTTPException(status_code=401, detail= str(e))
        
        email= payload.get("sub")

        db_user = await self.auth_repo.get_by_email(email)
        db_user.hashed_password = security.hash_password(new_password)
        
        remaining_time= max(payload.get("exp") - int(time.time()), 1)
        
        await self.auth_repo.update_object(db_user)
        await redis_setup.invalidate_token(reset_token, remaining_time)

        await self.audit_service.create_auditlog({
            "user_id": db_user.id,
            "action": f"{db_user.username} changed password",
            "entity": "User",
            "entity_id": db_user.id
        })
        
        return True
        
    
    async def logout(self, access_token: str) -> bool:
        if await redis_setup.is_token_blacklisted(access_token):
            raise HTTPException(status_code=401, detail="Token revoked")
        
        try:    
            payload = security.decode_token(access_token)
        except ValueError as e:
            raise HTTPException(status_code=401, detail= str(e))

        remaining_time = max(payload.get("exp") - int(time.time()), 1)
        user_id= payload.get("sub")
        # Blacklist access token
        await redis_setup.invalidate_token(access_token, remaining_time)

        # Remove refresh token
        await redis_setup.delete_cache(f"refresh:{user_id}")
        return True


    
    async def delete_my_account(self, current_user: User):
        
        current_user.acct_status = base.AccountStatus.DELETED
        await self.auth_repo.update_object(current_user)
        
        return await self.audit_service.create_auditlog({
            "user_id": current_user.id,
            "action": f"{current_user.email} deleted account",
            "entity": "User",
            "entity_id": current_user.id
        })
        
        
    async def get_admin_email(self):
        return await self.auth_repo.get_admin() 
    
    
    async def get_user(self, user_id: int):
        
        user= await self.auth_repo.get_by_model_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    
    async def validate_username(self, username: str):
        username = await self.auth_repo.check_username(username)
        if username:
            raise HTTPException(status_code=409, detail="Username has being taken, try using another one")
        return True
    
     
    async def resend_email(self, email: str):
        
        db_user= await self.auth_repo.get_by_email(email)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if db_user.is_verified:
            raise HTTPException(status_code= 400, detail= "Email already verified.")
        
        token= security.create_email_verification_token({"sub": str(db_user.id)})
        celery_tasks.email_verify_token_task.delay(db_user.email, token)
        return True
    
    
