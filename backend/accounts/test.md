1. Test Registration ✅
bash
curl -X POST http://localhost:8500/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123","password2":"TestPass123"}'
Expected Response:

json
{
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "phone": null,
        "avatar": null,
        "is_active": true,
        "created_at": "2024-01-01T12:00:00Z"
    }
}
2. Test Login (with username) ✅
bash
curl -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}'
Test Login (with email - works with our custom logic) ✅
bash
curl -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"TestPass123"}'
Expected Response:

json
{
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "phone": null,
        "avatar": null,
        "is_active": true,
        "created_at": "2024-01-01T12:00:00Z"
    }
}
3. Test Profile (with JWT token) ✅
bash
# Replace <your_access_token> with the actual token from login response
curl -X GET http://localhost:8500/api/auth/profile/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
Expected Response:

json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "phone": null,
    "avatar": null,
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z"
}
4. Test Update Profile (PATCH) ✅
bash
curl -X PATCH http://localhost:8500/api/auth/profile/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"phone":"+1234567890","email":"newemail@example.com"}'
5. Test Change Password ✅
bash
curl -X POST http://localhost:8500/api/auth/change-password/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "TestPass123",
    "new_password": "NewPass456",
    "confirm_password": "NewPass456"
  }'
Expected Response:

json
{
    "message": "Password changed successfully",
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
6. Test Logout ✅
bash
# First, save the refresh token from login response
curl -X POST http://localhost:8500/api/auth/logout/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJhbGciOiJIUzI1NiIs..."}'
Expected Response:

json
{
    "message": "Logged out successfully"
}
Complete Test Script
Here's a complete bash script to test everything:

bash
#!/bin/bash
# test_auth.sh

BASE_URL="http://localhost:8500/api/auth"

echo "========================================="
echo "1. Testing Registration"
echo "========================================="
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123","password2":"TestPass123"}')

echo $REGISTER_RESPONSE | jq '.'
ACCESS_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access')
REFRESH_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.refresh')

echo -e "\n✅ Access Token: ${ACCESS_TOKEN:0:50}..."
echo "✅ Refresh Token: ${REFRESH_TOKEN:0:50}..."

echo -e "\n========================================="
echo "2. Testing Login with Username"
echo "========================================="
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}')

echo $LOGIN_RESPONSE | jq '.'
NEW_ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access')

echo -e "\n========================================="
echo "3. Testing Login with Email"
echo "========================================="
LOGIN_EMAIL_RESPONSE=$(curl -s -X POST $BASE_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"TestPass123"}')

echo $LOGIN_EMAIL_RESPONSE | jq '.'

echo -e "\n========================================="
echo "4. Testing Profile (GET)"
echo "========================================="
PROFILE_RESPONSE=$(curl -s -X GET $BASE_URL/profile/ \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN")

echo $PROFILE_RESPONSE | jq '.'

echo -e "\n========================================="
echo "5. Testing Profile Update (PATCH)"
echo "========================================="
PROFILE_UPDATE=$(curl -s -X PATCH $BASE_URL/profile/ \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone":"+1234567890"}')

echo $PROFILE_UPDATE | jq '.'

echo -e "\n========================================="
echo "6. Testing Change Password"
echo "========================================="
PASSWORD_CHANGE=$(curl -s -X POST $BASE_URL/change-password/ \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "TestPass123",
    "new_password": "NewPass456",
    "confirm_password": "NewPass456"
  }')

echo $PASSWORD_CHANGE | jq '.'

# Extract new tokens from password change
NEW_ACCESS=$(echo $PASSWORD_CHANGE | jq -r '.access')
NEW_REFRESH=$(echo $PASSWORD_CHANGE | jq -r '.refresh')

echo -e "\n========================================="
echo "7. Testing Login with New Password"
echo "========================================="
LOGIN_NEW=$(curl -s -X POST $BASE_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"NewPass456"}')

echo $LOGIN_NEW | jq '.'

echo -e "\n========================================="
echo "8. Testing Logout"
echo "========================================="
LOGOUT=$(curl -s -X POST $BASE_URL/logout/ \
  -H "Authorization: Bearer $NEW_ACCESS" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\":\"$NEW_REFRESH\"}")

echo $LOGOUT | jq '.'

echo -e "\n========================================="
echo "✅ All tests completed!"
echo "========================================="
To run the script:
bash
chmod +x test_auth.sh
./test_auth.sh
Note: Make sure you have jq installed for JSON parsing:

bash
# Install jq if not already installed
sudo apt-get install jq  # Ubuntu/Debian
brew install jq          # macOS
Error Cases to Test
1. Invalid Registration (Passwords don't match)
bash
curl -X POST http://localhost:8500/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123","password2":"WrongPass"}'
Expected: 400 Bad Request with error message

2. Duplicate Registration
bash
curl -X POST http://localhost:8500/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123","password2":"TestPass123"}'
Expected: 400 Bad Request - "username already exists" or "email already exists"

3. Invalid Login
bash
curl -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"wronguser","password":"WrongPass"}'
Expected: 400 Bad Request - "Invalid credentials"

4. Unauthorized Profile Access
bash
curl -X GET http://localhost:8500/api/auth/profile/
Expected: 401 Unauthorized

Summary Table
Endpoint	Method	Auth Required	Body Required
/api/auth/register/	POST	❌	username, email, password, password2
/api/auth/login/	POST	❌	username, password
/api/auth/profile/	GET	✅	None
/api/auth/profile/	PATCH	✅	Fields to update
/api/auth/change-password/	POST	✅	old_password, new_password, confirm_password
/api/auth/logout/	POST	✅	refresh
These commands should work perfectly with your setup! The main change was fixing the login to use username instead of email (though your custom backend supports both).

