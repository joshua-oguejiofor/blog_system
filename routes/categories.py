from fastapi import APIRouter, Depends
from models.user import User
from schemas.category import CategoryResponse, CreateCategory
from service.category import CategoryService
from utility.dependency import (
    admin_required,
    current_user,
    get_cetegory_service,
)

router= APIRouter()



@router.post('/', status_code=201)
async def create_category(
    data: CreateCategory,
    admin: User= Depends(admin_required),
    service: CategoryService= Depends(get_cetegory_service)):
    
    await service.create(data)
    return {"msg":"Category created successfully"}


@router.get('/', status_code= 200, response_model= list[CategoryResponse])
async def get_category(
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(current_user),
    service: CategoryService= Depends(get_cetegory_service)):
        
    return await service.get_all_Category(limit= limit, offset= offset)


@router.put('/{category_id}', status_code= 200)
async def update(
    category_id: int,
    data: CreateCategory,
    admin: User= Depends(admin_required),
    service: CategoryService= Depends(get_cetegory_service)):
        
    await service.update(category_id, data)
    return {"msg":"Category updated successfully"}



@router.delete('/{category_id}', status_code= 204)
async def delete_category(
    category_id: int,
    admin: User= Depends(admin_required),
    service: CategoryService= Depends(get_cetegory_service)):
        
    await service.delete(category_id)
    

