import pytest


def assert_expense_fields_unchanged(updated_expense, original_expense, changed_fields):
    fields_to_check = [
        "id",
        "amount",
        "description",
        "expense_date",
        "category_id",
        "category",
        "tags",
    ]

    for field in fields_to_check:
        if field not in changed_fields:
            assert updated_expense[field] == original_expense[field]


def test_get_expenses(client, create_expense, create_category, create_tag, default_user_auth_headers):
    category = create_category("Food")
    tag = create_tag("Snacks")
    expense = create_expense(category=category, tags=[tag])

    response = client.get("/expenses", headers=default_user_auth_headers)

    assert response.status_code == 200
    assert len(response.json) == 1

    expense_from_response = response.json[0]

    assert expense_from_response["id"] == expense.id
    assert expense_from_response["amount"] == str(expense.amount)
    assert expense_from_response["description"] == expense.description
    assert expense_from_response["expense_date"] == expense.expense_date.isoformat()
    assert expense_from_response["category"]["id"] == category.id
    assert expense_from_response["tags"] == [{"id": tag.id, "name": tag.name}]


def test_no_expenses(client, default_user_auth_headers):
    response = client.get("/expenses", headers=default_user_auth_headers)

    assert response.status_code == 200
    assert response.json == []


@pytest.mark.parametrize(
    ("limit", "offset", "expected_descriptions"),
    [
        (1, 0, ["1"]),
        (1, 1, ["2"]),
        (2, 1, ["2", "3"]),
        (10, 10, []),
    ],
)
def test_get_expenses_with_limit_offset(
    client,
    create_expense,
    default_user_auth_headers,
    limit,
    offset,
    expected_descriptions,
):
    create_expense(description="1")
    create_expense(description="2")
    create_expense(description="3")

    response = client.get(f"/expenses?limit={limit}&offset={offset}",  headers=default_user_auth_headers)

    assert response.status_code == 200

    descriptions = [expense["description"] for expense in response.json]

    assert descriptions == expected_descriptions


@pytest.mark.parametrize(
    ("limit", "offset", "expected_status"),
    [
        (0, 0, 400),
        (-1, -1, 400),
        (1, -1, 400),
        (-1, 1, 400),
        (150, 1, 400),
        ("limit", 1, 400),
        (10, "offset", 400),
    ],
)
def test_get_expenses_with_limit_offset_invalid(
    client,
    default_user_auth_headers,
    limit,
    offset,
    expected_status,
):
    response = client.get(f"/expenses?limit={limit}&offset={offset}", headers=default_user_auth_headers)

    assert response.status_code == expected_status


def test_get_expense_by_id(client, create_expense, create_category, create_tag, default_user_auth_headers):
    category = create_category("Food")
    tag = create_tag("Snacks")
    expense = create_expense(category=category, tags=[tag])

    response = client.get(f"/expenses/{expense.id}", headers=default_user_auth_headers)

    assert response.status_code == 200

    expense_from_response = response.json

    assert expense_from_response["id"] == expense.id
    assert expense_from_response["amount"] == str(expense.amount)
    assert expense_from_response["description"] == expense.description
    assert expense_from_response["expense_date"] == expense.expense_date.isoformat()
    assert expense_from_response["category"]["id"] == category.id
    assert expense_from_response["tags"] == [{"id": tag.id, "name": tag.name}]


def test_get_expense_by_id_not_found(client, default_user_auth_headers):
    response = client.get("/expenses/99999999", headers=default_user_auth_headers)

    assert response.status_code == 404


def test_get_expense_by_id_without_tags(client, create_expense, create_category, default_user_auth_headers):
    category = create_category("Food")
    expense = create_expense(category=category, tags=[])

    response = client.get(f"/expenses/{expense.id}", headers=default_user_auth_headers)

    assert response.status_code == 200

    expense_from_response = response.json

    assert expense_from_response["id"] == expense.id
    assert expense_from_response["tags"] == []


