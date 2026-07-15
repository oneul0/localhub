from datetime import datetime, timedelta
import pytest
from app.db.models import Post


# --- 1. Posts List and Read Tests ---

# 게시글 목록을 최신순으로 정렬하여 페이지네이션 조회하는지 테스트
def test_list_posts(client, session):
    now = datetime.utcnow()
    p1 = Post(title="첫 번째 글", content="내용 1", password="pw1", created_at=now - timedelta(minutes=5))
    p2 = Post(title="두 번째 글", content="내용 2", password="pw2", created_at=now)
    session.add(p1)
    session.add(p2)
    session.commit()

    response = client.get("/api/posts?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Ordered by created_at.desc(), so second post (p2) should be first
    assert data[0]["title"] == "두 번째 글"
    assert data[1]["title"] == "첫 번째 글"


# 특정 ID의 게시글 상세 정보가 정상 반환되고 조회수(view_count)가 1 증가하는지 테스트
def test_get_post_success(client, session):
    p = Post(title="상세조회 글", content="상세 내용", password="pw")
    session.add(p)
    session.commit()
    post_id = p.post_id

    # First view
    response = client.get(f"/api/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["view_count"] == 1

    # Second view
    response2 = client.get(f"/api/posts/{post_id}")
    assert response2.status_code == 200
    assert response2.json()["view_count"] == 2


# 존재하지 않는 게시글 ID 상세 조회 시 404 에러가 나는지 테스트
def test_get_post_not_found(client):
    response = client.get("/api/posts/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


# --- 2. Post Create, Update, Delete Tests ---

# 새 게시글을 데이터베이스에 정상적으로 생성하는지 테스트
def test_create_post(client, session):
    post_payload = {"title": "신규 글", "content": "신규 내용", "password": "securepassword"}
    response = client.post("/api/posts", json=post_payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == "신규 글"
    assert "post_id" in data

    # Verify database insertion
    post_in_db = session.get(Post, data["post_id"])
    assert post_in_db is not None
    assert post_in_db.password == "securepassword"


# 올바른 비밀번호를 전달했을 때 게시글이 정상적으로 수정되는지 테스트
def test_update_post_success(client, session):
    p = Post(title="원본 글", content="원본 내용", password="mypassword")
    session.add(p)
    session.commit()
    post_id = p.post_id

    update_payload = {"title": "수정된 글", "content": "수정된 내용", "password": "mypassword"}
    response = client.put(f"/api/posts/{post_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["title"] == "수정된 글"


# 잘못된 비밀번호를 전달했을 때 게시글 수정이 거부(403 Forbidden)되는지 테스트
def test_update_post_forbidden(client, session):
    p = Post(title="원본 글", content="원본 내용", password="mypassword")
    session.add(p)
    session.commit()
    post_id = p.post_id

    update_payload = {"title": "수정 시도", "content": "수정 시도", "password": "wrong_password"}
    response = client.put(f"/api/posts/{post_id}", json=update_payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid password"


# 게시글 비밀번호 검증 API(verify-password)가 정상작동(성공 200, 실패 403)하는지 테스트
def test_verify_post_password(client, session):
    p = Post(title="검증 글", content="내용", password="mypassword")
    session.add(p)
    session.commit()
    post_id = p.post_id

    # Correct password
    res_correct = client.post(f"/api/posts/{post_id}/verify-password", json={"password": "mypassword"})
    assert res_correct.status_code == 200
    assert res_correct.json()["detail"] == "Password verified"

    # Wrong password
    res_wrong = client.post(f"/api/posts/{post_id}/verify-password", json={"password": "wrong"})
    assert res_wrong.status_code == 403
    assert res_wrong.json()["detail"] == "Invalid password"


# 올바른 비밀번호로 삭제 요청 시 게시글이 정상 삭제되고 DB에서 없어지는지 테스트
def test_delete_post_success(client, session):
    p = Post(title="삭제할 글", content="내용", password="mypassword")
    session.add(p)
    session.commit()
    post_id = p.post_id

    response = client.request("DELETE", f"/api/posts/{post_id}", json={"password": "mypassword"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Post deleted successfully"

    # Verify database removal
    assert session.get(Post, post_id) is None


# 잘못된 비밀번호로 삭제 요청 시 삭제가 거부(403 Forbidden)되는지 테스트
def test_delete_post_forbidden(client, session):
    p = Post(title="삭제 거부될 글", content="내용", password="mypassword")
    session.add(p)
    session.commit()
    post_id = p.post_id

    response = client.request("DELETE", f"/api/posts/{post_id}", json={"password": "wrong_password"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid password"
    
    # Verify post still exists in DB
    assert session.get(Post, post_id) is not None
