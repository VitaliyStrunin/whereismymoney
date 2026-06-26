import pytest


def test_get_tags(client, create_tag):
    test_tag_name = "SomeTestTag"
    create_tag(test_tag_name)
    response = client.get("/tags")

    assert response.status_code == 200

    tags = response.json
    names = {tag["name"] for tag in tags}

    assert test_tag_name in names


def test_get_tag_by_id_positive(client, create_tag):
    test_tag_name = "SomeTestTag"
    test_tag = create_tag(test_tag_name)

    response = client.get(f"/tags/{test_tag.id}")

    assert response.status_code == 200
    assert response.json["id"] == test_tag.id
    assert response.json["name"] == test_tag.name


def test_get_tag_by_id_not_found(client):
    response = client.get("/tags/-1")

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
    limit,
    offset,
    expected_names,
):
    create_tag("Food")
    create_tag("Snacks")
    create_tag("Rent")

    response = client.get(f"/tags?limit={limit}&offset={offset}")

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
    limit,
    offset,
):
    create_tag("Food")
    create_tag("Snacks")
    create_tag("Rent")

    response = client.get(f"/tags?limit={limit}&offset={offset}")

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({"name": ""}, 400),
        ({"name": "        "}, 400),
        ({"name": None}, 400),
    ],
)
def test_create_tag_invalid_params(client, payload, expected_status):
    response = client.post("/tags", json=payload)

    assert response.status_code == expected_status


def test_create_tag(client):
    payload = {"name": "SomeTestTag"}

    response = client.post("/tags", json=payload)

    assert response.status_code == 201
    assert response.json["name"] == payload["name"]


def test_update_tag(client, create_tag):
    test_tag = create_tag("SomeTag")

    response = client.patch(f"/tags/{test_tag.id}", json={"name": "new_name"})

    assert response.status_code == 200
    assert response.json["id"] == test_tag.id
    assert response.json["name"] == "new_name"


def test_update_tag_not_found(client):
    response = client.patch("/tags/-1", json={"name": "new_name"})

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("payload", "expected_status"),
    [
        ({"name": ""}, 400),
        ({"name": "        "}, 400),
        ({"name": None}, 400),
    ],
)
def test_update_tag_invalid_params(client, create_tag, payload, expected_status):
    test_tag = create_tag("SomeTag")

    response = client.patch(f"/tags/{test_tag.id}", json=payload)

    assert response.status_code == expected_status


def test_delete_tag(client, create_tag):
    test_tag = create_tag("SomeTag")

    response = client.delete(f"/tags/{test_tag.id}")
    check_response = client.get(f"/tags/{test_tag.id}")

    assert response.status_code == 200
    assert check_response.status_code == 404
