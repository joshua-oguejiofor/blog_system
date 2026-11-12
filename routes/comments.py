from fastapi import APIRouter, Depends
from models.user import User
from schemas import comment
from service.comment import CommentService
from utility.dependency import current_user, get_comment_service

router= APIRouter()


@router.post('/', status_code=201)
async def create_comment(
    data: comment.CreateComment,
    current_user: User= Depends(current_user),
    service: CommentService= Depends(get_comment_service)
    ):
    await service.create(data= data, current_user= current_user)
    return {"msg":"Comment added"}


@router.post('/{comment_id}/reply', status_code=200)
async def reply_comment(
    data: comment.RplyComment,
    current_user: User= Depends(current_user),
    service: CommentService= Depends(get_comment_service)
    ):
    await service.reply_to_comment(data= data, current_user= current_user)
    return {"msg":"Comment added"}

 

@router.get('/', status_code=200, response_model= list[comment.CommentResponse])
async def view_comments(
    post_id: int,
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(current_user),
    service: CommentService= Depends(get_comment_service)
):
    return await service.get_all_post_comment(post_id= post_id, limit= limit, offset= offset)



@router.get('/{comment_id}', status_code=200, response_model= comment.CommentResponse)
async def view_comment(
    comment_id: int,
    current_user: User= Depends(current_user),
    service: CommentService= Depends(get_comment_service)
):
    return await service.get_comment_by_id(comment_id)


@router.put('/{comment_id}', status_code=200)
async def update_comment(
    data: comment.UpdateComment,
    current_user: User= Depends(current_user),
    service: CommentService= Depends(get_comment_service)
    ):
    await service.update(data= data, current_user= current_user)
    return {"msg":"Comment updated"}


@router.delete('/{comment_id}', status_code=204)
async def delete_comment(
    comment_id: int,
    current_user: User= Depends(current_user),
    service: CommentService= Depends(get_comment_service)
):
    await service.delete(comment_id= comment_id, current_user= current_user)
    

