"""Automated tests for auth endpoints."""


# ── Registration ──────────────────────────────────────────────────────────────

def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "new@aispire.io", "password": "Secure123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@aispire.io"
    assert "password_hash" not in data
    assert "password" not in data


def test_register_duplicate_email(client, registered_user):
    response = client.post(
        "/auth/register",
        json={"email": registered_user["email"], "password": "Another123"},
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_success(client, registered_user):
    response = client.post("/auth/login", json=registered_user)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, registered_user):
    response = client.post(
        "/auth/login",
        json={"email": registered_user["email"], "password": "WrongPass"},
    )
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@aispire.io", "password": "Secure123"},
    )
    assert response.status_code == 401


# ── /auth/me ──────────────────────────────────────────────────────────────────

def test_get_me_with_valid_token(client, auth_token):
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {auth_token['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@aispire.io"
    assert "id" in data


def test_get_me_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 403


def test_get_me_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"},
    )
    assert response.status_code == 401


# ── Refresh ───────────────────────────────────────────────────────────────────

def test_refresh_token_success(client, auth_token):
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": auth_token["refresh_token"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # Rotation — new refresh token must be different
    assert data["refresh_token"] != auth_token["refresh_token"]


def test_refresh_invalid_token(client):
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "invalidtoken"},
    )
    assert response.status_code == 401


# ── Logout ────────────────────────────────────────────────────────────────────

def test_logout_invalidates_session(client, auth_token):
    # Use refresh token once successfully
    first = client.post(
        "/auth/refresh",
        json={"refresh_token": auth_token["refresh_token"]},
    )
    assert first.status_code == 200

    # Try to use the OLD refresh token again — should fail (rotated)
    second = client.post(
        "/auth/refresh",
        json={"refresh_token": auth_token["refresh_token"]},
    )
    assert second.status_code == 401