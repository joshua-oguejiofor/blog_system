import json

from bleach import clean
from core import redis_setup
from fastapi import HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from models.post_tag import Post
from models.user import User
from repositories.post_repository import PostRepository
from schemas import base, post
from slugify import slugify
from utility import cloud

from service import audit, media, notification, tags

"""service talks  to servce"""



class PostService:
    def __init__(
        self, post_repo: PostRepository, audit_service: audit.AuditService= None,
        media_service: media.MediaService= None,
        tag_service: tags.TagService= None,
        notification_service: notification.NotificationService= None): #Method overload
        self.post_repo= post_repo
        self.audit_service= audit_service
        self.notification_service= notification_service
        self.media_service= media_service
        self.tag_service= tag_service
       
       
         
    async def create(
        self, author: User, 
        category_id: int, title: str,
        content: str, tags_: list[str],
        file: UploadFile,
        ) -> bool:
        
        
        tags = await self.tag_service.get_or_create_tags(tag_names=tags_)
            
        #input sanitization
        title= clean(title)
        content= clean(content)
        
        excerpt= content[:100]# extract excerpt from content
        base_slug= slugify(title)# create slug
        slug= base_slug
        counter= 1 
        
        while await self.post_repo.get_by_slug(slug): #check slug to avoid any duplicate
            slug= f"{base_slug}-{counter}"
            counter += 1
        
        post_status = base.PostStatus.PUBLISHED if author.role == base.UserRole.ADMIN else base.PostStatus.PENDING
        post= Post(
            title= title, 
            slug= slug,
            content= content,
            excerpt= excerpt,
            author_id= author.id,
            category_id= category_id,
            status=post_status
        )
        
        if tags is not None:
            post.tags.extend(tags) # This prevent MissingGreenlet error
        
        await self.post_repo.save_post(post)        
        
        if file: 
            await self.media_service.create_media(
                post_title= title, 
                post_id= post.id, 
                author= author, 
                file= file)
            
        if author.role != base.UserRole.ADMIN:
            message= f"{author.username}'s post await your approval to be published. "
            await self.notification_service.notify_admin_of_post(
                author=author, 
                title= title,
                message= message,
                entity_id= post.id,
                entity_type= "Post"
                )
            
        return True
        
    
    async def search_post(self, search: str, offset: int, limit: int):
        return await self.post_repo.search_for_post(search= search, offset= offset, limit= limit)
        
        
            
    async def get_all_excerpts(self, offset: int, limit: int):
        
        excerpt= await self.post_repo.get_all_excerpt(offset= offset, limit= limit)
        if not excerpt:
            return []
        return excerpt
    
    # Users viewing only published posts
    async def view_all_posts(self, offset: int, limit: int):
        
        post= await self.post_repo.get_all_post(offset= offset, limit= limit)
        if not post:
            return []
        return post
    
    # Admin viewing all post in the application(Both published and non published)
    async def view_all_blog_posts(self, offset: int, limit: int):
        
        post= await self.post_repo.get_all_blog_post(offset= offset, limit= limit)
        if not post:
            return []
        return post
    
    async def list_my_post(self, current_user: User, offset: int, limit: int):
        
        author_post= await self.post_repo.get_my_posts(author_id= current_user.id, offset= offset, limit= limit)
        if not author_post:
            return []
        return author_post
    
  
    
    async def get_post_by_id(self, post_id: int, user: User):
        
        cached = await redis_setup.get_cache(key= f"post:{post_id}")
        if cached:                
            result= json.loads(cached) 
            
            #This convert the post dictionary format from redis to python object
            return post.PostResponse.model_validate(result) 
            
        # Cache miss - get from DB
        db_post = await self.post_repo.get_post_by_id(post_id)
        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")
        if user.role != base.UserRole.ADMIN and db_post.status != base.PostStatus.PUBLISHED:
            raise HTTPException(status_code=404, detail="post not found")
        
        # Cache the post
        await redis_setup.set_cache(f"post:{post_id}", 3600, json.dumps(jsonable_encoder(db_post)))
        return db_post



    async def update(
        self, author: User, 
        post_id: int, media_id: int,
        file: UploadFile,
        category_id: int, title: str,
        content: str, tags_: list[str]
        ) -> bool:
                
        db_post= await self.post_repo.get_post_with_tag(post_id) 
        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")
    
        if db_post.author_id != author.id and author.role != base.UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Unable to access")
                
        title = clean(title)
        content = clean(content)
        
        excerpt = content[:100]# extract excerpt from content
        base_slug = slugify(title)# create slug
        slug = base_slug
        counter = 1 
        
        while await self.post_repo.get_by_slug(slug): #check slug to avoid any duplicate
            slug= f"{base_slug}-{counter}"
            counter += 1
                 
        post_status = base.PostStatus.PUBLISHED if author.role == base.UserRole.ADMIN else base.PostStatus.PENDING
        
        db_post.title= title
        db_post.slug= slug
        db_post.content= content
        db_post.excerpt= excerpt
        db_post.author_id= author.id
        db_post.category_id= category_id
        db_post.status= post_status
        
        updated_tags = await self.tag_service.get_or_create_tags(tag_names= tags_)
        db_post.tags = updated_tags
        
        await self.post_repo.update_object(db_post)
        if file:
            await self.media_service.update_media(post_title= title, author= author, media_id= media_id, file= file)
            
        if author.role != base.UserRole.ADMIN:
            await self.notification_service.notify_admin_of_post(
                message= f"{author.username} updated post with tittle {db_post.title}", 
                author=author, 
                title= title, 
                entity_id=db_post.id,
                entity_type= "Post"
                )
            
        return True
        
        
    async def update_post_status(self, post_id: int, status: str):
        db_post= await self.post_repo.get_by_model_id(post_id)
        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")
        db_post.status= status
        return True
    
 
    async def delete(self, post_id, author: User):
        
        db_post= await self.post_repo.get_by_model_id(post_id) 
        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")
       
        if db_post.author_id != author.id and author.role != base.UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Unable to delete")
        
        public_id = await self.media_service.delete_media_from_post(post_id= db_post.id)
        
        await redis_setup.delete_cache(key= f"post:{post_id}")
        await self.post_repo.delete_object(db_post)

        await cloud.delete_from_cloud(media_url= public_id)
        
        return True
    
