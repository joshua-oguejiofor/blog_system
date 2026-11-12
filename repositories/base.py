"""This Base file contains basic operations for service layer """

from typing import Generic, TypeVar

from models.base import Base
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    #this will run once the class instance is called
    def __init__(self, model: type[ModelType], db: AsyncSession):# set to acept two arguments
        self.model = model #dependency injection for model
        self.db = db #dependency injection for database
    
    
    async def get_by_slug(self, slug: str):
        return await self.db.scalar(select(self.model).where(self.model.slug == slug))
    
   
    async def get_by_model_id(self, id: int) -> ModelType | None:
        return await self.db.get(self.model, id)
        
    
    async def get_all(self, offset: int, limit: int, related_table= None, filters= None, order_by= None) -> list[ModelType]:
        
        query= select(self.model)

        if related_table is not None:
            query= query.options(selectinload(related_table))
        
        if filters is not None:
            query= query.where(*filters)
            
        if order_by is not None:
            query= query.order_by(order_by)

        query= query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
        

    
    

    async def create_object(self, data: dict) -> ModelType:
        obj = self.model(**data)
        
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


    async def update_object(self, obj: ModelType) -> ModelType:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


    async def delete_object(self, obj: ModelType) -> None:
        await self.db.delete(obj)
        await self.db.flush()

