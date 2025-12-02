import pytest
from httpx import AsyncClient


async def register_and_get_token(client: AsyncClient) -> tuple[str, int]:
    """Helper to register user and get token + org_id."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "StrongPassword123",
            "name": "Test User",
            "organization_name": "Test Org",
        },
    )
    data = response.json()
    return data["access_token"], data["organization_id"]


async def create_contact(client: AsyncClient, token: str, org_id: int) -> int:
    """Helper to create a contact."""
    response = await client.post(
        "/api/v1/contacts",
        json={"name": "John Doe", "email": "john@example.com"},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_deal(client: AsyncClient):
    """Test creating a deal."""
    token, org_id = await register_and_get_token(client)
    contact_id = await create_contact(client, token, org_id)

    response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Test Deal",
            "amount": 10000,
            "currency": "USD",
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Deal"
    assert data["status"] == "new"
    assert data["stage"] == "qualification"


@pytest.mark.asyncio
async def test_cannot_win_deal_with_zero_amount(client: AsyncClient):
    """Test that deal cannot be marked as won with amount <= 0."""
    token, org_id = await register_and_get_token(client)
    contact_id = await create_contact(client, token, org_id)

    # Create deal with 0 amount
    create_response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Zero Deal",
            "amount": 0,
            "currency": "USD",
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    deal_id = create_response.json()["id"]

    # Try to mark as won
    response = await client.patch(
        f"/api/v1/deals/{deal_id}",
        json={"status": "won"},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert response.status_code == 400
    assert "amount" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_deal_status_change_creates_activity(client: AsyncClient):
    """Test that changing deal status creates an activity record."""
    token, org_id = await register_and_get_token(client)
    contact_id = await create_contact(client, token, org_id)

    # Create deal
    create_response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Activity Test Deal",
            "amount": 5000,
            "currency": "USD",
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    deal_id = create_response.json()["id"]

    # Change status to won
    await client.patch(
        f"/api/v1/deals/{deal_id}",
        json={"status": "won"},
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )

    # Check activities
    activities_response = await client.get(
        f"/api/v1/deals/{deal_id}/activities",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": str(org_id),
        },
    )
    assert activities_response.status_code == 200
    activities = activities_response.json()["items"]
    assert len(activities) >= 1
    assert any(a["type"] == "status_changed" for a in activities)