def test_create_expense(client, create_category, create_tag, default_user_auth_headers):
    category = create_category("Food")
    tag = create_tag("Snacks")
    expense_payload = {
        "amount": "100.0",
        "description": "SomeDescription",
        "expense_date": "2026-06-30",
        "category_id": category.id,
        "tag_ids": [tag.id],
    }

    response = client.post("/expenses", json=expense_payload, headers=default_user_auth_headers)

    assert response.status_code == 201

    expense_from_response = response.json

    assert expense_from_response["amount"] == str(expense_payload["amount"])
    assert expense_from_response["description"] == expense_payload["description"]
    assert expense_from_response["expense_date"] == expense_payload["expense_date"]
    assert expense_from_response["category"]["id"] == category.id
    assert expense_from_response["tags"] == [{"id": tag.id, "name": tag.name}]


@pytest.mark.parametrize(
    ("description", "expected_status"),
    [
        (None, 400),
        ("a" * 1000, 400),
        (123, 400),
    ],
)
def test_create_expense_invalid_description(
    client,
    create_category,
    create_tag,
    default_user_auth_headers,
    description,
    expected_status,
):
    category = create_category("Food")
    tag = create_tag("Snacks")
    expense_payload = {
        "amount": "100.0",
        "description": description,
        "expense_date": "2026-06-30",
        "category_id": category.id,
        "tag_ids": [tag.id],
    }

    response = client.post("/expenses", json=expense_payload, headers=default_user_auth_headers)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "category_id",
    [
        -1,
        "not a category_id",
        0,
    ],
)
def test_create_expense_invalid_category(client, create_tag, default_user_auth_headers, category_id):
    tag = create_tag("Snacks")
    expense_payload = {
        "amount": "100.0",
        "description": "SomeDescription",
        "expense_date": "2026-06-30",
        "category_id": category_id,
        "tag_ids": [tag.id],
    }

    response = client.post("/expenses", json=expense_payload, headers=default_user_auth_headers)

    assert response.status_code == 400


def test_create_expense_category_not_found(client, create_tag, default_user_auth_headers):
    tag = create_tag("Snacks")
    expense_payload = {
        "amount": "100.0",
        "description": "SomeDescription",
        "expense_date": "2026-06-30",
        "category_id": 42,
        "tag_ids": [tag.id],
    }

    response = client.post("/expenses", json=expense_payload, headers=default_user_auth_headers)

    assert response.status_code == 404


def test_create_expense_invalid_tag(client, create_category, default_user_auth_headers):
    category = create_category("SomeCategory")
    expense_payload = {
        "amount": "100.0",
        "description": "SomeDescription",
        "expense_date": "2026-06-30",
        "category_id": category.id,
        "tag_ids": ["Some tags", "But not ids"],
    }

    response = client.post("/expenses", json=expense_payload, headers=default_user_auth_headers)

    assert response.status_code == 400


def test_create_expense_tag_not_found(client, create_category, default_user_auth_headers):
    category = create_category("SomeCategory")
    expense_payload = {
        "amount": "100.0",
        "description": "SomeDescription",
        "expense_date": "2026-06-30",
        "category_id": category.id,
        "tag_ids": [42],
    }

    response = client.post("/expenses", json=expense_payload, headers=default_user_auth_headers)

    assert response.status_code == 404


@pytest.mark.parametrize(
    "field_to_remove",
    [
        "amount",
        "expense_date",
        "category_id",
    ],
)
def test_create_expense_missing_required_fields(
    client,
    create_category,
    default_user_auth_headers,
    field_to_remove,
):
    category = create_category("Food")
    payload = {
        "amount": "100.00",
        "description": "SomeDescription",
        "expense_date": "2026-06-30",
        "category_id": category.id,
        "tag_ids": [],
    }
    payload.pop(field_to_remove)

    response = client.post("/expenses", json=payload, headers=default_user_auth_headers)

    assert response.status_code == 400


