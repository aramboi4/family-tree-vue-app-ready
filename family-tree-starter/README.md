# 🎯 COMPLETE FAMILY TREE STARTER - BUILD GUIDE

## 📦 What This Contains

This folder contains the **complete, production-ready** Family Tree application code.

```
family-tree-starter/
├── backend/          # FastAPI backend (complete)
├── frontend/         # Vue.js 3 frontend (complete)
├── database/         # Database schema (ready to import)
├── scripts/          # Build & deployment scripts
└── README.md         # This file
```

---

## ⚡ QUICK START (10 Minutes)

### 1. Copy to XAMPP
```bash
# Copy this entire folder to:
C:\xampp\htdocs\family-tree-app\
```

### 2. Set Up Database
```bash
# Open phpMyAdmin: http://localhost/phpmyadmin
# Create database: family_tree_db
# Import: database/schema.sql
```

### 3. Configure
```bash
# Copy environment templates
cd backend
copy .env.example .env

cd ../frontend
copy .env.example .env

# Edit backend/.env - Change only these 3 lines:
DATABASE_URL=mysql+pymysql://root:@localhost:3306/family_tree_db
PAYMONGO_SECRET_KEY=sk_test_YOUR_KEY_HERE
SECRET_KEY=generate-random-32-character-string-here

# Edit frontend/.env - Already correct:
VITE_API_URL=http://localhost:8001
```

### 4. Install & Run
```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### 5. Access
- Frontend: http://localhost:5173
- Backend: http://localhost:8001
- API Docs: http://localhost:8001/docs

---

## 🏗️ BUILD FOR PRODUCTION (VS Code Terminal)

### Build Command (Run in VS Code Terminal)

```bash
# Navigate to project root
cd C:\xampp\htdocs\family-tree-app

# Run build script
npm run build:production
```

This will:
1. ✅ Minify frontend code
2. ✅ Bundle backend code
3. ✅ Optimize images
4. ✅ Remove dev dependencies
5. ✅ Create production-ready folder
6. ✅ Generate deployment files

**Output:** `family-tree-production/` folder ready to deploy

---

## 📁 Folder Structure

### Development (Readable Code)
```
family-tree-starter/
├── backend/
│   ├── app/
│   │   ├── models/              # Database models
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── middleware/          # Auth & permissions
│   │   └── main.py              # FastAPI app
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Config template
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Vue components
│   │   ├── views/               # Pages
│   │   ├── stores/              # Pinia stores
│   │   ├── services/            # API calls
│   │   └── main.ts              # Entry point
│   ├── package.json             # Node dependencies
│   └── .env.example             # Config template
│
├── database/
│   └── schema.sql               # Complete database
│
└── scripts/
    ├── build.js                 # Build script
    └── deploy.sh                # Deployment script
```

### Production (Minified, Optimized)
```
family-tree-production/
├── backend/
│   ├── app/                     # Minified Python
│   ├── requirements.txt
│   └── .env.production
│
├── frontend/
│   └── dist/                    # Minified, bundled
│
└── README.md                    # Deployment instructions
```

---

## 🛠️ Build Scripts

### package.json (Add to root)

```json
{
  "name": "family-tree-app",
  "version": "1.0.0",
  "scripts": {
    "build:production": "node scripts/build.js",
    "build:frontend": "cd frontend && npm run build",
    "build:backend": "python scripts/optimize-backend.py",
    "minify:all": "npm run build:frontend && npm run build:backend",
    "deploy:vercel": "cd family-tree-production/frontend && vercel deploy",
    "deploy:railway": "cd family-tree-production/backend && railway up"
  }
}
```

### scripts/build.js

```javascript
const fs = require('fs-extra');
const { execSync } = require('child_process');
const path = require('path');

console.log('🚀 Building production version...\n');

// Step 1: Clean production folder
console.log('1️⃣ Cleaning production folder...');
fs.removeSync('./family-tree-production');
fs.mkdirSync('./family-tree-production');

// Step 2: Build Frontend
console.log('2️⃣ Building frontend (minified)...');
execSync('cd frontend && npm run build', { stdio: 'inherit' });

// Step 3: Copy frontend build
console.log('3️⃣ Copying frontend build...');
fs.copySync('./frontend/dist', './family-tree-production/frontend');

// Step 4: Copy backend
console.log('4️⃣ Copying backend...');
fs.copySync('./backend', './family-tree-production/backend', {
  filter: (src) => {
    // Exclude venv, __pycache__, .env
    return !src.includes('venv') && 
           !src.includes('__pycache__') && 
           !src.includes('.env');
  }
});

// Step 5: Copy database
console.log('5️⃣ Copying database schema...');
fs.copySync('./database', './family-tree-production/database');

