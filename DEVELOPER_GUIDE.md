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
│   Vue 3 SPA     │  (Frontend - Port 5173 dev / 3000 prod)
│   + Vite        │
│   + Pinia       │
└────────┬────────┘
         │ HTTP/Cookie Auth
         ▼
┌─────────────────┐
│  FastAPI        │  (Backend - Port 8001)
│  + Pydantic     │
└────────┬────────┘
         │ Motor (async MongoDB driver)
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
- **Vite 5.0** - Build tool & dev server (fast HMR)
- **Pinia 2.1** - State management
- **Vue Router 4.2** - Client-side routing
- **Axios 1.6** - HTTP client
- **Tailwind CSS 3.4** - Utility-first CSS
- **Capacitor 6.1** - Mobile app wrapper (optional)

### Backend
- **FastAPI 0.115** - Modern Python web framework
- **Motor 3.6** - Async MongoDB driver (pymongo wrapper)
- **Pydantic 2.12** - Data validation
- **PyJWT 2.10** - JWT tokens
- **Bcrypt 4.2** - Password hashing
- **ReportLab 5.0** - PDF generation
- **Python-dotenv 1.0** - Environment variables

### Database
- **MongoDB 7.0+** - Document-based NoSQL database
  - Collections instead of tables
  - Documents (JSON-like) instead of rows
  - No schema required (flexible structure)
  - Automatic ObjectId for `_id` field

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
├── QUICK_SETUP.md
└── README.md
```

---

## Database Schema

### MongoDB Collections

#### 1. `users`
```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  email: "user@example.com" (unique, indexed),
  password_hash: "$2b$12$...",
  full_name: "John Doe",
  role: "user" | "admin",
  created_at: ISODate("2025-01-01T00:00:00Z")
}
```
**Indexes**: `email` (unique)

#### 2. `families`
```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439012"),
  name: "Smith Family",
  description: "Our family tree",
  created_by: ObjectId("507f1f77bcf86cd799439011"),
  created_at: ISODate("2025-01-01T00:00:00Z"),
  join_code: "ABC12345" (unique, 8 chars),
  subscription_plan: "free" | "basic" | "premium",
  person_count: 10,
  person_limit: 50
}
```
**Indexes**: `join_code` (unique)

#### 3. `family_members`
```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439013"),
  family_id: ObjectId("507f1f77bcf86cd799439012"),
  user_id: ObjectId("507f1f77bcf86cd799439011"),
  role: "admin" | "editor" | "viewer",
  joined_at: ISODate("2025-01-01T00:00:00Z")
}
```
**Indexes**: Compound on (`family_id`, `user_id`)

#### 4. `persons`
```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439014"),
  family_id: ObjectId("507f1f77bcf86cd799439012"),
  first_name: "John",
  middle_name: "Michael",
  last_name: "Smith",
  nickname: "Johnny",
  gender: "male" | "female" | "other",
  birth_date: "1990-01-15",
  death_date: "2050-12-31" | null,
  birth_place: "New York, USA",
  bio: "Biography here...",
  profile_image_url: "https://...",
  photo_gallery: ["https://...", "https://..."],
  facebook_url: "https://facebook.com/...",
  is_deceased: false,
  father_id: "507f1f77bcf86cd799439015" | null,
  mother_id: "507f1f77bcf86cd799439016" | null,
  spouse_ids: ["507f1f77bcf86cd799439017"],
  generation_level: 2,
  x: 100,  // Tree visualization position
  y: 200,  // Tree visualization position
  created_at: ISODate("2025-01-01T00:00:00Z"),
  updated_at: ISODate("2025-01-01T00:00:00Z")
}
```

#### 5. `support_tickets`
```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439018"),
  user_id: ObjectId("507f1f77bcf86cd799439011"),
  family_id: ObjectId("507f1f77bcf86cd799439012"),
  ticket_type: "feature" | "bug" | "issue",
  title: "Add export feature",
  description: "Need to export family tree as PDF",
  screenshot_url: "https://...",
  status: "pending" | "reviewing" | "approved" | "rejected" | "resolved",
  priority: "low" | "medium" | "high" | "critical",
  reward_slots: 5,  // 1-15 person slots
  is_rewarded: true,
  admin_notes: "Great suggestion!",
  reviewed_by: ObjectId("507f1f77bcf86cd799439011"),
  reviewed_at: ISODate("2025-01-02T00:00:00Z"),
  created_at: ISODate("2025-01-01T00:00:00Z"),
  updated_at: ISODate("2025-01-02T00:00:00Z")
}
```

#### 6. `login_attempts`
```javascript
{
  identifier: "192.168.1.1:user@example.com",
  failed_count: 3,
  last_attempt: ISODate("2025-01-01T12:00:00Z")
}
```
**TTL Index**: Auto-expires after 15 minutes

#### 7. `password_reset_tokens`
```javascript
{
  token: "random-token-string",
  user_id: ObjectId("507f1f77bcf86cd799439011"),
  expires_at: ISODate("2025-01-01T13:00:00Z"),
  used: false
}
```
**TTL Index**: `expires_at` (auto-delete expired tokens)

---

## API Endpoints Reference

### Base URL
- **Local**: `http://localhost:8001`
- **Production**: `https://your-domain.com`

