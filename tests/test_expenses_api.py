

def test_get_expenses(client,
                      create_expense,
                      create_category,
                      create_tag
                      ):

    category = create_category("Food")
    tag = create_tag("Snacks")
    expense = create_expense(category=category, tags=[tag])

    response = client.get("/expenses")

    assert response.status_code == 200
    assert len(response.json) == 1

    expense_from_response = response.json[0]

    assert expense_from_response["id"] == expense.id
    assert expense_from_response["description"] == expense.description
    assert expense_from_response["expense_date"] == expense.expense_date.isoformat()
    assert expense_from_response["category"]["id"] == category.id
    assert expense_from_response["tags"] == [
        {"id": tag.id, "name": tag.name}
    ]
