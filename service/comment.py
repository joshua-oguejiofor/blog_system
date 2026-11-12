from fastapi import HTTPException
from models.user import User
from repositories.comment_repository import CommentRepository
from schemas import comment

from service import notification, post


class CommentService:
    def __init__(self, comment_repo: CommentRepository, post_service: post.PostService= None, notification_service: notification.NotificationService= None):
        self.comment_repo= comment_repo
        self.post_service= post_service
        self.notification_service= notification_service



    async def create(self, data: comment.CreateComment, current_user: User):
        
        db_post= await self.post_service.get_post_by_id(post_id=data.post_id, user=current_user)
        db_comment= await self.comment_repo.create_object({
            "post_id": db_post.id,
            "user_id": current_user.id,
            "content": data.content,
            })
        
        message= f"{current_user.username} commented on your {db_post.title} post"
        await self.notification_service.notify_author(
            message= message,
            post_title= db_post.title,
            entity_id= db_comment.id,
            entity_type= "Comment",
            sender_id= current_user.id,
            recipient_id= db_post.author_id
        )
        return True


    async def get_all_post_comment(self, post_id: int, limit: int, offset: int):
        
        comment = await self.comment_repo.get_all_comment(post_id= post_id, limit= limit, offset= offset)
        if not comment:
            return []
        
        return comment


    async def get_comment_by_id(self, comment_id: int):
        
        comment= await self.comment_repo.get_by_model_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment



    async def update(self, current_user: User, data: comment.UpdateComment):
        
        db_comment = await self.get_comment_by_id(data.comment_id)
        
        if db_comment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unable to access")

        db_comment.parent_id= db_comment.parent_id
        db_comment.post_id= db_comment.post_id
        db_comment.user_id= current_user.id
        db_comment.content= data.content
            
        return await self.comment_repo.update_object(db_comment)


    async def reply_to_comment(self, current_user: User, data: comment.RplyComment):
        
        db_comment= await self.get_comment_by_id(data.parent_id)
        
        replied_comment= await self.comment_repo.create_object({
            "post_id": db_comment.post_id,
            "user_id": current_user.id,
            "parent_id": db_comment.id,
            "content": data.content
        })
        
        message= f"{current_user.username} replied to your comment {db_comment.content}"
        await self.notification_service.replied_comment_notification(
            message= message,
            sender_id= current_user.id,
            recipient_id= db_comment.user_id,
            entity_id= replied_comment.id,
        )
    
        return True
        
        
    async def delete(self, comment_id: int, current_user: User):
        
        db_comment = await self.get_comment_by_id(comment_id)
        
        if db_comment.user_id != current_user.id and current_user.role.value not in ["admin", "author"]:
            raise HTTPException(status_code= 403, detail= "Unable to delete")

        return await self.comment_repo.delete_object(db_comment)


