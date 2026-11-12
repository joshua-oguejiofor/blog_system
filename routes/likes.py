from fastapi import APIRouter, Depends
from models.user import User
from schemas.likes import LikeResponse
from service.like import LikeService
from utility.dependency import current_user, get_like_service

router = APIRouter()


@router.post("/{post_id}/toggle", status_code=200)
async def toggle_like(
    post_id: int,
    current_user: User= Depends(current_user),
    service: LikeService = Depends(get_like_service)):
    
    return await service.toggle_like(current_user= current_user, post_id= post_id)


@router.get("/", status_code=200, response_model=list[LikeResponse])
async def get_likes(post_id: int,
    current_user: User= Depends(current_user),
    service: LikeService = Depends(get_like_service)):
    
    return await service.view_all_post_likes(post_id)


@router.get("/me", status_code=200, response_model=list[LikeResponse])
async def get_liked_post(
    post_id: int, 
    current_user: User= Depends(current_user),
    service: LikeService = Depends(get_like_service)):
    
    return await service.view_my_likes(post_id=post_id, user_id= current_user.id)

