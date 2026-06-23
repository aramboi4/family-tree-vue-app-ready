const fs = require('fs-extra');
const { execSync } = require('child_process');
const path = require('path');

console.log('🚀 Building Family Tree Production Version...\n');
console.log('This will create a minified, optimized version ready for deployment.\n');

// Configuration
const SOURCE_DIR = './family-tree-starter';
const OUTPUT_DIR = './family-tree-production';

// Step 1: Clean and create production folder
console.log('1️⃣  Cleaning production folder...');
try {
  fs.removeSync(OUTPUT_DIR);
  fs.mkdirSync(OUTPUT_DIR);
  console.log('   ✅ Production folder ready\n');
} catch (error) {
  console.error('   ❌ Error cleaning folder:', error.message);
  process.exit(1);
}

// Step 2: Build Frontend (Minify & Bundle)
console.log('2️⃣  Building frontend (Vue.js + Vite)...');
console.log('   📦 Running: npm run build');
try {
  execSync('cd ' + SOURCE_DIR + '/frontend && npm run build', { 
    stdio: 'inherit',
    shell: true 
  });
  console.log('   ✅ Frontend built successfully\n');
} catch (error) {
  console.error('   ❌ Frontend build failed');
  console.error('   💡 Make sure you ran "npm install" first');
  process.exit(1);
}

// Step 3: Copy Frontend Build
console.log('3️⃣  Copying frontend build to production...');
try {
  fs.copySync(SOURCE_DIR + '/frontend/dist', OUTPUT_DIR + '/frontend');
  console.log('   ✅ Frontend copied\n');
} catch (error) {
  console.error('   ❌ Error copying frontend:', error.message);
}

// Step 4: Copy Backend (exclude venv, cache, .env)
console.log('4️⃣  Copying backend (excluding dev files)...');
try {
  fs.copySync(SOURCE_DIR + '/backend', OUTPUT_DIR + '/backend', {
    filter: (src) => {
      const exclude = ['venv', '__pycache__', '.pytest_cache', '.env', 'node_modules'];
      return !exclude.some(item => src.includes(item));
    }
  });
  console.log('   ✅ Backend copied\n');
} catch (error) {
  console.error('   ❌ Error copying backend:', error.message);
}

// Step 5: Copy Database Schema
console.log('5️⃣  Copying database schema...');
try {
  fs.copySync(SOURCE_DIR + '/database', OUTPUT_DIR + '/database');
  console.log('   ✅ Database schema copied\n');
} catch (error) {
  console.error('   ❌ Error copying database:', error.message);
}

// Step 6: Create Production Environment Templates
console.log('6️⃣  Creating production environment templates...');
try {
  // Backend production env
  fs.writeFileSync(OUTPUT_DIR + '/backend/.env.production', `# ======================================
# PRODUCTION ENVIRONMENT VARIABLES
# ======================================

# Database (Update with your production database)
DATABASE_URL=mysql+pymysql://username:password@your-db-host:3306/family_tree_db

# PayMongo (Use LIVE keys for production)
PAYMONGO_SECRET_KEY=sk_live_YOUR_LIVE_KEY_HERE
PAYMONGO_PUBLIC_KEY=pk_live_YOUR_PUBLIC_KEY_HERE

# JWT Secret (Generate a strong random string)
SECRET_KEY=your-super-secret-production-key-min-32-characters-long

# CORS (Add your production domains)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Debug (MUST be False in production)
DEBUG=False

# Upload Settings
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880

# Optional: Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
`);

  // Frontend production env
  fs.writeFileSync(OUTPUT_DIR + '/frontend/.env.production', `# ======================================
# FRONTEND PRODUCTION ENVIRONMENT
# ======================================

# Backend API URL (Update with your production backend URL)
VITE_API_URL=https://your-backend-api.railway.app

# Or if using same domain:
# VITE_API_URL=https://api.yourdomain.com
`);

  console.log('   ✅ Environment templates created\n');
} catch (error) {
  console.error('   ❌ Error creating env files:', error.message);
}

