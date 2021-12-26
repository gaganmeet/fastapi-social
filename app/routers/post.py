from sys import prefix
from .. import models, schemas
from typing import List
from fastapi import  Response, HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(title=post.title, content=post.content,
                           published=post.published)
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, response: Response, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": "Post not found"}
    return post


@router.delete("/{post_id}")
def delete_post(post_id: int, response: Response, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id)

    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post not found with id {post_id}")

    post.delete()
    db.commit()
    response.status_code = status.HTTP_204_NO_CONTENT
    return post


@router.put("/posts/{post_id}", response_model=schemas.PostResponse)
def update_post(post: schemas.PostCreate, post_id: int, response: Response, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    updated_post = post_query.first()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post not found with id {post_id}")
    post_query.update(post.dict())
    db.commit()
    return post_query.first()
