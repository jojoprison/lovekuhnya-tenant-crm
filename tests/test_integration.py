"""
Полный интеграционный тест (из ТЗ):
регистрация → создание организации → добавление участника →
создание контакта → сделки → задачи → аналитика
"""

from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_crm_scenario(client: AsyncClient):
    """
    Полный сценарий использования CRM:
    1. Регистрация пользователя (owner) с организацией
    2. Создание контакта
    3. Создание сделки
    4. Создание задачи
    5. Добавление комментария
    6. Изменение статуса сделки
    7. Получение аналитики
    """

    # ============================================
    # 1. РЕГИСТРАЦИЯ
    # ============================================
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@company.com",
            "password": "SecurePassword123",
            "name": "Company Owner",
            "organization_name": "Test Company Inc",
        },
    )
    assert register_response.status_code == 201, register_response.json()

    reg_data = register_response.json()
    access_token = reg_data["access_token"]
    org_id = reg_data["organization_id"]

    assert reg_data["user"]["email"] == "owner@company.com"
    assert reg_data["organization_name"] == "Test Company Inc"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Organization-Id": str(org_id),
    }

    # ============================================
    # 2. ПРОВЕРКА ОРГАНИЗАЦИЙ
    # ============================================
    orgs_response = await client.get(
        "/api/v1/organizations/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert orgs_response.status_code == 200
    orgs = orgs_response.json()
    assert len(orgs) == 1
    assert orgs[0]["name"] == "Test Company Inc"

    # ============================================
    # 3. СОЗДАНИЕ КОНТАКТА
    # ============================================
    contact_response = await client.post(
        "/api/v1/contacts",
        json={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
        },
        headers=headers,
    )
    assert contact_response.status_code == 201, contact_response.json()

    contact = contact_response.json()
    contact_id = contact["id"]
    assert contact["name"] == "John Doe"
    assert contact["email"] == "john.doe@example.com"

    # Проверка списка контактов
    contacts_list = await client.get("/api/v1/contacts", headers=headers)
    assert contacts_list.status_code == 200
    assert contacts_list.json()["total"] == 1

    # ============================================
    # 4. СОЗДАНИЕ СДЕЛКИ
    # ============================================
    deal_response = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Website Redesign Project",
            "amount": 15000.00,
            "currency": "USD",
        },
        headers=headers,
    )
    assert deal_response.status_code == 201, deal_response.json()

    deal = deal_response.json()
    deal_id = deal["id"]
    assert deal["title"] == "Website Redesign Project"
    assert deal["status"] == "new"
    assert deal["stage"] == "qualification"
    assert float(deal["amount"]) == 15000.00

    # ============================================
    # 5. СОЗДАНИЕ ЗАДАЧИ
    # ============================================
    due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    task_response = await client.post(
        "/api/v1/tasks",
        json={
            "deal_id": deal_id,
            "title": "Initial call with client",
            "description": "Discuss project requirements",
            "due_date": due_date,
        },
        headers=headers,
    )
    assert task_response.status_code == 201, task_response.json()

    task = task_response.json()
    task_id = task["id"]
    assert task["title"] == "Initial call with client"
    assert task["is_done"] == False

    # Проверка списка задач
    tasks_list = await client.get(
        f"/api/v1/tasks?deal_id={deal_id}",
        headers=headers,
    )
    assert tasks_list.status_code == 200
    assert len(tasks_list.json()["items"]) == 1

    # ============================================
    # 6. ДОБАВЛЕНИЕ КОММЕНТАРИЯ (ACTIVITY)
    # ============================================
    comment_response = await client.post(
        f"/api/v1/deals/{deal_id}/activities",
        json={
            "type": "comment",
            "payload": {"text": "Client is very interested in the project"},
        },
        headers=headers,
    )
    assert comment_response.status_code == 201, comment_response.json()

    comment = comment_response.json()
    assert comment["type"] == "comment"
    assert (
        comment["payload"]["text"] == "Client is very interested in the project"
    )

    # ============================================
    # 7. ИЗМЕНЕНИЕ СТАДИИ СДЕЛКИ
    # ============================================
    stage_response = await client.patch(
        f"/api/v1/deals/{deal_id}",
        json={"stage": "proposal"},
        headers=headers,
    )
    assert stage_response.status_code == 200
    assert stage_response.json()["stage"] == "proposal"

    # Проверка что создалась activity для изменения стадии
    activities_response = await client.get(
        f"/api/v1/deals/{deal_id}/activities",
        headers=headers,
    )
    assert activities_response.status_code == 200
    activities = activities_response.json()["items"]
    assert any(a["type"] == "stage_changed" for a in activities)

    # ============================================
    # 8. ЗАКРЫТИЕ СДЕЛКИ КАК WON
    # ============================================
    won_response = await client.patch(
        f"/api/v1/deals/{deal_id}",
        json={"status": "won", "stage": "closed"},
        headers=headers,
    )
    assert won_response.status_code == 200
    won_deal = won_response.json()
    assert won_deal["status"] == "won"
    assert won_deal["stage"] == "closed"

    # Проверка activity для изменения статуса
    activities_response = await client.get(
        f"/api/v1/deals/{deal_id}/activities",
        headers=headers,
    )
    activities = activities_response.json()["items"]
    assert any(a["type"] == "status_changed" for a in activities)

    # ============================================
    # 9. АНАЛИТИКА: SUMMARY
    # ============================================
    summary_response = await client.get(
        "/api/v1/analytics/deals/summary",
        headers=headers,
    )
    assert summary_response.status_code == 200
    summary = summary_response.json()

    # У нас 1 выигранная сделка на $15000
    assert "won" in summary["by_status"]
    assert summary["by_status"]["won"]["count"] == 1
    assert summary["by_status"]["won"]["total_amount"] == 15000.0
    assert summary["avg_won_amount"] == 15000.0

    # ============================================
    # 10. АНАЛИТИКА: FUNNEL
    # ============================================
    funnel_response = await client.get(
        "/api/v1/analytics/deals/funnel",
        headers=headers,
    )
    assert funnel_response.status_code == 200
    funnel = funnel_response.json()
    assert "stages" in funnel

    # ============================================
    # 11. ЗАВЕРШЕНИЕ ЗАДАЧИ
    # ============================================
    complete_task = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"is_done": True},
        headers=headers,
    )
    assert complete_task.status_code == 200
    assert complete_task.json()["is_done"] == True

    # ============================================
    # 12. ПРОВЕРКА БИЗНЕС-ПРАВИЛА: НЕЛЬЗЯ УДАЛИТЬ КОНТАКТ СО СДЕЛКАМИ
    # ============================================
    delete_contact = await client.delete(
        f"/api/v1/contacts/{contact_id}",
        headers=headers,
    )
    assert delete_contact.status_code == 409  # Conflict