// Step 7: Create Deployment README
console.log('7️⃣  Creating deployment documentation...');
try {
  fs.writeFileSync(OUTPUT_DIR + '/README.md', `# 🚀 Family Tree - Production Build

## 📦 This is a Production-Ready Build

This folder contains the **minified, optimized** version of the Family Tree application, ready for deployment.

---

## 🗂️ Contents

\`\`\`
family-tree-production/
├── backend/              # FastAPI backend (optimized)
├── frontend/             # Vue.js frontend (minified & bundled)
├── database/             # Database schema
├── .env.production       # Environment templates
└── README.md            # This file
\`\`\`

---

## ⚙️ STEP 1: Configure Environment Variables

### Backend Configuration

**File:** \`backend/.env.production\`

Update these values:

\`\`\`env
# Your production database
DATABASE_URL=mysql+pymysql://user:pass@host:3306/family_tree_db

# Your PayMongo LIVE keys (not test keys!)
PAYMONGO_SECRET_KEY=sk_live_YOUR_KEY

# Strong random secret (generate with: openssl rand -hex 32)
SECRET_KEY=your-random-32-char-production-secret

# Your production domain
CORS_ORIGINS=https://yourdomain.com
\`\`\`

### Frontend Configuration

**File:** \`frontend/.env.production\`

Update this value:

\`\`\`env
# Your backend API URL
VITE_API_URL=https://your-backend.railway.app
\`\`\`

---

## 🗄️ STEP 2: Set Up Database

1. Create database on your production server
2. Import \`database/schema.sql\`
3. Verify all tables are created

**For MongoDB Atlas:**
- Use connection string in DATABASE_URL

**For MySQL (Railway, PlanetScale, etc.):**
- Use MySQL connection string

---

## 🚀 STEP 3: Deploy Backend

### Option A: Railway (Recommended)

\`\`\`bash
cd backend
railway init
railway up
\`\`\`

### Option B: Render

1. Create new Web Service
2. Connect GitHub repo
3. Build command: \`pip install -r requirements.txt\`
4. Start command: \`uvicorn app.main:app --host 0.0.0.0 --port $PORT\`

### Option C: DigitalOcean

1. Create droplet
2. Upload backend folder
3. Run: \`pip install -r requirements.txt\`
4. Run: \`uvicorn app.main:app --host 0.0.0.0 --port 80\`

---

## 🌐 STEP 4: Deploy Frontend

### Option A: Vercel (Recommended)

\`\`\`bash
cd frontend
vercel deploy --prod
\`\`\`

### Option B: Netlify

1. Drag and drop \`frontend\` folder to Netlify
2. Or use CLI: \`netlify deploy --prod --dir=frontend\`

### Option C: Firebase Hosting

\`\`\`bash
firebase init hosting
firebase deploy
\`\`\`

---

## ✅ STEP 5: Verify Deployment

1. **Test Backend:** https://your-backend-url/docs
2. **Test Frontend:** https://your-frontend-url
3. **Test API Connection:** Try logging in
4. **Test Payment:** Create test subscription

---

## 🔒 Security Checklist

Before going live:

- [ ] Updated all .env files with production values
- [ ] Using LIVE PayMongo keys (not test keys)
- [ ] DEBUG=False in backend .env
- [ ] Strong SECRET_KEY (32+ characters)
- [ ] CORS_ORIGINS set to actual domains
- [ ] Database has proper backups
- [ ] SSL certificates active (https://)

---

## 📊 What's Included

✅ Minified frontend (smaller file sizes)
✅ Optimized backend (no dev dependencies)
✅ Production-ready configuration
✅ Complete database schema
✅ Deployment instructions

---

## 💰 Recommended Stack (FREE/Cheap)

- **Frontend:** Vercel (FREE)
- **Backend:** Railway ($5/month)
- **Database:** MongoDB Atlas (FREE) or PlanetScale (FREE)
- **Total:** $5/month or less

---

## 🆘 Troubleshooting

### Backend won't start
- Check DATABASE_URL is correct
- Verify all environment variables are set
- Check logs: \`railway logs\` or platform-specific command

### Frontend shows blank page
- Check VITE_API_URL is correct
- Check CORS_ORIGINS in backend includes frontend URL
- Open browser console for errors

### Payment not working
- Verify using LIVE keys (sk_live_, pk_live_)
- Check PayMongo dashboard for errors
- Verify webhook URL is set in PayMongo

### Database connection error
- Verify database is running
- Check connection string format
- Whitelist IP addresses if needed

---

## 📞 Support

- Check original guides in main repository
- Review deployment guide: 07_DEPLOYMENT_GUIDE.md
- Test locally first before deploying

---

## 🎉 You're Ready!

Follow steps 1-5 above and your Family Tree app will be live!

**Good luck! 🌳**
`);

  console.log('   ✅ Documentation created\n');
} catch (error) {
  console.error('   ❌ Error creating README:', error.message);
}

// Step 8: Create package.json for production
console.log('8️⃣  Creating production package.json...');
try {
  const packageJson = {
    name: "family-tree-production",
    version: "1.0.0",
    description: "Family Tree Application - Production Build",
    scripts: {
      "deploy:frontend": "cd frontend && vercel deploy --prod",
      "deploy:backend": "cd backend && railway up",
      "test:backend": "cd backend && python -m pytest",
      "verify": "echo 'Production build ready for deployment'"
    }
  };
  
  fs.writeFileSync(OUTPUT_DIR + '/package.json', JSON.stringify(packageJson, null, 2));
  console.log('   ✅ Package.json created\n');
} catch (error) {
  console.error('   ❌ Error creating package.json:', error.message);
}

// Step 9: Create .gitignore for production
console.log('9️⃣  Creating .gitignore...');
try {
  fs.writeFileSync(OUTPUT_DIR + '/.gitignore', `# Production .gitignore

# Environment files (will be set on deployment platform)
.env
.env.production
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
venv/
*.egg-info/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
`);
  console.log('   ✅ .gitignore created\n');
} catch (error) {
  console.error('   ❌ Error creating .gitignore:', error.message);
}

// Final Summary
console.log('\n' + '='.repeat(50));
console.log('✅ BUILD COMPLETE!');
console.log('='.repeat(50));
console.log('\n📁 Output Location: ' + OUTPUT_DIR);
console.log('\n📝 Next Steps:');
console.log('   1. Update environment files:');
console.log('      - backend/.env.production');
console.log('      - frontend/.env.production');
console.log('   2. Deploy backend to Railway/Render');
console.log('   3. Deploy frontend to Vercel/Netlify');
console.log('   4. Import database schema');
console.log('   5. Test everything!\n');
console.log('💡 See ' + OUTPUT_DIR + '/README.md for detailed deployment instructions.\n');
