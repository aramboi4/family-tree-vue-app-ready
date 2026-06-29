# 🚀 Family Tree App - Deployment Guide

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
- **MongoDB 7.0+** (Not MySQL/XAMPP!)

### MongoDB Setup

**Option 1: Local MongoDB**

**Windows:**
1. Download MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Run installer and select "Complete" installation
3. Install as a Windows Service
4. MongoDB will start automatically

**Mac:**
```bash
# Install via Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community

# Verify
mongosh
```

**Linux (Ubuntu/Debian):**
```bash
# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
mongosh
```

**Option 2: MongoDB Atlas (Cloud - Free Tier)**

1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free cluster (M0)
3. Create database user
4. Whitelist IP (0.0.0.0/0 for development)
5. Get connection string:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

### Backend Setup

```bash
cd /app/backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your values (see below)

# Run the server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Setup

```bash
cd /app/frontend

# Install dependencies
yarn install
# or
npm install

# Create .env file
cp .env.example .env
# Edit .env with API URL (see below)

# Run development server
yarn dev

# Build for production
yarn build
```

---

## 🔐 Environment Variables

### Backend `.env`

```env
# MongoDB Connection
# For local MongoDB:
MONGO_URL="mongodb://localhost:27017"

# For MongoDB Atlas (cloud):
# MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"

# Database Name
DB_NAME="family_tree_db"

# JWT Secret (Generate 64+ character random string)
JWT_SECRET="your-secret-key-min-32-characters-change-in-production"

# Admin Account
ADMIN_EMAIL="admin@familytree.com"
ADMIN_PASSWORD="admin123"

# Frontend URL (for CORS)
FRONTEND_URL="http://localhost:3000"

# CORS Origins
CORS_ORIGINS="*"
```

**Generate JWT_SECRET:**
```bash
# Linux/Mac
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Frontend `.env`

```env
# API URL (empty for relative paths in development)
VITE_API_URL=""

# Backend URL
REACT_APP_BACKEND_URL="http://localhost:8001"
```

**For Production:**
```env
VITE_API_URL=""
REACT_APP_BACKEND_URL="https://api.yourdomain.com"
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

### MongoDB Data Check
```bash
# Open MongoDB shell
mongosh

# Use database
use family_tree_db

# List collections
show collections

# View users
db.users.find().pretty()

# View families
db.families.find().pretty()

# Count documents
db.users.countDocuments()

# Exit
exit
```

---

## 🚀 Deployment

### Production Checklist
- [ ] Update `JWT_SECRET` to strong random value (64+ chars)
- [ ] Set `ADMIN_PASSWORD` to secure password
- [ ] Configure `FRONTEND_URL` to production domain
- [ ] Set `VITE_API_URL` to production API
- [ ] Enable HTTPS for all endpoints
- [ ] Configure MongoDB connection (Atlas or self-hosted)
- [ ] Set up database backups
- [ ] Enable MongoDB authentication
- [ ] Set up monitoring and logging
- [ ] Test all critical flows
- [ ] Configure firewall rules
- [ ] Set up SSL certificates

### Deployment Options

#### Option 1: Docker Deployment

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8001

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# Build application
COPY . .
RUN yarn build

# Production image
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: family-tree-mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=changeme
    restart: unless-stopped

  backend:
    build: ./backend
    container_name: family-tree-backend
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://admin:changeme@mongodb:27017
      - DB_NAME=family_tree_db
      - JWT_SECRET=${JWT_SECRET}
      - ADMIN_EMAIL=${ADMIN_EMAIL}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - FRONTEND_URL=${FRONTEND_URL}
    depends_on:
      - mongodb
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: family-tree-frontend
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=
      - REACT_APP_BACKEND_URL=http://localhost:8001
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  mongodb_data:
```

**Run with Docker:**
```bash
# Create .env file with your values
echo "JWT_SECRET=$(openssl rand -hex 32)" > .env
echo "ADMIN_EMAIL=admin@yourdomain.com" >> .env
echo "ADMIN_PASSWORD=SecurePassword123!" >> .env
echo "FRONTEND_URL=https://yourdomain.com" >> .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

#### Option 2: Traditional Server Deployment

**1. Set up MongoDB**
```bash
# Install MongoDB
# (See MongoDB Setup section above)

# Enable authentication
mongosh
use admin
db.createUser({
  user: "familytree_admin",
  pwd: "SecurePassword123!",
  roles: [{ role: "readWrite", db: "family_tree_db" }]
})
exit

# Update MongoDB config to require auth
sudo nano /etc/mongod.conf
# Add:
# security:
#   authorization: enabled

