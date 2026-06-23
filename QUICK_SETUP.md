# ⚡ QUICK SETUP - Family Tree App (10 Minutes)

## 🎯 Goal: Get Family Tree App Running in 10 Minutes

This guide is for **copy-paste setup**. No complex configuration, just 3 values to change!

---

## ✅ Prerequisites (Install These First)

1. **XAMPP** - Download: https://www.apachefriends.org/download.html
2. **Python 3.10+** - Download: https://www.python.org/downloads/
3. **Node.js 18+** - Download: https://nodejs.org/

---

## 📦 STEP 1: Get the Code (2 minutes)

### Option A: From GitHub (After you push)
```bash
git clone https://github.com/YOUR-USERNAME/family-tree-vue-app.git
cd family-tree-vue-app
```

### Option B: Copy Local Files
```bash
# Copy this entire folder to XAMPP:
Copy: family-tree-starter/
To: C:\xampp\htdocs\family-tree-app\
```

---

## 🗄️ STEP 2: Set Up Database (3 minutes)

### 2.1 Start XAMPP
1. Open **XAMPP Control Panel**
2. Click **Start** next to **MySQL**
3. Wait for it to turn green ✅

### 2.2 Create Database
1. Open browser: http://localhost/phpmyadmin
2. Click **"New"** (left sidebar)
3. Database name: `family_tree_db`
4. Click **"Create"**

### 2.3 Import Schema
1. Click on `family_tree_db` database
2. Click **"Import"** tab
3. Click **"Choose File"**
4. Select: `database/schema.sql` (from the code you copied)
5. Click **"Go"** at bottom
6. Wait for success message ✅

**Done!** Database is ready with all tables.

---

## ⚙️ STEP 3: Configure (5 minutes)

### 3.1 Backend Configuration

**File:** `backend/.env`

Copy `backend/.env.example` to `backend/.env`, then update **ONLY these 3 lines:**

```env
# Database (Change only if you set a MySQL password)
DATABASE_URL=mysql+pymysql://root:@localhost:3306/family_tree_db

# PayMongo (Get test key from https://dashboard.paymongo.com/)
PAYMONGO_SECRET_KEY=sk_test_PASTE_YOUR_KEY_HERE

# Secret (Generate random string, min 32 characters)
SECRET_KEY=change-this-to-something-very-random-min-32-chars
```

**That's it!** Everything else is pre-configured.

### 3.2 Frontend Configuration

**File:** `frontend/.env`

Copy `frontend/.env.example` to `frontend/.env`:

```env
VITE_API_URL=http://localhost:8001
```

**Done!** Only 1 line, already correct for local dev.

---

## 🚀 STEP 4: Run the App (3 minutes)

### 4.1 Backend

Open **Terminal/Command Prompt**:

```bash
# Navigate to backend
cd C:\xampp\htdocs\family-tree-app\backend

# Create virtual environment (first time only)
python -m venv venv

# Activate it
venv\Scripts\activate          # Windows
# or
source venv/bin/activate       # Mac/Linux

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8001
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

✅ **Backend running!**

### 4.2 Frontend

Open **NEW Terminal/Command Prompt**:

```bash
# Navigate to frontend
cd C:\xampp\htdocs\family-tree-app\frontend

# Install dependencies (first time only)
npm install
# or
yarn install

# Run development server
npm run dev
# or
yarn dev
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
- **📚 API Docs:** http://localhost:8001/docs

---

## ✅ Quick Test

1. Go to http://localhost:5173
2. Click **"Register"**
3. Create an account:
   - Email: `admin@test.com`
   - Password: `password123`
   - Full Name: `Admin User`
4. Click **"Sign Up"**
5. You should be logged in ✅

---

## 🔧 Only Change These Values

### For Local Development:
**Everything works with defaults!** No changes needed.

### For Production:
Update these 3 values:

**Backend `.env`:**
```env
DATABASE_URL=mysql+pymysql://user:pass@your-server/family_tree_db
PAYMONGO_SECRET_KEY=sk_live_YOUR_LIVE_KEY
SECRET_KEY=your-super-secret-production-key-min-32-chars
```

**Frontend `.env`:**
```env
VITE_API_URL=https://your-backend.railway.app
```

---

## 📱 For PayMongo Test Mode

1. Sign up: https://dashboard.paymongo.com/signup
2. Go to **"API Keys"**
3. Copy **"Secret Key"** (starts with `sk_test_`)
4. Paste in `backend/.env`:
   ```env
   PAYMONGO_SECRET_KEY=sk_test_YOUR_KEY_HERE
   ```

**Test cards for PayMongo:**
- Card: `4343 4343 4343 4345`
- Expiry: Any future date
- CVC: Any 3 digits

---

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version    # Should be 3.10+

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend won't start
```bash
# Check Node version
node --version      # Should be 18+

# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database connection error
```bash
# Make sure XAMPP MySQL is running (green in control panel)
# Check database exists in phpMyAdmin
# Check DATABASE_URL in backend/.env
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
# 1. Start XAMPP (MySQL)
Open XAMPP Control Panel → Start MySQL

# 2. Start Backend (Terminal 1)
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8001

# 3. Start Frontend (Terminal 2)
cd frontend
npm run dev

# 4. Code!
Open http://localhost:5173 in browser
```

---

## 🎯 What You Get Out of the Box

✅ **Authentication System**
- User registration
- Login with JWT
- Password hashing

✅ **Family Tree Management**
- Create families
- Add members
- Assign roles (Admin/Editor/Viewer)

✅ **Person Management**
- Add persons
- Edit details
- Upload photos

✅ **Basic Tree Visualization**
- View family tree
- Search persons

✅ **Subscription System**
- 5 plans (Free → Elite)
- Upgrade with PayMongo

✅ **RBAC**
- Admin: Full access
- Editor: Can edit
- Viewer: View only

✅ **API Documentation**
- Auto-generated at http://localhost:8001/docs
- Try API endpoints directly

---

## 🚀 Next Steps

After basic setup works:

1. **Customize Features** - Add your own features
2. **Update Branding** - Change colors, logo, app name
3. **Add Data** - Create family trees and test
4. **Deploy** - Follow `07_DEPLOYMENT_GUIDE.md`

---

## 💡 Pro Tips

### Speed up future startups:
```bash
# Create shortcuts in terminal
alias backend="cd ~/family-tree-app/backend && source venv/bin/activate && uvicorn app.main:app --reload"
alias frontend="cd ~/family-tree-app/frontend && npm run dev"
```

### Auto-restart on code changes:
- ✅ Backend auto-reloads (--reload flag)
- ✅ Frontend auto-reloads (Vite HMR)
- Just save files and see changes!

---

## 📞 Need Help?

- **Setup Issues:** Check `02_LOCAL_SETUP_GUIDE.md` (detailed version)
- **Features:** Check `03_IMPLEMENTATION_GUIDE.md`
- **Deployment:** Check `07_DEPLOYMENT_GUIDE.md`
- **Code Questions:** Check `PROJECT_STATUS.md`

---

## ✅ Success Checklist

- [ ] XAMPP MySQL is running (green)
- [ ] Database `family_tree_db` exists
- [ ] All tables imported (8 tables)
- [ ] Backend running on port 8001
- [ ] Frontend running on port 5173
- [ ] Can access http://localhost:5173
- [ ] Can register a new user
- [ ] Can login successfully
- [ ] Can create a family tree

**All checked?** 🎉 **You're ready to build!**

---

**Total Setup Time:** ~10 minutes  
**Copy → Configure → Run → Done!**
