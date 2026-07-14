from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..db.database import get_session
from ..db.models import Place

router = APIRouter(prefix="/api/places", tags=["places"])


@router.get("", response_model=List[Place])
def search_places(
    region: Optional[str] = Query(None),
    content_type_id: Optional[str] = Query(None, alias="contenttypeid"),
    keyword: Optional[str] = Query(None),
    session: Session = Depends(get_session),
) -> List[Place]:
    statement = select(Place)
    if region:
        statement = statement.where(Place.region == region)
    if content_type_id:
        statement = statement.where(Place.contenttypeid == content_type_id)
    if keyword:
        keyword_pattern = f"%{keyword}%"
        statement = statement.where(Place.title.ilike(keyword_pattern))
    statement = statement.order_by(Place.title)
    results = session.exec(statement).all()
    return results


@router.get("/{contentid}", response_model=Place)
def get_place(contentid: str, session: Session = Depends(get_session)) -> Place:
    place = session.get(Place, contentid)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place
