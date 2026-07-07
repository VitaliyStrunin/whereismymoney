import pytest


def test_get_tags(client, create_tag, default_user_auth_headers):
    test_tag_name = "SomeTestTag"
    create_tag(test_tag_name)
    response = client.get("/tags", headers=default_user_auth_headers)

    assert response.status_code == 200

    tags = response.json
    names = {tag["name"] for tag in tags}

    assert test_tag_name in names


def test_get_tag_by_id_positive(client, create_tag, default_user_auth_headers):
    test_tag_name = "SomeTestTag"
    test_tag = create_tag(test_tag_name)

    response = client.get(f"/tags/{test_tag.id}", headers=default_user_auth_headers)

    assert response.status_code == 200
    assert response.json["id"] == test_tag.id
    assert response.json["name"] == test_tag.name


def test_get_tag_by_id_not_found(client, default_user_auth_headers):
    response = client.get("/tags/-1", headers=default_user_auth_headers)

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("limit", "offset", "expected_names"),
    [
        (1, 0, ["Food"]),
        (2, 0, ["Food", "Snacks"]),
        (1, 1, ["Snacks"]),
        (2, 1, ["Snacks", "Rent"]),
        (10, 0, ["Food", "Snacks", "Rent"]),
        (10, 10, []),
    ],
)
def test_get_tags_with_limit_and_offset(
    client,
    create_tag,
    default_user_auth_headers,
    limit,
    offset,
    expected_names,
):
    create_tag("Food")
    create_tag("Snacks")
    create_tag("Rent")

    response = client.get(f"/tags?limit={limit}&offset={offset}", headers=default_user_auth_headers)

    assert response.status_code == 200

    names = [tag["name"] for tag in response.json]

    assert names == expected_names


@pytest.mark.parametrize(
    ("limit", "offset"),
    [
        (0, 0),
        (0, 1),
        (-1, 1),
        (-1, -1),
        (1, -1),
    ],
)
def test_get_tags_with_limit_and_offset_invalid_params(
    client,
    create_tag,
    default_user_auth_headers,
    limit,
    offset,
):
    create_tag("Food")
    create_tag("Snacks")
    create_tag("Rent")

    response = client.get(f"/tags?limit={limit}&offset={offset}", headers=default_user_auth_headers)

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({"name": ""}, 400),
        ({"name": "        "}, 400),
        ({"name": None}, 400),
    ],
)
def test_create_tag_invalid_params(client, default_user_auth_headers,payload, expected_status):
    response = client.post("/tags", json=payload, headers=default_user_auth_headers)

    assert response.status_code == expected_status


def test_create_tag(client, default_user_auth_headers):
    payload = {"name": "SomeTestTag"}

    response = client.post("/tags", json=payload, headers=default_user_auth_headers)

    assert response.status_code == 201
    assert response.json["name"] == payload["name"]


def test_create_tag_duplicate_name_for_same_user(client, default_user_auth_headers):
    payload = {"name": "Food"}

    first_response = client.post("/tags", json=payload, headers=default_user_auth_headers)
    second_response = client.post("/tags", json=payload, headers=default_user_auth_headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_different_users_can_create_tags_with_same_name(
    client,
    create_user,
    make_auth_headers,
):
    user_a = create_user(email="tag-same-name-a@test.com")
    user_b = create_user(email="tag-same-name-b@test.com")
    user_a_auth_headers = make_auth_headers(user_a)
    user_b_auth_headers = make_auth_headers(user_b)
    payload = {"name": "Food"}

    user_a_response = client.post("/tags", json=payload, headers=user_a_auth_headers)
    user_b_response = client.post("/tags", json=payload, headers=user_b_auth_headers)

    assert user_a_response.status_code == 201
    assert user_b_response.status_code == 201
    assert user_a_response.json["name"] == payload["name"]
    assert user_b_response.json["name"] == payload["name"]


def test_update_tag(client, create_tag, default_user_auth_headers):
    test_tag = create_tag("SomeTag")

    response = client.patch(f"/tags/{test_tag.id}", json={"name": "new_name"}, headers=default_user_auth_headers)

    assert response.status_code == 200
    assert response.json["id"] == test_tag.id
    assert response.json["name"] == "new_name"


def test_update_tag_not_found(client, default_user_auth_headers):
    response = client.patch("/tags/-1", json={"name": "new_name"}, headers=default_user_auth_headers)

    assert response.status_code == 404


def test_update_tag_to_existing_name_for_same_user(
    client,
    create_tag,
    default_user_auth_headers,
):
    existing_tag = create_tag("Food")
    tag_to_update = create_tag("Transport")

    response = client.patch(
        f"/tags/{tag_to_update.id}",
        json={"name": existing_tag.name},
        headers=default_user_auth_headers,
    )
    check_response = client.get(
        f"/tags/{tag_to_update.id}",
        headers=default_user_auth_headers,
    )

    assert response.status_code == 409
    assert check_response.status_code == 200
    assert check_response.json["name"] == tag_to_update.name


def test_user_can_update_tag_to_name_used_by_another_user(
    client,
    create_user,
    create_tag,
    make_auth_headers,
):
    user_a = create_user(email="tag-update-same-name-a@test.com")
    user_b = create_user(email="tag-update-same-name-b@test.com")
    user_a_auth_headers = make_auth_headers(user_a)

    other_user_tag = create_tag("Food", user=user_b)
    tag_to_update = create_tag("Transport", user=user_a)

    response = client.patch(
        f"/tags/{tag_to_update.id}",
        json={"name": other_user_tag.name},
        headers=user_a_auth_headers,
    )

    assert response.status_code == 200
    assert response.json["id"] == tag_to_update.id
    assert response.json["name"] == other_user_tag.name


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({"name": ""}, 400),
        ({"name": "        "}, 400),
        ({"name": None}, 400),
    ],
)
def test_update_tag_invalid_params(client, create_tag, default_user_auth_headers, payload, expected_status):
    test_tag = create_tag("SomeTag")

    response = client.patch(f"/tags/{test_tag.id}", json=payload, headers=default_user_auth_headers)

    assert response.status_code == expected_status


