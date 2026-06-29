# ⚡ QUICK SETUP - Family Tree App (15 Minutes)

## 🎯 Goal: Get Family Tree App Running in 15 Minutes

This guide is for **copy-paste setup**. No complex configuration, just a few simple steps!

---

## ✅ Prerequisites (Install These First)

1. **MongoDB** - Download: https://www.mongodb.com/try/download/community
   - Choose "MongoDB Community Server" for your operating system
   - During installation, select "Complete" setup and install as a service
   
2. **Python 3.10+** - Download: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation
   
3. **Node.js 18+** - Download: https://nodejs.org/
   - Download the LTS (Long Term Support) version

---

## 📦 STEP 1: Get the Code (2 minutes)

### Option A: From GitHub
```bash
git clone https://github.com/aramboi4/family-tree-vue-app-ready.git
cd family-tree-vue-app-ready
```

### Option B: If you already have the code
```bash
cd family-tree-vue-app-ready
```

---

## 🗄️ STEP 2: Set Up MongoDB Database (3 minutes)

### 2.1 Start MongoDB

**Windows:**
```bash
# MongoDB should start automatically if installed as a service
# To verify, open Command Prompt and run:
mongo --version
# or for newer versions:
mongosh --version
```

**Mac:**
```bash
# Start MongoDB service
brew services start mongodb-community

# Or run manually:
mongod --config /usr/local/etc/mongod.conf
```

**Linux:**
```bash
# Start MongoDB service
sudo systemctl start mongod

# Enable MongoDB to start on boot
sudo systemctl enable mongod

# Check status
sudo systemctl status mongod
```

### 2.2 Verify MongoDB is Running

```bash
# Open MongoDB shell
mongosh

# You should see MongoDB shell prompt. Type 'exit' to quit
exit
```

**Done!** MongoDB will automatically create the database and collections when the app starts.

---

## ⚙️ STEP 3: Configure (5 minutes)

### 3.1 Backend Configuration

**File:** `backend/.env`

Create a new file `backend/.env` and add:

```env
# MongoDB Connection
MONGO_URL=mongodb://localhost:27017
DB_NAME=family_tree_db

# JWT Secret (Generate a random string, minimum 32 characters)
JWT_SECRET=your-super-secret-key-change-this-in-production-min-32-chars

# Admin Account (Change these!)
ADMIN_EMAIL=admin@familytree.com
ADMIN_PASSWORD=admin123

# CORS
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=*
```

**That's it!** Everything else is pre-configured.

### 3.2 Frontend Configuration

**File:** `frontend/.env`

Create a new file `frontend/.env` and add:

```env
VITE_API_URL=http://localhost:8001
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Done!** Only 2 lines needed for local development.

---

## 🚀 STEP 4: Run the App (5 minutes)

### 4.1 Backend

Open **Terminal/Command Prompt**:

```bash
# Navigate to backend
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate it
venv\Scripts\activate          # Windows
# or
source venv/bin/activate       # Mac/Linux

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the server
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

**Expected output:**
```
✅ Connected to MongoDB: family_tree_db
✅ Admin user created: admin@familytree.com
✅ Test credentials written to /app/memory/test_credentials.md
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

✅ **Backend running!**

### 4.2 Frontend

Open **NEW Terminal/Command Prompt**:

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
yarn install
# or if you don't have yarn:
npm install

# Run development server
yarn dev
# or
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

✅ **Frontend running!**

---

## 🎉 STEP 5: Access Your App

Open browser and go to:

- **🌐 Frontend:** http://localhost:5173
- **🔌 Backend API:** http://localhost:8001
- **📚 API Docs:** http://localhost:8001/api/docs

---

## ✅ Quick Test

1. Go to http://localhost:5173
2. Click **"Register"**
3. Create an account:
   - Email: `test@example.com`
   - Password: `password123`
   - Full Name: `Test User`
4. Click **"Sign Up"**
5. You should be logged in ✅

**OR login with admin account:**
- Email: `admin@familytree.com`
- Password: `admin123`

---

## 🔧 Only Change These Values

### For Local Development:
**Everything works with defaults!** No changes needed.

### For Production:
Update these values in `backend/.env`:

```env
MONGO_URL=mongodb://your-mongo-host:27017
# or for MongoDB Atlas:
# MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

