#!/bin/bash
# Smoke test для LoveKuhnya Tenant CRM API
# Проверяет основные сценарии по ТЗ

set -e

BASE_URL="${BASE_URL:-http://localhost:8007/api/v1}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${CYAN}[TEST]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }
header() { echo -e "\n${BOLD}${YELLOW}=== $1 ===${NC}\n"; }

# Генерируем уникальный email
TIMESTAMP=$(date +%s)
EMAIL="smoke_${TIMESTAMP}@test.com"
PASSWORD="TestPass123"
ORG_NAME="Smoke Test Org ${TIMESTAMP}"

header "1. HEALTH CHECK"
log "GET /health"
curl -s http://localhost:8007/health | jq .
success "API is running"

header "2. REGISTRATION"
log "POST /auth/register"
REGISTER_RESP=$(curl -s -X POST "${BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${EMAIL}\",
    \"password\": \"${PASSWORD}\",
    \"name\": \"Smoke Tester\",
    \"organization_name\": \"${ORG_NAME}\"
  }")
echo "$REGISTER_RESP" | jq .
USER_ID=$(echo "$REGISTER_RESP" | jq -r '.user.id')
[ "$USER_ID" != "null" ] && success "User created: id=$USER_ID" || fail "Registration failed"

header "3. LOGIN"
log "POST /auth/login"
LOGIN_RESP=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"${EMAIL}\", \"password\": \"${PASSWORD}\"}")
echo "$LOGIN_RESP" | jq .
ACCESS_TOKEN=$(echo "$LOGIN_RESP" | jq -r '.access_token')
[ "$ACCESS_TOKEN" != "null" ] && success "Got access token" || fail "Login failed"

AUTH="Authorization: Bearer ${ACCESS_TOKEN}"

header "4. GET ORGANIZATIONS"
log "GET /organizations/me"
ORGS_RESP=$(curl -s -X GET "${BASE_URL}/organizations/me" -H "$AUTH")
echo "$ORGS_RESP" | jq .
ORG_ID=$(echo "$ORGS_RESP" | jq -r '.[0].id // .[0].organization.id')
[ "$ORG_ID" != "null" ] && [ "$ORG_ID" != "" ] && success "Organization: id=$ORG_ID" || fail "No organizations"

ORG_HEADER="X-Organization-Id: ${ORG_ID}"

header "5. CREATE CONTACT"
log "POST /contacts"
CONTACT_RESP=$(curl -s -X POST "${BASE_URL}/contacts" \
  -H "$AUTH" -H "$ORG_HEADER" -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  }')
echo "$CONTACT_RESP" | jq .
CONTACT_ID=$(echo "$CONTACT_RESP" | jq -r '.id')
[ "$CONTACT_ID" != "null" ] && success "Contact created: id=$CONTACT_ID" || fail "Contact creation failed"

header "6. LIST CONTACTS"
log "GET /contacts"
curl -s -X GET "${BASE_URL}/contacts" -H "$AUTH" -H "$ORG_HEADER" | jq .
success "Contacts listed"

header "7. CREATE DEAL"
log "POST /deals"
DEAL_RESP=$(curl -s -X POST "${BASE_URL}/deals" \
  -H "$AUTH" -H "$ORG_HEADER" -H "Content-Type: application/json" \
  -d "{
    \"contact_id\": ${CONTACT_ID},
    \"title\": \"Website Redesign\",
    \"amount\": 15000.00,
    \"currency\": \"USD\"
  }")
echo "$DEAL_RESP" | jq .
DEAL_ID=$(echo "$DEAL_RESP" | jq -r '.id')
[ "$DEAL_ID" != "null" ] && success "Deal created: id=$DEAL_ID" || fail "Deal creation failed"

header "8. LIST DEALS (with filters)"
log "GET /deals?status=new"
curl -s -X GET "${BASE_URL}/deals?status=new" -H "$AUTH" -H "$ORG_HEADER" | jq .
success "Deals listed"

header "9. UPDATE DEAL - Change stage"
log "PATCH /deals/${DEAL_ID} (stage -> proposal)"
PATCH_RESP=$(curl -s -X PATCH "${BASE_URL}/deals/${DEAL_ID}" \
  -H "$AUTH" -H "$ORG_HEADER" -H "Content-Type: application/json" \
  -d '{"stage": "proposal"}')
echo "$PATCH_RESP" | jq .
success "Deal stage updated"

header "10. CREATE TASK"
DUE_DATE=$(date -v+7d +%Y-%m-%d 2>/dev/null || date -d "+7 days" +%Y-%m-%d)
log "POST /tasks (due_date: ${DUE_DATE})"
TASK_RESP=$(curl -s -X POST "${BASE_URL}/tasks" \
  -H "$AUTH" -H "$ORG_HEADER" -H "Content-Type: application/json" \
  -d "{
    \"deal_id\": ${DEAL_ID},
    \"title\": \"Follow up call\",
    \"description\": \"Discuss proposal details\",
    \"due_date\": \"${DUE_DATE}T10:00:00\"
  }")
echo "$TASK_RESP" | jq .
TASK_ID=$(echo "$TASK_RESP" | jq -r '.id')
[ "$TASK_ID" != "null" ] && success "Task created: id=$TASK_ID" || fail "Task creation failed"

