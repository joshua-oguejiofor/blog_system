from fastapi import HTTPException
from repositories.category_repository import CategoryRepository
from schemas.category import CreateCategory
from slugify import slugify

from .audit import AuditService


class CategoryService:
    def __init__(self, category_repo: CategoryRepository, audit_service: AuditService):
        self.category_repo= category_repo
        self.audit_service= audit_service
        
        
    async def create(self, data: CreateCategory) -> bool:
        
        if await self.category_repo.get_name(data.name):
            raise HTTPException(status_code=409, detail= f"Name '{data.name}' already exist.")
        
        base_slug= slugify(data.name)
        slug= base_slug
        counter= 1
        
        while await self.category_repo.get_slug(slug):
            slug= f"{base_slug}-{counter}"
            counter += 1
        
        category= {
            "name": data.name,
            "slug": slug,
            "description": data.description
        }
        await self.category_repo.create_object(category)
        return True
    
    
    async def get_all_Category(self, limit: int, offset: int):
        
        return await self.category_repo.get_category(limit= limit, offset= offset)
    
    
    async def update(self, category_id: int, data: CreateCategory) -> bool:
        
        db_category= await self.category_repo.get_by_model_id(category_id)
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found.")
        
        base_slug= slugify(data.name)
        slug= base_slug
        counter= 1
        
        while await self.category_repo.get_slug(slug):
            slug= f"{base_slug}-{counter}"
            counter += 1
            
        db_category.name= data.name
        db_category.slug= slug
        db_category.description= data.description
        
        await self.category_repo.update_object(db_category)
        return True
    
    
    async def delete(self, category_id: int) -> bool:
        
        db_category= await self.category_repo.get_by_model_id(category_id)
        if not db_category:
            raise HTTPException(status_code= 404, detail= f"category with id '{category_id} not found")
        
        return await self.category_repo.delete_object(db_category)
        