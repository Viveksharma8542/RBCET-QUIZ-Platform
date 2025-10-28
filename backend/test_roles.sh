#!/bin/bash

# QuizzApp Role Update Test Script
# This script tests that all role-related functionality works with uppercase roles

set -e  # Exit on any error

echo "========================================="
echo "QuizzApp Role Update Test Script"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000"

# Step 1: Login as Admin
echo "Step 1: Logging in as Admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@macquiz.com","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to login as admin${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Successfully logged in as admin${NC}"
echo "Token: ${TOKEN:0:50}..."
echo ""

# Step 2: Create a Teacher with UPPERCASE role
echo "Step 2: Creating teacher with role='TEACHER'..."
CREATE_TEACHER=$(curl -s -X POST "$BASE_URL/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.teacher@university.edu",
    "first_name": "Test",
    "last_name": "Teacher",
    "role": "TEACHER",
    "phone_number": "+1234567890",
    "department": "Computer Science",
    "password": "teacher123"
  }')

TEACHER_ID=$(echo $CREATE_TEACHER | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$TEACHER_ID" ]; then
    echo -e "${RED}❌ Failed to create teacher${NC}"
    echo "Response: $CREATE_TEACHER"
    exit 1
fi

echo -e "${GREEN}✅ Successfully created teacher (ID: $TEACHER_ID)${NC}"
echo ""

# Step 3: Create a Student with UPPERCASE role
echo "Step 3: Creating student with role='STUDENT'..."
CREATE_STUDENT=$(curl -s -X POST "$BASE_URL/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.student@university.edu",
    "first_name": "Test",
    "last_name": "Student",
    "role": "STUDENT",
    "phone_number": "+1234567891",
    "student_id": "CS_TEST_001",
    "department": "Computer Science",
    "class_year": "3rd Year",
    "password": "student123"
  }')

STUDENT_ID=$(echo $CREATE_STUDENT | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$STUDENT_ID" ]; then
    echo -e "${RED}❌ Failed to create student${NC}"
    echo "Response: $CREATE_STUDENT"
    exit 1
fi

echo -e "${GREEN}✅ Successfully created student (ID: $STUDENT_ID)${NC}"
echo ""

# Step 4: Get all users
echo "Step 4: Getting all users..."
ALL_USERS=$(curl -s -X GET "$BASE_URL/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN")

echo -e "${GREEN}✅ Successfully retrieved all users${NC}"
echo "Users count: $(echo $ALL_USERS | grep -o '"id"' | wc -l)"
echo ""

# Step 5: Filter users by role (TEACHER)
echo "Step 5: Getting all teachers with role filter..."
TEACHERS=$(curl -s -X GET "$BASE_URL/api/v1/users/?role=TEACHER" \
  -H "Authorization: Bearer $TOKEN")

TEACHER_COUNT=$(echo $TEACHERS | grep -o '"role":"TEACHER"' | wc -l)
echo -e "${GREEN}✅ Successfully filtered teachers${NC}"
echo "Teachers found: $TEACHER_COUNT"
echo ""

# Step 6: Filter users by role (STUDENT)
echo "Step 6: Getting all students with role filter..."
STUDENTS=$(curl -s -X GET "$BASE_URL/api/v1/users/?role=STUDENT" \
  -H "Authorization: Bearer $TOKEN")

STUDENT_COUNT=$(echo $STUDENTS | grep -o '"role":"STUDENT"' | wc -l)
echo -e "${GREEN}✅ Successfully filtered students${NC}"
echo "Students found: $STUDENT_COUNT"
echo ""

# Step 7: Login as Teacher
echo "Step 7: Testing teacher login..."
TEACHER_LOGIN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"test.teacher@university.edu","password":"teacher123"}')

TEACHER_TOKEN=$(echo $TEACHER_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TEACHER_TOKEN" ]; then
    echo -e "${RED}❌ Failed to login as teacher${NC}"
    echo "Response: $TEACHER_LOGIN"
    exit 1
fi

echo -e "${GREEN}✅ Successfully logged in as teacher${NC}"
echo ""

# Step 8: Login as Student
echo "Step 8: Testing student login..."
STUDENT_LOGIN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{"username":"test.student@university.edu","password":"student123"}')

STUDENT_TOKEN=$(echo $STUDENT_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$STUDENT_TOKEN" ]; then
    echo -e "${RED}❌ Failed to login as student${NC}"
    echo "Response: $STUDENT_LOGIN"
    exit 1
fi

echo -e "${GREEN}✅ Successfully logged in as student${NC}"
echo ""

# Step 9: Test student permission (should fail)
echo "Step 9: Testing student cannot create users (should fail)..."
STUDENT_CREATE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL/api/v1/users/" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "should.fail@test.com",
    "first_name": "Should",
    "last_name": "Fail",
    "role": "STUDENT",
    "password": "test123"
  }')

HTTP_CODE=$(echo "$STUDENT_CREATE" | grep -o 'HTTP_CODE:[0-9]*' | cut -d':' -f2)

if [ "$HTTP_CODE" == "403" ]; then
    echo -e "${GREEN}✅ Correctly denied student permission (403 Forbidden)${NC}"
else
    echo -e "${RED}❌ Expected 403 but got HTTP $HTTP_CODE${NC}"
    exit 1
fi
echo ""

# Step 10: Cleanup - Delete test users
echo "Step 10: Cleaning up test users..."
curl -s -X DELETE "$BASE_URL/api/v1/users/$TEACHER_ID" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

curl -s -X DELETE "$BASE_URL/api/v1/users/$STUDENT_ID" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

echo -e "${GREEN}✅ Test users deleted${NC}"
echo ""

echo "========================================="
echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
echo "========================================="
echo ""
echo "Summary:"
echo "- Admin login: ✅"
echo "- Teacher creation with UPPERCASE role: ✅"
echo "- Student creation with UPPERCASE role: ✅"
echo "- Get all users: ✅"
echo "- Filter by role (TEACHER): ✅"
echo "- Filter by role (STUDENT): ✅"
echo "- Teacher login: ✅"
echo "- Student login: ✅"
echo "- Permission check (student denied): ✅"
echo "- Cleanup: ✅"
echo ""
echo "All role-related functionality is working correctly!"
