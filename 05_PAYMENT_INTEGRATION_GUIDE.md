# 💳 Payment Integration Guide - Philippine Payment Methods

## 📋 Overview

Subscription plans are **FAMILY TREE-BASED**, not user-based:
- Each family tree has its own subscription plan
- Users can purchase/upgrade plans for family trees they admin
- Different family trees can have different plans
- Payment applies to the specific family tree, not the user's account

## 🇵🇭 Philippine Payment Methods Supported

### Primary Payment Options:
1. **GCash** - Most popular e-wallet in Philippines
2. **Maya** (formerly PayMaya) - Second largest e-wallet
3. **QR Ph** - QR code payments (GCash/Maya compatible)
4. **InstaPay** - Bank-to-bank instant transfers
5. **Bank Transfer** - Direct bank deposits
6. **Credit/Debit Cards** - Visa, Mastercard

---

## 🚀 Recommended Payment Gateway: PayMongo

**PayMongo** is the best option for Philippine payments because:
- ✅ Supports GCash, Maya, GrabPay
- ✅ Supports credit/debit cards
- ✅ QR Ph compatible
- ✅ Bank transfers (InstaPay/PESONet)
- ✅ Easy integration
- ✅ Competitive fees (3.5% + ₱15 per transaction)
- ✅ Automatic webhook notifications
- ✅ Test mode for development

**Website:** https://www.paymongo.com/

### Alternative Options:
- **Xendit** - https://www.xendit.co/en-ph/
- **Dragonpay** - https://www.dragonpay.ph/
- **PayPal** - Limited GCash support

---

## 📊 Database Schema Updates

### Update Subscriptions to be Family-Based

```sql
-- Drop old user-based subscription (if exists)
-- DROP TABLE IF EXISTS user_subscriptions;

-- Family-based Subscriptions Table
CREATE TABLE family_subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) UNIQUE NOT NULL,
    plan ENUM('free', 'basic', 'standard', 'pro', 'elite') DEFAULT 'free',
    status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
    person_limit INT DEFAULT 50,
    amount DECIMAL(10, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'PHP',
    billing_cycle ENUM('monthly', 'yearly') DEFAULT 'monthly',
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    auto_renew BOOLEAN DEFAULT TRUE,
    purchased_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (purchased_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_family_id (family_id),
    INDEX idx_status (status),
    INDEX idx_period_end (current_period_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Payment Transactions Table
CREATE TABLE payment_transactions (
    id VARCHAR(36) PRIMARY KEY,
    family_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    subscription_id VARCHAR(36),
    payment_gateway VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'PHP',
    status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    plan ENUM('basic', 'standard', 'pro', 'elite') NOT NULL,
    billing_cycle ENUM('monthly', 'yearly') NOT NULL,
    payment_details JSON,
    webhook_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES family_subscriptions(id) ON DELETE SET NULL,
    INDEX idx_family_id (family_id),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Subscription Plans Reference Table
CREATE TABLE subscription_plans (
    id VARCHAR(36) PRIMARY KEY,
    plan_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    person_limit INT NOT NULL,
    monthly_price DECIMAL(10, 2) NOT NULL,
    yearly_price DECIMAL(10, 2) NOT NULL,
    features JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default plans
INSERT INTO subscription_plans (id, plan_code, name, description, person_limit, monthly_price, yearly_price, features) VALUES
('plan-free', 'free', 'Free Plan', 'Basic family tree features', 50, 0.00, 0.00, '{"pdf_export": true, "watermark": true, "api_access": false}'),
('plan-basic', 'basic', 'Basic Plan', 'Extended family tree', 100, 100.00, 1000.00, '{"pdf_export": true, "watermark": false, "api_access": false}'),
('plan-standard', 'standard', 'Standard Plan', 'Large family tree with API', 200, 200.00, 2000.00, '{"pdf_export": true, "watermark": false, "api_access": true}'),
('plan-pro', 'pro', 'Pro Plan', 'Professional features', 500, 400.00, 4000.00, '{"pdf_export": true, "watermark": false, "api_access": true, "premium_templates": true}'),
('plan-elite', 'elite', 'Elite Plan', 'Unlimited family tree', 999999, 600.00, 6000.00, '{"pdf_export": true, "watermark": false, "api_access": true, "premium_templates": true, "priority_support": true}');
```

