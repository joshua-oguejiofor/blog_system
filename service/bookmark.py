from fastapi import HTTPException
from models.user import User
from repositories.bookmark_repository import BookMarkRepositroy

from service.post import PostService


class BookMarkService:
    def __init__(self, bookmark_repo: BookMarkRepositroy, post_service: PostService):
        self.bookmark_repo= bookmark_repo
        self.post_service = post_service
        
    async def create(self, post_id: int, current_user: User):        
        db_post = await self.post_service.get_post_by_id(post_id=post_id, user= current_user)
        
        bookmark_count, bookmark_id = await self.bookmark_repo.check_bookmark(user_id=current_user.id, post_id=db_post.id)
        if bookmark_count >= 200:
            raise HTTPException(
                status_code=400,
                detail="Bookmark limit reached. Remove a bookmarked post before adding a new one."
            )
        if bookmark_id:
            raise HTTPException(status_code=409, detail="post already bookmarked")
        
        bookmark= {
            "user_id": current_user.id,
            "post_id": db_post.id,
            "title_name": db_post.title
        }
        await self.bookmark_repo.create_object(bookmark)
        return True
    
    
    async def get_all_user_bookmark(self, user_id: int, offset: int, limit: int):
        
        db_bookmark= await self.bookmark_repo.get_user_bookmark(user_id= user_id, offset=offset, limit=limit)
        if not db_bookmark:
            return []
        return db_bookmark
    
    
    async def get_bookmark_by_id(self, bookmark_id):
        
        bookmark= await self.bookmark_repo.get_by_model_id(bookmark_id)
        if not bookmark:
            raise HTTPException(status_code=404, detail= f"Bookmark with id {bookmark_id} not found")
        
        return bookmark
    
    
    async def remove_bookmark_by_id(self, bookmark_id: int, user_id: int):
        
        bookmark= await self.get_bookmark_by_id(bookmark_id)
        
        if bookmark.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unable to delete")
        
        await self.bookmark_repo.delete_object(bookmark)
        return True
        
        
        
