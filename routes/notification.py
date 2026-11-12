from fastapi import APIRouter, Depends
from models.user import User
from schemas.notification import NotificationResponse
from service.notification import NotificationService
from utility.dependency import admin_required, current_user, get_notification_service

router= APIRouter()



@router.post('/', status_code=200)
async def notify_user(
    user_id: int,
    message: str,
    current_user: User= Depends(admin_required),
    service: NotificationService= Depends(get_notification_service)
):
    await service.notify_user(recipient_id= user_id, message= message, sender_id= current_user.id)
    return {"msg": "Notification sent successfully"}
    
    
"""Will add /me"""
@router.get('/', status_code=200, response_model= list[NotificationResponse])
async def get_all_notifications(
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(current_user),
    service: NotificationService= Depends(get_notification_service)
):
    return await service.get_user_notifications(current_user= current_user, limit= limit, offset= offset)


  
@router.get('/{notification_id}', status_code=200, response_model= NotificationResponse)
async def view_notification(
    notification_id: int,
    current_user: User= Depends(current_user),
    service: NotificationService= Depends(get_notification_service)
):
    return await service.get_notifications_by_id(notification_id= notification_id, current_user= current_user)


 

@router.delete('/{notification_id}', status_code=204)
async def delete_notification(
    notification_id: int,
    current_user: User= Depends(current_user),
    service: NotificationService= Depends(get_notification_service)
):
    await service.delete(notification_id= notification_id, current_user= current_user)

    