For MongoDB, use similar structure in collections.

---

## 🔧 Backend Implementation

### 1. PayMongo Integration Setup

**Install Dependencies:**

```bash
pip install requests
```

**Backend Configuration (`backend/.env`):**

```env
# PayMongo
PAYMONGO_SECRET_KEY=sk_test_your_secret_key_here
PAYMONGO_PUBLIC_KEY=pk_test_your_public_key_here
PAYMONGO_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# For Production:
# PAYMONGO_SECRET_KEY=sk_live_your_live_secret_key
# PAYMONGO_PUBLIC_KEY=pk_live_your_live_public_key
```

### 2. Payment Models

**`backend/app/models/payment.py`:**

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class PaymentMethod(str, Enum):
    GCASH = "gcash"
    MAYA = "paymaya"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    GRABPAY = "grab_pay"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class SubscriptionPlanCode(str, Enum):
    FREE = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PRO = "pro"
    ELITE = "elite"

class CreatePaymentRequest(BaseModel):
    family_id: str
    plan: SubscriptionPlanCode
    billing_cycle: BillingCycle
    payment_method: PaymentMethod

class PaymentIntentCreate(BaseModel):
    amount: int  # in centavos (₱100.00 = 10000)
    currency: str = "PHP"
    payment_method_allowed: list[str]
    description: str
    statement_descriptor: str = "Family Tree Subscription"

class FamilySubscription(BaseModel):
    id: str = Field(alias="_id")
    family_id: str
    plan: str
    status: str = "active"
    person_limit: int
    amount: float
    currency: str = "PHP"
    billing_cycle: str
    current_period_start: datetime
    current_period_end: datetime
    auto_renew: bool = True
    purchased_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class PaymentTransaction(BaseModel):
    id: str = Field(alias="_id")
    family_id: str
    user_id: str
    subscription_id: Optional[str] = None
    payment_gateway: str = "paymongo"
    payment_method: str
    transaction_id: Optional[str] = None
    amount: float
    currency: str = "PHP"
    status: str = "pending"
    plan: str
    billing_cycle: str
    payment_details: Optional[Dict[str, Any]] = None
    webhook_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
```

### 3. PayMongo Service

**`backend/app/services/paymongo_service.py`:**

```python
import requests
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import base64

