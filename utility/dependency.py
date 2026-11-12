from __future__ import annotations

import logging

from core import redis_setup
from core.database import get_db
from core.security import decode_token
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

logger= logging.getLogger(__name__)



async def current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: AsyncSession = Depends(get_db)) -> User:
    token= credentials.credentials
    
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    if await redis_setup.is_token_blacklisted(token):
        raise credentials_exception
     
    try:
        payload= decode_token(token)
        
    except ValueError:
        raise credentials_exception
    
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    user_repo = auth_repository.AuthRepository(db)
    user = await user_repo.get_by_model_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail= "User not found")    
    
    if not user.username:
        raise HTTPException(status_code=403, detail= "No profile dected, be sure to create a profile for ths account.")    
    
    if user.acct_status.value != "active": 
        raise HTTPException(status_code=403, detail=f"Account deceted to be '{user.acct_status.value}' contact our support team if you feel this is a mistake.")
    
    return user




async def admin_required(admin: User= Depends(current_user)) -> User:
    
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return admin


async def admin_or_author_required(admin_or_author: User= Depends(current_user)) -> User:
    
    if admin_or_author.role.value not in ["admin", "author"]:
        raise HTTPException(status_code=403, detail="Unable to access")
    
    return admin_or_author


"""Repositories dependency injection(DI)
Reason for this method is to avoid thight coupling and 
multilpe DI at the route layer.
For consistency each function have it needed repository
"""

from repositories import (
    audit_repository,
    auth_repository,
    bookmark_repository,
    category_repository,
    comment_repository,
    like_repository,
    media_repository,
    notification_repository,
    post_repository,
    tag_repository,
    user_repository,
)
from service import (
    audit,
    auth,
    bookmark,
    category,
    comment,
    like,
    media,
    notification,
    post,
    tags,
    user,
)


def get_audit_service(db: AsyncSession= Depends(get_db)):
    audit_repo = audit_repository.AuditRepository(db)
    return audit.AuditService(audit_repo= audit_repo)
    

#verified
def get_auth_service(db: AsyncSession= Depends(get_db)):
    auth_repo= auth_repository.AuthRepository(db)
    audit_service= get_audit_service(db)
    return auth.AuthService(auth_repo= auth_repo, audit_service= audit_service)

 #verified
def get_user_service(db: AsyncSession = Depends(get_db)):
    user_repo=  user_repository.UserRepository(db)
    auth_service= get_auth_service(db)
    audit_service= get_audit_service(db)
    return user.UserService(
        user_repo= user_repo, 
        auth_service= auth_service, 
        audit_service= audit_service)
       
  
 #verified 
def get_post_service(db: AsyncSession = Depends(get_db)):
    media_service= get_media_service(db)
    post_repo =  post_repository.PostRepository(db)
    audit_service= get_audit_service(db)
    notification_service= get_notification_service(db)
    tag_service= get_tag_service(db)
    return post.PostService(
        tag_service= tag_service, 
        media_service= media_service, 
        post_repo= post_repo, 
        audit_service= audit_service, 
        notification_service= notification_service)
    
     
 #verified
def get_cetegory_service(db: AsyncSession = Depends(get_db)):
    category_repo =  category_repository.CategoryRepository(db)
    audit_service= get_audit_service(db)
    return category.CategoryService(category_repo, audit_service)
   
    #verified
def get_media_service(db: AsyncSession = Depends(get_db)):
    media_repo =  media_repository.MediaRepository(db)
    audit_service= get_audit_service(db)
    return media.MediaService(media_repo= media_repo, audit_service= audit_service)

 #verified
def get_tag_service(db: AsyncSession= Depends(get_db)):
    tag_repo= tag_repository.TagRepository(db)
    audit_service= get_audit_service(db)
    return tags.TagService(tag_repo, audit_service)


"""will stll add post service to complete this section"""
def get_bookmark_service(db: AsyncSession= Depends(get_db)):
    bookmark_repo= bookmark_repository.BookMarkRepositroy(db)
    post_service = get_post_service(db)
    return bookmark.BookMarkService(bookmark_repo= bookmark_repo, post_service=post_service)

def get_notification_service(db: AsyncSession= Depends(get_db)):
    notification_repo= notification_repository.NotificationRepository(db)
    auth_service= get_auth_service(db)
    return notification.NotificationService(notification_repo= notification_repo, auth_service= auth_service)

 #verified
def get_like_service(db: AsyncSession= Depends(get_db)):
    like_repo= like_repository.LikeRepository(db)
    post_service= get_post_service(db)
    return like.LikeService(like_repo, post_service= post_service)

 #verified
def get_comment_service(db: AsyncSession= Depends(get_db)):
    comment_repo= comment_repository.CommentRepository(db)
    post_service= get_post_service(db)
    notification_service= get_notification_service(db)
    return comment.CommentService(notification_service= notification_service, comment_repo= comment_repo, post_service= post_service)