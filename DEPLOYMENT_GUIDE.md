# 🚀 Family Tree App - Ready to Deploy Guide

## Overview
Complete Vue.js + FastAPI + MongoDB family tree application with RBAC, support tickets, and copy-paste ready code.

---

## 📋 Features Implemented

### ✅ Authentication & Authorization
- JWT cookie-based authentication
- User registration and login
- Password hashing with bcrypt
- Brute force protection (5 attempts = 15 min lockout)
- Admin seeding on startup

### ✅ Role-Based Access Control (RBAC)
- **Admin Role** (Min 1, Max 5 per family tree)
  - Full access to everything
  - Can purchase/upgrade subscription plans
  - Can invite any role (Admin/Editor/Viewer)
  - Can manage all members
- **Editor Role** (Unlimited)
  - Can update family details
  - Can add/edit/delete persons
  - Can invite Editors and Viewers only
  - Cannot purchase plans or delete family
- **Viewer Role** (Unlimited)
  - View-only access
  - Cannot modify anything

### ✅ Family Tree Management
- Create and manage family trees
- Join code system for invitations
- Member management with role assignment
- Person records (add/edit/delete)
- Subscription tiers (Free, Basic, Premium)

### ✅ Support Ticket System
- Submit feature requests and bug reports
- Screenshot attachment support
- Admin review and approval system
- Reward system: 1-15 person slots per ticket
- Status tracking (pending, reviewing, approved, rejected, resolved)

---

## 🗂️ Project Structure

```
/app/
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── models.py          # Pydantic models
│   ├── config.py          # Configuration & env vars
│   ├── database.py        # MongoDB connection
│   ├── auth.py            # Authentication utilities
│   ├── rbac.py            # RBAC utilities
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── frontend/
│   ├── src/
│   │   ├── views/        # Vue pages
│   │   ├── stores/       # Pinia stores
│   │   ├── router/       # Vue Router
│   │   ├── services/     # API services
│   │   └── main.js       # App entry
│   ├── package.json      # Dependencies
│   ├── vite.config.js    # Vite configuration
│   └── .env              # Frontend env vars
└── memory/
    └── test_credentials.md  # Test accounts
```

---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB

### Backend Setup

```bash
cd /app/backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your values

# Run the server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Setup

```bash
cd /app/frontend

# Install dependencies
yarn install

# Configure environment  
cp .env.example .env
# Edit .env with API URL

# Run development server
yarn dev

# Build for production
yarn build
```

---

## 🔐 Environment Variables

### Backend `.env`
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="family_tree_db"
JWT_SECRET="your-secret-key-min-32-characters"
ADMIN_EMAIL="admin@familytree.com"
ADMIN_PASSWORD="admin123"
FRONTEND_URL="http://localhost:3000"
CORS_ORIGINS="*"
```

### Frontend `.env`
```env
VITE_API_URL=""
REACT_APP_BACKEND_URL="https://your-domain.com"
```

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password

### Families
- `GET /api/families` - List user's families
- `POST /api/families` - Create family
- `GET /api/families/{id}` - Get family details
- `PUT /api/families/{id}` - Update family (Admin/Editor)
- `DELETE /api/families/{id}` - Delete family (Admin only)

### Members (RBAC)
- `GET /api/families/{id}/members` - List members
- `POST /api/families/{id}/members/invite` - Invite member
- `PUT /api/families/{id}/members/{member_id}` - Update role (Admin)
- `DELETE /api/families/{id}/members/{member_id}` - Remove member (Admin)
- `GET /api/families/{id}/my-role` - Get current user's role & permissions

### Persons
- `GET /api/families/{id}/persons` - List persons
- `POST /api/persons` - Add person (Admin/Editor)
- `GET /api/persons/{id}` - Get person
- `PUT /api/persons/{id}` - Update person (Admin/Editor)
- `DELETE /api/persons/{id}` - Delete person (Admin/Editor)

### Support Tickets
- `GET /api/tickets` - List tickets
- `POST /api/tickets` - Create ticket
- `GET /api/tickets/{id}` - Get ticket details
- `PUT /api/tickets/{id}` - Update ticket (Admin only)

---

## 🧪 Testing

### Test Accounts
- **Admin**: `admin@familytree.com` / `admin123`
- **Editor**: `editor@test.com` / `test123`

### Quick API Test
```bash
# Health check
curl http://localhost:8001/api/health

# Login
curl -c cookies.txt -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@familytree.com","password":"admin123"}'

# Get current user
curl -b cookies.txt http://localhost:8001/api/auth/me
```

---

## 🚀 Deployment

### Production Checklist
- [ ] Update `JWT_SECRET` to strong random value
- [ ] Set `ADMIN_PASSWORD` to secure password
- [ ] Configure `FRONTEND_URL` to production domain
- [ ] Set `VITE_API_URL` to production API
- [ ] Enable HTTPS for all endpoints
- [ ] Configure MongoDB connection string
- [ ] Set up monitoring and logging
- [ ] Test all critical flows

### Docker Deployment (Optional)
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
RUN yarn build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

---

## 📝 Common Tasks

### Add a New Admin
```bash
curl -b cookies.txt -X POST http://localhost:8001/api/families/{family_id}/members/invite \
  -H "Content-Type: application/json" \
  -d '{"family_id":"{family_id}","email":"newadmin@example.com","role":"admin"}'
```

### Approve Support Ticket with Reward
```bash
curl -b cookies.txt -X PUT http://localhost:8001/api/tickets/{ticket_id} \
  -H "Content-Type: application/json" \
  -d '{"status":"approved","reward_slots":10,"admin_notes":"Approved"}'
```

### Check User's Role
```bash
curl -b cookies.txt http://localhost:8001/api/families/{family_id}/my-role
```

---

## 🐛 Troubleshooting

### Backend Issues
```bash
# Check backend logs
tail -f /var/log/supervisor/backend.*.log

# Verify MongoDB connection
mongosh
use family_tree_db
db.users.find({role: "admin"}).pretty()

# Restart backend
sudo supervisorctl restart backend
```

### Frontend Issues
```bash
# Check frontend logs
tail -f /var/log/supervisor/frontend.*.log

# Clear node modules and reinstall
rm -rf node_modules yarn.lock
yarn install

# Restart frontend
sudo supervisorctl restart frontend
```

---

## 📚 Next Steps

### Recommended Enhancements
1. **Payment Integration** - Add GCash, Maya, InstaPay
2. **Mobile App** - Implement Capacitor for iOS/Android
3. **PDF Export** - Generate family tree PDFs
4. **Email Notifications** - Send invites and updates
5. **Activity Logs** - Track changes to family trees
6. **Advanced Search** - Filter and search persons
7. **Photo Galleries** - Add multiple photos per person
8. **Relationship Mapping** - Visualize connections
9. **Multi-language** - Add internationalization
10. **Analytics Dashboard** - Track usage and metrics

---

## 📖 Documentation

- Auth implementation: `/app/auth_testing.md`
- Test credentials: `/app/memory/test_credentials.md`
- API health: `GET /api/health`
- API docs: `http://localhost:8001/api/docs`

---

## 🆘 Support

For issues or questions:
1. Check `/app/memory/test_credentials.md` for test accounts
2. Review API docs at `/api/docs`
3. Check logs in `/var/log/supervisor/`
4. Verify environment variables in `.env` files

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**License**: MIT
