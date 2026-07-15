import pytest
from app.db.models import Place


# --- 1. Places Search Tests ---

# 등록된 모든 장소 목록을 반환하는지 테스트
def test_search_places_all(client, session):
    p1 = Place(contentid="201", title="해운대 해수욕장", region="해운대구", contenttypeid="12", mapx=129.1, mapy=35.1)
    p2 = Place(contentid="202", title="태종대", region="영도구", contenttypeid="12", mapx=129.0, mapy=35.0)
    session.add(p1)
    session.add(p2)
    session.commit()

    response = client.get("/api/places")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Ordered by title alphabetically: "태종대" (ㅌ) vs "해운대" (ㅎ) -> "태종대" should be first
    assert data[0]["contentid"] == "202"
    assert data[1]["contentid"] == "201"


# 특정 지역(region)으로 필터링하여 검색하는지 테스트
def test_search_places_by_region(client, session):
    p1 = Place(contentid="201", title="해운대 해수욕장", region="해운대구", contenttypeid="12", mapx=129.1, mapy=35.1)
    p2 = Place(contentid="202", title="태종대", region="영도구", contenttypeid="12", mapx=129.0, mapy=35.0)
    session.add(p1)
    session.add(p2)
    session.commit()

    response = client.get("/api/places?region=영도구")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["contentid"] == "202"


# 특정 컨텐츠 타입 ID(contenttypeid)로 필터링하여 검색하는지 테스트
def test_search_places_by_content_type(client, session):
    p1 = Place(contentid="201", title="해운대 해수욕장", region="해운대구", contenttypeid="12", mapx=129.1, mapy=35.1)
    p2 = Place(contentid="202", title="파라다이스 호텔", region="해운대구", contenttypeid="32", mapx=129.15, mapy=35.15)
    session.add(p1)
    session.add(p2)
    session.commit()

    # Testing alias 'contenttypeid'
    response = client.get("/api/places?contenttypeid=32")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["contentid"] == "202"


# 제목 키워드(keyword) 대소문자 구분 없이 일부 매칭하여 검색하는지 테스트
def test_search_places_by_keyword(client, session):
    p1 = Place(contentid="201", title="Haeundae Beach", region="해운대구", contenttypeid="12", mapx=129.1, mapy=35.1)
    p2 = Place(contentid="202", title="Gwangalli Beach", region="수영구", contenttypeid="12", mapx=129.2, mapy=35.2)
    session.add(p1)
    session.add(p2)
    session.commit()

    response = client.get("/api/places?keyword=haeundae")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Haeundae Beach"


# --- 2. Place Detail Tests ---

# 특정 ID의 장소 상세 정보를 올바르게 가져오는지 테스트
def test_get_place_detail_success(client, session):
    p = Place(contentid="777", title="동백섬", region="해운대구", contenttypeid="12", mapx=129.12, mapy=35.12)
    session.add(p)
    session.commit()

    response = client.get("/api/places/777")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "동백섬"
    assert data["region"] == "해운대구"


# 존재하지 않는 장소 ID 조회 시 404 Not Found 에러가 나는지 테스트
def test_get_place_detail_not_found(client):
    response = client.get("/api/places/non_existent_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Place not found"
