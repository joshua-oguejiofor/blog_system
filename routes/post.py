from fastapi import APIRouter, Depends, File, Form, UploadFile
from models.user import User
from schemas import base, post
from service.post import PostService
from utility.dependency import (
    admin_or_author_required,
    admin_required,
    current_user,
    get_post_service,
)

router= APIRouter()




@router.post("/", status_code=201)
async def create_post(
    category_id: int = Form(..., ge=1),
    title: str = Form(..., min_length=5, max_length=200),
    content: str = Form(..., min_length=10),
    tags: list[str] = Form(default_factory=list),
    file: UploadFile | None = File(None),
    author: User = Depends(admin_or_author_required),
    service: PostService = Depends(get_post_service),
):
    await service.create(
        author=author,
        category_id=category_id,
        title=title, content=content,
        tags_= tags, file= file
        )
    
    return {"msg":"Post pending. Awaiting admin aproval before publishing"}
    

@router.get('/excerpts', status_code= 200, response_model= list[post.ExcerptResponse])
async def get_excerpt(
    offset: int= 0,
    limit: int= 20,
    service: PostService= Depends(get_post_service)):
    
    return await service.get_all_excerpts(offset= offset, limit=limit)


@router.get('/me', status_code= 200, response_model= list[post.PostResponse])
async def get_my_posts(
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(current_user), 
    service: PostService= Depends(get_post_service)):
    
    return await service.list_my_post(offset= offset, limit=limit, current_user= current_user)


@router.get('/', status_code= 200, response_model= list[post.PostResponse])
async def get_posts(
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(current_user), 
    service: PostService= Depends(get_post_service)):
    
    return await service.view_all_posts(offset= offset, limit=limit)

# For admin
@router.get('/admin', status_code= 200, response_model= list[post.PostResponse])
async def get_all_blog_posts(
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(admin_required), 
    service: PostService= Depends(get_post_service)):
    
    return await service.view_all_blog_posts(offset= offset, limit=limit)


@router.get('/{post_id}', status_code= 200, response_model= post.PostResponse)
async def view_post(
    post_id: int,
    current_user: User= Depends(current_user), 
    service: PostService= Depends(get_post_service)):
    
    return await service.get_post_by_id(post_id=post_id, user=current_user)

@router.post('/search', status_code= 200)
async def search_post( 
    search: str,
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(current_user), 
    service: PostService= Depends(get_post_service)):
    
    return await service.search_post(search= search, offset= offset, limit= limit)
    

@router.put('/{post_id}', status_code=200)
async def update_post(
    media_id: int | None,
    post_id: int,
    category_id: int = Form(..., ge=1),
    title: str = Form(..., min_length=5, max_length=200),
    content: str = Form(..., min_length=10),
    tags: list[str] = Form(default_factory=list),
    file: UploadFile | None = File(None),
    author: User = Depends(admin_or_author_required),
    service: PostService = Depends(get_post_service),
):
    await service.update(
        author= author,
        file= file,
        tags_= tags,
        title= title,
        category_id= category_id,
        content= content,
        post_id= post_id,
        media_id=media_id
        )
    
    return {"msg":"Post updated. Awaiting admin aproval before publishing"}
    
    
@router.patch('/status', status_code= 200)
async def post_status(
    post_id: int,
    status: base.PostStatus,
    admin: User= Depends(admin_required),
    service: PostService= Depends(get_post_service)
):
    await service.update_post_status(post_id= post_id, status= status)

    return {"msg":f"Posts status set to be {status.value}"}
    

@router.delete('/{post_id}', status_code=204)
async def delete_post(
    post_id: int,
    author: User= Depends(admin_or_author_required),
    service: PostService= Depends(get_post_service)
):
    await service.delete(author= author, post_id= post_id)






  