@pytest.mark.asyncio
async def test_business_rule_won_requires_positive_amount(client: AsyncClient):
    """Тест бизнес-правила: нельзя закрыть сделку как won с amount <= 0."""

    # Регистрация
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@test.com",
            "password": "Password123",
            "name": "Test User",
            "organization_name": "Test Org",
        },
    )
    data = reg.json()
    headers = {
        "Authorization": f"Bearer {data['access_token']}",
        "X-Organization-Id": str(data["organization_id"]),
    }

    # Создание контакта
    contact = await client.post(
        "/api/v1/contacts",
        json={"name": "Contact"},
        headers=headers,
    )
    contact_id = contact.json()["id"]

    # Создание сделки с amount = 0
    deal = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "Zero Deal",
            "amount": 0,
        },
        headers=headers,
    )
    deal_id = deal.json()["id"]

    # Попытка закрыть как won
    response = await client.patch(
        f"/api/v1/deals/{deal_id}",
        json={"status": "won"},
        headers=headers,
    )
    assert response.status_code == 400
    assert "amount" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_business_rule_task_due_date_not_in_past(client: AsyncClient):
    """Тест бизнес-правила: due_date задачи не может быть в прошлом."""

    # Регистрация
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test2@test.com",
            "password": "Password123",
            "name": "Test User",
            "organization_name": "Test Org",
        },
    )
    data = reg.json()
    headers = {
        "Authorization": f"Bearer {data['access_token']}",
        "X-Organization-Id": str(data["organization_id"]),
    }

    # Создание контакта и сделки
    contact = await client.post(
        "/api/v1/contacts",
        json={"name": "Contact"},
        headers=headers,
    )
    deal = await client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact.json()["id"],
            "title": "Deal",
            "amount": 1000,
        },
        headers=headers,
    )
    deal_id = deal.json()["id"]

    # Попытка создать задачу с прошедшей датой
    past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
    response = await client.post(
        "/api/v1/tasks",
        json={
            "deal_id": deal_id,
            "title": "Past Task",
            "due_date": past_date,
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert "past" in response.json()["detail"].lower()