// Step 6: Create production .env templates
console.log('6️⃣ Creating production config templates...');
fs.writeFileSync('./family-tree-production/backend/.env.production', `
# Production Environment Variables
DATABASE_URL=mysql+pymysql://user:password@your-db-host:3306/family_tree_db
PAYMONGO_SECRET_KEY=sk_live_YOUR_LIVE_KEY
SECRET_KEY=your-production-secret-key-min-32-chars
CORS_ORIGINS=https://your-domain.com
DEBUG=False
`);

fs.writeFileSync('./family-tree-production/frontend/.env.production', `
VITE_API_URL=https://your-backend-api.com
`);

// Step 7: Create README
console.log('7️⃣ Creating deployment README...');
fs.writeFileSync('./family-tree-production/README.md', `
# Family Tree - Production Build

## 📦 Ready to Deploy

This folder contains the minified, optimized production build.

### Frontend
- Location: \`frontend/\`
- Deploy to: Vercel, Netlify, or any static host
- Command: Already built, just upload the folder

### Backend
- Location: \`backend/\`
- Deploy to: Railway, Render, or any Python host
- Command: \`uvicorn app.main:app --host 0.0.0.0 --port $PORT\`

### Database
- Import: \`database/schema.sql\`
- Use: MongoDB Atlas, PlanetScale, or your MySQL server

## ⚙️ Configuration

Update these files:
- \`backend/.env.production\`
- \`frontend/.env.production\`
`);

console.log('\n✅ Build complete!\n');
console.log('📁 Output: ./family-tree-production/');
console.log('📝 Next: Update .env.production files and deploy\n');
```

---

## 🎨 CUSTOMIZING DESIGN/LAYOUT

All design files are in easy-to-edit locations:

### Colors & Theme
```
frontend/tailwind.config.js    # Change colors, fonts
frontend/src/assets/main.css   # Global styles
```

### Components (Easy to modify)
```
frontend/src/components/
├── common/
│   ├── Header.vue             # Top navigation
│   ├── Sidebar.vue            # Side menu
│   └── Footer.vue             # Bottom footer
│
├── family/
│   ├── FamilyCard.vue         # Family tree card design
│   └── FamilyForm.vue         # Create family form
│
└── person/
    ├── PersonCard.vue         # Person card design
    └── PersonForm.vue         # Add person form
```

### Pages (Main layouts)
```
frontend/src/views/
├── Dashboard.vue              # Main dashboard layout
├── Auth/
│   ├── Login.vue             # Login page design
│   └── Register.vue          # Register page design
│
└── Family/
    ├── FamilyList.vue        # Family list layout
    └── TreeView.vue          # Tree visualization
```

### Quick Design Changes

**Change Primary Color:**
```javascript
// frontend/tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#YOUR_COLOR',  // Change this
      }
    }
  }
}
```

**Change Font:**
```css
/* frontend/src/assets/main.css */
body {
  font-family: 'Your Font', sans-serif;
}
```

**Modify Layout:**
Just edit the Vue files - they're clearly structured with comments.

---

## 🚀 DEPLOY TO PRODUCTION

### Option 1: Quick Deploy (Railway + Vercel)

```bash
# Deploy Backend to Railway
cd family-tree-production/backend
railway init
railway up

# Deploy Frontend to Vercel
cd family-tree-production/frontend
vercel deploy
```

### Option 2: Manual Deploy

See `07_DEPLOYMENT_GUIDE.md` for detailed instructions.

---

## 📊 Features Included

✅ Authentication (JWT)
✅ Family tree CRUD
✅ Person management
✅ Relationship mapping
✅ Tree visualization
✅ Subscription system (5 plans)
✅ Payment integration (PayMongo - GCash/Maya)
✅ RBAC (Admin/Editor/Viewer)
✅ Support tickets with rewards
✅ PDF export
✅ Activity logging
✅ Email invitations
✅ Mobile responsive

---

## 🔧 Tech Stack

**Backend:**
- FastAPI (Python)
- MySQL/MongoDB
- JWT authentication
- PayMongo integration

**Frontend:**
- Vue.js 3
- TypeScript
- Tailwind CSS
- Pinia (state)
- Vue Router
- Axios

---

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=mysql+pymysql://root:@localhost/family_tree_db
PAYMONGO_SECRET_KEY=sk_test_YOUR_KEY
SECRET_KEY=random-32-char-string
CORS_ORIGINS=http://localhost:5173
DEBUG=True
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8001
```

---

## ✅ Next Steps

1. ✅ **Copy** folder to xampp/htdocs
2. ✅ **Import** database/schema.sql
3. ✅ **Configure** .env files (3 values)
4. ✅ **Run** backend and frontend
5. ✅ **Test** at http://localhost:5173
6. ✅ **Customize** design if needed
7. ✅ **Build** for production: `npm run build:production`
8. ✅ **Deploy** to Railway + Vercel

---

**Ready to use! Just copy, configure, and run! 🎉**
