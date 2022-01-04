from typing import Optional
from pydantic import BaseModel,EmailStr
from datetime import datetime

from pydantic.types import conint

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    

class CreatePost(PostBase):
    pass

class UpdatePost(PostBase):
    pass

class Post(PostBase):
    id : int
    created_at : datetime
    owner_id : int

    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    email :  EmailStr
    password : str

class ResponseUser(BaseModel):
    email :  EmailStr
    created_at : datetime
    
    class Config:
        orm_mode = True

class GetUser(BaseModel):
    id : int
    email : EmailStr

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email :  EmailStr
    password : str

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
    post_id : int
    dir : conint(le=1)
    