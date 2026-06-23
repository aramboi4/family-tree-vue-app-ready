# Auth Testing Playbook

## Step 1: MongoDB Verification

```bash
mongosh
use family_tree_db
db.users.find({role: "admin"}).pretty()
db.users.findOne({role: "admin"}, {password_hash: 1})
```

**Expected:**
- bcrypt hash starts with `$2b$`
- indexes exist on users.email (unique), login_attempts.identifier, password_reset_tokens.expires_at (TTL)

## Step 2: API Testing

### Test Admin Login
```bash
API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '"' -f 2)

# Login and save cookies
curl -c cookies.txt -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@familytree.com","password":"admin123"}'

# Check cookies
cat cookies.txt

# Test authenticated endpoint with cookies
curl -b cookies.txt "$API_URL/api/auth/me"
```

**Expected:**
- Login should return the user object and set `access_token` + `refresh_token` cookies
- The `/me` call should return the same user using those cookies

### Test User Registration
```bash
curl -c cookies.txt -X POST "$API_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Verify logged in
curl -b cookies.txt "$API_URL/api/auth/me"
```

### Test Logout
```bash
curl -b cookies.txt -X POST "$API_URL/api/auth/logout"

# Should fail (401)
curl -b cookies.txt "$API_URL/api/auth/me"
```

## Step 3: Frontend Testing

1. Navigate to http://localhost:3000/
2. Should redirect to /login
3. Register a new account
4. Should automatically log in and redirect to /dashboard
5. Logout
6. Login with the registered account
7. Should redirect to /dashboard

## Step 4: Test Brute Force Protection

```bash
# Try 6 failed login attempts
for i in {1..6}; do
  curl -X POST "$API_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@familytree.com","password":"wrongpassword"}'
done
```

**Expected:** After 5 attempts, should return 429 Too Many Requests with lockout message.
