from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from google import genai
from google.genai import types
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
    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key is not configured")

    prompt = (
        "당신은 부산 여행을 돕는 친절한 안내자입니다. "
        "사용자의 질문에 자연스럽고 명확한 한국어로 답변하세요. "
        "부산 관광지 정보를 언급할 때는 데이터베이스에 있는 장소를 참고해 답변에 포함하세요."
    )
    try:
        client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    attempts=3,
                    initial_delay=1.0,
                    max_delay=4.0,
                    exp_base=2.0,
                    jitter=0.5,
                    http_status_codes=[503],
                )
            ),
        )
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=request.message,
                config=types.GenerateContentConfig(
                    system_instruction=prompt,
                    max_output_tokens=2000,
                    temperature=0.9,
                ),
            )
            answer = response.text or ""
        finally:
            client.close()
    except Exception as exc:
        detail = str(exc)
        raise HTTPException(status_code=502, detail=detail)

    answer = answer.strip()
    related_places = extract_related_places_from_answer(answer, session)
    if not related_places:
        place_ids = extract_place_ids(answer)
        if place_ids:
            statement = select(Place).where(Place.contentid.in_(place_ids))
            related_places = session.exec(statement).all()

    related_places_response = [
        RelatedPlace(
            contentid=p.contentid,
            title=p.title,
            mapx=p.mapx,
            mapy=p.mapy
        )
        for p in related_places
    ]

    return ChatResponse(answer=answer, related_places=related_places_response)
