# 🚀 Family Tree App - XAMPP Localhost Setup Guide

Yes! You can absolutely develop this project using XAMPP on localhost. Here's how:

## 🎯 What You'll Use from XAMPP

From XAMPP, you'll primarily use:
- ✅ **MySQL** - For the database (instead of MongoDB)
- ✅ **Apache** (optional) - For hosting frontend build
- ❌ **PHP** - Not needed (we're using Python for backend)

**Additional Requirements:**
- Python 3.10+ (for FastAPI backend)
- Node.js 18+ (for Vue.js frontend)

---

## 📋 OPTION 1: XAMPP with MySQL (Recommended for Localhost)

This approach uses XAMPP's MySQL instead of MongoDB, making it easier for local development.

### Step 1: Install Required Software

1. **XAMPP** - Download from [https://www.apachefriends.org](https://www.apachefriends.org)
2. **Python 3.10+** - Download from [https://www.python.org](https://www.python.org)
3. **Node.js 18+** - Download from [https://nodejs.org](https://nodejs.org)

### Step 2: Start XAMPP Services

1. Open XAMPP Control Panel
2. Start **MySQL** (required)
3. Start **Apache** (optional - only if you want to host frontend via Apache)

### Step 3: Create Database

1. Open [http://localhost/phpmyadmin](http://localhost/phpmyadmin)
2. Create a new database: `family_tree_db`
3. Click on the database
4. Go to "SQL" tab and run this SQL:

```sql
-- Create Users Table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Families Table
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

-- Create Family Members Table (roles)
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

-- Create Persons Table
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

-- Create Couples Table
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
    INDEX idx_family_id (family_id),
    INDEX idx_person1 (person1_id),
    INDEX idx_person2 (person2_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Relationships Table (parent-child)
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
    INDEX idx_parent_couple (parent_couple_id),
    INDEX idx_child (child_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Invitations Table
CREATE TABLE invitations (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role ENUM('admin', 'editor', 'viewer') DEFAULT 'viewer',
    token VARCHAR(255) UNIQUE NOT NULL,
    invited_by VARCHAR(36) NOT NULL,
    invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    accepted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Activity Log Table
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
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Step 4: Backend Setup (Python FastAPI with MySQL)

1. **Create project folder:**
```bash
# Create in xampp/htdocs or any preferred location
mkdir C:\xampp\htdocs\family-tree-app
cd C:\xampp\htdocs\family-tree-app
mkdir backend
```

2. **Create `backend/requirements.txt`:**
```txt
fastapi==0.110.0
uvicorn[standard]==0.27.1
pymysql==1.1.0
sqlalchemy==2.0.25
pydantic==2.6.1
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
python-dotenv==1.0.1
reportlab==4.0.9
pillow==10.2.0
aiofiles==23.2.1
cryptography==42.0.2
```

3. **Install dependencies:**
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

4. **Create `backend/.env`:**
```env
# MySQL (XAMPP)
DATABASE_URL=mysql+pymysql://root:@localhost:3306/family_tree_db

# JWT
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8100

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880

# App
DEBUG=True
```

5. **Create `backend/app/database.py`:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/family_tree_db")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=True  # Set to False in production
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

6. **Create `backend/app/main.py`:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Family Tree API",
    description="API for Family Tree SaaS Application",
    version="1.0.0"
)

# CORS
origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Import routes (we'll create these)
# from app.routes import auth, families, persons, relationships
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(families.router, prefix="/api/families", tags=["Families"])
# app.include_router(persons.router, prefix="/api/persons", tags=["Persons"])
# app.include_router(relationships.router, prefix="/api/relationships", tags=["Relationships"])

@app.get("/")
async def root():
    return {
        "message": "Family Tree API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

7. **Run the backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --port 8001
```

Backend will run at: **http://localhost:8001**

### Step 5: Frontend Setup (Vue.js)

1. **Create Vue.js project:**
```bash
cd C:\xampp\htdocs\family-tree-app
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
```

2. **Install dependencies:**
```bash
npm install vue-router pinia axios
npm install -D tailwindcss postcss autoprefixer
npm install primevue primeicons
```

3. **Initialize Tailwind:**
```bash
npx tailwindcss init -p
```

4. **Create `frontend/.env`:**
```env
VITE_API_URL=http://localhost:8001
```

5. **Configure `frontend/vite.config.ts`:**
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: true,
  },
})
```

6. **Run the frontend:**
```bash
cd frontend
npm run dev
```

Frontend will run at: **http://localhost:5173**

---

## 🌐 Access Your Application

Once both servers are running:

- **Frontend (Vue.js):** http://localhost:5173
- **Backend API:** http://localhost:8001
- **API Docs (Swagger):** http://localhost:8001/docs
- **phpMyAdmin:** http://localhost/phpmyadmin

---

## 📱 Mobile Development on Localhost

For mobile app testing on your local network:

1. **Find your local IP address:**
   - Windows: `ipconfig` (look for IPv4 Address, e.g., 192.168.1.100)
   - Mac/Linux: `ifconfig` or `ip addr`

2. **Update frontend `.env`:**
```env
VITE_API_URL=http://192.168.1.100:8001
```

3. **Update backend CORS:**
```env
ALLOWED_ORIGINS=http://localhost:5173,http://192.168.1.100:5173
```

4. **Access from mobile:**
   - Open browser on phone: `http://192.168.1.100:5173`
   - Or build native app with Capacitor

---

## 🚀 Quick Start Commands

**Every time you start development:**

1. **Start XAMPP:**
   - Open XAMPP Control Panel
   - Start MySQL

2. **Start Backend:**
```bash
cd C:\xampp\htdocs\family-tree-app\backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8001
```

3. **Start Frontend:**
```bash
cd C:\xampp\htdocs\family-tree-app\frontend
npm run dev
```

---

## 📋 OPTION 2: XAMPP + MongoDB (If You Prefer MongoDB)

If you still want to use MongoDB with XAMPP:

1. **Install MongoDB separately:** Download from [https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)

2. **Start MongoDB service:**
   - Windows: MongoDB runs as a service automatically
   - Or manually: `mongod --dbpath C:\data\db`

3. **Use the original backend setup** from IMPLEMENTATION_GUIDE.md with MongoDB

4. **XAMPP is only used for:**
   - Hosting the frontend (optional)
   - You won't use MySQL from XAMPP in this case

---

## 🎯 Recommended Folder Structure with XAMPP

```
C:\xampp\htdocs\family-tree-app\
├── backend\
│   ├── venv\
│   ├── app\
│   ├── uploads\
│   ├── requirements.txt
│   └── .env
├── frontend\
│   ├── node_modules\
│   ├── src\
│   ├── public\
│   ├── package.json
│   └── .env
└── database\
    └── schema.sql  (your database export)
```

---

## ⚠️ Common Issues with XAMPP

### Issue 1: MySQL Port Already in Use
**Solution:** Change MySQL port in XAMPP config or stop other MySQL instances

### Issue 2: Python not found
**Solution:** Add Python to PATH during installation or manually

### Issue 3: Cannot connect to MySQL from Python
**Solution:** Check MySQL is running in XAMPP and credentials in `.env` are correct

### Issue 4: CORS errors
**Solution:** Verify `ALLOWED_ORIGINS` in backend `.env` includes your frontend URL

---

## 🎉 You're All Set!

With XAMPP, you get:
- ✅ MySQL database (visual management via phpMyAdmin)
- ✅ Easy local development
- ✅ Familiar XAMPP interface
- ✅ Can export/import database easily

**Next Steps:**
1. Follow the setup steps above
2. Start building your backend API routes
3. Create your Vue.js components
4. Test everything on localhost
5. Later, add Capacitor for mobile apps

**Need the complete backend routes and frontend components?** Let me know and I'll provide them!
