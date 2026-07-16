import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from google import genai
from google.genai import types
from openai import OpenAI
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ..core.config import settings
from ..db.database import get_session
from ..db.models import Place

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])
logger = logging.getLogger(__name__)
OPENAI_MODEL = "gpt-5-mini"

SYSTEM_PROMPT = (
    "당신은 부산 여행을 돕는 친절한 안내자입니다. "
    "사용자의 질문에 자연스럽고 명확한 한국어로 답변하세요. "
    "부산 관광지 정보를 언급할 때는 데이터베이스에 있는 장소를 참고해 답변에 포함하세요."
)


class ChatRequest(BaseModel):
    message: str


class RelatedPlace(BaseModel):
    contentid: str
    title: Optional[str] = None
    mapx: Optional[float] = None
    mapy: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    related_places: List[RelatedPlace] = Field(default_factory=list)

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


def call_openai(message: str, prompt: str) -> str:
    client = OpenAI(api_key=settings.openai_api_key)
    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=prompt,
            input=message,
            max_output_tokens=2000,
        )
        return response.output_text or ""
    finally:
        client.close()


def call_gemini(message: str, prompt: str) -> str:
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
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=prompt,
                max_output_tokens=2000,
                temperature=0.9,
            ),
        )
        return response.text or ""
    finally:
        client.close()


def get_provider_order() -> List[str]:
    if settings.chatbot_provider == "openai":
        return ["openai"]
    if settings.chatbot_provider == "gemini":
        return ["gemini"]
    return ["openai", "gemini"]


def has_provider_key(provider: str) -> bool:
    if provider == "openai":
        return bool(settings.openai_api_key)
    return bool(settings.gemini_api_key)


def generate_answer(message: str, prompt: str = SYSTEM_PROMPT) -> str:
    providers = [
        provider
        for provider in get_provider_order()
        if has_provider_key(provider)
    ]
    if not providers:
        raise HTTPException(
            status_code=500,
            detail="No API key is configured for the selected chatbot provider(s)",
        )

    failed_providers = []
    for provider in providers:
        try:
            if provider == "openai":
                return call_openai(message, prompt).strip()
            return call_gemini(message, prompt).strip()
        except Exception as exc:
            failed_providers.append(provider)
            logger.warning(
                "Chatbot provider '%s' failed (%s)",
                provider,
                type(exc).__name__,
            )

    raise HTTPException(
        status_code=502,
        detail=(
            "All configured chatbot providers failed: "
            + ", ".join(failed_providers)
        ),
    )


@router.post("/query", response_model=ChatResponse)
def query_chatbot(request: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    answer = generate_answer(request.message)
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
