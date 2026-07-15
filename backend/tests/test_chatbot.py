import pytest
from app.api.chatbot import extract_place_ids, extract_related_places_from_answer
from app.core.config import settings
from app.db.models import Place


# --- 1. Unit Tests ---

# 답변에서 단일 관광지 ID를 올바르게 파싱해내는지 테스트
def test_extract_place_ids_single():
    assert extract_place_ids("추천하는 곳의 번호는 12345 입니다.") == ["12345"]


# 답변에서 여러 개의 공백 구분 관광지 ID들을 파싱해내는지 테스트
def test_extract_place_ids_multiple():
    assert extract_place_ids("추천 관광지 코드는 1001 1002 입니다.") == ["1001", "1002"]


# 답변에 숫자 관광지 ID가 없을 때 빈 리스트가 리턴되는지 테스트
def test_extract_place_ids_none():
    assert extract_place_ids("해운대 해수욕장을 추천합니다.") == []


# 텍스트와 숫자가 섞인 무효한 ID가 파싱에서 제외되는지 테스트
def test_extract_place_ids_mixed():
    # "cs12345" is not purely digits, so it shouldn't be extracted
    assert extract_place_ids("관광지ID는 cs12345 입니다.") == []


# 답변 내 텍스트와 DB 장소명이 정확히 일치할 때 장소를 추출하는지 테스트
def test_extract_related_places_exact(session):
    p1 = Place(contentid="101", title="해운대 해수욕장", mapx=129.1, mapy=35.1)
    session.add(p1)
    session.commit()

    matches = extract_related_places_from_answer("해운대 해수욕장에 가보세요.", session)
    assert len(matches) == 1
    assert matches[0].title == "해운대 해수욕장"


# 영문 장소명의 대소문자 매칭 구분 없이 일치 시 장소를 추출하는지 테스트
def test_extract_related_places_case_insensitive(session):
    p1 = Place(contentid="102", title="Haeundae", mapx=129.1, mapy=35.1)
    session.add(p1)
    session.commit()

    matches = extract_related_places_from_answer("Let's visit HAEUNDAE beach.", session)
    assert len(matches) == 1
    assert matches[0].title == "Haeundae"


# 답변 내 매칭되는 장소명이 전혀 없을 때 빈 리스트가 리턴되는지 테스트
def test_extract_related_places_no_match(session):
    p1 = Place(contentid="103", title="해운대", mapx=129.1, mapy=35.1)
    session.add(p1)
    session.commit()

    matches = extract_related_places_from_answer("부산 시내를 드라이브하세요.", session)
    assert len(matches) == 0


# --- 2. Integration Tests ---

# 챗봇 질의 API 호출 성공 및 관련 장소 매칭 추천이 정상 응답되는지 테스트
def test_query_chatbot_success(client, session, mocker):
    # Setup key and mock model
    mocker.patch.object(settings, "gemini_api_key", "test_gemini_key")
    mocker.patch.object(settings, "gemini_model", "test-model")

    # Mock Google GenAI Client
    mock_client = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_response.text = "광안대교 야경이 참 아름다워요."
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("google.genai.Client", return_value=mock_client)

    # Populate DB
    place = Place(contentid="999", title="광안대교", mapx=129.2, mapy=35.2)
    session.add(place)
    session.commit()

    # Query API
    response = client.post("/api/chatbot/query", json={"message": "광안대교 어때?"})
    assert response.status_code == 200
    data = response.json()
    assert "광안대교" in data["answer"]
    assert len(data["related_places"]) == 1
    assert data["related_places"][0]["contentid"] == "999"


# 답변 텍스트 매칭 실패 시 답변 내 ID 정보 기반 폴백 매칭이 정상 작동하는지 테스트
def test_query_chatbot_fallback_id(client, session, mocker):
    mocker.patch.object(settings, "gemini_api_key", "test_gemini_key")
    mocker.patch.object(settings, "gemini_model", "test-model")

    # Mock Client
    mock_client = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_response.text = "제가 추천하는 곳의 번호는 777 입니다."
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("google.genai.Client", return_value=mock_client)

    # Populate DB
    place = Place(contentid="777", title="숨겨진 관광지", mapx=129.3, mapy=35.3)
    session.add(place)
    session.commit()

    # Query API
    response = client.post("/api/chatbot/query", json={"message": "번호로 추천해줘"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["related_places"]) == 1
    assert data["related_places"][0]["contentid"] == "777"


# Gemini API 키 설정이 누락되었을 때 500 에러를 반환하는지 테스트
def test_query_chatbot_key_missing(client, mocker):
    mocker.patch.object(settings, "gemini_api_key", None)

    # Query API
    response = client.post("/api/chatbot/query", json={"message": "안녕하세요"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Gemini API key is not configured"


# Gemini API 호출 과정에서 에러 발생 시 502 에러를 반환하는지 테스트
def test_query_chatbot_api_error(client, mocker):
    mocker.patch.object(settings, "gemini_api_key", "test_gemini_key")
    mocker.patch.object(settings, "gemini_model", "test-model")

    # Mock Client to raise exception
    mock_client = mocker.MagicMock()
    mock_client.models.generate_content.side_effect = Exception("API Quota Exceeded")
    mocker.patch("google.genai.Client", return_value=mock_client)

    # Query API
    response = client.post("/api/chatbot/query", json={"message": "에러 발생해라"})
    assert response.status_code == 502
    assert "API Quota Exceeded" in response.json()["detail"]
