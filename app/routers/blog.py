from fastapi import status, Depends, APIRouter, HTTPException, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models,schemas, oauth2

router = APIRouter(
    prefix = '/posts',
    tags = ['Posts']
)

#CREATE NEW POST
@router.post("/", status_code = status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post:schemas.CreatePost, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    
    new_post = models.Blog(owner_id = current_user.id, **post.dict())
    
    db.add(new_post)
    
    db.commit()
    
    db.refresh(new_post)

    return new_post


#GET ALL POST
@router.get("/")
def get_posts(db: Session = Depends(get_db), limit : int = 3, skip : int = 0, search : Optional[str] = ""):
    
    posts_with_vote = db.query(models.Blog, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Blog.id, isouter = True).group_by(models.Blog.id).filter(models.Blog.title.contains(search)).limit(limit).offset(skip).all()

    return posts_with_vote

#GET POST BY ID
@router.get("/{id}")
def get_post(id:int, db: Session = Depends(get_db)):
    
    post = db.query(models.Blog, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Blog.id, isouter = True).group_by(models.Blog.id).filter(models.Blog.id == id).first()

    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id : {id} was not found")

    return post

#GET ALL POST BY USER ID
@router.get("/user/{id}")
def get_post_by_user_id(id : int, db : Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    query = db.query(models.Blog, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Blog.id, isouter = True).group_by(models.Blog.id).filter(models.Blog.owner_id == id)
    posts = query.all() 

    if not posts:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"user with id : {id} doesnt have any posts")

    return posts

#EDIT POST BY ID
@router.put("/{id}", response_model=schemas.Post)
def update_post(id:int, updated_post: schemas.UpdatePost, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Blog).filter(models.Blog.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id : {id} does not exist")

    if post.owner_id != current_user.id:
         raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Not authorized to perform requested action")

    post_query.update(updated_post.dict(), synchronize_session=False)
    
    db.commit()
   
    return post


#DELETE POST BY ID
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Blog).filter(models.Blog.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"post with id : {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Not authorized to perform requested action")


    post_query.delete(synchronize_session=False)
    
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT) 
