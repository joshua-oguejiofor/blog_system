"""Bookmark will be eager loaded with post
This will be create, get by id, get all and remove"""

from fastapi import APIRouter, Depends
from models.user import User
from schemas.bookmark import BookMarkResponse
from service.bookmark import BookMarkService
from utility.dependency import current_user, get_bookmark_service

router= APIRouter()


@router.post('/', status_code=200)
async def create_bookmark(
    post_id: int,
    current_user: User= Depends(current_user),
    service: BookMarkService= Depends(get_bookmark_service)
):
    await service.create(post_id=post_id, current_user= current_user)
    return {"msg":"Post added to your bookmarks"}
    

@router.get('/', status_code=200, response_model=list[BookMarkResponse])
async def get_user_bookmarks(
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(current_user),
    service: BookMarkService= Depends(get_bookmark_service)
):
    return await service.get_all_user_bookmark(offset=offset, limit=limit, user_id= current_user.id)
    


@router.get('/{bookmark_id}', status_code=200, response_model=BookMarkResponse)
async def view_bookmark(
    bookmark_id: int,
    current_user: User= Depends(current_user),
    service: BookMarkService= Depends(get_bookmark_service)
):
    return await service.get_bookmark_by_id(bookmark_id=bookmark_id)
    


@router.delete('/{bookmark_id}', status_code=204)
async def delete_bookmark(
    bookmark_id: int,
    current_user: User= Depends(current_user),
    service: BookMarkService= Depends(get_bookmark_service)
):
    await service.remove_bookmark_by_id(bookmark_id=bookmark_id, user_id=current_user.id)
    