class PayMongoService:
    def __init__(self):
        self.secret_key = os.getenv("PAYMONGO_SECRET_KEY")
        self.public_key = os.getenv("PAYMONGO_PUBLIC_KEY")
        self.base_url = "https://api.paymongo.com/v1"
        
        # Create auth header (base64 encode secret key)
        auth_string = f"{self.secret_key}:"
        self.auth_header = base64.b64encode(auth_string.encode()).decode()
    
    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json"
        }
    
    def create_payment_intent(
        self,
        amount: int,  # in centavos
        payment_method: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment intent
        amount: in centavos (₱100.00 = 10000)
        payment_method: gcash, paymaya, card, grab_pay
        """
        url = f"{self.base_url}/payment_intents"
        
        # Map payment methods
        payment_method_types = {
            "gcash": "gcash",
            "maya": "paymaya",
            "paymaya": "paymaya",
            "card": "card",
            "grab_pay": "grab_pay"
        }
        
        payload = {
            "data": {
                "attributes": {
                    "amount": amount,
                    "payment_method_allowed": [payment_method_types.get(payment_method, payment_method)],
                    "payment_method_options": {
                        "card": {"request_three_d_secure": "any"}
                    },
                    "currency": "PHP",
                    "description": description,
                    "statement_descriptor": "Family Tree",
                    "metadata": metadata or {}
                }
            }
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=self.get_headers()
        )
        
        return response.json()
    
    def create_payment_method(
        self,
        payment_type: str,
        billing_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment method
        """
        url = f"{self.base_url}/payment_methods"
        
        payload = {
            "data": {
                "attributes": {
                    "type": payment_type,
                    "billing": billing_details or {}
                }
            }
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=self.get_headers()
        )
        
        return response.json()
    
    def attach_payment_intent(
        self,
        payment_intent_id: str,
        payment_method_id: str,
        return_url: str
    ) -> Dict[str, Any]:
        """
        Attach payment method to payment intent
        """
        url = f"{self.base_url}/payment_intents/{payment_intent_id}/attach"
        
        payload = {
            "data": {
                "attributes": {
                    "payment_method": payment_method_id,
                    "return_url": return_url
                }
            }
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=self.get_headers()
        )
        
        return response.json()
    
    def get_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve payment intent details
        """
        url = f"{self.base_url}/payment_intents/{payment_intent_id}"
        
        response = requests.get(
            url,
            headers=self.get_headers()
        )
        
        return response.json()
    
    def create_source(
        self,
        amount: int,
        payment_type: str,
        redirect_url: Dict[str, str],
        billing_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment source (for GCash, GrabPay)
        """
        url = f"{self.base_url}/sources"
        
        payload = {
            "data": {
                "attributes": {
                    "amount": amount,
                    "redirect": redirect_url,
                    "type": payment_type,
                    "currency": "PHP",
                    "billing": billing_details or {}
                }
            }
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=self.get_headers()
        )
        
        return response.json()
    
    def get_source(self, source_id: str) -> Dict[str, Any]:
        """
        Retrieve source details
        """
        url = f"{self.base_url}/sources/{source_id}"
        
        response = requests.get(
            url,
            headers=self.get_headers()
        )
        
        return response.json()

# Pricing helper
PLAN_PRICES = {
    "basic": {"monthly": 10000, "yearly": 100000},  # ₱100/month, ₱1000/year
    "standard": {"monthly": 20000, "yearly": 200000},  # ₱200/month, ₱2000/year
    "pro": {"monthly": 40000, "yearly": 400000},  # ₱400/month, ₱4000/year
    "elite": {"monthly": 60000, "yearly": 600000}  # ₱600/month, ₱6000/year
}

PERSON_LIMITS = {
    "free": 50,
    "basic": 100,
    "standard": 200,
    "pro": 500,
    "elite": 999999
}
```

### 4. Payment Routes

**`backend/app/routes/payments.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional
from datetime import datetime, timedelta
import uuid
from app.models.payment import (
    CreatePaymentRequest, 
    FamilySubscription,
    PaymentTransaction,
    PaymentMethod
)
from app.services.paymongo_service import PayMongoService, PLAN_PRICES, PERSON_LIMITS
from app.database import get_db
from app.utils.auth import get_current_user, require_family_admin

router = APIRouter()
paymongo = PayMongoService()

@router.get("/plans")
async def get_subscription_plans(db = Depends(get_db)):
    """
    Get all available subscription plans
    """
    plans = await db.subscription_plans.find({"is_active": True}).to_list(10)
    return plans

@router.get("/family/{family_id}/subscription")
async def get_family_subscription(
    family_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get current subscription for a family tree
    """
    # Verify user has access to family
    family_member = await db.family_members.find_one({
        "family_id": family_id,
        "user_id": current_user["id"]
    })
    
    if not family_member:
        raise HTTPException(status_code=403, detail="Access denied")
    
    subscription = await db.family_subscriptions.find_one({"family_id": family_id})
    
    if not subscription:
        # Return default free plan
        return {
            "family_id": family_id,
            "plan": "free",
            "status": "active",
            "person_limit": 50,
            "amount": 0.00,
            "billing_cycle": "monthly"
        }
    
    return FamilySubscription(**subscription)

@router.post("/family/{family_id}/subscribe")
async def create_subscription_payment(
    family_id: str,
    payment_request: CreatePaymentRequest,
    current_user: dict = Depends(require_family_admin(family_id)),
    db = Depends(get_db)
):
    """
    Create a payment for family subscription
    Only family admins can purchase subscriptions
    """
    # Verify family exists
    family = await db.families.find_one({"_id": family_id})
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    # Get plan price
    plan = payment_request.plan.value
    billing_cycle = payment_request.billing_cycle.value
    
    if plan == "free":
        raise HTTPException(status_code=400, detail="Cannot purchase free plan")
    
    amount_centavos = PLAN_PRICES[plan][billing_cycle]
    amount_pesos = amount_centavos / 100
    
    # Create payment transaction record
    transaction_id = str(uuid.uuid4())
    transaction = {
        "_id": transaction_id,
        "family_id": family_id,
        "user_id": current_user["id"],
        "payment_gateway": "paymongo",
        "payment_method": payment_request.payment_method.value,
        "amount": amount_pesos,
        "currency": "PHP",
        "status": "pending",
        "plan": plan,
        "billing_cycle": billing_cycle,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.payment_transactions.insert_one(transaction)
    
    # Create PayMongo payment based on method
    try:
        if payment_request.payment_method in [PaymentMethod.GCASH, PaymentMethod.MAYA, PaymentMethod.GRABPAY]:
            # Use Source API for e-wallets
            redirect_urls = {
                "success": f"https://your-frontend-url.com/payment/success?transaction_id={transaction_id}",
                "failed": f"https://your-frontend-url.com/payment/failed?transaction_id={transaction_id}"
            }
            
            payment_type_map = {
                "gcash": "gcash",
                "maya": "paymaya",
                "paymaya": "paymaya",
                "grab_pay": "grab_pay"
            }
            
            source = paymongo.create_source(
                amount=amount_centavos,
                payment_type=payment_type_map[payment_request.payment_method.value],
                redirect_url=redirect_urls,
                billing_details={
                    "name": current_user.get("full_name", ""),
                    "email": current_user.get("email", "")
                }
            )
            
            # Update transaction with payment details
            await db.payment_transactions.update_one(
                {"_id": transaction_id},
                {
                    "$set": {
                        "transaction_id": source["data"]["id"],
                        "payment_details": source,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "transaction_id": transaction_id,
                "checkout_url": source["data"]["attributes"]["redirect"]["checkout_url"],
                "payment_method": payment_request.payment_method.value,
                "amount": amount_pesos,
                "currency": "PHP"
            }
        
        else:
            # Use Payment Intent API for cards
            payment_intent = paymongo.create_payment_intent(
                amount=amount_centavos,
                payment_method=payment_request.payment_method.value,
                description=f"Family Tree {plan.title()} Plan - {billing_cycle.title()}",
                metadata={
                    "family_id": family_id,
                    "transaction_id": transaction_id,
                    "user_id": current_user["id"]
                }
            )
            
            await db.payment_transactions.update_one(
                {"_id": transaction_id},
                {
                    "$set": {
                        "transaction_id": payment_intent["data"]["id"],
                        "payment_details": payment_intent,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "transaction_id": transaction_id,
                "payment_intent_id": payment_intent["data"]["id"],
                "client_key": payment_intent["data"]["attributes"]["client_key"],
                "amount": amount_pesos,
                "currency": "PHP"
            }
    
    except Exception as e:
        # Update transaction as failed
        await db.payment_transactions.update_one(
            {"_id": transaction_id},
            {"$set": {"status": "failed", "updated_at": datetime.utcnow()}}
        )
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")

@router.post("/webhook")
async def paymongo_webhook(request: Request, db = Depends(get_db)):
    """
    PayMongo webhook handler
    Handles payment success/failure notifications
    """
    payload = await request.json()
    
    event_type = payload.get("data", {}).get("attributes", {}).get("type")
    
    if event_type == "source.chargeable":
        # Payment successful - update subscription
        source_id = payload["data"]["attributes"]["data"]["id"]
        
        # Find transaction
        transaction = await db.payment_transactions.find_one({
            "transaction_id": source_id
        })
        
        if transaction:
            # Update transaction status
            await db.payment_transactions.update_one(
                {"_id": transaction["_id"]},
                {
                    "$set": {
                        "status": "paid",
                        "webhook_data": payload,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Create or update family subscription
            period_start = datetime.utcnow()
            period_end = period_start + timedelta(days=30 if transaction["billing_cycle"] == "monthly" else 365)
            
            subscription = {
                "family_id": transaction["family_id"],
                "plan": transaction["plan"],
                "status": "active",
                "person_limit": PERSON_LIMITS[transaction["plan"]],
                "amount": transaction["amount"],
                "currency": "PHP",
                "billing_cycle": transaction["billing_cycle"],
                "current_period_start": period_start,
                "current_period_end": period_end,
                "auto_renew": True,
                "purchased_by": transaction["user_id"],
                "updated_at": datetime.utcnow()
            }
            
            await db.family_subscriptions.update_one(
                {"family_id": transaction["family_id"]},
                {"$set": subscription},
                upsert=True
            )
            
            # Update family person limit
            await db.families.update_one(
                {"_id": transaction["family_id"]},
                {"$set": {"person_limit": PERSON_LIMITS[transaction["plan"]]}}
            )
            
            # Log activity
            await db.activity_log.insert_one({
                "_id": str(uuid.uuid4()),
                "family_id": transaction["family_id"],
                "user_id": transaction["user_id"],
                "action": "subscription_upgraded",
                "details": f"Upgraded to {transaction['plan'].title()} plan",
                "created_at": datetime.utcnow()
            })
    
    return {"status": "success"}

@router.get("/transaction/{transaction_id}")
async def get_transaction_status(
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Check transaction status
    """
    transaction = await db.payment_transactions.find_one({
        "_id": transaction_id,
        "user_id": current_user["id"]
    })
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return PaymentTransaction(**transaction)
```

### 5. Add to main.py

```python
from app.routes import payments

app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
```

---

## 🎨 Frontend Implementation

### 1. Upgrade Button on Family Tree View

**`frontend/src/views/Family/FamilyTreeView.vue`:**

```vue
<template>
  <div class="family-tree-container">
    <!-- Header with Upgrade Button -->
    <div class="flex justify-between items-center mb-6 p-4 bg-white rounded shadow">
      <div>
        <h1 class="text-2xl font-bold">{{ family.name }}</h1>
        <p class="text-sm text-gray-600">
          Plan: <span class="font-semibold">{{ subscription.plan }}</span> 
          | Persons: {{ family.person_count }} / {{ subscription.person_limit }}
        </p>
      </div>
      
      <!-- Upgrade Plan Button -->
      <button
        v-if="canUpgrade"
        @click="showUpgradeModal = true"
        class="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition flex items-center gap-2"
        data-testid="upgrade-plan-btn"
      >
        <i class="pi pi-arrow-up"></i>
        Upgrade Plan
      </button>
    </div>
    
    <!-- Usage Warning -->
    <div 
      v-if="isNearLimit" 
      class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4 rounded"
    >
      <div class="flex items-center">
        <i class="pi pi-exclamation-triangle text-yellow-600 mr-3"></i>
        <div>
          <p class="text-sm font-medium text-yellow-800">
            You're using {{ family.person_count }} of {{ subscription.person_limit }} person slots
          </p>
          <p class="text-xs text-yellow-700 mt-1">
            Upgrade your plan to add more family members
          </p>
        </div>
      </div>
    </div>
    
    <!-- Tree Visualization -->
    <div class="tree-canvas bg-white rounded shadow p-6">
      <!-- Your tree component here -->
    </div>
    
    <!-- Upgrade Modal -->
    <UpgradePlanModal
      v-if="showUpgradeModal"
      :family-id="familyId"
      :current-plan="subscription.plan"
      @close="showUpgradeModal = false"
      @success="handleUpgradeSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'
import UpgradePlanModal from '@/components/subscription/UpgradePlanModal.vue'

const route = useRoute()
const familyId = route.params.id as string

const family = ref({})
const subscription = ref({
  plan: 'free',
  person_limit: 50
})
const showUpgradeModal = ref(false)

const canUpgrade = computed(() => {
  // Only admins can upgrade
  return family.value.role === 'admin' && subscription.value.plan !== 'elite'
})

const isNearLimit = computed(() => {
  const usage = family.value.person_count / subscription.value.person_limit
  return usage >= 0.8  // 80% or more
})

onMounted(async () => {
  await loadFamilyData()
  await loadSubscription()
})

async function loadFamilyData() {
  try {
    const response = await api.get(`/api/families/${familyId}`)
    family.value = response.data
  } catch (error) {
    console.error('Error loading family:', error)
  }
}

async function loadSubscription() {
  try {
    const response = await api.get(`/api/payments/family/${familyId}/subscription`)
    subscription.value = response.data
  } catch (error) {
    console.error('Error loading subscription:', error)
  }
}

function handleUpgradeSuccess() {
  showUpgradeModal.value = false
  loadSubscription()
  loadFamilyData()
}
</script>
```

### 2. Upgrade Plan Modal

**`frontend/src/components/subscription/UpgradePlanModal.vue`:**

```vue
<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
        <h2 class="text-2xl font-bold">Upgrade Your Family Tree Plan</h2>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">
          <i class="pi pi-times text-xl"></i>
        </button>
      </div>
      
      <!-- Plans -->
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="plan in plans"
            :key="plan.plan_code"
            :class="[
              'border rounded-lg p-6 cursor-pointer transition',
              selectedPlan === plan.plan_code ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300',
              plan.plan_code === currentPlan ? 'opacity-60 cursor-not-allowed' : ''
            ]"
            @click="selectPlan(plan)"
          >
            <!-- Current Plan Badge -->
            <div v-if="plan.plan_code === currentPlan" class="bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded mb-3 inline-block">
              Current Plan
            </div>
            
            <h3 class="text-xl font-bold mb-2">{{ plan.name }}</h3>
            <p class="text-3xl font-bold mb-1">
              ₱{{ formatPrice(plan.monthly_price) }}
              <span class="text-sm font-normal text-gray-600">/month</span>
            </p>
            <p class="text-sm text-gray-600 mb-4">
              ₱{{ formatPrice(plan.yearly_price) }}/year (save 17%)
            </p>
            
            <div class="space-y-2 mb-4">
              <p class="text-sm flex items-center gap-2">
                <i class="pi pi-users text-blue-600"></i>
                <span>{{ plan.person_limit === 999999 ? 'Unlimited' : plan.person_limit }} persons</span>
              </p>
              <p class="text-sm flex items-center gap-2">
                <i class="pi pi-file-pdf text-blue-600"></i>
                <span>PDF Export {{ plan.features.watermark ? '(with watermark)' : '' }}</span>
              </p>
              <p v-if="plan.features.api_access" class="text-sm flex items-center gap-2">
                <i class="pi pi-code text-blue-600"></i>
                <span>API Access</span>
              </p>
              <p v-if="plan.features.premium_templates" class="text-sm flex items-center gap-2">
                <i class="pi pi-star text-blue-600"></i>
                <span>Premium Templates</span>
              </p>
            </div>
            
            <button
              v-if="plan.plan_code !== currentPlan && plan.plan_code !== 'free'"
              :class="[
                'w-full py-2 rounded font-semibold transition',
                selectedPlan === plan.plan_code
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              {{ selectedPlan === plan.plan_code ? 'Selected' : 'Select Plan' }}
            </button>
          </div>
        </div>
        
        <!-- Billing Cycle Selection -->
        <div v-if="selectedPlan" class="mt-8 bg-gray-50 rounded-lg p-6">
          <h3 class="font-semibold mb-4">Choose Billing Cycle</h3>
          <div class="grid grid-cols-2 gap-4">
            <div
              :class="[
                'border rounded-lg p-4 cursor-pointer transition',
                billingCycle === 'monthly' ? 'border-blue-600 bg-blue-50' : 'border-gray-300'
              ]"
              @click="billingCycle = 'monthly'"
            >
              <p class="font-semibold">Monthly</p>
              <p class="text-2xl font-bold">₱{{ getSelectedPlanPrice('monthly') }}</p>
              <p class="text-sm text-gray-600">Billed monthly</p>
            </div>
            <div
              :class="[
                'border rounded-lg p-4 cursor-pointer transition relative',
                billingCycle === 'yearly' ? 'border-blue-600 bg-blue-50' : 'border-gray-300'
              ]"
              @click="billingCycle = 'yearly'"
            >
              <span class="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded">
                Save 17%
              </span>
              <p class="font-semibold">Yearly</p>
              <p class="text-2xl font-bold">₱{{ getSelectedPlanPrice('yearly') }}</p>
              <p class="text-sm text-gray-600">Billed annually</p>
            </div>
          </div>
        </div>
        
        <!-- Payment Method Selection -->
        <div v-if="selectedPlan" class="mt-6 bg-gray-50 rounded-lg p-6">
          <h3 class="font-semibold mb-4">Choose Payment Method</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              v-for="method in paymentMethods"
              :key="method.value"
              :class="[
                'border rounded-lg p-4 cursor-pointer transition flex flex-col items-center',
                paymentMethod === method.value ? 'border-blue-600 bg-blue-50' : 'border-gray-300'
              ]"
              @click="paymentMethod = method.value"
            >
              <img :src="method.logo" :alt="method.label" class="h-12 mb-2">
              <p class="text-sm font-medium">{{ method.label }}</p>
            </div>
          </div>
        </div>
        
        <!-- Checkout Button -->
        <div v-if="selectedPlan" class="mt-6 flex justify-end gap-4">
          <button
            @click="$emit('close')"
            class="px-6 py-3 border rounded-lg font-semibold hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="proceedToPayment"
            :disabled="loading || !paymentMethod"
            class="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Processing...' : `Pay ₱${getTotalAmount()}` }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const props = defineProps<{
  familyId: string
  currentPlan: string
}>()

