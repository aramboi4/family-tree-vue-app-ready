# 🧑‍💻 Family Tree SaaS - Developer Guide

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Database Schema](#database-schema)
5. [API Endpoints Reference](#api-endpoints-reference)
6. [Authentication Flow](#authentication-flow)
7. [RBAC Implementation](#rbac-implementation)
8. [Adding New Features](#adding-new-features)
9. [Code Patterns & Best Practices](#code-patterns--best-practices)
10. [Testing Guide](#testing-guide)
11. [Deployment Guide](#deployment-guide)
12. [Troubleshooting](#troubleshooting)

---

## System Architecture

### High-Level Overview
```
┌─────────────────┐
│   Vue 3 SPA     │  (Frontend - Port 3000)
│   + Vite        │
│   + Pinia       │
└────────┬────────┘
         │ HTTP/Cookie Auth
         ▼
┌─────────────────┐
│  FastAPI        │  (Backend - Port 8001)
│  + Pydantic     │
└────────┬────────┘
         │ Motor (async)
         ▼
┌─────────────────┐
│   MongoDB       │  (Database - Port 27017)
└─────────────────┘
```

### Request Flow
1. **User Action** → Vue Component
2. **API Call** → Axios Service (`/frontend/src/services/api.js`)
3. **HTTP Request** → FastAPI Endpoint (`/backend/server.py`)
4. **RBAC Check** → `/backend/rbac.py` utilities
5. **Database Query** → MongoDB via Motor
6. **Response** → JSON back to frontend
7. **State Update** → Pinia store
8. **UI Update** → Vue reactivity

---

## Tech Stack

### Frontend
- **Vue 3.4** - Progressive JavaScript framework
- **Vite 5.0** - Build tool & dev server
- **Pinia 2.1** - State management
- **Vue Router 4.2** - Client-side routing
- **Axios 1.6** - HTTP client
- **Tailwind CSS 3.4** - Utility-first CSS
- **Capacitor 6.1** - Mobile app wrapper

### Backend
- **FastAPI 0.115** - Modern Python web framework
- **Motor 3.6** - Async MongoDB driver
- **Pydantic 2.12** - Data validation
- **PyJWT 2.10** - JWT tokens
- **Bcrypt 4.2** - Password hashing
- **ReportLab 5.0** - PDF generation

### Database
- **MongoDB** - Document-based NoSQL

---

## Project Structure

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI app (1,500+ lines)
│   ├── models.py              # Pydantic models (250+ lines)
│   ├── auth.py                # JWT auth utilities
│   ├── rbac.py                # Role-based access control
│   ├── config.py              # Configuration & env vars
│   ├── database.py            # MongoDB connection
│   ├── pdf_generator.py       # PDF export utilities
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── views/            # Vue pages
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── FamilyList.vue
│   │   │   ├── CreateFamily.vue
│   │   │   ├── FamilyDetails.vue
│   │   │   └── PersonManagement.vue
│   │   ├── components/       # Reusable components
│   │   │   └── FamilyTreeVisualization.vue
│   │   ├── stores/           # Pinia stores
│   │   │   └── auth.js
│   │   ├── router/           # Vue Router config
│   │   │   └── index.js
│   │   ├── services/         # API services
│   │   │   └── api.js
│   │   ├── App.vue           # Root component
│   │   └── main.js           # Entry point
│   ├── capacitor.config.json # Mobile app config
│   ├── vite.config.js        # Vite configuration
│   ├── tailwind.config.js    # Tailwind config
│   ├── package.json          # Dependencies
│   └── .env                  # Frontend env vars
│
├── DEPLOYMENT_GUIDE.md
├── DEVELOPER_GUIDE.md         # This file
└── README.md
```

---

## Database Schema

### Collections

#### 1. `users`
```javascript
{
  _id: ObjectId,
  email: String (unique),
  password_hash: String,
  full_name: String,
  role: "user" | "admin",
  created_at: DateTime
}
```
**Indexes**: `email` (unique)

#### 2. `families`
```javascript
{
  _id: ObjectId,
  name: String,
  description: String,
  created_by: ObjectId (ref: users),
  created_at: DateTime,
  join_code: String (unique, 8 chars),
  subscription_plan: "free" | "basic" | "premium",
  person_count: Number,
  person_limit: Number
}
```
**Indexes**: `join_code` (unique)

#### 3. `family_members`
```javascript
{
  _id: ObjectId,
  family_id: ObjectId (ref: families),
  user_id: ObjectId (ref: users),
  role: "admin" | "editor" | "viewer",
  joined_at: DateTime
}
```
**Indexes**: Compound on (`family_id`, `user_id`)

#### 4. `persons`
```javascript
{
  _id: ObjectId,
  family_id: ObjectId (ref: families),
  first_name: String,
  middle_name: String,
  last_name: String,
  nickname: String,
  gender: "male" | "female" | "other",
  birth_date: String,
  death_date: String,
  birth_place: String,
  bio: String,
  profile_image_url: String,
  photo_gallery: [String],         // Array of photo URLs
  facebook_url: String,
  is_deceased: Boolean,
  father_id: String (ref: persons),  // Parent relationship
  mother_id: String (ref: persons),  // Parent relationship
  spouse_ids: [String],              // Spouse relationships
  generation_level: Number,
  x: Number,                         // Tree visualization position
  y: Number,                         // Tree visualization position
  created_at: DateTime,
  updated_at: DateTime
}
```

#### 5. `support_tickets`
```javascript
{
  _id: ObjectId,
  user_id: ObjectId (ref: users),
  family_id: ObjectId (ref: families),
  ticket_type: "feature" | "bug" | "issue",
  title: String,
  description: String,
  screenshot_url: String,
  status: "pending" | "reviewing" | "approved" | "rejected" | "resolved",
  priority: "low" | "medium" | "high" | "critical",
  reward_slots: Number (1-15),
  is_rewarded: Boolean,
  admin_notes: String,
  reviewed_by: ObjectId (ref: users),
  reviewed_at: DateTime,
  created_at: DateTime,
  updated_at: DateTime
}
```

#### 6. `login_attempts`
```javascript
{
  identifier: String (IP:email),
  failed_count: Number,
  last_attempt: DateTime
}
```
**TTL Index**: Auto-expires after 15 minutes

#### 7. `password_reset_tokens`
```javascript
{
  token: String,
  user_id: ObjectId (ref: users),
  expires_at: DateTime,
  used: Boolean
}
```
**TTL Index**: `expires_at`

---

## API Endpoints Reference

### Base URL
- **Local**: `http://localhost:8001`
- **Production**: `https://your-domain.com`

All backend routes must have `/api` prefix for Kubernetes ingress routing.

### Authentication

#### POST `/api/auth/register`
Register a new user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response**:
```json
{
  "_id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "created_at": "2025-12-24T00:00:00Z"
}
```

**Cookies Set**: `access_token`, `refresh_token`

#### POST `/api/auth/login`
Login user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response**: Same as register

**Features**:
- Brute force protection (5 attempts = 15 min lockout)
- Sets httpOnly cookies
- Returns user object

#### GET `/api/auth/me`
Get current authenticated user.

**Headers**: Cookie with `access_token`

**Response**:
```json
{
  "_id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user"
}
```

---

### Families

#### POST `/api/families`
Create a new family tree.

**RBAC**: Authenticated users

**Request**:
```json
{
  "name": "Smith Family",
  "description": "Our family tree"
}
```

**Response**:
```json
{
  "_id": "family_id",
  "name": "Smith Family",
  "description": "Our family tree",
  "created_by": "user_id",
  "join_code": "ABC12345",
  "subscription_plan": "free",
  "person_count": 0,
  "person_limit": 50
}
```

**Automatic Actions**:
- Creates family record
- Adds creator as Admin member
- Generates unique 8-char join code

---

### Persons

#### POST `/api/persons`
Add a new person to family tree.

**RBAC**: Admin or Editor only

**Request**:
```json
{
  "family_id": "family_id",
  "first_name": "John",
  "last_name": "Smith",
  "middle_name": "Michael",
  "gender": "male",
  "birth_date": "1990-01-15",
  "father_id": "father_person_id",
  "mother_id": "mother_person_id",
  "bio": "Biography here"
}
```

**Response**: Person object with all fields

**Key Fields**:
- `father_id`, `mother_id`: For parent relationships (used in PDF & tree visualization)
- `spouse_ids`: Array for spouse relationships
- `photo_gallery`: Array of photo URLs
- `generation_level`: Auto-calculated based on parents

---

### Member Management (RBAC)

#### POST `/api/families/{family_id}/members/invite`
Invite a user to family with role.

**RBAC**:
- Admin can invite: Admin, Editor, Viewer
- Editor can invite: Editor, Viewer

**Request**:
```json
{
  "family_id": "family_id",
  "email": "invitee@example.com",
  "role": "editor"
}
```

**Validation**:
- Max 5 admins per family
- Inviter must have permission to invite that role
- User must exist in system

---

## Authentication Flow

### Cookie-Based JWT Authentication

```
┌─────────────┐
│   Login     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  POST /api/auth/login               │
│  {email, password}                  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Verify password (bcrypt)           │
│  Create access_token (15 min)       │
│  Create refresh_token (7 days)      │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Set httpOnly cookies               │
│  - access_token                     │
│  - refresh_token                    │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Return user object                 │
└─────────────────────────────────────┘
```

### Token Refresh Flow

```
Access token expires (15 min)
        │
        ▼
Frontend receives 401
        │
        ▼
POST /api/auth/refresh
   (uses refresh_token cookie)
        │
        ▼
New access_token set in cookie
        │
        ▼
Retry original request
```

### Code Location
- **Backend**: `/app/backend/auth.py` - `create_access_token()`, `create_refresh_token()`, `get_current_user()`
- **Frontend**: `/app/frontend/src/services/api.js` - Response interceptor handles 401

---

## RBAC Implementation

### Role Hierarchy
```
Admin (Min 1, Max 5 per family)
  ├── Full access to everything
  ├── Can purchase subscriptions
  ├── Can invite any role
  └── Can transfer admin role

Editor (Unlimited)
  ├── Can update family details
  ├── Can add/edit/delete persons
  ├── Can invite Editors & Viewers
  └── Cannot delete family

Viewer (Unlimited)
  ├── Read-only access
  ├── Can view: parents, name, age, gender, birthday, picture
  └── Cannot see: bio, birth place, other personal details
```

### Permission Check Pattern

**Backend** (`/app/backend/rbac.py`):
```python
from rbac import check_admin_or_editor_role

@app.put("/api/persons/{person_id}")
async def update_person(
    person_id: str,
    person_data: PersonUpdate,
    current_user: dict = Depends(get_current_user)
):
    # Get person's family
    person = await db.persons.find_one({"_id": ObjectId(person_id)})
    
    # Check role
    await check_admin_or_editor_role(
        current_user["_id"],
        str(person["family_id"])
    )
    
    # Proceed with update...
```

**Frontend** (`/app/frontend/src/views/PersonManagement.vue`):
```javascript
// Load user's role
async function loadUserRole() {
  const response = await api.get(`/api/families/${familyId}/my-role`)
  userRole.value = response.data.role
}

// Computed property for UI permissions
const canEdit = computed(() => {
  return userRole.value === 'admin' || userRole.value === 'editor'
})

// Conditionally show buttons
<button v-if="canEdit" @click="editPerson(person)">
  Edit
</button>
```

### RBAC Functions Reference

**File**: `/app/backend/rbac.py`

```python
# Check if user is family member
await check_family_membership(user_id, family_id)

# Check if user is admin
await check_admin_role(user_id, family_id)

# Check if admin or editor
await check_admin_or_editor_role(user_id, family_id)

# Check if can invite role
can_invite = await can_invite_role(inviter_role, invitee_role)

# Check admin limit (max 5)
admin_count = await check_admin_limit(family_id)

# Validate admin addition
await validate_admin_addition(family_id)  # Raises error if >= 5

# Get permissions for role
permissions = Permissions.get_permissions(role)
# Returns: { "can_update_family": True, "can_delete_family": False, ... }
```

---

## Adding New Features

### 1. Adding a New API Endpoint

**Step 1**: Define Pydantic Model (`/app/backend/models.py`)
```python
class NewFeatureCreate(BaseModel):
    field1: str
    field2: Optional[int] = None

class NewFeatureResponse(BaseModel):
    id: str = Field(alias="_id")
    field1: str
    field2: Optional[int] = None
    created_at: datetime
    
    class Config:
        populate_by_name = True
```

**Step 2**: Create Endpoint (`/app/backend/server.py`)
```python
@app.post("/api/new-feature", status_code=status.HTTP_201_CREATED)
async def create_new_feature(
    data: NewFeatureCreate,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Create new feature\"\"\"
    db = get_db()
    
    # RBAC check if needed
    await check_admin_role(current_user["_id"], family_id)
    
    # Create document
    new_doc = {
        "_id": ObjectId(),
        "user_id": ObjectId(current_user["_id"]),
        "field1": data.field1,
        "field2": data.field2,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.collection_name.insert_one(new_doc)
    
    return {
        "_id": str(new_doc["_id"]),
        "field1": new_doc["field1"],
        "field2": new_doc["field2"],
        "created_at": new_doc["created_at"]
    }
```

**Step 3**: Update Frontend API Service (`/app/frontend/src/services/api.js` - if needed, or call directly)

**Step 4**: Create Vue Component/View
```vue
<script setup>
import { ref } from 'vue'
import api from '@/services/api'

const data = ref({ field1: '', field2: null })
const loading = ref(false)

async function submitData() {
  loading.value = true
  try {
    const response = await api.post('/api/new-feature', data.value)
    console.log('Created:', response.data)
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}
</script>
```

---

### 2. Adding a New Database Collection

**Step 1**: Update Database Indexes (`/app/backend/database.py`)
```python
async def connect_db():
    global client, db
    # ... existing code ...
    
    # Add new indexes
    await db.new_collection.create_index("field_name", unique=True)
    await db.new_collection.create_index([("field1", 1), ("field2", -1)])
```

**Step 2**: Create Pydantic Models (see previous section)

**Step 3**: Add CRUD Endpoints (see previous section)

---

### 3. Adding RBAC to Existing Endpoint

**Before** (No RBAC):
```python
@app.delete("/api/resource/{id}")
async def delete_resource(id: str):
    await db.resources.delete_one({"_id": ObjectId(id)})
    return {"message": "Deleted"}
```

**After** (With RBAC):
```python
from rbac import check_admin_role

@app.delete("/api/resource/{id}")
async def delete_resource(
    id: str,
    current_user: dict = Depends(get_current_user)  # Step 1: Add dependency
):
    # Step 2: Get resource to find family_id
    resource = await db.resources.find_one({"_id": ObjectId(id)})
    if not resource:
        raise HTTPException(404, "Not found")
    
    # Step 3: Check permissions
    await check_admin_role(current_user["_id"], str(resource["family_id"]))
    
    # Step 4: Proceed if authorized
    await db.resources.delete_one({"_id": ObjectId(id)})
    return {"message": "Deleted"}
```

---

## Code Patterns & Best Practices

### 1. MongoDB ObjectId Handling

**❌ Wrong**:
```python
# Don't return MongoDB _id directly (serialization error)
return person
```

**✅ Correct**:
```python
# Always exclude _id or convert to string
person = await db.persons.find_one({"_id": ObjectId(person_id)}, {"_id": 0})

# Or convert to string in response
return {
    "_id": str(person["_id"]),
    "name": person["name"]
}
```

### 2. DateTime Handling

**❌ Wrong**:
```python
from datetime import datetime
created_at = datetime.now()  # Naive datetime
```

**✅ Correct**:
```python
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)  # UTC aware
```

### 3. Environment Variables

**❌ Wrong**:
```python
# Hardcoded
mongo_url = "mongodb://localhost:27017"
jwt_secret = "my-secret-key"
```

**✅ Correct**:
```python
import os
from config import settings

mongo_url = os.environ.get("MONGO_URL", settings.MONGO_URL)
jwt_secret = os.environ.get("JWT_SECRET", settings.JWT_SECRET)
```

### 4. API Error Handling

**Backend**:
```python
from fastapi import HTTPException, status

# Use appropriate status codes
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)

# Provide helpful error messages
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email already registered"
)
```

**Frontend**:
```javascript
try {
  const response = await api.post('/api/endpoint', data)
} catch (error) {
  const message = error.response?.data?.detail || 'Something went wrong'
  console.error('Error:', message)
  // Show to user
}
```

### 5. Vue Composables Pattern

**Creating a Composable** (`/app/frontend/src/composables/useFamily.js`):
```javascript
import { ref } from 'vue'
import api from '@/services/api'

export function useFamily() {
  const families = ref([])
  const loading = ref(false)
  
  async function loadFamilies() {
    loading.value = true
    try {
      const response = await api.get('/api/families')
      families.value = response.data
    } catch (error) {
      console.error('Failed to load families:', error)
    } finally {
      loading.value = false
    }
  }
  
  return {
    families,
    loading,
    loadFamilies
  }
}
```

**Using in Component**:
```vue
<script setup>
import { onMounted } from 'vue'
import { useFamily } from '@/composables/useFamily'

const { families, loading, loadFamilies } = useFamily()

onMounted(loadFamilies)
</script>
```

---

## Testing Guide

### Backend Testing (curl)

**Test Authentication**:
```bash
# Login
curl -c cookies.txt -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@familytree.com","password":"admin123"}'

# Get current user
curl -b cookies.txt http://localhost:8001/api/auth/me
```

**Test CRUD Operations**:
```bash
# Create family
FAMILY_ID=$(curl -b cookies.txt -s -X POST http://localhost:8001/api/families \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Family","description":"Test"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['_id'])")

# List families
curl -b cookies.txt http://localhost:8001/api/families

# Get family
curl -b cookies.txt http://localhost:8001/api/families/$FAMILY_ID
```

### Frontend Testing (Manual)

1. **Login Flow**:
   - Navigate to `/login`
   - Enter credentials
   - Verify redirect to `/dashboard`
   - Check cookies in DevTools

2. **RBAC Testing**:
   - Login as Admin
   - Create family
   - Invite Editor
   - Logout and login as Editor
   - Verify Editor can add persons but not delete family
   - Login as Viewer
   - Verify Viewer sees limited fields

3. **Person Management**:
   - Add person with parents
   - Switch to Tree view
   - Verify relationships show correctly
   - Export PDF and check parent relationships

---

## Deployment Guide

### Environment Variables Checklist

**Backend** (`.env`):
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="family_tree_db"
JWT_SECRET="[Generate 64-char random string]"
ADMIN_EMAIL="admin@yourdomain.com"
ADMIN_PASSWORD="[Secure password]"
FRONTEND_URL="https://app.yourdomain.com"
```

**Frontend** (`.env`):
```env
VITE_API_URL=""
REACT_APP_BACKEND_URL="https://api.yourdomain.com"
```

### Build Commands

**Backend**:
```bash
cd /app/backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001
```

**Frontend**:
```bash
cd /app/frontend
yarn install
yarn build  # Creates /dist folder
```

### Docker Deployment

**Backend Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Frontend Dockerfile**:
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
RUN yarn build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Troubleshooting

### Common Issues

#### 1. "MongoServerError: E11000 duplicate key error"

**Cause**: Trying to insert document with duplicate unique field

**Solution**:
```python
# Check if exists before inserting
existing = await db.users.find_one({"email": email})
if existing:
    raise HTTPException(400, "Email already registered")
```

#### 2. "401 Unauthorized" on `/api/auth/me`

**Cause**: Cookie not being sent or token expired

**Solution**:
- Check `withCredentials: true` in axios config
- Verify cookie domain matches
- Check token expiration

#### 3. "CORS Error" in browser

**Cause**: Frontend and backend on different domains

**Solution** (Backend `/app/backend/server.py`):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL")],
    allow_credentials=True,  # Important for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. "Person not showing in Tree View"

**Cause**: Missing x, y coordinates

**Solution**: Click "Grid" then "Tree" to trigger auto-layout

#### 5. "Viewer seeing restricted fields"

**Cause**: Frontend not checking `isViewer`

**Solution**:
```vue
<div v-if="!isViewer">
  <!-- Restricted content -->
</div>
```

---

## Quick Reference

### File Locations Cheat Sheet

| Task | File |
|------|------|
| Add API endpoint | `/app/backend/server.py` |
| Add data model | `/app/backend/models.py` |
| Add RBAC check | `/app/backend/rbac.py` |
| Update database schema | `/app/backend/database.py` |
| Add Vue page | `/app/frontend/src/views/` |
| Add route | `/app/frontend/src/router/index.js` |
| Add component | `/app/frontend/src/components/` |
| Auth logic | `/app/backend/auth.py` |
| API client config | `/app/frontend/src/services/api.js` |
| State management | `/app/frontend/src/stores/` |

### Code Snippet Templates

**Add New Endpoint**:
```python
@app.post("/api/endpoint")
async def endpoint_name(
    data: ModelName,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    # Your logic here
    return {"result": "success"}
```

**Add New Vue View**:
```vue
<template>
  <div>
    <!-- Your template -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

// Your logic here
</script>
```

---

## Contact & Support

For questions or issues:
1. Check this guide first
2. Review API docs at `/api/docs`
3. Check logs in `/var/log/supervisor/`
4. Review test credentials in `/app/memory/test_credentials.md`

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Maintained by**: Development Team
