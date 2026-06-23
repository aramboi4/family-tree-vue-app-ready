# 🚀 Complete Deployment Guide - Local & Live

This guide covers everything you need to deploy the Family Tree application on **localhost** (XAMPP/MongoDB) and **production** (live servers).

---

## 📑 Table of Contents

1. [Local Development Setup](#local-development-setup)
   - [Option A: XAMPP + MySQL](#option-a-xampp--mysql)
   - [Option B: MongoDB](#option-b-mongodb)
2. [Live Production Deployment](#live-production-deployment)
   - [Backend Deployment](#backend-deployment-live)
   - [Frontend Deployment](#frontend-deployment-live)
   - [Database Setup](#database-setup-live)
3. [Mobile App Deployment](#mobile-app-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)

---

# 🖥️ Local Development Setup

## Prerequisites

Download and install these first:

### Required for All Setups:
- **Python 3.10+**: https://www.python.org/downloads/
  - ✅ During installation, check "Add Python to PATH"
- **Node.js 18+**: https://nodejs.org/
  - ✅ LTS version recommended
- **Git**: https://git-scm.com/downloads
- **Code Editor**: VS Code (https://code.visualstudio.com/)

### Choose ONE Database Option:

---

## Option A: XAMPP + MySQL

### 1. Download XAMPP
- **Download**: https://www.apachefriends.org/download.html
- **Choose**: XAMPP for Windows/Mac/Linux
- **Version**: Latest version (includes PHP 8.2, MySQL/MariaDB)
- **Size**: ~150MB

### 2. Install XAMPP
```
Windows: Run installer → Install to C:\xampp
Mac: Drag to Applications folder
Linux: sudo ./xampp-linux-x64-installer.run
```

### 3. Start XAMPP Services
1. Open **XAMPP Control Panel**
2. Start **MySQL** (click Start button)
3. Start **Apache** (optional - for phpMyAdmin)

### 4. Create Database
1. Open browser: http://localhost/phpmyadmin
2. Click "New" (left sidebar)
3. Database name: `family_tree_db`
4. Collation: `utf8mb4_unicode_ci`
5. Click "Create"

### 5. Create Database Tables

Click on `family_tree_db` → SQL tab → paste this:

```sql
-- Users Table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Families Table
CREATE TABLE families (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    join_code VARCHAR(10) UNIQUE NOT NULL,
    subscription_plan ENUM('free', 'basic', 'standard', 'pro', 'elite') DEFAULT 'free',
    person_count INT DEFAULT 0,
    person_limit INT DEFAULT 50,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_created_by (created_by),
    INDEX idx_join_code (join_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Family Members Table
CREATE TABLE family_members (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    role ENUM('admin', 'editor', 'viewer') DEFAULT 'viewer',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_family_user (family_id, user_id),
    INDEX idx_family_id (family_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Persons Table
CREATE TABLE persons (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    last_name VARCHAR(255) NOT NULL,
    nickname VARCHAR(255),
    gender ENUM('male', 'female', 'other') NOT NULL,
    birth_date DATE,
    death_date DATE,
    birth_place VARCHAR(255),
    bio TEXT,
    profile_image_url TEXT,
    facebook_url TEXT,
    is_deceased BOOLEAN DEFAULT FALSE,
    is_orphan BOOLEAN DEFAULT FALSE,
    generation_level INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    INDEX idx_family_id (family_id),
    INDEX idx_name (first_name, last_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Couples Table
CREATE TABLE couples (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    person1_id VARCHAR(36) NOT NULL,
    person2_id VARCHAR(36) NOT NULL,
    marriage_date DATE,
    divorce_date DATE,
    status ENUM('married', 'divorced', 'separated', 'partners', 'widowed') DEFAULT 'married',
    is_root_couple BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (person1_id) REFERENCES persons(id) ON DELETE CASCADE,
    FOREIGN KEY (person2_id) REFERENCES persons(id) ON DELETE CASCADE,
    INDEX idx_family_id (family_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Relationships Table
CREATE TABLE relationships (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    parent_couple_id VARCHAR(36),
    child_id VARCHAR(36) NOT NULL,
    relationship_type ENUM('biological', 'adopted', 'step', 'foster') DEFAULT 'biological',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_couple_id) REFERENCES couples(id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES persons(id) ON DELETE CASCADE,
    INDEX idx_family_id (family_id),
    INDEX idx_child (child_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Support Tickets Table
CREATE TABLE support_tickets (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    family_id VARCHAR(36),
    ticket_type ENUM('feature', 'bug', 'issue') NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    screenshot_url TEXT,
    status ENUM('pending', 'reviewing', 'approved', 'rejected', 'resolved') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    reward_slots INT DEFAULT 0,
    is_rewarded BOOLEAN DEFAULT FALSE,
    admin_notes TEXT,
    reviewed_by VARCHAR(36),
    reviewed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET NULL,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Activity Log Table
CREATE TABLE activity_log (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_family_id (family_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

Click **Go** to execute.

### 6. Backend Setup (XAMPP + MySQL)

```bash
# Navigate to project
cd C:\xampp\htdocs\family-tree-app
# Or wherever you cloned the project

# Create backend virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 7. Configure Backend Environment

Create `backend/.env`:

```env
# MySQL Database (XAMPP)
DATABASE_URL=mysql+pymysql://root:@localhost:3306/family_tree_db

# JWT Secret (change this!)
SECRET_KEY=your-super-secret-key-min-32-characters-long-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880

# Debug
DEBUG=True
```

### 8. Run Backend

```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --port 8001
```

✅ Backend running at: **http://localhost:8001**
✅ API Docs at: **http://localhost:8001/docs**

### 9. Frontend Setup

Open a **NEW terminal**:

```bash
cd C:\xampp\htdocs\family-tree-app\frontend

# Install dependencies
npm install
# or
yarn install

# Create .env file
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8001
```

### 10. Run Frontend

```bash
cd frontend
npm run dev
# or
yarn dev
```

✅ Frontend running at: **http://localhost:5173**

### 11. Access Your App

Open browser: **http://localhost:5173**

---

## Option B: MongoDB

### 1. Download MongoDB

**Download MongoDB Community Server:**
- **Windows**: https://www.mongodb.com/try/download/community
  - Choose: Windows x64, MSI installer
  - Size: ~300MB
- **Mac**: https://www.mongodb.com/try/download/community
  - Or use Homebrew: `brew install mongodb-community`
- **Linux**: https://docs.mongodb.com/manual/administration/install-on-linux/

### 2. Install MongoDB

#### Windows:
1. Run MongoDB installer (`.msi`)
2. Choose "Complete" installation
3. ✅ Check "Install MongoDB as a Service"
4. ✅ Check "Install MongoDB Compass" (GUI tool)
5. Click Install

MongoDB will start automatically as a Windows service.

#### Mac:
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community
```

#### Linux (Ubuntu/Debian):
```bash
# Import MongoDB GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 3. Verify MongoDB Installation

```bash
# Check if MongoDB is running
# Windows (Command Prompt):
net start | find "MongoDB"

# Mac/Linux:
brew services list | grep mongodb
# or
sudo systemctl status mongod
```

### 4. MongoDB Compass (GUI - Optional but Recommended)

If not installed with MongoDB:
- **Download**: https://www.mongodb.com/try/download/compass
- Install and open
- Connect to: `mongodb://localhost:27017`

### 5. Backend Setup (MongoDB)

```bash
cd family-tree-app/backend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Configure Backend for MongoDB

Create `backend/.env`:

```env
# MongoDB
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=family_tree_db

# JWT Secret
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880

# Debug
DEBUG=True
```

### 7. Run Backend

```bash
cd backend
# Make sure venv is activated
uvicorn app.main:app --reload --port 8001
```

✅ Backend running at: **http://localhost:8001**

**Note**: MongoDB collections will be created automatically when you first add data.

### 8. Frontend Setup (Same for Both Options)

```bash
cd frontend
npm install  # or yarn install

# Create .env
echo "VITE_API_URL=http://localhost:8001" > .env

# Run
npm run dev  # or yarn dev
```

✅ Frontend: **http://localhost:5173**

---

## 🌐 Quick Local Setup Summary

### Daily Development Workflow

**XAMPP + MySQL:**
1. Start XAMPP Control Panel → Start MySQL
2. Terminal 1: `cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8001`
3. Terminal 2: `cd frontend && npm run dev`
4. Open: http://localhost:5173

**MongoDB:**
1. MongoDB starts automatically (or `brew services start mongodb-community`)
2. Terminal 1: `cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8001`
3. Terminal 2: `cd frontend && npm run dev`
4. Open: http://localhost:5173

---

# 🌍 Live Production Deployment

## Backend Deployment (Live)

### Option 1: Railway (Recommended - Easy)

**Railway** - Free tier available, auto-deploys from GitHub

1. **Sign up**: https://railway.app/ (GitHub account)

2. **Create New Project**:
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your `family-tree-vue-app` repository
   - Choose `backend` as root directory

3. **Add MongoDB Database**:
   - Click "New" → "Database" → "Add MongoDB"
   - Railway will create MongoDB and add connection string

4. **Environment Variables**:
   In Railway dashboard → Variables tab, add:
   ```env
   MONGO_URL=${{MongoDB.MONGO_URL}}  # Auto-filled by Railway
   DATABASE_NAME=family_tree_db
   SECRET_KEY=your-production-secret-key-very-long-and-random
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
   DEBUG=False
   ```

5. **Deploy**:
   - Railway auto-deploys on git push
   - Get your backend URL: `https://your-app.railway.app`

**Cost**: Free tier (500 hours/month) → $5/month for more

---

### Option 2: Render

**Render** - Free tier with auto-deploy

1. **Sign up**: https://render.com/

2. **Create Web Service**:
   - New → Web Service
   - Connect GitHub repo
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add MongoDB**:
   - Use MongoDB Atlas (free): https://www.mongodb.com/cloud/atlas/register
   - Create free cluster
   - Get connection string
   - Whitelist all IPs: `0.0.0.0/0`

4. **Environment Variables** (in Render):
   ```env
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
   DATABASE_NAME=family_tree_db
   SECRET_KEY=your-production-secret
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   DEBUG=False
   ```

5. **Deploy**: Automatic on git push

**Cost**: Free tier available

---

### Option 3: DigitalOcean App Platform

1. **Sign up**: https://www.digitalocean.com/
2. Create App → GitHub repo
3. Detect Python app
4. Add MongoDB (managed database or Atlas)
5. Set environment variables
6. Deploy

**Cost**: $5/month

---

### Option 4: Heroku

1. **Sign up**: https://www.heroku.com/
2. Install Heroku CLI
3. Deploy:
   ```bash
   cd backend
   heroku create your-app-name
   heroku addons:create mongolab:sandbox  # Free MongoDB
   git push heroku main
   ```

**Cost**: Free tier (with credit card) → $7/month

---

## Frontend Deployment (Live)

### Option 1: Vercel (Recommended - Free)

**Perfect for Vue.js apps**

1. **Sign up**: https://vercel.com/ (GitHub account)

2. **Import Project**:
   - New Project
   - Import from GitHub: `family-tree-vue-app`
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build` or `yarn build`
   - Output Directory: `dist`

3. **Environment Variables**:
   ```env
   VITE_API_URL=https://your-backend.railway.app
   ```

4. **Deploy**: Click Deploy
   - Get URL: `https://your-app.vercel.app`
   - Auto-deploys on git push

**Cost**: Free for personal projects

---

### Option 2: Netlify

1. **Sign up**: https://www.netlify.com/
2. New site from Git → GitHub repo
3. Base directory: `frontend`
4. Build command: `npm run build`
5. Publish directory: `dist`
6. Add env var: `VITE_API_URL`

**Cost**: Free tier available

---

### Option 3: Firebase Hosting

1. Install Firebase CLI: `npm install -g firebase-tools`
2. Login: `firebase login`
3. Init: `firebase init hosting`
4. Deploy:
   ```bash
   cd frontend
   npm run build
   firebase deploy
   ```

**Cost**: Free tier (10GB/month)

---

## Database Setup (Live)

### MongoDB Atlas (Recommended - Free Tier)

1. **Sign up**: https://www.mongodb.com/cloud/atlas/register

2. **Create Cluster**:
   - Choose FREE tier (M0)
   - Select region (closest to users)
   - Cluster name: `family-tree-cluster`

3. **Database Access**:
   - Create user: `admin` with strong password
   - Database User Privileges: Read & Write

4. **Network Access**:
   - Add IP: `0.0.0.0/0` (allow from anywhere)
   - Or add specific IPs of your hosting

5. **Get Connection String**:
   - Click "Connect" → "Connect your application"
   - Copy connection string:
     ```
     mongodb+srv://admin:<password>@family-tree-cluster.xxxxx.mongodb.net/
     ```
   - Replace `<password>` with your actual password

6. **Use in Backend**:
   ```env
   MONGO_URL=mongodb+srv://admin:yourpassword@family-tree-cluster.xxxxx.mongodb.net/family_tree_db
   ```

**Cost**: Free tier (512MB storage)

---

### MySQL on Live Server

If using MySQL in production:

**Options:**
1. **PlanetScale** (free tier): https://planetscale.com/
2. **Railway MySQL**: https://railway.app/
3. **AWS RDS Free Tier**: https://aws.amazon.com/rds/free/

**Example - PlanetScale:**
1. Sign up: https://planetscale.com/
2. Create database: `family-tree-db`
3. Get connection string
4. Add to backend env vars

---

## Complete Production Stack Example

### Recommended Free Stack:

```
Frontend: Vercel (Free)
├── Vue.js app
└── URL: https://family-tree.vercel.app

Backend: Railway (Free/~$5)
├── FastAPI server
└── URL: https://family-tree-api.railway.app

Database: MongoDB Atlas (Free)
├── M0 Cluster
└── 512MB storage

Total Cost: FREE or $5/month
```

---

## Environment Configuration

### Development (.env)
```env
# Backend
DATABASE_URL=mysql+pymysql://root:@localhost:3306/family_tree_db
# or
MONGO_URL=mongodb://localhost:27017
ALLOWED_ORIGINS=http://localhost:5173

# Frontend
VITE_API_URL=http://localhost:8001
```

### Production (.env)
```env
# Backend
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/family_tree_db
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app.com
DEBUG=False
SECRET_KEY=very-long-random-production-secret

# Frontend
VITE_API_URL=https://your-backend.railway.app
```

---

## 📱 Mobile App Deployment

### iOS App Store

**Prerequisites:**
- Mac with Xcode
- Apple Developer Account ($99/year)

**Steps:**
1. Build frontend: `cd frontend && npm run build`
2. Sync to iOS: `npx cap sync ios`
3. Open Xcode: `npx cap open ios`
4. Configure signing (Team, Bundle ID)
5. Archive app: Product → Archive
6. Upload to App Store Connect
7. Submit for review

**Submission Time**: 1-3 days review

---

### Google Play Store

**Prerequisites:**
- Android Studio
- Google Play Developer Account ($25 one-time)

**Steps:**
1. Build: `cd frontend && npm run build`
2. Sync: `npx cap sync android`
3. Open: `npx cap open android`
4. Generate signed APK: Build → Generate Signed Bundle/APK
5. Create app in Play Console
6. Upload AAB file
7. Submit for review

**Submission Time**: Few hours to 1 day

---

## 🔧 Troubleshooting

### Local Development Issues

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check if port 8001 is in use
# Windows:
netstat -ano | findstr :8001
# Mac/Linux:
lsof -i :8001
```

**Frontend won't start:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

**Database connection failed (MySQL):**
- Ensure XAMPP MySQL is running
- Check username: `root`, password: (empty)
- Database exists: `family_tree_db`

**Database connection failed (MongoDB):**
```bash
# Check if MongoDB is running
# Windows:
net start MongoDB

# Mac:
brew services list

# Linux:
sudo systemctl status mongod
```

---

### Production Issues

**Backend 502/504 errors:**
- Check environment variables are set
- Verify DATABASE_URL is correct
- Check logs in hosting platform

**CORS errors:**
- Add frontend URL to `ALLOWED_ORIGINS`
- Include both with and without trailing slash

**Database connection timeout:**
- Whitelist hosting platform IPs
- For MongoDB Atlas: use `0.0.0.0/0`

**Build fails:**
- Check Node/Python versions match requirements
- Verify all dependencies in package.json/requirements.txt

---

## 📊 Deployment Checklist

### Before Going Live:

- [ ] Change SECRET_KEY to strong random value
- [ ] Set DEBUG=False in production
- [ ] Update ALLOWED_ORIGINS with production URLs
- [ ] Set up database backups
- [ ] Configure SSL certificates (handled by Vercel/Railway)
- [ ] Test all API endpoints
- [ ] Test authentication flow
- [ ] Test file uploads
- [ ] Test on mobile devices
- [ ] Set up error monitoring (Sentry)
- [ ] Set up analytics (Google Analytics)

---

## 🎯 Quick Reference

### Local URLs:
- Frontend: http://localhost:5173
- Backend: http://localhost:8001
- API Docs: http://localhost:8001/docs
- phpMyAdmin: http://localhost/phpmyadmin

### Recommended Production Stack:
- **Frontend**: Vercel (Free)
- **Backend**: Railway ($5/month)
- **Database**: MongoDB Atlas (Free)
- **Total**: $5/month

### Support:
- MongoDB Help: https://docs.mongodb.com/
- XAMPP Help: https://www.apachefriends.org/support.html
- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app/

---

**Your Family Tree app is ready to deploy! 🚀🌳**
