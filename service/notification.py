from celery_tasks import celery_tasks
from fastapi import HTTPException
from models.user import User
from repositories.notification_repository import NotificationRepository

from service import auth


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository= None, auth_service: auth.AuthService= None):
        
        self.notification_repo= notification_repo
        self.auth_service= auth_service
        
    async def notify_admin_of_post(
        self, 
        title: str,
        author: User, 
        message: str, 
        entity_id: int,
        entity_type: int
        ) -> bool:
        
        admin= await self.auth_service.get_admin_email()
        
        await self.notification_repo.create_object({
            "sender_id": author.id,
            "recipient_id": admin.id,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "message": message,
            "notification_type": "Post Approval"
        })  

        celery_tasks.aproval_needed_task.delay(admin.email, author.username, title)
        
        return True
    
       
    async def notify_author(
        self, 
        post_title: str,
        message: str, 
        recipient_id: int, 
        sender_id: int, 
        entity_id: int, 
        entity_type: str
        ) -> bool:
   
        
        await self.notification_repo.create_object({
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "message": message,
            "notification_type": "Post Notification"
        })
        
        author= await self.auth_service.get_user(user_id= recipient_id)
        celery_tasks.notify_author_task.delay(author.email, post_title)
        
        return True
    
    
    async def replied_comment_notification(
        self,  
        entity_id: int,
        message: str, 
        sender_id: int, 
        recipient_id: int
        ) -> bool:
        
        
        await self.notification_repo.create_object({
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "entity_id": entity_id,
            "entity_type": "Comment",
            "message": message,
            "notification_type": "Replied comment"
        })
        
        return True
    
    
    async def notify_user(
        self,  
        message: str, 
        sender_id: int, 
        recipient_id: int
        ) -> bool:
        
        
        await self.notification_repo.create_object({
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "entity_id": recipient_id,
            "entity_type": "User",
            "message": message,
            "notification_type": "Admin Notification"
        })
        
        return True
    
    async def get_user_notifications(self, current_user: User, limit: int, offset: int):
        
        db_notification= await self.notification_repo.get_all_my_notiffication(user_id=current_user.id, limit= limit, offset= offset)
        if not db_notification:
            return []
        return db_notification
        
    
    
    async def get_notifications_by_id(self, current_user: User, notification_id: int):
        
        db_notification= await self.notification_repo.get_by_model_id(notification_id)
        
        if not db_notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        if db_notification.recipient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unable to access")
        
        db_notification.is_read = True
        await self.notification_repo.update_object(db_notification)
        return db_notification
         
         
    async def delete(self, notification_id, current_user: User):
        
        db_notification= await self.get_notifications_by_id(
            notification_id= notification_id, 
            current_user= current_user)
        
        return await self.notification_repo.delete_object(db_notification)

