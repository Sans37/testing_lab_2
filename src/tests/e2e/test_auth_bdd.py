import os
import uuid
import pytest
from pytest_bdd import scenarios, given, when, then
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.infrastructure.database.models.user_model import UserModel

pytestmark = pytest.mark.e2e

scenarios("bdd/auth_2fa.feature")


@pytest.fixture(scope="function")
def auth_context(test_db_session: Session, monkeypatch):
    # Enable test environment and 2FA for these scenarios
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("TWO_FA_ENABLED", "true")
    monkeypatch.setenv("AUTH_MAX_ATTEMPTS", "3")

    ctx = {"test_db_session": test_db_session}
    yield ctx

    # Cleanup user if created
    user_id = ctx.get("user_id")
    if user_id:
        try:
            user = test_db_session.query(UserModel).filter(UserModel.id == user_id).first()
            if user:
                test_db_session.delete(user)
                test_db_session.commit()
        except Exception:
            test_db_session.rollback()


@given("a technical user exists")
async def technical_user_exists(client: AsyncClient, auth_context):
    password = os.getenv("E2E_TECH_USER_PASSWORD")
    if not password:
        raise RuntimeError("Set E2E_TECH_USER_PASSWORD env var for BDD tests")

    email = f"bdd_{uuid.uuid4()}@example.com"
    user_data = {
        "name": "BDD User",
        "email": email,
        "password": password,
        "phone": "+79999999999",
        "address": "BDD Street"
    }
    resp = await client.post("/api/v2/auth/register", json=user_data)
    assert resp.status_code == 201
    user = resp.json()["user"]
    auth_context.update({
        "email": email,
        "password": password,
        "user_id": user["id"],
    })


@when("the user logs in with correct password")
async def login_correct(client: AsyncClient, auth_context):
    resp = await client.post(
        "/api/v2/auth/login",
        json={"email": auth_context["email"], "password": auth_context["password"]}
    )
    auth_context["login_response"] = resp


@then("2FA is required")
async def two_fa_required(auth_context):
    resp = auth_context["login_response"]
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("two_fa_required") is True
    auth_context["session_id"] = data.get("session_id")


@when("the user verifies the 2FA code")
async def verify_2fa(client: AsyncClient, auth_context):
    otp = await client.get(
        "/api/v2/auth/test-otp",
        params={"session_id": auth_context["session_id"]}
    )
    code = otp.json().get("code")
    resp = await client.post(
        "/api/v2/auth/verify-2fa",
        json={"session_id": auth_context["session_id"], "code": code}
    )
    auth_context["token_response"] = resp


@then("an access token is issued")
async def token_issued(auth_context):
    resp = auth_context["token_response"]
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("token")
    auth_context["token"] = data["token"]


@when("the user submits an incorrect password 3 times")
async def incorrect_passwords(client: AsyncClient, auth_context):
    for _ in range(3):
        resp = await client.post(
            "/api/v2/auth/login",
            json={"email": auth_context["email"], "password": "wrong_password"}
        )
        auth_context["last_login_status"] = resp.status_code


@then("the account is locked")
async def account_locked(auth_context):
    assert auth_context.get("last_login_status") == 423


@when("the user requests unlock and confirms the code")
async def unlock_flow(client: AsyncClient, auth_context):
    resp = await client.post(
        "/api/v2/auth/unlock/request",
        json={"email": auth_context["email"]}
    )
    assert resp.status_code == 200

    otp = await client.get(
        "/api/v2/auth/test-otp",
        params={"email": auth_context["email"]}
    )
    code = otp.json().get("code")

    resp = await client.post(
        "/api/v2/auth/unlock/confirm",
        json={"email": auth_context["email"], "code": code}
    )
    assert resp.status_code == 200


@then("login works again")
async def login_works_again(client: AsyncClient, auth_context):
    resp = await client.post(
        "/api/v2/auth/login",
        json={"email": auth_context["email"], "password": auth_context["password"]}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("two_fa_required") is True


@given("the user is logged in with 2FA")
async def user_logged_in_with_2fa(client: AsyncClient, auth_context):
    resp = await client.post(
        "/api/v2/auth/login",
        json={"email": auth_context["email"], "password": auth_context["password"]}
    )
    session_id = resp.json().get("session_id")
    otp = await client.get(
        "/api/v2/auth/test-otp",
        params={"session_id": session_id}
    )
    code = otp.json().get("code")
    verify = await client.post(
        "/api/v2/auth/verify-2fa",
        json={"session_id": session_id, "code": code}
    )
    token = verify.json().get("token")
    auth_context["token"] = token


@when("the user requests a password change OTP")
async def request_password_change_otp(client: AsyncClient, auth_context):
    resp = await client.post(
        "/api/v2/auth/request-password-change-otp",
        headers={"Authorization": f"Bearer {auth_context['token']}"}
    )
    assert resp.status_code == 200


@when("the user confirms password change")
async def confirm_password_change(client: AsyncClient, auth_context):
    new_password = "NewPass123!"
    otp = await client.get(
        "/api/v2/auth/test-otp",
        params={"email": auth_context["email"]}
    )
    code = otp.json().get("code")
    resp = await client.post(
        "/api/v2/auth/change-password",
        headers={"Authorization": f"Bearer {auth_context['token']}"},
        json={
            "current_password": auth_context["password"],
            "new_password": new_password,
            "otp_code": code
        }
    )
    assert resp.status_code == 200
    auth_context["new_password"] = new_password


@then("login with the new password succeeds")
async def login_with_new_password(client: AsyncClient, auth_context):
    resp = await client.post(
        "/api/v2/auth/login",
        json={"email": auth_context["email"], "password": auth_context["new_password"]}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("two_fa_required") is True