const emit = defineEmits(['close', 'success'])

const plans = ref([])
const selectedPlan = ref('')
const billingCycle = ref<'monthly' | 'yearly'>('monthly')
const paymentMethod = ref('')
const loading = ref(false)

const paymentMethods = [
  { value: 'gcash', label: 'GCash', logo: '/images/gcash-logo.png' },
  { value: 'maya', label: 'Maya', logo: '/images/maya-logo.png' },
  { value: 'grab_pay', label: 'GrabPay', logo: '/images/grabpay-logo.png' },
  { value: 'card', label: 'Card', logo: '/images/card-logo.png' }
]

onMounted(async () => {
  await loadPlans()
})

async function loadPlans() {
  try {
    const response = await api.get('/api/payments/plans')
    plans.value = response.data.filter(p => p.plan_code !== 'free')
  } catch (error) {
    console.error('Error loading plans:', error)
  }
}

function selectPlan(plan: any) {
  if (plan.plan_code !== props.currentPlan) {
    selectedPlan.value = plan.plan_code
  }
}

function formatPrice(price: number) {
  return price.toFixed(2)
}

function getSelectedPlanPrice(cycle: 'monthly' | 'yearly') {
  const plan = plans.value.find(p => p.plan_code === selectedPlan.value)
  if (!plan) return '0.00'
  return formatPrice(cycle === 'monthly' ? plan.monthly_price : plan.yearly_price)
}