@pytest.mark.parametrize(
    "expense_date",
    [
        "",
        "100% not a date",
        "30-06-2026",
        "2026/10/21",
    ],
)
def test_create_expense_invalid_expense_date(client, create_category, default_user_auth_headers, expense_date):
    category = create_category("Food")
    payload = {
        "amount": "100.00",
        "description": "SomeDescription",
        "expense_date": expense_date,
        "category_id": category.id,
        "tag_ids": [],
    }

    response = client.post("/expenses", json=payload, headers=default_user_auth_headers)

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("amount", "expected_status"),
    [
        (0, 400),
        (-1, 400),
        ("", 400),
        ("invalid amount", 400),
        (None, 400),
        (1289741627854781235612367813901285412873, 400),
        (1284.123124123124123123, 400),
    ],
)
def test_create_expense_invalid_amount(
    client,
    create_category,
    create_tag,
    default_user_auth_headers,
    amount,
    expected_status,
):
    category = create_category("Food")
    tag = create_tag("Snacks")
    expense_payload = {
        "amount": amount,
        "description": "SomeDescription",
        "expense_date": "2026-06-30",
        "category_id": category.id,
        "tag_ids": [tag.id],
    }

    response = client.post("/expenses", json=expense_payload, headers=default_user_auth_headers)

    assert response.status_code == expected_status


def test_update_expense_all_fields(client, create_expense, create_category, default_user_auth_headers):
    expense = create_expense()
    category = create_category("Food")

    update_data = {
        "amount": "42",
        "description": "SomeUpdatedDescription",
        "expense_date": "1999-12-31",
        "category_id": category.id,
        "tag_ids": [],
    }

    response = client.patch(f"/expenses/{expense.id}", json=update_data, headers=default_user_auth_headers)

    assert response.status_code == 200

    updated_expense = response.json

    assert updated_expense["id"] == expense.id
    assert updated_expense["amount"] == str(update_data["amount"])
    assert updated_expense["description"] == str(update_data["description"])
    assert updated_expense["expense_date"] == str(update_data["expense_date"])
    assert updated_expense["category_id"] == update_data["category_id"]
    assert updated_expense["category"] == {"id": category.id, "name": category.name}
    assert updated_expense["tags"] == []


@pytest.mark.parametrize(
    ("test_field", "test_value", "expected_value"),
    [
        ("amount", "150.00", "150.00"),
        ("description", "New description", "New description"),
        ("expense_date", "2026-07-01", "2026-07-01"),
    ],
)
def test_update_expense_one_simple_field(
    client,
    create_expense,
    create_category,
    create_tag,
    default_user_auth_headers,
    test_field,
    test_value,
    expected_value,
):
    category = create_category("Food")
    tag = create_tag("Snack")
    expense = create_expense(category=category, tags=[tag])

    original_response = client.get(f"/expenses/{expense.id}", headers=default_user_auth_headers)
    original_expense = original_response.json

    response = client.patch(
        f"/expenses/{expense.id}",
        json={test_field: test_value},
        headers=default_user_auth_headers
    )

    assert response.status_code == 200

    updated_expense = response.json

    assert updated_expense[test_field] == expected_value
    assert_expense_fields_unchanged(
        updated_expense=updated_expense,
        original_expense=original_expense,
        changed_fields={test_field},
    )


def test_update_expense_category_only(
    client,
    create_expense,
    create_category,
    create_tag,
    default_user_auth_headers
):
    old_category = create_category("Food")
    new_category = create_category("Transport")
    tag = create_tag("Snack")
    expense = create_expense(category=old_category, tags=[tag])

    original_response = client.get(f"/expenses/{expense.id}", headers=default_user_auth_headers)
    original_expense = original_response.json

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"category_id": new_category.id},
        headers=default_user_auth_headers
    )

    assert response.status_code == 200

    updated_expense = response.json

    assert updated_expense["category_id"] == new_category.id
    assert updated_expense["category"] == {
        "id": new_category.id,
        "name": new_category.name,
    }
    assert_expense_fields_unchanged(
        updated_expense=updated_expense,
        original_expense=original_expense,
        changed_fields={"category_id", "category"},
    )


