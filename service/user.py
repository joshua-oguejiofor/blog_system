import json
from uuid import uuid4

from core.config import settings
from core.security import decode_token
from fastapi import HTTPException, UploadFile
from models.user import Profile, User
from repositories.user_repository import UserRepository
from schemas.base import UserRole
from utility import cloud

from service import audit, auth


class UserService:
    def __init__(self, user_repo: UserRepository, audit_service: audit.AuditService= None, auth_service: auth.AuthService= None):
        self.user_repo= user_repo
        self.audit_service= audit_service
        self.auth_service= auth_service
       
       
       
    async def create_profile(
        self, username : str,
        bio: str, 
        profile_photo: UploadFile,
        website_url: str,
        country: str,
        social_links: dict,
        token: str
        ) -> bool:
        
        
        try:
            payload= decode_token(token)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=f"{e}")
        
        if payload.get("type") != "access":
            raise HTTPException(status_code=400, detail="Access token required.")
        
        user_id= int(payload.get("sub"))
        
        await self.auth_service.validate_username(username)
        
        folder_path= None
        custom_filename= None
        
        if profile_photo:
            if profile_photo.content_type not in settings.ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported image type for {profile_photo.content_type}. Allowed: {", ".join(settings.ALLOWED_IMAGE_TYPES)}")
            
            raw_size= len(await profile_photo.read())
            if raw_size > settings.MAX_IMAGE_SIZE:
                raise HTTPException(status_code=400, detail="Image exceded 5 MB limit")
            
            await profile_photo.seek(0)
            
            custom_filename= f"{profile_photo.filename}-{uuid4().hex}"#added uuid to avoid conflicting image
            folder_path= "blog/profile-image/"
                            
        social_links_dict = json.loads(social_links) if social_links else {}

        saved_profile= await self.user_repo.create_object({
            "user_id": user_id,
            "bio": bio,
            "website_url": website_url,
            "country": country,
            "social_links": social_links_dict
        })
        
        db_profile= await self.user_repo.get_profile_by_id(saved_profile.id)
        db_profile.user.username = username
          
        if profile_photo:
            cloudinary_response = await cloud.save_to_cloud(
                    file= profile_photo, 
                    folder_path= folder_path,
                    custom_filename= custom_filename
                    )
            
            saved_profile.profile_image_public_id= cloudinary_response["public_id"]
            saved_profile.profile_mime= profile_photo.content_type
            
        return True
    
    
    async def view_profile(self, profile_id: int) -> Profile:
        
        profile= await self.user_repo.get_profile_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
       
        return profile
    
    
    
    async def view_all_profile(self, offset: int, limit: int) -> Profile:
        
        profile= await self.user_repo.get_all_profile(offset= offset, limit= limit)
        if not profile:
            return []
        return profile
    
   
    async def update_profile(
       self, 
        username : str, bio: str, 
        profile_photo: UploadFile, website_url: str,
        country: str, social_links: dict,
        current_user: User
        ) -> bool:
        
        db_profile= await self.user_repo.get_profile_by_user_id(current_user.id)
        if not db_profile:
            raise HTTPException(status_code=404, detail="No active user found")
          
        folder_path= None
        custom_filename= None
        
        if profile_photo:
            if profile_photo.content_type not in settings.ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported image type for {profile_photo.content_type}. Allowed: {", ".join(settings.ALLOWED_IMAGE_TYPES)}")
        
            raw= await profile_photo.read() 
            if len(raw) > settings.MAX_IMAGE_SIZE:
                raise HTTPException(status_code=400, detail="Image exceded 5 MB limit")
            
            await profile_photo.seek(0)
            
            custom_filename= f"{profile_photo.filename}-{uuid4().hex}"#added uuid to avoid conflicting image
            folder_path= "blog/profile-image/"
                            
        social_links_dict = json.loads(social_links) if social_links else {}
        
        db_profile.bio= bio
        db_profile. website_url= website_url
        db_profile.country= country
        db_profile.social_links= social_links_dict
        db_profile.user.username= username
        
         # Upload the replacement file
        if profile_photo: 
            response = await cloud.save_to_cloud(
                file= profile_photo,
                folder_path= folder_path, 
                custom_filename= custom_filename)
            
            if db_profile.profile_image_public_id:  
            # Delete old Cloudinary resource after successful upload
                await cloud.delete_from_cloud(db_profile.profile_image_public_id)

            db_profile.profile_image_public_id= response["public_id"]
            db_profile.profile_mime= profile_photo.content_type

        await self.user_repo.update_object(db_profile)
        
        return True
        
    """Will implement compensation action and for section where external service is used"""
    async def remove_image(self, current_user: User) -> bool:
        
        db_user= await self.user_repo.get_profile_by_user_id(current_user.id)
        if not db_user:
            raise HTTPException(status_code=404, detail= "Profile not found")
        if db_user.profile_image_public_id is None:
            raise HTTPException(status_code=404, detail= "Image not found")
        
        await cloud.delete_from_cloud(db_user.profile_image_public_id)
        
        db_user.profile_image_public_id= None
        db_user.profile_mime= None

        await self.user_repo.update_object(db_user)
        await self.audit_service.create_auditlog({
            "user_id": current_user.id,
            "action": f"{current_user.email} removed profile image",
            "entity": "Profile",
            "entity_id": db_user.id
        })        
        return True
        
        
    """database delete will be "set null"""
    async def delete_user_account(self, current_user: User) -> bool:
        if current_user.role == UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Unable to delete")
        return await self.auth_service.delete_my_account(current_user)
        
        
    
    
    async def get_user_by_username(self, username: str, limit: int, offset: int):
        return await self.user_repo.search_user(username= username, limit= limit, offset= offset)
        
 
     
    async def update_user_status(self, status: str, user_id: int, current_user: User):

        db_user= await self.auth_service.get_user(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if db_user.role == UserRole.ADMIN:
            raise HTTPException(status_code= 400, detail="Admin status change not supported")
        
        db_user.acct_status= status
        
        await self.audit_service.create_auditlog({
            "user_id": db_user.id,
            "action": f"{current_user.role.value} updated user account status",
            "entity": "User",
            "entity_id": db_user.id
        })
        return True
           
    
    async def update_user_role(self, role: str, user_id: int, current_user: User):  
        
        if role == UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Multiple admin not allowed")
        
        db_user= await self.auth_service.get_user(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if db_user.role == role:
            raise HTTPException(status_code=400, detail=f"User is alread a/an {role.value}")
        
        if db_user.role == UserRole.ADMIN:
            raise HTTPException(status_code= 400, detail="Admin role change not supported")
        
        db_user.role= role
        
        await self.audit_service.create_auditlog({
            "user_id": db_user.id,
            "action": f"{current_user.role.value} updated user account role",
            "entity": "User",
            "entity_id": db_user.id
            })
    
        return True











