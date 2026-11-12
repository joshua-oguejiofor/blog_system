from fastapi import APIRouter, Depends
from models.user import User
from schemas.tags import CreateTag, TagResponse
from service.tags import TagService
from utility.dependency import admin_required, current_user, get_tag_service

router= APIRouter()


@router.post('/', status_code=201)
async def create_tag(
    tag: CreateTag,
    admin: User= Depends(admin_required),
    service: TagService= Depends(get_tag_service)
):
    await service.create(tag.name)
    return {"msg":"Tag created successfully"}


@router.get('/', status_code=200, response_model= list[TagResponse])
async def view_all_tag(
    offset: int= 0,
    limit: int= 20,
    current_user: dict= Depends(current_user),
    service: TagService= Depends(get_tag_service)
):
    return await service.get_tags(offset= offset, limit= limit)



@router.put('/{tag_id}', status_code=200)
async def update_tag(    
    tag: CreateTag,
    tag_id: int,
    admin: User= Depends(admin_required),
    service: TagService= Depends(get_tag_service)
):
    await service.update(tag_id, tag.name)
    return {"msg":"Updated successfully"}



@router.delete('/{tag_id}', status_code=204)
async def delete_tag(
    tag_id: int,
    admin: User= Depends(admin_required),
    service: TagService= Depends(get_tag_service)
):
    await service.delete(tag_id)
