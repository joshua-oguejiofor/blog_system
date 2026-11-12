from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.user import User
from pydantic import HttpUrl
from schemas import base, user
from service.user import UserService
from utility.dependency import admin_required, current_user, get_user_service

"""will still convert this layer to loose coupling, and add current_user"""

router= APIRouter()


#done
@router.post('/', status_code=201)
async def create_profile(
    username: str= Form(..., min_length= 3, max_length= 30),
    bio: str | None= Form(None),
    profile_photo: UploadFile | None= File(None),
    website_url: HttpUrl | None= Form(None),
    country: str = Form(..., min_length=2, max_length=100),
    social_links: str | None = Form(None),# will add HttpUrl
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    service: UserService= Depends(get_user_service)):

    token= credentials.credentials
    
    await service.create_profile(
        token= token,
        username= username,
        bio= bio, 
        profile_photo= profile_photo,
        website_url= str(website_url) if website_url else None,
        country= country,
        social_links= social_links)    
    
    return {"msg":"Profile created successfully."}

    
#done
@router.get('/{profile_id}', status_code=200, response_model= user.ViewProfile)
async def view_profile(
    profile_id: int,
    current_user: User= Depends(current_user), 
    service: UserService= Depends(get_user_service)):
    
    return await service.view_profile(profile_id= profile_id)

#done
@router.get('/', status_code=200, response_model= list[user.ViewProfile])
async def view_all_profile(
    offset: int= 0,
    limit: int= 20,
    admin: User= Depends(admin_required), 
    service: UserService= Depends(get_user_service)):
    
    return await service.view_all_profile(offset= offset, limit= limit)

#done
@router.put('/{user_id}', status_code=200)
async def update_profile(
    username: str= Form(..., min_length= 3, max_length= 30),
    bio: str | None= Form(None),
    profile_photo: UploadFile | None= File(None),
    website_url: HttpUrl | None= Form(None),
    country: str = Form(..., min_length=2, max_length=100),
    social_links: dict | None = Form(None),# will add HttpUrl
    current_user: User= Depends(current_user),
    service: UserService= Depends(get_user_service)):

    await service.update_profile(
        username= username,
        bio= bio, 
        profile_photo= profile_photo,
        website_url= str(website_url) if website_url else None,
        country= country, 
        social_links= social_links,
        current_user= current_user
    )    
    return {"msg":"Profile updated successfully."}

#done 
@router.patch('/remove', status_code=200)
async def remove_profile_image(
    current_user: User= Depends(current_user), 
    service: UserService= Depends(get_user_service)):
    
    return await service.remove_image(current_user= current_user)


@router.delete('/', status_code=204)
async def delete_account(
    current_user: User= Depends(current_user),
    service: UserService= Depends(get_user_service)):

    await service.delete_user_account(current_user= current_user)



@router.patch("/{user_id}/status", status_code= 200)
async def change_user_status(
    user_id: int,
    status: base.AccountStatus,
    current_user: User= Depends(admin_required),
    service: UserService= Depends(get_user_service)):

    await service.update_user_status(
        status= status,
        user_id= user_id,
        current_user= current_user
    )
    return {"msg": "User status updated"}


@router.patch("/{user_id}/role", status_code= 200)
async def change_user_role(
    user_id: int,
    role: base.UserRole,
    current_user: User= Depends(admin_required),
    service: UserService= Depends(get_user_service)):

    await service.update_user_role(
        role= role ,
        user_id= user_id,
        current_user= current_user
    )
    return {"msg": "User role updated"}

 
@router.post('/search', status_code=200, response_model= list[user.ViewProfile])
async def search_user(
    username: str,
    offset: int= 0,
    limit: int= 20,
    current_user: User= Depends(current_user),
    service: UserService= Depends(get_user_service)):
    
    return await service.get_user_by_username(username= username, limit= limit, offset= offset)
    
