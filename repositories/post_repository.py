from models.post_tag import Post, Tags
from schemas.base import PostStatus
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    # This will run once the class instance is called
    def __init__(self, db: AsyncSession):# Have one parameter to acept one argument when the class is called
        super().__init__(Post, db)# This is calling the parent class and passing two arguments corresponding to the parent class parameter
    
    
    async def get_post_by_id(self, post_id):
        result=  await self.db.execute(
            select(Post)
            .options(selectinload(Post.media))
            .where(Post.id == post_id)
        )
        return result.scalar_one_or_none()
      
    
    async def get_all_post(self, offset: int, limit: int):
        
        result= await self.db.execute(
            select(Post)
            .options(selectinload(Post.media))
            .where(Post.status == PostStatus.PUBLISHED)
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
      
    # Admin view only
    async def get_all_blog_post(self, offset: int, limit: int):
        
        result= await self.db.execute(
            select(Post)
            .options(selectinload(Post.media))
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
      
    
    async def get_my_posts(self, author_id: int, offset: int, limit: int):
        
        result= await self.db.execute(
            select(Post)
            .options(selectinload(Post.media))
            .where(Post.author_id == author_id)
            .order_by(Post.title)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
      
    
    async def get_all_excerpt(self, offset: int, limit: int):
                
        result= await self.db.execute(
            select(Post)
            .where(Post.status == PostStatus.PUBLISHED)
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
    
    
    async def search_for_post(self, search: str, offset: int, limit: int):
        result= await self.db.execute(
            select(Post)
            .outerjoin(Post.tags)
            
            .where(
            or_(
                Post.title.ilike(f"%{search}%"),
                Tags.name.ilike(f"%{search}%"),
                Post.excerpt.ilike(f"%{search}%"),
            ), Post.status == PostStatus.PUBLISHED)
            .distinct()
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit))
        
        return result.scalars().all()

    
    async def get_post_with_tag(self, post_id: int) -> Post | None:
        result = await self.db.execute(
            select(Post).where(Post.id == post_id)
            .options(selectinload(Post.tags))
        )
        return result.scalar_one_or_none()
    
    async def save_post(self, post: Post):
        self.db.add(post)
        await self.db.flush()
        await self.db.refresh(post)
        return post
        
    
    