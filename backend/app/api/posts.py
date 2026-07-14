from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from ..db.database import get_session
from ..db.models import Post


class PostCreate(BaseModel):
    title: str
    content: str
    password: str


class PostUpdate(BaseModel):
    title: str
    content: str
    password: str


class PostRead(BaseModel):
    post_id: int
    title: str
    content: str
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("", response_model=List[PostRead])
def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
) -> List[Post]:
    offset = (page - 1) * page_size
    statement = select(Post).order_by(Post.created_at.desc()).offset(offset).limit(page_size)
    results = session.exec(statement).all()
    return results


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, session: Session = Depends(get_session)) -> Post:
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.view_count += 1
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.post("", response_model=PostRead, status_code=201)
def create_post(post_data: PostCreate, session: Session = Depends(get_session)) -> Post:
    new_post = Post(**post_data.dict())
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post


@router.put("/{post_id}", response_model=PostRead)
def update_post(post_id: int, post_data: PostUpdate, session: Session = Depends(get_session)) -> Post:
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.password != post_data.password:
        raise HTTPException(status_code=403, detail="Invalid password")
    post.title = post_data.title
    post.content = post_data.content
    post.updated_at = datetime.utcnow()
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


class PasswordRequest(BaseModel):
    password: str


@router.delete("/{post_id}")
def delete_post(post_id: int, body: PasswordRequest, session: Session = Depends(get_session)) -> dict:
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.password != body.password:
        raise HTTPException(status_code=403, detail="Invalid password")
    session.delete(post)
    session.commit()
    return {"detail": "Post deleted successfully"}
