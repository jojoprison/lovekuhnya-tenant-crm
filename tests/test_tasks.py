from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient


async def setup_deal(client: AsyncClient) -> tuple[str, int, int]:
    """Helper to register user, create contact and deal."""
    # Register
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "StrongPassword123",
            "name": "Test User",
            "organization_name": "Test Org",
        },
    )
    data = reg_response.json()
    token = data["access_token"]
    org_id = data["organization_id"]

    # Create contact
    contact_response = await client.post(
        "/api/v1/contacts",
        json={"name": "John Doe"},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    contact_id = contact_response.json()["id"]

    # Create deal
    deal_response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Test Deal",
            "amount": 1000,
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    deal_id = deal_response.json()["id"]

    return token, org_id, deal_id


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    """Test creating a task."""
    token, org_id, deal_id = await setup_deal(client)

    future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    response = await client.post(
        "/api/v1/tasks",
        json={
            "deal_id": deal_id,
            "title": "Call client",
            "due_date": future_date,
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Call client"
    assert data["is_done"] == False


@pytest.mark.asyncio
async def test_cannot_create_task_with_past_due_date(client: AsyncClient):
    """Test that task cannot be created with due_date in the past."""
    token, org_id, deal_id = await setup_deal(client)

    past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
    response = await client.post(
        "/api/v1/tasks",
        json={
            "deal_id": deal_id,
            "title": "Past Task",
            "due_date": past_date,
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert response.status_code == 400
    assert "past" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_complete_task(client: AsyncClient):
    """Test marking task as done."""
    token, org_id, deal_id = await setup_deal(client)

    future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "deal_id": deal_id,
            "title": "Complete me",
            "due_date": future_date,
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    task_id = create_response.json()["id"]

    # Mark as done
    response = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"is_done": True},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert response.status_code == 200
    assert response.json()["is_done"] == True
