"""注册-登录-资源审核闭环测试。"""
import sys
from pathlib import Path

from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.localization.messages import MESSAGES


def test_register_login_and_resource_flow(test_app: TestClient) -> None:
    """完整模拟注册、角色升级、提交资源、管理员审核流程。"""

    register_payload = {"username": "creator1", "nickname": "测试用户", "password": "StrongPass123"}
    response = test_app.post("/api/auth/register", json=register_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["message"] == MESSAGES["register_success"]

    # 默认管理员登录并升级角色
    admin_login = test_app.post("/api/auth/login", json={"username": "admin", "password": "Admin123"})
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    users_response = test_app.get("/api/users/", headers=admin_headers)
    assert users_response.status_code == 200
    created_user = next(user for user in users_response.json()["data"] if user["username"] == register_payload["username"])
    user_id = created_user["id"]
    promote_payload = {"role": "practitioner"}
    promote_response = test_app.patch(f"/api/users/{user_id}", json=promote_payload, headers=admin_headers)
    assert promote_response.status_code == 200
    assert promote_response.json()["data"]["role"] == "practitioner"

    # 登录创作者账号
    login_response = test_app.post("/api/auth/login", json={"username": register_payload["username"], "password": register_payload["password"]})
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resource_payload = {
        "title": "文化遗产案例",
        "resource_type": "text",
        "synopsis": "这是一个用于测试的文化资源描述，内容不少于十个字。",
        "tags": ["测试"],
        "file_path": "/uploads/demo.pdf",
        "submit_for_review": True,
        "trails": [
            {
                "place_name": "福州",
                "longitude": 119.30,
                "latitude": 26.08,
                "order_no": 1
            }
        ],
    }
    create_response = test_app.post("/api/resources", json=resource_payload, headers=headers)
    assert create_response.status_code == 200
    resource_body = create_response.json()
    assert resource_body["message"] == MESSAGES["resource_created"]
    resource_id = resource_body["data"]["id"]
    assert resource_body["data"]["status"] == "pending"

    list_response = test_app.get("/api/resources", params={"page": 1, "page_size": 5}, headers=admin_headers)
    assert list_response.status_code == 200
    body_list = list_response.json()
    assert any(item["id"] == resource_id for item in body_list["data"])
    assert body_list["meta"]["total"] >= 1

    update_response = test_app.post(
        f"/api/resources/{resource_id}/review",
        params={"decision": "approve"},
        headers=admin_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["status"] == "approved"

    summary_response = test_app.get("/api/resources/summary")
    assert summary_response.status_code == 200
    summary_body = summary_response.json()
    assert summary_body["data"]["total"] >= 1
    assert summary_body["data"]["approved"] >= 1

    audit_response = test_app.get("/api/audits", headers=admin_headers)
    assert audit_response.status_code == 200
    audit_body = audit_response.json()
    assert audit_body["message"] == MESSAGES["audit_list"]
    create_log = next(log for log in audit_body["data"] if log["action"] == "create_resource")
    assert create_log["ip"]
    assert "title" in create_log["note"]


def test_default_accounts_can_login(test_app: TestClient) -> None:
    """确保预置的管理员、从业者与普通用户均可登录。"""

    credentials = [
        ("admin", "Admin123"),
        ("opera_practitioner", "Practitioner123"),
        ("heritage_user", "Heritage123"),
    ]
    for username, password in credentials:
        response = test_app.post("/api/auth/login", json={"username": username, "password": password})
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["access_token"]
