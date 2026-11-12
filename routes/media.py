from fastapi import APIRouter, Depends
from models.user import User
from schemas.media import MediaResponse
from service import media
from utility.dependency import (
    admin_or_author_required,
    admin_required,
    current_user,
    get_media_service,
)

router= APIRouter()



@router.get('/', status_code= 200, response_model= list[MediaResponse])
async def view_all_media(
    offset: int= 0,
    limit: int= 20,
    admin: User= Depends(admin_required), 
    service: media.MediaService= Depends(get_media_service)):
    
    return await service.get_all_media(offset= offset, limit= limit)


@router.get('/me', status_code= 200, response_model= list[MediaResponse])
async def view_my_medias(
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(admin_or_author_required), 
    service: media.MediaService= Depends(get_media_service)):
    
    return await service.get_my_medias(current_user= current_user, limit= limit, offset= offset)

 

@router.get('/{media_id}', status_code= 200, response_model= MediaResponse)
async def view_media(
    media_id: int,     
    current_user: User= Depends(current_user),
    service: media.MediaService= Depends(get_media_service)):
    return await service.get_media_by_id(media_id= media_id)




@router.delete('/{media_id}', status_code= 204)
async def delete_media(
    image_id: int, 
    current_user: User= Depends(admin_required),
    service: media.MediaService= Depends(get_media_service)):
    
    await service.delete_media(media_id= image_id)
