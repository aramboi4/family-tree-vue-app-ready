# 🌳 Family Tree SaaS Application

A complete Vue.js + FastAPI + MongoDB family tree management platform with role-based access control, support tickets, and subscription management.

## 🚀 Quick Start

**📖 See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete setup instructions**

### Features
- ✅ JWT Cookie-Based Authentication
- ✅ Role-Based Access Control (Admin/Editor/Viewer)
- ✅ Family Tree Management
- ✅ Member Invitations with Join Codes
- ✅ Support Ticket System with Rewards
- ✅ Subscription Tiers (Free/Basic/Premium)
- ✅ Person Management (Add/Edit/Delete)

### Tech Stack
- **Frontend**: Vue 3 + Vite + Pinia + Tailwind CSS
- **Backend**: FastAPI + Python 3.11
- **Database**: MongoDB
- **Auth**: JWT (httpOnly cookies)

## 📦 Installation

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001

# Frontend  
cd frontend
yarn install
yarn dev
```

## 🔐 Default Credentials

- **Admin**: `admin@familytree.com` / `admin123`

## 📚 Documentation

- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete setup & deployment guide
- **[auth_testing.md](./auth_testing.md)** - Authentication testing procedures
- **/app/memory/test_credentials.md** - Test account credentials
- **API Docs**: http://localhost:8001/api/docs

## 🎯 Key Endpoints

- **Auth**: `/api/auth/login`, `/api/auth/register`
- **Families**: `/api/families`
- **Members**: `/api/families/{id}/members`
- **Persons**: `/api/persons`
- **Tickets**: `/api/tickets`

## 🧪 Quick API Test

```bash
curl http://localhost:8001/api/health
```

## 📝 License

MIT

---

**For detailed installation, configuration, API documentation, and deployment instructions, please refer to [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)**
