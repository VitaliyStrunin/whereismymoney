import pytest

from backend.core.security import create_access_token, decode_access_token


def test_register_user(client):
    user_data = {"email": "test@gmail.com", "plain_password": "TestPassword"}
    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    assert response.json['email'] == user_data['email']
    assert "password_hash"  not in response.json
    assert "plain_password" not in response.json


def test_login_user(client, create_user):
    user = create_user(email="test@gmail.com", plain_password="SomeTestPassword")
    login_data = {"email": "test@gmail.com", "plain_password": "SomeTestPassword"}

    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 200
    assert "access_token" in response.json
    assert response.json["token_type"] == "bearer"

    access_token = response.json["access_token"]
    user_id = decode_access_token(access_token)

    assert user_id == user.id


@pytest.mark.parametrize(
    ("email", "plain_password", "expected_status"),
    [
        ("not email", "correctpassword", 400),
        ("email@gmail.com", "pwd", 400),
        ("email@gmail.com", "pwd" * 150, 400),
        ("email@gmail.com", None, 400),
        (None, "correctpassword", 400),
    ]
)
def test_register_invalid(client, email, plain_password, expected_status):
    user_data = {"email": email, "plain_password": plain_password}
    response = client.post("/auth/register", json=user_data)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("email", "plain_password", "expected_status"),
    [
        ("test@gmail.com", "wrongpassword", 401),
        ("wrongemail@gmail.com", "correctpassword", 401),
    ]
)
def test_login_wrong_credentials(client, create_user, email, plain_password, expected_status):
    create_user(email="test@gmail.com", plain_password="correctpassword")
    login_data = {"email": email, "plain_password": plain_password}

    response = client.post("/auth/login", json=login_data)

    assert response.status_code == expected_status


def test_register_duplicate_email(client, create_user):
    create_user(email="test@gmail.com", plain_password="correctpassword")

    register_data = {"email": "test@gmail.com", "plain_password": "correctpassword"}
    response = client.post("/auth/register", json=register_data)

    assert response.status_code == 409


def test_get_me(client, create_user):
    user = create_user()
    access_token = create_access_token(user.id)

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json['id'] == user.id
    assert response.json['email'] == user.email
    assert "password_hash" not in response.json


def test_get_me_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_get_me_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer some-wrong-token"})

    assert response.status_code == 401
