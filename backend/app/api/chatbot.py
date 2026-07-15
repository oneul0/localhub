from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from sqlmodel import Session, select

from ..core.config import settings
from ..db.database import get_session
from ..db.models import Place

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str


class RelatedPlace(BaseModel):
    contentid: str
    title: Optional[str] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    related_places: List[RelatedPlace] = []

    model_config = {"from_attributes": True}


def extract_place_ids(answer: str) -> List[str]:
    tokens = answer.replace("\n", " ").split()
    return [token for token in tokens if token.isdigit()]


def extract_related_places_from_answer(answer: str, session: Session) -> List[Place]:
    normalized_answer = answer.lower()
    statement = select(Place)
    places = session.exec(statement).all()
    matches = []
    for place in places:
        if place.title and place.title.lower() in normalized_answer:
            matches.append(place)
    return matches


@router.post("/query", response_model=ChatResponse)
def query_chatbot(request: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured")
    else:
        print(settings.openai_api_key)

    prompt = (
        "당신은 부산 여행을 돕는 친절한 안내자입니다. "
        "사용자의 질문에 자연스럽고 명확한 한국어로 답변하세요. "
        "부산 관광지 정보를 언급할 때는 데이터베이스에 있는 장소를 참고해 답변에 포함하세요."
    )
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": request.message},
            ],
            max_tokens=500,
            temperature=0.9,
        )
        answer = response.choices[0].message.content or ""
    except Exception as exc:
        detail = str(exc)
        if hasattr(exc, "status_code"):
            detail = f"Error code: {exc.status_code} - {detail}"
        raise HTTPException(status_code=502, detail=detail)

    answer = answer.strip()
    related_places = extract_related_places_from_answer(answer, session)
    if not related_places:
        place_ids = extract_place_ids(answer)
        if place_ids:
            statement = select(Place).where(Place.contentid.in_(place_ids))
            related_places = session.exec(statement).all()

    return ChatResponse(answer=answer, related_places=related_places)