DB_NAME=family_tree_db
JWT_SECRET=your-super-secret-production-key-min-32-chars-very-random
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=SecurePassword123!
FRONTEND_URL=https://yourdomain.com
```

And in `frontend/.env`:

```env
VITE_API_URL=
REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

---

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version    # Should be 3.10+

# Check if MongoDB is running
mongosh
exit

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend won't start
```bash
# Check Node version
node --version      # Should be 18+

# Clear and reinstall
rm -rf node_modules yarn.lock
yarn install
```

### Database connection error
```bash
# Make sure MongoDB is running
# Windows: Check Services (services.msc) for MongoDB
# Mac: brew services list
# Linux: sudo systemctl status mongod

# Check MONGO_URL in backend/.env
# Default should be: mongodb://localhost:27017
```

### Cannot connect to MongoDB
```bash
# Test MongoDB connection
mongosh mongodb://localhost:27017

# If this fails, reinstall MongoDB or check if it's running
```

### CORS error in browser
```bash
# Check frontend .env has correct backend URL
# Check backend is running on port 8001
# Restart both frontend and backend
```

---

## 📋 Daily Development Workflow

### Every time you start developing:

```bash
# 1. Start MongoDB (if not running as service)
# Windows: Already running if installed as service
# Mac: brew services start mongodb-community
# Linux: sudo systemctl start mongod

# 2. Start Backend (Terminal 1)
cd backend
source venv/bin/activate    # Mac/Linux
# or
venv\Scripts\activate       # Windows
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# 3. Start Frontend (Terminal 2)
cd frontend
yarn dev
# or
npm run dev

# 4. Code!
Open http://localhost:5173 in browser
```

---

## 🎯 What You Get Out of the Box

✅ **Authentication System**
- User registration
- Login with JWT cookies
- Password hashing with bcrypt
- Brute force protection

✅ **Family Tree Management**
- Create families
- Add members
- Assign roles (Admin/Editor/Viewer)
- Join code system

✅ **Person Management**
- Add persons
- Edit details
- Upload photos
- Track relationships

✅ **Role-Based Access Control (RBAC)**
- Admin: Full access
- Editor: Can edit
- Viewer: View only

✅ **Support Ticket System**
- Submit bug reports
- Request features
- Reward system (1-15 person slots)

✅ **API Documentation**
- Auto-generated at http://localhost:8001/api/docs
- Try API endpoints directly

---

## 🚀 Next Steps

After basic setup works:

1. **Explore the App** - Create family trees and add members
2. **Test RBAC** - Invite users with different roles
3. **Customize** - Change colors, logo, app name
4. **Deploy** - Follow `DEPLOYMENT_GUIDE.md`

---

## 💡 Pro Tips

### View MongoDB Data:
```bash
# Open MongoDB shell
mongosh

# Use the database
use family_tree_db

# List all collections
show collections

# View users
db.users.find().pretty()

# View families
db.families.find().pretty()

# Exit
exit
```

### Auto-restart on code changes:
- ✅ Backend auto-reloads (--reload flag)
- ✅ Frontend auto-reloads (Vite HMR)
- Just save files and see changes!

---

## 📞 Need Help?

- **Setup Issues:** Check `DEVELOPER_GUIDE.md` (detailed version)
- **Deployment:** Check `DEPLOYMENT_GUIDE.md`
- **API Questions:** Visit http://localhost:8001/api/docs
- **MongoDB Issues:** https://www.mongodb.com/docs/manual/

---

## ✅ Success Checklist

- [ ] MongoDB is running
- [ ] Backend `.env` file created
- [ ] Frontend `.env` file created
- [ ] Backend running on port 8001
- [ ] Frontend running on port 5173
- [ ] Can access http://localhost:5173
- [ ] Can register a new user
- [ ] Can login successfully
- [ ] Can create a family tree
- [ ] Can add family members

**All checked?** 🎉 **You're ready to build!**

---

**Total Setup Time:** ~15 minutes  
**Copy → Configure → Run → Done!**