# Restart MongoDB
sudo systemctl restart mongod
```

**2. Deploy Backend**
```bash
# Install Python 3.11+
sudo apt install python3.11 python3.11-venv

# Create app directory
sudo mkdir -p /opt/family-tree
sudo chown $USER:$USER /opt/family-tree
cd /opt/family-tree

# Copy backend files
cp -r backend /opt/family-tree/

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Create .env file
nano backend/.env
# (Add your production values)

# Create systemd service
sudo nano /etc/systemd/system/family-tree-backend.service
```

**backend service file:**
```ini
[Unit]
Description=Family Tree Backend
After=network.target mongodb.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/family-tree/backend
Environment="PATH=/opt/family-tree/venv/bin"
ExecStart=/opt/family-tree/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl enable family-tree-backend
sudo systemctl start family-tree-backend
sudo systemctl status family-tree-backend
```

**3. Deploy Frontend**
```bash
# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Build frontend
cd /opt/family-tree/frontend
yarn install
yarn build

# Configure Nginx
sudo nano /etc/nginx/sites-available/family-tree
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /opt/family-tree/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/family-tree /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Install SSL certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
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

### Backup MongoDB Database
```bash
# Backup
mongodump --db family_tree_db --out /backup/$(date +%Y%m%d)

# Restore
mongorestore --db family_tree_db /backup/20250101/family_tree_db
```

---

## 🐛 Troubleshooting

### Backend Issues
```bash
# Check backend logs
tail -f /var/log/supervisor/backend.*.log

# Check if backend is running
curl http://localhost:8001/api/health

# Verify MongoDB connection
mongosh mongodb://localhost:27017
use family_tree_db
db.users.find({role: "admin"}).pretty()
exit

# Restart backend
sudo systemctl restart family-tree-backend
# or
sudo supervisorctl restart backend
```

### Frontend Issues
```bash
# Check frontend logs
tail -f /var/log/supervisor/frontend.*.log

# Clear node modules and reinstall
rm -rf node_modules yarn.lock
yarn install

# Rebuild
yarn build

# Restart frontend
sudo systemctl restart nginx
```

### MongoDB Issues
```bash
# Check MongoDB status
sudo systemctl status mongod

# View MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# Restart MongoDB
sudo systemctl restart mongod

# Check disk space
df -h

# Repair MongoDB (if corrupted)
sudo systemctl stop mongod
sudo -u mongodb mongod --repair --dbpath /var/lib/mongodb
sudo systemctl start mongod
```

---

## 📚 Next Steps

### Recommended Enhancements
1. **Email Notifications** - Send invites and password reset emails
2. **Mobile App** - Implement Capacitor for iOS/Android
3. **PDF Export** - Generate family tree PDFs with photos
4. **Advanced Search** - Filter and search persons by attributes
5. **Photo Galleries** - Multiple photos per person with captions
6. **Activity Logs** - Track all changes to family trees
7. **Multi-language** - Add internationalization (i18n)
8. **Analytics Dashboard** - Track usage and metrics
9. **Import/Export** - GEDCOM format support
10. **Social Sharing** - Share family trees on social media

---

## 📖 Documentation

- API documentation: `http://localhost:8001/api/docs` (Swagger UI)
- Test credentials: `/app/memory/test_credentials.md`
- Developer guide: `DEVELOPER_GUIDE.md`
- Quick setup: `QUICK_SETUP.md`

---

## 🆘 Support

For issues or questions:
1. Check `/app/memory/test_credentials.md` for test accounts
2. Review API docs at `/api/docs`
3. Check MongoDB data: `mongosh` → `use family_tree_db` → `db.users.find()`
4. Verify environment variables in `.env` files
5. Check service logs (backend, frontend, MongoDB)

---

## 🔒 Security Best Practices

### Production Security Checklist
- [ ] Use strong JWT_SECRET (64+ random characters)
- [ ] Enable MongoDB authentication
- [ ] Use HTTPS/SSL for all connections
- [ ] Set secure password for admin account
- [ ] Restrict MongoDB access to localhost or VPN
- [ ] Enable firewall (only ports 80, 443, 22)
- [ ] Regular security updates (apt update && apt upgrade)
- [ ] Set up automated backups
- [ ] Use environment variables (never hardcode secrets)
- [ ] Enable rate limiting on API endpoints
- [ ] Set secure cookie flags (httpOnly, secure, sameSite)
- [ ] Implement CORS properly (don't use *)

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Database**: MongoDB (NoSQL - Not MySQL!)  
**License**: MIT

