import pytest


def test_get_categories(client, create_category):
    test_category_name = "SomeTestCategory"
    create_category(test_category_name)
    response = client.get("/categories")

    assert response.status_code == 200

    categories = response.json
    names = {category['name'] for category in categories}

    assert test_category_name in names

def test_get_category_by_id_positive(client, create_category):
    test_category_name = "SomeTestCategory"
    test_category = create_category(test_category_name)

    response = client.get(f"/categories/{test_category.id}")

    assert response.status_code == 200
    assert response.json['id'] == test_category.id
    assert response.json['name'] == test_category.name


def test_get_category_by_id_not_found(client, create_category):
    response = client.get("/categories/-1")

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
                                              limit,
                                              offset,
                                              expected_names):
    create_category("Food")
    create_category("Snacks")
    create_category("Rent")

    response = client.get(f"/categories?limit={limit}&offset={offset}")

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
                                              limit,
                                              offset
                                            ):
    create_category("Food")
    create_category("Snacks")
    create_category("Rent")

    response = client.get(f"/categories?limit={limit}&offset={offset}")

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({"name": ""}, 400),
        ({"name": None}, 400),
    ]
)
def test_create_category_invalid_params(client,
                         payload,
                         expected_status
                        ):

    response = client.post("/categories", json=payload)

    assert response.status_code == expected_status


def test_create_category(client):
    payload = {"name": "SomeTestCategory"}

    response = client.post("/categories", json=payload)

    assert response.status_code == 201
    assert response.json["name"] == payload["name"]


def test_update_category(client, create_category):
    test_category = create_category("SomeCategory")

    response = client.patch(f"/categories/{test_category.id}", json={"name": "new_name"})

    assert response.status_code == 200
    assert response.json['id'] == test_category.id
    assert response.json['name'] == 'new_name'


def test_update_category_not_found(client):
    response = client.patch("/categories/-1", json={"name": "new_name"})

    assert response.status_code == 404


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
                                        payload,
                                        expected_status):
    test_category = create_category("SomeCategory")

    response = client.patch(f"/categories/{test_category.id}", json=payload)

    assert response.status_code == expected_status


def test_delete_category(client, create_category):
    test_category = create_category("SomeCategory")

    response = client.delete(f"/categories/{test_category.id}")
    check_response = client.get(f"/categories/{test_category.id}")

    assert response.status_code == 200
    assert check_response.status_code == 404


def test_delete_category_not_found(client):
    response = client.delete("/categories/99999999")

    assert response.status_code == 404


def test_delete_used_category(client, create_category, create_expense):
    category = create_category("SomeCategory")
    create_expense(category=category)

    response = client.delete(f"/categories/{category.id}")

    assert response.status_code == 409
