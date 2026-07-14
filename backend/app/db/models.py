from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Place(SQLModel, table=True):
    contentid: str = Field(primary_key=True, index=True)
    contenttypeid: Optional[str] = None
    title: Optional[str] = None
    addr1: Optional[str] = None
    addr2: Optional[str] = None
    areacode: Optional[str] = None
    cat1: Optional[str] = None
    cat2: Optional[str] = None
    cat3: Optional[str] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None
    zipcode: Optional[str] = None
    tel: Optional[str] = None
    firstimage: Optional[str] = None
    firstimage2: Optional[str] = None
    createdtime: Optional[str] = None
    modifiedtime: Optional[str] = None
    mlevel: Optional[str] = None
    cpyrhtDivCd: Optional[str] = None
    sigungucode: Optional[str] = None
    lDongRegnCd: Optional[str] = None
    lDongSignguCd: Optional[str] = None
    lclsSystm1: Optional[str] = None
    lclsSystm2: Optional[str] = None
    lclsSystm3: Optional[str] = None
    region: Optional[str] = None
    contentType: Optional[str] = None


class PostBase(SQLModel):
    title: str
    content: str


class Post(PostBase, table=True):
    post_id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    view_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