def test_delete_tag(client, create_tag, default_user_auth_headers):
    test_tag = create_tag("SomeTag")

    response = client.delete(f"/tags/{test_tag.id}", headers=default_user_auth_headers)
    check_response = client.get(f"/tags/{test_tag.id}", headers=default_user_auth_headers)

    assert response.status_code == 200
    assert check_response.status_code == 404


def test_user_can_see_only_own_tags_in_list(
    client,
    create_user,
    create_tag,
    default_user_auth_headers,
):
    other_user = create_user(email="other-user@test.com")

    own_tag = create_tag("OwnTag")
    other_tag = create_tag("OtherTag", user=other_user)

    response = client.get("/tags", headers=default_user_auth_headers)

    assert response.status_code == 200

    tag_ids = {tag["id"] for tag in response.json}

    assert own_tag.id in tag_ids
    assert other_tag.id not in tag_ids


def test_users_can_see_only_their_tags_by_id(
    client,
    create_user,
    create_tag,
    make_auth_headers,
):
    user_a = create_user(email="user-a@test.com")
    user_b = create_user(email="user-b@test.com")

    user_a_headers = make_auth_headers(user_a)
    user_b_headers = make_auth_headers(user_b)

    user_a_tag = create_tag("UserATag", user=user_a)

    user_a_response = client.get(f"/tags/{user_a_tag.id}", headers=user_a_headers)
    user_b_response = client.get(f"/tags/{user_a_tag.id}", headers=user_b_headers)

    assert user_a_response.status_code == 200
    assert user_a_response.json["id"] == user_a_tag.id
    assert user_b_response.status_code == 404


def test_user_cannot_update_other_user_tag(
    client,
    create_user,
    create_tag,
    make_auth_headers,
):
    owner = create_user(email="tag-owner@test.com")
    other_user = create_user(email="tag-other-user@test.com")

    owner_headers = make_auth_headers(owner)
    other_user_headers = make_auth_headers(other_user)

    owner_tag = create_tag("OwnerTag", user=owner)

    response = client.patch(
        f"/tags/{owner_tag.id}",
        json={"name": "UpdatedByOtherUser"},
        headers=other_user_headers,
    )
    owner_response = client.get(f"/tags/{owner_tag.id}", headers=owner_headers)

    assert response.status_code == 404
    assert owner_response.status_code == 200
    assert owner_response.json["name"] == owner_tag.name


def test_user_cannot_delete_other_user_tag(
    client,
    create_user,
    create_tag,
    make_auth_headers,
):
    owner = create_user(email="tag-delete-owner@test.com")
    other_user = create_user(email="tag-delete-other-user@test.com")

    owner_headers = make_auth_headers(owner)
    other_user_headers = make_auth_headers(other_user)

    owner_tag = create_tag("OwnerTag", user=owner)

    response = client.delete(f"/tags/{owner_tag.id}", headers=other_user_headers)
    owner_response = client.get(f"/tags/{owner_tag.id}", headers=owner_headers)

    assert response.status_code == 404
    assert owner_response.status_code == 200
    assert owner_response.json["id"] == owner_tag.id