function getTotalAmount() {
  return getSelectedPlanPrice(billingCycle.value)
}

async function proceedToPayment() {
  loading.value = true
  
  try {
    const response = await api.post(`/api/payments/family/${props.familyId}/subscribe`, {
      family_id: props.familyId,
      plan: selectedPlan.value,
      billing_cycle: billingCycle.value,
      payment_method: paymentMethod.value
    })
    
    // Redirect to payment page
    if (response.data.checkout_url) {
      // For e-wallets (GCash, Maya, GrabPay)
      window.location.href = response.data.checkout_url
    } else {
      // For cards, handle payment intent
      // You would integrate PayMongo.js here for card payments
      console.log('Payment intent:', response.data)
    }
    
  } catch (error) {
    console.error('Payment error:', error)
    alert('Payment failed. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>
```

---

## 📱 Payment Flow

### User Journey:

1. **User navigates to Family Tree page**
2. **Sees current plan and "Upgrade Plan" button** (if admin)
3. **Clicks "Upgrade Plan"**
4. **Modal opens showing all plans with pricing**
5. **Selects desired plan** (Basic/Standard/Pro/Elite)
6. **Chooses billing cycle** (Monthly or Yearly)
7. **Selects payment method** (GCash/Maya/Card/GrabPay)
8. **Clicks "Pay ₱XXX"**
9. **Redirected to payment gateway** (GCash app, Maya app, etc.)
10. **Completes payment** in e-wallet app
11. **Redirected back to success page**
12. **Webhook updates subscription** automatically
13. **Family tree person limit updated** immediately

---

## 🔔 Payment Success/Failure Handling

**`frontend/src/views/Payment/PaymentSuccess.vue`:**

```vue
<template>
  <div class="max-w-md mx-auto mt-20 text-center">
    <div class="bg-white rounded-lg shadow-lg p-8">
      <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <i class="pi pi-check text-3xl text-green-600"></i>
      </div>
      <h1 class="text-2xl font-bold mb-2">Payment Successful!</h1>
      <p class="text-gray-600 mb-6">
        Your family tree has been upgraded successfully.
      </p>
      <button
        @click="$router.push(`/families/${familyId}/tree`)"
        class="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700"
      >
        Go to Family Tree
      </button>
    </div>
  </div>
</template>
```

---

## 🧪 Testing Payment Integration

### 1. PayMongo Test Mode

Use test credentials:
- **Test Secret Key**: `sk_test_...`
- **Test Public Key**: `pk_test_...`

### 2. Test Cards

```
Card Number: 4343 4343 4343 4345
Expiry: Any future date
CVC: Any 3 digits
```

### 3. Test GCash/Maya

In test mode, you'll get a mock payment page that you can approve/decline.

---

## 💰 Pricing Summary

```
Plan         Monthly    Yearly     Person Limit
Free         ₱0         ₱0         50
Basic        ₱100       ₱1,000     100
Standard     ₱200       ₱2,000     200
Pro          ₱400       ₱4,000     500
Elite        ₱600       ₱6,000     Unlimited
```

---

## 📋 Implementation Checklist

- [ ] Install PayMongo account (https://dashboard.paymongo.com/signup)
- [ ] Get API keys (test and live)
- [ ] Update database schema (family-based subscriptions)
- [ ] Implement PayMongo service
- [ ] Create payment routes
- [ ] Add upgrade button to family tree view
- [ ] Create upgrade plan modal
- [ ] Implement webhook handler
- [ ] Test with test cards/e-wallets
- [ ] Switch to live keys for production
- [ ] Set up webhook URL in PayMongo dashboard

---

## 🌟 Key Features

✅ **Family-based subscriptions** (not user-based)
✅ **Multiple payment methods** (GCash, Maya, Cards, GrabPay)
✅ **Upgrade button on family tree page**
✅ **Visual plan comparison**
✅ **Monthly and yearly billing**
✅ **Automatic subscription activation**
✅ **Webhook-based payment verification**
✅ **Transaction history tracking**

---

**Your family tree app now has complete Philippine payment integration! 💳🇵🇭**
