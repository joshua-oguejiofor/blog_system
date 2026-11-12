
from uuid import uuid4

from core.config import settings
from fastapi import HTTPException, UploadFile
from models.user import User
from repositories.media_repository import MediaRepository
from schemas.base import UserRole
from slugify import slugify
from utility import cloud

from service.audit import AuditService


class MediaService:
    def __init__(self, media_repo: MediaRepository, audit_service: AuditService= None):
        self.media_repo= media_repo
        self.audit_service= audit_service
        
    
    async def create_media(
        self, post_title: str, 
        post_id: int, author: User, 
        file: UploadFile
        ) -> bool:
        

        image_type= settings.ALLOWED_IMAGE_TYPES
        media_type= settings.ALLOWED_MEDIA_TYPES 
        
        if file.content_type not in image_type and file.content_type not in media_type:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported media type for {file.content_type}. Allowed: {", ".join(settings.ALLOWED_IMAGE_TYPES)} or {", ".join(settings.ALLOWED_MEDIA_TYPES)}")
            
        # Read file size securely
        raw_size = len(await file.read())
        
        if file.content_type in media_type and raw_size > settings.MAX_MEDIA_SIZE:
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 20 MB limit")
        
        if file.content_type in image_type and raw_size > settings.MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail=f"Image {file.filename} exceeds 5 MB limit")
            
        # Reset file pointer back to the beginning after reading it
        await file.seek(0)
        
        folder_path = "blog/featured_images"        
        custom_filename = f"{slugify(post_title[:50])}-{uuid4().hex}"
        saved_media= await self.media_repo.create_object({
            "post_id": post_id,
            "file_name": file.filename,
            "file_size": raw_size,# / (1024 * 1024),
            "file_type": file.content_type,
            "uploaded_by": author.id,
        })
        
        # Upload media  to Cloudinary
        cloudinary_response = await cloud.save_to_cloud(
            file=file, 
            folder_path=folder_path,
            custom_filename=custom_filename
            )
        saved_media.public_id = cloudinary_response["public_id"]
        return True
        

    async def get_media_by_id(self, media_id: int):

        db_media = await self.media_repo.get_by_model_id(media_id)
        if not db_media:
            raise HTTPException(
                status_code=404, 
                detail=f"Media with id '{media_id}' not found")
        return db_media
    
    
    async def get_all_media(self, offset: int, limit: int):
        
        medias = await self.media_repo.get_medias(offset=offset, limit=limit)
        if not medias:
            return [] 
        return medias
    
    
    async def get_my_medias(self, current_user: User, offset: int, limit: int):
        
        medias = await self.media_repo.get_my_medias(user_id=current_user.id, offset=offset, limit=limit)
        if not medias:
            return []
        
        return medias
    
    
    async def update_media(
    self, post_title: str,
    media_id: int, author: User, 
    file: UploadFile
    ) -> bool:
        
        
        db_media = await self.get_media_by_id(media_id)

        image_types = settings.ALLOWED_IMAGE_TYPES
        media_types = settings.ALLOWED_MEDIA_TYPES

       
        if db_media.uploaded_by != author.id and author.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Unable to update.")

        # Validate file type
        if file.content_type not in image_types and file.content_type not in media_types:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported media type '{file.content_type}'. "
                    f"Allowed image types: {', '.join(image_types)}. "
                    f"Allowed media types: {', '.join(media_types)}."
                ))

        # Read file to determine size
        content = await file.read()
        raw_size = len(content)

        # Validate size
        if file.content_type in media_types and raw_size > settings.MAX_MEDIA_SIZE:
            raise HTTPException(status_code=400, detail=f"{file.filename} exceeds the maximum media size.")

        if file.content_type in image_types and raw_size > settings.MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail=f"{file.filename} exceeds the maximum image size.")

        # Reset the file pointer for Cloudinary upload
        await file.seek(0)

        # Update database object
        db_media.file_name = file.filename
        db_media.file_size = raw_size / (1024 * 1024)  # MB
        db_media.file_type = file.content_type
        db_media.uploaded_by = author.id

        #Case where the post title is updated
        folder_path = "blog/featured_images"        
        custom_filename = f"{slugify(post_title[:50])}-{uuid4().hex}"
        
        # Delete old Cloudinary resource after successful upload
        await cloud.delete_from_cloud(db_media.public_id)

        # Upload the replacement file
        response = await cloud.save_to_cloud(
            file=file,
            folder_path=folder_path, 
            custom_filename=custom_filename)
        
        
        db_media.public_id = response["public_id"] # Apend the media public_id after retriving from the cloud
        
        # Save changes
        await self.media_repo.update_object(db_media)

        return True
    
    
    
    # works from admin panel
    async def delete_media(self, media_id: int) -> bool:
        
        db_media= await self.get_media_by_id(media_id)
        
        await cloud.delete_from_cloud(media_url= db_media.public_id)
        await self.media_repo.delete_object(db_media)
        
        return True
    

    # if a post is deleted, the media willbe deleted from cloud storage
    async def delete_media_from_post(self, post_id: int) -> bool:
        
        db_media = await self.media_repo.delete_media_with_post(post_id=post_id)
        
        if not db_media:
            return None
        
        public_id = db_media.public_id
        
        await self.media_repo.delete_object(db_media)
                
        return public_id
