import asyncio

import cloudinary
import cloudinary.uploader
from core.config import settings  # Assuming your keys are in a config/env file
from fastapi import UploadFile

# 1. Configure the SDK
cloud_config = cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY.get_secret_value(),
    api_secret=settings.CLOUDINARY_API_SECRET.get_secret_value(),
    secure=True # Ensures HTTPS URLs are generated
)


async def save_to_cloud(file: UploadFile, folder_path: str, custom_filename: str):
    #The tread runs a function that's why the cloud uploder if in line 
    #with the rest of the parameter cause the tred runs the first parameter
    #as the function.
    return await asyncio.to_thread( 
        cloudinary.uploader.upload,
        file= file.file,
        folder= folder_path,
        public_id= custom_filename,
        overwrite=True,            # Safe because we explicitly intend to replace this exact slot
        resource_type="auto" # Handles images or video automatically
    )


async def delete_from_cloud(media_url: str):
    return await asyncio.to_thread( 
        cloudinary.uploader.destroy,
        media_url, invalidate=True)

    