header "11. BUSINESS RULE: Task due_date in past (should fail)"
log "POST /tasks with past date"
PAST_TASK=$(curl -s -X POST "${BASE_URL}/tasks" \
  -H "$AUTH" -H "$ORG_HEADER" -H "Content-Type: application/json" \
  -d "{
    \"deal_id\": ${DEAL_ID},
    \"title\": \"Past task\",
    \"due_date\": \"2020-01-01T10:00:00\"
  }")
echo "$PAST_TASK" | jq .
echo "$PAST_TASK" | grep -q "past" && success "Correctly rejected past due_date" || fail "Should reject past date"

header "12. ADD COMMENT TO DEAL"
log "POST /deals/${DEAL_ID}/activities"
COMMENT_RESP=$(curl -s -X POST "${BASE_URL}/deals/${DEAL_ID}/activities" \
  -H "$AUTH" -H "$ORG_HEADER" -H "Content-Type: application/json" \
  -d '{
    "type": "comment",
    "payload": {"text": "Client is interested, scheduling demo"}
  }')
echo "$COMMENT_RESP" | jq .
success "Comment added"

header "13. GET DEAL ACTIVITIES (timeline)"
log "GET /deals/${DEAL_ID}/activities"
curl -s -X GET "${BASE_URL}/deals/${DEAL_ID}/activities" -H "$AUTH" -H "$ORG_HEADER" | jq .
success "Activities retrieved"

header "14. UPDATE DEAL - Mark as WON"
log "PATCH /deals/${DEAL_ID} (status -> won, stage -> closed)"
WON_RESP=$(curl -s -X PATCH "${BASE_URL}/deals/${DEAL_ID}" \
  -H "$AUTH" -H "$ORG_HEADER" -H "Content-Type: application/json" \
  -d '{"status": "won", "stage": "closed"}')
echo "$WON_RESP" | jq .
success "Deal marked as won"

header "15. BUSINESS RULE: Cannot win deal with amount <= 0"
log "Create deal with amount=0, try to mark as won"
ZERO_DEAL=$(curl -s -X POST "${BASE_URL}/deals" \
  -H "$AUTH" -H "$ORG_HEADER" -H "Content-Type: application/json" \
  -d "{\"contact_id\": ${CONTACT_ID}, \"title\": \"Zero Deal\", \"amount\": 0}")
ZERO_ID=$(echo "$ZERO_DEAL" | jq -r '.id')
ZERO_WON=$(curl -s -X PATCH "${BASE_URL}/deals/${ZERO_ID}" \
  -H "$AUTH" -H "$ORG_HEADER" -H "Content-Type: application/json" \
  -d '{"status": "won"}')
echo "$ZERO_WON" | jq .
echo "$ZERO_WON" | grep -q "amount" && success "Correctly rejected won with amount=0" || fail "Should reject"

header "16. ANALYTICS - Deals Summary"
log "GET /analytics/deals/summary"
curl -s -X GET "${BASE_URL}/analytics/deals/summary" -H "$AUTH" -H "$ORG_HEADER" | jq .
success "Summary retrieved"

header "17. ANALYTICS - Sales Funnel"
log "GET /analytics/deals/funnel"
curl -s -X GET "${BASE_URL}/analytics/deals/funnel" -H "$AUTH" -H "$ORG_HEADER" | jq .
success "Funnel retrieved"

header "18. BUSINESS RULE: Cannot delete contact with deals"
log "DELETE /contacts/${CONTACT_ID} (should fail - has deals)"
DEL_CONTACT=$(curl -s -X DELETE "${BASE_URL}/contacts/${CONTACT_ID}" -H "$AUTH" -H "$ORG_HEADER")
echo "$DEL_CONTACT" | jq .
echo "$DEL_CONTACT" | grep -qi "deal\|conflict" && success "Correctly rejected delete" || fail "Should reject"

header "19. COMPLETE TASK"
log "PATCH /tasks/${TASK_ID} (is_done -> true)"
curl -s -X PATCH "${BASE_URL}/tasks/${TASK_ID}" \
  -H "$AUTH" -H "$ORG_HEADER" -H "Content-Type: application/json" \
  -d '{"is_done": true}' | jq .
success "Task completed"

header "20. LIST TASKS (only open)"
log "GET /tasks?deal_id=${DEAL_ID}&only_open=true"
curl -s -X GET "${BASE_URL}/tasks?deal_id=${DEAL_ID}&only_open=true" -H "$AUTH" -H "$ORG_HEADER" | jq .
success "Open tasks listed"

header "21. REFRESH TOKEN"
REFRESH_TOKEN=$(echo "$LOGIN_RESP" | jq -r '.refresh_token')
log "POST /auth/refresh"
curl -s -X POST "${BASE_URL}/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"${REFRESH_TOKEN}\"}" | jq .
success "Token refreshed"

echo ""
echo -e "${BOLD}${GREEN}========================================${NC}"
echo -e "${BOLD}${GREEN}  ALL SMOKE TESTS PASSED!${NC}"
echo -e "${BOLD}${GREEN}========================================${NC}"
echo ""