def test_update_expense_tags_only(
    client,
    create_expense,
    create_category,
    create_tag,
    default_user_auth_headers
):
    category = create_category("Food")
    old_tag = create_tag("OldTag")
    new_tag_1 = create_tag("NewTag1")
    new_tag_2 = create_tag("NewTag2")
    expense = create_expense(category=category, tags=[old_tag])

    original_response = client.get(f"/expenses/{expense.id}", headers=default_user_auth_headers)
    original_expense = original_response.json

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"tag_ids": [new_tag_1.id, new_tag_2.id]},
        headers=default_user_auth_headers
    )

    assert response.status_code == 200

    updated_expense = response.json

    assert {tag["id"] for tag in updated_expense["tags"]} == {
        new_tag_1.id,
        new_tag_2.id,
    }
    assert {tag["name"] for tag in updated_expense["tags"]} == {
        new_tag_1.name,
        new_tag_2.name,
    }
    assert_expense_fields_unchanged(
        updated_expense=updated_expense,
        original_expense=original_expense,
        changed_fields={"tags"},
    )


def test_update_expense_clear_tags(
    client,
    create_expense,
    create_category,
    create_tag,
    default_user_auth_headers
):
    category = create_category("Food")
    tag = create_tag("Snack")
    expense = create_expense(category=category, tags=[tag])

    original_response = client.get(f"/expenses/{expense.id}", headers=default_user_auth_headers)
    original_expense = original_response.json

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"tag_ids": []},
        headers=default_user_auth_headers
    )

    assert response.status_code == 200

    updated_expense = response.json

    assert updated_expense["tags"] == []
    assert_expense_fields_unchanged(
        updated_expense=updated_expense,
        original_expense=original_expense,
        changed_fields={"tags"},
    )


def test_update_expense_empty_payload(client, create_expense, default_user_auth_headers):
    expense = create_expense()

    original_response = client.get(f"/expenses/{expense.id}", headers=default_user_auth_headers)
    original_expense = original_response.json

    response = client.patch(f"/expenses/{expense.id}", json={}, headers=default_user_auth_headers)

    assert response.status_code == 200
    assert response.json == original_expense


def test_update_expense_not_found(client, default_user_auth_headers):
    response = client.patch(
        "/expenses/99999999",
        json={"description": "New description"},
        headers=default_user_auth_headers
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "amount",
    [
        0,
        -1,
        "",
        "invalid amount",
        None,
        "100000000.00",
        "12.345",
    ],
)
def test_update_expense_invalid_amount(client, create_expense, default_user_auth_headers, amount):
    expense = create_expense()

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"amount": amount},
        headers=default_user_auth_headers
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "description",
    [
        None,
        123,
        "a" * 1000,
    ],
)
def test_update_expense_invalid_description(client, create_expense, default_user_auth_headers, description):
    expense = create_expense()

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"description": description},
        headers=default_user_auth_headers
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "expense_date",
    [
        "",
        "not-a-date",
        "30-06-2026",
        "2026/06/30",
    ],
)
def test_update_expense_invalid_expense_date(client, create_expense, default_user_auth_headers, expense_date):
    expense = create_expense()

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"expense_date": expense_date},
        headers=default_user_auth_headers
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "category_id",
    [
        0,
        -1,
        "not-id",
        None,
    ],
)
def test_update_expense_invalid_category_id(client, create_expense, default_user_auth_headers, category_id):
    expense = create_expense()

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"category_id": category_id},
        headers=default_user_auth_headers
    )

    assert response.status_code == 400


def test_update_expense_category_not_found(client, create_expense, default_user_auth_headers):
    expense = create_expense()

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"category_id": 99999999},
        headers=default_user_auth_headers
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "tag_ids",
    [
        "not-a-list",
        123,
        None,
        ["not-id"],
        [0],
        [-1],
    ],
)
def test_update_expense_invalid_tag_ids(client, create_expense, default_user_auth_headers, tag_ids):
    expense = create_expense()

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"tag_ids": tag_ids},
        headers=default_user_auth_headers
    )

    assert response.status_code == 400


