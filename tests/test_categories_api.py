import pytest


def test_get_categories(client, create_category, default_user_auth_headers):
    test_category_name = "SomeTestCategory"
    create_category(test_category_name)
    response = client.get("/categories", headers=default_user_auth_headers)

    assert response.status_code == 200

    categories = response.json
    names = {category['name'] for category in categories}

    assert test_category_name in names

def test_get_category_by_id_positive(client, create_category, default_user_auth_headers):
    test_category_name = "SomeTestCategory"
    test_category = create_category(test_category_name)

    response = client.get(f"/categories/{test_category.id}", headers=default_user_auth_headers)

    assert response.status_code == 200
    assert response.json['id'] == test_category.id
    assert response.json['name'] == test_category.name


def test_get_category_by_id_not_found(client, default_user_auth_headers):
    response = client.get("/categories/-1", headers=default_user_auth_headers)

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
    ]
)
def test_get_categories_with_limit_and_offset(client,
                                              create_category,
                                              default_user_auth_headers,
                                              limit,
                                              offset,
                                              expected_names
                                              ):
    create_category("Food")
    create_category("Snacks")
    create_category("Rent")

    response = client.get(f"/categories?limit={limit}&offset={offset}", headers=default_user_auth_headers)

    assert response.status_code == 200

    names = [category["name"] for category in response.json]

    assert names == expected_names


@pytest.mark.parametrize(
    ("limit", "offset"),
    [
        (0, 0),
        (0, 1),
        (-1, 1),
        (-1, -1),
        (1, -1),
    ]
)
def test_get_categories_with_limit_and_offset_invalid_params(client,
                                                             create_category,
                                                             default_user_auth_headers,
                                                             limit,
                                                             offset
                                                             ):
    create_category("Food")
    create_category("Snacks")
    create_category("Rent")

    response = client.get(f"/categories?limit={limit}&offset={offset}", headers=default_user_auth_headers)

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({"name": ""}, 400),
        ({"name": None}, 400),
    ]
)
def test_create_category_invalid_params(client,
                                        default_user_auth_headers,
                                        payload,
                                        expected_status
                                        ):

    response = client.post("/categories", json=payload, headers=default_user_auth_headers)

    assert response.status_code == expected_status


def test_create_category(client, default_user_auth_headers):
    payload = {"name": "SomeTestCategory"}

    response = client.post("/categories", json=payload, headers=default_user_auth_headers)

    assert response.status_code == 201
    assert response.json["name"] == payload["name"]


def test_create_category_duplicate_name_for_same_user(client, default_user_auth_headers):
    payload = {"name": "Food"}

    first_response = client.post("/categories", json=payload, headers=default_user_auth_headers)
    second_response = client.post("/categories", json=payload, headers=default_user_auth_headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_different_users_can_create_categories_with_same_name(
    client,
    create_user,
    make_auth_headers,
):
    user_a = create_user(email="category-same-name-a@test.com")
    user_b = create_user(email="category-same-name-b@test.com")
    user_a_auth_headers = make_auth_headers(user_a)
    user_b_auth_headers = make_auth_headers(user_b)
    payload = {"name": "Food"}

    user_a_response = client.post("/categories", json=payload, headers=user_a_auth_headers)
    user_b_response = client.post("/categories", json=payload, headers=user_b_auth_headers)

    assert user_a_response.status_code == 201
    assert user_b_response.status_code == 201
    assert user_a_response.json["name"] == payload["name"]
    assert user_b_response.json["name"] == payload["name"]


def test_update_category(client, create_category, default_user_auth_headers):
    test_category = create_category("SomeCategory")

    response = client.patch(f"/categories/{test_category.id}", json={"name": "new_name"},headers=default_user_auth_headers)

    assert response.status_code == 200
    assert response.json['id'] == test_category.id
    assert response.json['name'] == 'new_name'


def test_update_category_not_found(client, default_user_auth_headers):
    response = client.patch("/categories/-1", json={"name": "new_name"}, headers=default_user_auth_headers)

    assert response.status_code == 404


def test_update_category_to_existing_name_for_same_user(
    client,
    create_category,
    default_user_auth_headers,
):
    existing_category = create_category("Food")
    category_to_update = create_category("Transport")

    response = client.patch(
        f"/categories/{category_to_update.id}",
        json={"name": existing_category.name},
        headers=default_user_auth_headers,
    )
    check_response = client.get(
        f"/categories/{category_to_update.id}",
        headers=default_user_auth_headers,
    )

    assert response.status_code == 409
    assert check_response.status_code == 200
    assert check_response.json["name"] == category_to_update.name


def test_user_can_update_category_to_name_used_by_another_user(
    client,
    create_user,
    create_category,
    make_auth_headers,
):
    user_a = create_user(email="category-update-same-name-a@test.com")
    user_b = create_user(email="category-update-same-name-b@test.com")
    user_a_auth_headers = make_auth_headers(user_a)

    other_user_category = create_category("Food", user=user_b)
    category_to_update = create_category("Transport", user=user_a)

    response = client.patch(
        f"/categories/{category_to_update.id}",
        json={"name": other_user_category.name},
        headers=user_a_auth_headers,
    )

    assert response.status_code == 200
    assert response.json["id"] == category_to_update.id
    assert response.json["name"] == other_user_category.name


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({"name": ""}, 400),
        ({"name": "        "}, 400),
        ({"name": None}, 400),
    ]
)
def test_update_category_invalid_params(client,
                                        create_category,
                                        default_user_auth_headers,
                                        payload,
                                        expected_status
                                        ):
    test_category = create_category("SomeCategory")

    response = client.patch(f"/categories/{test_category.id}", json=payload, headers=default_user_auth_headers)

    assert response.status_code == expected_status


def test_delete_category(client, create_category, default_user_auth_headers):
    test_category = create_category("SomeCategory")

    response = client.delete(f"/categories/{test_category.id}", headers=default_user_auth_headers)
    check_response = client.get(f"/categories/{test_category.id}", headers=default_user_auth_headers)

    assert response.status_code == 200
    assert check_response.status_code == 404


def test_delete_category_not_found(client, default_user_auth_headers):
    response = client.delete("/categories/99999999", headers=default_user_auth_headers)

    assert response.status_code == 404


def test_delete_used_category(client, create_category, create_expense, default_user_auth_headers):
    category = create_category("SomeCategory")
    create_expense(category=category)

    response = client.delete(f"/categories/{category.id}", headers=default_user_auth_headers)

    assert response.status_code == 409


def test_users_can_see_only_their_categories(client, create_user, create_category, make_auth_headers):
    user_a = create_user("a@gmail.com")
    user_b = create_user("b@gmail.com")
    a_auth_headers = make_auth_headers(user_a)
    b_auth_headers = make_auth_headers(user_b)
    a_category = create_category(user=user_a)

    a_response = client.get(f"/categories/{a_category.id}", headers=a_auth_headers)
    assert a_response.status_code == 200
    assert a_response.json['id'] == a_category.id

    b_response = client.get(f"/categories/{a_category.id}", headers=b_auth_headers)
    assert b_response.status_code == 404


def test_unauthorized_user_cannot_see_categories(client, default_user, create_category):
    a_category = create_category()

    response = client.get(f"/categories/{a_category.id}")

    assert response.status_code == 401
