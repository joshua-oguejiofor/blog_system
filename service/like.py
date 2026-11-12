from models.user import User
from repositories.like_repository import LikeRepository

from service import post


class LikeService:
    def __init__(self, like_repo: LikeRepository, post_service: post.PostService):
        self.like_repo = like_repo
        self.post_service= post_service

    async def toggle_like(self, current_user: User, post_id: int):
        
        await self.post_service.get_post_by_id(post_id=post_id, user=current_user)
        
        existing = await self.like_repo.like_exists(user_id= current_user.id, post_id= post_id)

        if existing:
            await self.like_repo.delete_object(existing)
            return {"count": await self.like_repo.count_post_likes(post_id)}

        like= {"user_id": current_user.id, "post_id": post_id}
        
        await self.like_repo.create_object(like)
        return {"count": await self.like_repo.count_post_likes(post_id)}


    #View all user that liked a post
    async def view_all_post_likes(self, post_id: int):
        
        result=  await self.like_repo.get_post_likes(post_id)
        if not result:
            return []
        return  result
    
    
    #user viewing post that they liked
    async def view_my_likes(self, post_id: int, user_id: int):
        
        result=  await self.like_repo.check_user_likes(post_id=post_id, user_id=user_id)
        if not result:
            return []
        return result