def test_update_expense_tag_not_found(client, create_expense, default_user_auth_headers):
    expense = create_expense()

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"tag_ids": [99999999]},
        headers=default_user_auth_headers
    )

    assert response.status_code == 404


def test_delete_expense(client, create_expense, default_user_auth_headers):
    expense = create_expense()

    response = client.delete(f"/expenses/{expense.id}", headers=default_user_auth_headers)

    assert response.status_code == 200

    check_deleted_response = client.get(f"/expenses/{expense.id}", headers=default_user_auth_headers)

    assert check_deleted_response.status_code == 404


def test_delete_expense_not_found(client, default_user_auth_headers):
    response = client.delete("/expenses/999999", headers=default_user_auth_headers)

    assert response.status_code == 404


def test_user_can_see_only_own_expenses_in_list(
    client,
    create_user,
    create_category,
    create_tag,
    create_expense,
    make_auth_headers,
):
    user_a = create_user(email="expense-list-user-a@test.com")
    user_b = create_user(email="expense-list-user-b@test.com")

    user_a_headers = make_auth_headers(user_a)

    user_a_category = create_category(user=user_a)
    user_a_tag = create_tag(user=user_a)
    user_b_category = create_category(user=user_b)
    user_b_tag = create_tag(user=user_b)

    user_a_expense = create_expense(
        description="User A expense",
        category=user_a_category,
        tags=[user_a_tag],
        user=user_a,
    )
    user_b_expense = create_expense(
        description="User B expense",
        category=user_b_category,
        tags=[user_b_tag],
        user=user_b,
    )

    response = client.get("/expenses", headers=user_a_headers)

    assert response.status_code == 200

    expense_ids = {expense["id"] for expense in response.json}

    assert user_a_expense.id in expense_ids
    assert user_b_expense.id not in expense_ids


def test_user_cannot_get_other_user_expense_by_id(
    client,
    create_user,
    create_category,
    create_tag,
    create_expense,
    make_auth_headers,
):
    owner = create_user(email="expense-get-owner@test.com")
    other_user = create_user(email="expense-get-other-user@test.com")

    owner_headers = make_auth_headers(owner)
    other_user_headers = make_auth_headers(other_user)

    category = create_category(user=owner)
    tag = create_tag(user=owner)
    expense = create_expense(category=category, tags=[tag], user=owner)

    owner_response = client.get(f"/expenses/{expense.id}", headers=owner_headers)
    other_user_response = client.get(
        f"/expenses/{expense.id}",
        headers=other_user_headers,
    )

    assert owner_response.status_code == 200
    assert owner_response.json["id"] == expense.id
    assert other_user_response.status_code == 404


def test_user_cannot_update_other_user_expense(
    client,
    create_user,
    create_category,
    create_tag,
    create_expense,
    make_auth_headers,
):
    owner = create_user(email="expense-update-owner@test.com")
    other_user = create_user(email="expense-update-other-user@test.com")

    owner_headers = make_auth_headers(owner)
    other_user_headers = make_auth_headers(other_user)

    category = create_category(user=owner)
    tag = create_tag(user=owner)
    expense = create_expense(
        description="Original description",
        category=category,
        tags=[tag],
        user=owner,
    )

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"description": "Updated by other user"},
        headers=other_user_headers,
    )
    owner_response = client.get(f"/expenses/{expense.id}", headers=owner_headers)

    assert response.status_code == 404
    assert owner_response.status_code == 200
    assert owner_response.json["description"] == expense.description


