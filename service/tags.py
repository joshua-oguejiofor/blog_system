from fastapi import HTTPException
from models.post_tag import Tags
from repositories.tag_repository import TagRepository
from slugify import slugify

from service.audit import AuditService


class TagService:
    def __init__(self, tag_repo: TagRepository, audit_service: AuditService):
        self.tag_repo= tag_repo
        self.audit_service= audit_service
        
    
    # Admin only
    async def create(self, tag_name: str) -> bool:
        
        if await self.tag_repo.get_tag_name(tag_name):
            raise HTTPException(status_code=409, detail= f"Name '{tag_name}' already exist")
        
        slug= slugify(tag_name)
        await self.tag_repo.create_object({
            "name": tag_name,
            "slug": slug
        })
        return True
        
    
    """Retrieves existing tags and creates any missing tags in the database."""    
    async def get_or_create_tags(self, tag_names: list[str]) -> list[Tags]:
        
        # levraging set to avoid duplactes
        parsed_names = set()
        for names in tag_names:
            
            if not names:
                return None
            
            for split_name in names.split(","):
                parsed_names.add(split_name)
            
        unique_names = list(parsed_names)

        existing_tags = await self.tag_repo.check_tags(unique_names)
          
        existing_map = {tag.name: tag for tag in existing_tags}
        tags = []
        
        for name in unique_names:
            if name in existing_map:
                tags.append(existing_map[name])
            else:
                slug = slugify(name)
                new_tag = await self.tag_repo.create_object({
                    "name": name,
                    "slug": slug
                })
                tags.append(new_tag)
        
        return tags


    
    async def get_tags(self, limit: int, offset: int) -> list[Tags]:
        return await self.tag_repo.get_all_tags(limit= limit, offset= offset)
    
    
    
    async def update(self, tag_id: int, tag_name: str) -> bool:
        
        db_tag=  await self.tag_repo.get_by_model_id(tag_id)
        if not db_tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        if await self.tag_repo.get_tag_name(tag_name):
            raise HTTPException(status_code=409, detail= f"Name '{tag_name}' already exist")
        
        slug= slugify(tag_name)
        
        db_tag.name= tag_name
        db_tag.slug= slug
        
        
        await self.tag_repo.update_object(db_tag)
        return True
    
    
    async def delete(self, tag_id: int) -> bool:
        
        db_tag= await self.tag_repo.get_by_model_id(tag_id)
        if not db_tag: 
            raise HTTPException(status_code=404, detail=f"Tag with id '{tag_id} not found")
        
        await self.tag_repo.delete_object(db_tag)
        return True
    
    
    
    
    

