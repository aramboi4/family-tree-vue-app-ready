#!/bin/bash

# Rename guide files with proper order numbers

# Step 1: Understanding the project
mv MIGRATION_PLAN.md 01_MIGRATION_PLAN.md

# Step 2: Local development setup
mv XAMPP_SETUP_GUIDE.md 02_LOCAL_SETUP_GUIDE.md

# Step 3: Implementation
mv IMPLEMENTATION_GUIDE.md 03_IMPLEMENTATION_GUIDE.md

# Step 4: RBAC features
mv RBAC_GUIDE.md 04_RBAC_GUIDE.md

# Step 5: Payment integration
mv PAYMENT_INTEGRATION_GUIDE.md 05_PAYMENT_INTEGRATION_GUIDE.md

# Step 6: Support tickets feature
mv FEATURE_SUPPORT_TICKETS.md 06_SUPPORT_TICKETS_GUIDE.md

# Step 7: Deployment
mv DEPLOYMENT_GUIDE.md 07_DEPLOYMENT_GUIDE.md

echo "✅ All guides renamed successfully!"