**Important**: All backend routes must have `/api` prefix for Kubernetes ingress routing.

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
  "_id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Cookies Set**: `access_token` (15 min), `refresh_token` (7 days)

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
  "_id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user"
}
```

#### POST `/api/auth/logout`
Logout and clear cookies.

**Response**:
```json
{
  "message": "Logged out successfully"
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
  "_id": "507f1f77bcf86cd799439012",
  "name": "Smith Family",
  "description": "Our family tree",
  "created_by": "507f1f77bcf86cd799439011",
  "join_code": "ABC12345",
  "subscription_plan": "free",
  "person_count": 0,
  "person_limit": 50
}
```

**Automatic Actions**:
- Creates family record in MongoDB
- Adds creator as Admin member
- Generates unique 8-char join code

#### GET `/api/families`
List all families the user is a member of.

#### GET `/api/families/{family_id}`
Get family details.

#### PUT `/api/families/{family_id}`
Update family details (Admin or Editor only).

#### DELETE `/api/families/{family_id}`
Delete family tree (Admin only).

---

### Persons

#### POST `/api/persons`
Add a new person to family tree.

**RBAC**: Admin or Editor only

**Request**:
```json
{
  "family_id": "507f1f77bcf86cd799439012",
  "first_name": "John",
  "last_name": "Smith",
  "middle_name": "Michael",
  "gender": "male",
  "birth_date": "1990-01-15",
  "father_id": "507f1f77bcf86cd799439015",
  "mother_id": "507f1f77bcf86cd799439016",
  "bio": "Biography here"
}
```

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
  "family_id": "507f1f77bcf86cd799439012",
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
# Always convert ObjectId to string
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

### 4. MongoDB Queries

**Find one document**:
```python
user = await db.users.find_one({"email": "user@example.com"})
```

**Find multiple documents**:
```python
users = await db.users.find({"role": "admin"}).to_list(100)
```

**Insert document**:
```python
new_user = {
    "_id": ObjectId(),
    "email": "user@example.com",
    "created_at": datetime.now(timezone.utc)
}
await db.users.insert_one(new_user)
```

**Update document**:
```python
await db.users.update_one(
    {"_id": ObjectId(user_id)},
    {"$set": {"full_name": "New Name"}}
)
```

**Delete document**:
```python
await db.users.delete_one({"_id": ObjectId(user_id)})
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
curl -b cookies.txt -X POST http://localhost:8001/api/families \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Family","description":"Test"}'

# List families
curl -b cookies.txt http://localhost:8001/api/families
```

### MongoDB Testing

```bash
# Open MongoDB shell
mongosh

# Use database
use family_tree_db

# List collections
show collections

# View users
db.users.find().pretty()

# View specific user
db.users.findOne({email: "admin@familytree.com"})

# Count documents
db.users.countDocuments()

# Exit
exit
```

---

## Deployment Guide

### Environment Variables Checklist

**Backend** (`.env`):
```env
MONGO_URL="mongodb://localhost:27017"
# or MongoDB Atlas:
# MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"

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

---

## Troubleshooting

### Common Issues

#### 1. "MongoServerError: E11000 duplicate key error"

**Cause**: Trying to insert document with duplicate unique field (email or join_code)

**Solution**:
```python
# Check if exists before inserting
existing = await db.users.find_one({"email": email})
if existing:
    raise HTTPException(400, "Email already registered")
```

#### 2. "Connection refused" when connecting to MongoDB

**Cause**: MongoDB is not running

**Solution**:
```bash
# Check if MongoDB is running
mongosh

# If fails, start MongoDB:
# Windows: services.msc → MongoDB → Start
# Mac: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

#### 3. "401 Unauthorized" on `/api/auth/me`

**Cause**: Cookie not being sent or token expired

**Solution**:
- Check `withCredentials: true` in axios config
- Verify cookie domain matches
- Check token expiration

#### 4. "CORS Error" in browser

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

---

## Quick Reference

### File Locations Cheat Sheet

| Task | File |
|------|------|
| Add API endpoint | `/app/backend/server.py` |
| Add data model | `/app/backend/models.py` |
| Add RBAC check | `/app/backend/rbac.py` |
| Update database indexes | `/app/backend/database.py` |
| Add Vue page | `/app/frontend/src/views/` |
| Add route | `/app/frontend/src/router/index.js` |
| Add component | `/app/frontend/src/components/` |
| Auth logic | `/app/backend/auth.py` |
| API client config | `/app/frontend/src/services/api.js` |
| State management | `/app/frontend/src/stores/` |

---

## Contact & Support

For questions or issues:
1. Check this guide first
2. Review API docs at `/api/docs`
3. Check MongoDB: `mongosh` → `use family_tree_db` → `db.users.find()`
4. Review test credentials in `/app/memory/test_credentials.md`

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Database**: MongoDB (NoSQL)  
**Maintained by**: Development Team