def test_user_cannot_delete_other_user_expense(
    client,
    create_user,
    create_category,
    create_tag,
    create_expense,
    make_auth_headers,
):
    owner = create_user(email="expense-delete-owner@test.com")
    other_user = create_user(email="expense-delete-other-user@test.com")

    owner_headers = make_auth_headers(owner)
    other_user_headers = make_auth_headers(other_user)

    category = create_category(user=owner)
    tag = create_tag(user=owner)
    expense = create_expense(category=category, tags=[tag], user=owner)

    response = client.delete(f"/expenses/{expense.id}", headers=other_user_headers)
    owner_response = client.get(f"/expenses/{expense.id}", headers=owner_headers)

    assert response.status_code == 404
    assert owner_response.status_code == 200
    assert owner_response.json["id"] == expense.id


def test_user_cannot_create_expense_with_other_user_category(
    client,
    create_user,
    create_category,
    create_tag,
    make_auth_headers,
):
    category_owner = create_user(email="expense-create-category-owner@test.com")
    current_user = create_user(email="expense-create-category-current@test.com")

    current_user_headers = make_auth_headers(current_user)

    other_user_category = create_category(user=category_owner)
    current_user_tag = create_tag(user=current_user)
    payload = {
        "amount": "100.00",
        "description": "SomeDescription",
        "expense_date": "2026-06-30",
        "category_id": other_user_category.id,
        "tag_ids": [current_user_tag.id],
    }

    response = client.post("/expenses", json=payload, headers=current_user_headers)

    assert response.status_code == 404


def test_user_cannot_create_expense_with_other_user_tag(
    client,
    create_user,
    create_category,
    create_tag,
    make_auth_headers,
):
    tag_owner = create_user(email="expense-create-tag-owner@test.com")
    current_user = create_user(email="expense-create-tag-current@test.com")

    current_user_headers = make_auth_headers(current_user)

    current_user_category = create_category(user=current_user)
    other_user_tag = create_tag(user=tag_owner)
    payload = {
        "amount": "100.00",
        "description": "SomeDescription",
        "expense_date": "2026-06-30",
        "category_id": current_user_category.id,
        "tag_ids": [other_user_tag.id],
    }

    response = client.post("/expenses", json=payload, headers=current_user_headers)

    assert response.status_code == 404


def test_user_cannot_update_expense_to_other_user_category(
    client,
    create_user,
    create_category,
    create_tag,
    create_expense,
    make_auth_headers,
):
    category_owner = create_user(email="expense-patch-category-owner@test.com")
    current_user = create_user(email="expense-patch-category-current@test.com")

    current_user_headers = make_auth_headers(current_user)

    current_user_category = create_category(user=current_user)
    current_user_tag = create_tag(user=current_user)
    other_user_category = create_category(user=category_owner)
    expense = create_expense(
        category=current_user_category,
        tags=[current_user_tag],
        user=current_user,
    )

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"category_id": other_user_category.id},
        headers=current_user_headers,
    )
    check_response = client.get(f"/expenses/{expense.id}", headers=current_user_headers)

    assert response.status_code == 404
    assert check_response.status_code == 200
    assert check_response.json["category_id"] == current_user_category.id


def test_user_cannot_update_expense_to_other_user_tag(
    client,
    create_user,
    create_category,
    create_tag,
    create_expense,
    make_auth_headers,
):
    tag_owner = create_user(email="expense-patch-tag-owner@test.com")
    current_user = create_user(email="expense-patch-tag-current@test.com")

    current_user_headers = make_auth_headers(current_user)

    current_user_category = create_category(user=current_user)
    current_user_tag = create_tag(user=current_user)
    other_user_tag = create_tag(user=tag_owner)
    expense = create_expense(
        category=current_user_category,
        tags=[current_user_tag],
        user=current_user,
    )

    response = client.patch(
        f"/expenses/{expense.id}",
        json={"tag_ids": [other_user_tag.id]},
        headers=current_user_headers,
    )
    check_response = client.get(f"/expenses/{expense.id}", headers=current_user_headers)

    assert response.status_code == 404
    assert check_response.status_code == 200
    assert check_response.json["tags"] == [
        {"id": current_user_tag.id, "name": current_user_tag.name}
    ]
