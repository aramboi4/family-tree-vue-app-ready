# 🎫 Support Ticket System with Reward Feature

## Overview

Users can submit tickets for:
- Feature suggestions
- Bug reports  
- General issues

**Reward System:**
- Users get **10 person slots by default** for approved features or critical bugs
- Admin can adjust reward from **1-15 slots** per ticket
- Slots are added to the user's family tree

---

## 📊 Database Schema

### Add to MySQL Schema (XAMPP Setup)

```sql
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
    INDEX idx_family_id (family_id),
    INDEX idx_status (status),
    INDEX idx_ticket_type (ticket_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Ticket Comments Table (for admin-user communication)
CREATE TABLE ticket_comments (
    id VARCHAR(36) PRIMARY KEY,
    ticket_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    comment TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES support_tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_ticket_id (ticket_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### For MongoDB Setup

```javascript
// Support Tickets Collection
{
  _id: ObjectId,
  user_id: String,
  family_id: String,
  ticket_type: String, // 'feature', 'bug', 'issue'
  title: String,
  description: String,
  screenshot_url: String,
  status: String, // 'pending', 'reviewing', 'approved', 'rejected', 'resolved'
  priority: String, // 'low', 'medium', 'high', 'critical'
  reward_slots: Number,
  is_rewarded: Boolean,
  admin_notes: String,
  reviewed_by: String,
  reviewed_at: Date,
  created_at: Date,
  updated_at: Date
}

// Ticket Comments Collection
{
  _id: ObjectId,
  ticket_id: String,
  user_id: String,
  comment: String,
  is_admin: Boolean,
  created_at: Date
}
```

---

## 🔧 Backend Implementation

### 1. Pydantic Models

**`backend/app/models/ticket.py`:**

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TicketType(str, Enum):
    FEATURE = "feature"
    BUG = "bug"
    ISSUE = "issue"

class TicketStatus(str, Enum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESOLVED = "resolved"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketCreate(BaseModel):
    family_id: Optional[str] = None
    ticket_type: TicketType
    title: str
    description: str
    screenshot_url: Optional[str] = None

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    admin_notes: Optional[str] = None

class TicketReward(BaseModel):
    ticket_id: str
    reward_slots: int = Field(ge=1, le=15, description="Reward slots (1-15)")
    admin_notes: Optional[str] = None

class Ticket(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    family_id: Optional[str] = None
    ticket_type: TicketType
    title: str
    description: str
    screenshot_url: Optional[str] = None
    status: TicketStatus = TicketStatus.PENDING
    priority: TicketPriority = TicketPriority.MEDIUM
    reward_slots: int = 0
    is_rewarded: bool = False
    admin_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class TicketCommentCreate(BaseModel):
    comment: str

class TicketComment(BaseModel):
    id: str = Field(alias="_id")
    ticket_id: str
    user_id: str
    comment: str
    is_admin: bool = False
    created_at: datetime
    
    class Config:
        populate_by_name = True
```

### 2. API Routes

**`backend/app/routes/tickets.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List, Optional
from datetime import datetime
import uuid
import os
from app.models.ticket import (
    TicketCreate, TicketUpdate, TicketReward, Ticket, 
    TicketCommentCreate, TicketComment, TicketStatus, TicketPriority
)
from app.database import get_db
from app.utils.auth import get_current_user, require_admin

router = APIRouter()

# User Endpoints

@router.post("/", response_model=Ticket, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create a new support ticket
    
    Users can submit:
    - Feature suggestions
    - Bug reports
    - General issues
    """
    ticket = {
        "_id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "family_id": ticket_data.family_id,
        "ticket_type": ticket_data.ticket_type,
        "title": ticket_data.title,
        "description": ticket_data.description,
        "screenshot_url": ticket_data.screenshot_url,
        "status": "pending",
        "priority": "medium",
        "reward_slots": 0,
        "is_rewarded": False,
        "admin_notes": None,
        "reviewed_by": None,
        "reviewed_at": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.support_tickets.insert_one(ticket)
    return Ticket(**ticket)

@router.post("/upload-screenshot")
async def upload_screenshot(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload screenshot for ticket
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only image files (JPEG, PNG, GIF) are allowed"
        )
    
    # Validate file size (max 5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 5MB"
        )
    
    # Save file
    upload_dir = "uploads/tickets"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    filepath = os.path.join(upload_dir, filename)
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Return URL
    return {
        "url": f"/uploads/tickets/{filename}",
        "filename": filename
    }

@router.get("/my-tickets", response_model=List[Ticket])
async def get_my_tickets(
    status: Optional[TicketStatus] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get current user's tickets
    """
    query = {"user_id": current_user["id"]}
    if status:
        query["status"] = status
    
    tickets = await db.support_tickets.find(query).sort("created_at", -1).to_list(100)
    return [Ticket(**ticket) for ticket in tickets]

@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get ticket by ID (user can only view their own tickets)
    """
    ticket = await db.support_tickets.find_one({
        "_id": ticket_id,
        "user_id": current_user["id"]
    })
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return Ticket(**ticket)

@router.post("/{ticket_id}/comments", response_model=TicketComment)
async def add_comment(
    ticket_id: str,
    comment_data: TicketCommentCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Add comment to ticket
    """
    # Verify ticket exists and user has access
    ticket = await db.support_tickets.find_one({
        "_id": ticket_id,
        "user_id": current_user["id"]
    })
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    comment = {
        "_id": str(uuid.uuid4()),
        "ticket_id": ticket_id,
        "user_id": current_user["id"],
        "comment": comment_data.comment,
        "is_admin": False,
        "created_at": datetime.utcnow()
    }
    
    await db.ticket_comments.insert_one(comment)
    return TicketComment(**comment)

@router.get("/{ticket_id}/comments", response_model=List[TicketComment])
async def get_ticket_comments(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get all comments for a ticket
    """
    # Verify ticket exists and user has access
    ticket = await db.support_tickets.find_one({
        "_id": ticket_id,
        "user_id": current_user["id"]
    })
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    comments = await db.ticket_comments.find({
        "ticket_id": ticket_id
    }).sort("created_at", 1).to_list(100)
    
    return [TicketComment(**comment) for comment in comments]

# Admin Endpoints

@router.get("/admin/all", response_model=List[Ticket])
async def get_all_tickets_admin(
    status: Optional[TicketStatus] = None,
    ticket_type: Optional[str] = None,
    priority: Optional[TicketPriority] = None,
    current_user: dict = Depends(require_admin),
    db = Depends(get_db)
):
    """
    Get all tickets (admin only)
    """
    query = {}
    if status:
        query["status"] = status
    if ticket_type:
        query["ticket_type"] = ticket_type
    if priority:
        query["priority"] = priority
    
    tickets = await db.support_tickets.find(query).sort("created_at", -1).to_list(500)
    return [Ticket(**ticket) for ticket in tickets]

@router.put("/admin/{ticket_id}", response_model=Ticket)
async def update_ticket_admin(
    ticket_id: str,
    update_data: TicketUpdate,
    current_user: dict = Depends(require_admin),
    db = Depends(get_db)
):
    """
    Update ticket (admin only)
    """
    ticket = await db.support_tickets.find_one({"_id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    update_fields = {
        "updated_at": datetime.utcnow(),
        "reviewed_by": current_user["id"],
        "reviewed_at": datetime.utcnow()
    }
    
    if update_data.status:
        update_fields["status"] = update_data.status
    if update_data.priority:
        update_fields["priority"] = update_data.priority
    if update_data.admin_notes:
        update_fields["admin_notes"] = update_data.admin_notes
    
    await db.support_tickets.update_one(
        {"_id": ticket_id},
        {"$set": update_fields}
    )
    
    updated_ticket = await db.support_tickets.find_one({"_id": ticket_id})
    return Ticket(**updated_ticket)

@router.post("/admin/{ticket_id}/reward", response_model=dict)
async def reward_ticket(
    ticket_id: str,
    reward_data: TicketReward,
    current_user: dict = Depends(require_admin),
    db = Depends(get_db)
):
    """
    Reward user with additional person slots (admin only)
    
    Rules:
    - Default: 10 slots for approved features or critical bugs
    - Admin can set 1-15 slots
    - Slots are added to user's family tree
    """
    ticket = await db.support_tickets.find_one({"_id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket["is_rewarded"]:
        raise HTTPException(status_code=400, detail="Ticket already rewarded")
    
    # Validate reward slots (1-15)
    if reward_data.reward_slots < 1 or reward_data.reward_slots > 15:
        raise HTTPException(
            status_code=400,
            detail="Reward slots must be between 1 and 15"
        )
    
    # Update ticket
    await db.support_tickets.update_one(
        {"_id": ticket_id},
        {
            "$set": {
                "reward_slots": reward_data.reward_slots,
                "is_rewarded": True,
                "status": "approved",
                "admin_notes": reward_data.admin_notes,
                "reviewed_by": current_user["id"],
                "reviewed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Add slots to user's family tree
    if ticket["family_id"]:
        family = await db.families.find_one({"_id": ticket["family_id"]})
        if family:
            new_limit = family["person_limit"] + reward_data.reward_slots
            await db.families.update_one(
                {"_id": ticket["family_id"]},
                {"$set": {"person_limit": new_limit}}
            )
    
    # Log activity
    await db.activity_log.insert_one({
        "_id": str(uuid.uuid4()),
        "family_id": ticket["family_id"],
        "user_id": ticket["user_id"],
        "action": "ticket_rewarded",
        "details": f"Received {reward_data.reward_slots} person slots for ticket: {ticket['title']}",
        "created_at": datetime.utcnow()
    })
    
    return {
        "message": f"Rewarded {reward_data.reward_slots} slots to user",
        "ticket_id": ticket_id,
        "reward_slots": reward_data.reward_slots
    }

@router.post("/admin/{ticket_id}/comments", response_model=TicketComment)
async def add_admin_comment(
    ticket_id: str,
    comment_data: TicketCommentCreate,
    current_user: dict = Depends(require_admin),
    db = Depends(get_db)
):
    """
    Add admin comment to ticket
    """
    ticket = await db.support_tickets.find_one({"_id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    comment = {
        "_id": str(uuid.uuid4()),
        "ticket_id": ticket_id,
        "user_id": current_user["id"],
        "comment": comment_data.comment,
        "is_admin": True,
        "created_at": datetime.utcnow()
    }
    
    await db.ticket_comments.insert_one(comment)
    return TicketComment(**comment)
```

### 3. Add to main.py

```python
from app.routes import tickets

app.include_router(tickets.router, prefix="/api/tickets", tags=["Support Tickets"])
```

---

## 🎨 Frontend Implementation

### 1. Vue Component - Submit Ticket Form

**`frontend/src/views/Support/SubmitTicket.vue`:**

```vue
<template>
  <div class="max-w-2xl mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">Submit Support Ticket</h1>
    
    <form @submit.prevent="submitTicket" class="space-y-6">
      <!-- Ticket Type -->
      <div>
        <label class="block text-sm font-medium mb-2">Ticket Type</label>
        <select v-model="form.ticket_type" required class="w-full p-2 border rounded">
          <option value="">Select type...</option>
          <option value="feature">Feature Suggestion</option>
          <option value="bug">Bug Report</option>
          <option value="issue">General Issue</option>
        </select>
      </div>
      
      <!-- Family Tree -->
      <div>
        <label class="block text-sm font-medium mb-2">Family Tree (Optional)</label>
        <select v-model="form.family_id" class="w-full p-2 border rounded">
          <option value="">Select family tree...</option>
          <option v-for="family in families" :key="family.id" :value="family.id">
            {{ family.name }}
          </option>
        </select>
        <p class="text-xs text-gray-500 mt-1">
          Select if this ticket relates to a specific family tree
        </p>
      </div>
      
      <!-- Title -->
      <div>
        <label class="block text-sm font-medium mb-2">Title</label>
        <input
          v-model="form.title"
          type="text"
          required
          placeholder="Brief description of the issue or feature"
          class="w-full p-2 border rounded"
        />
      </div>
      
      <!-- Description -->
      <div>
        <label class="block text-sm font-medium mb-2">Description</label>
        <textarea
          v-model="form.description"
          required
          rows="6"
          placeholder="Provide detailed information..."
          class="w-full p-2 border rounded"
        ></textarea>
      </div>
      
      <!-- Screenshot Upload -->
      <div>
        <label class="block text-sm font-medium mb-2">Screenshot (Optional)</label>
        <input
          type="file"
          accept="image/*"
          @change="handleFileUpload"
          class="w-full"
        />
        <p class="text-xs text-gray-500 mt-1">
          Max file size: 5MB (JPEG, PNG, GIF)
        </p>
        
        <!-- Screenshot Preview -->
        <div v-if="screenshotPreview" class="mt-4">
          <img :src="screenshotPreview" alt="Preview" class="max-w-sm border rounded" />
        </div>
      </div>
      
      <!-- Reward Info -->
      <div class="bg-blue-50 border border-blue-200 rounded p-4">
        <h3 class="font-semibold text-blue-900 mb-2">🎁 Reward Program</h3>
        <p class="text-sm text-blue-800">
          If your suggestion is approved or you report a critical bug, 
          you'll receive <strong>up to 15 additional person slots</strong> for your family tree!
        </p>
      </div>
      
      <!-- Submit Button -->
      <div>
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-3 rounded font-semibold hover:bg-blue-700 disabled:bg-gray-400"
        >
          {{ loading ? 'Submitting...' : 'Submit Ticket' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const loading = ref(false)
const families = ref([])
const screenshotPreview = ref('')

const form = ref({
  ticket_type: '',
  family_id: '',
  title: '',
  description: '',
  screenshot_url: ''
})

onMounted(async () => {
  // Load user's families
  try {
    const response = await api.get('/api/families')
    families.value = response.data
  } catch (error) {
    console.error('Error loading families:', error)
  }
})

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // Show preview
  const reader = new FileReader()
  reader.onload = (e) => {
    screenshotPreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
  
  // Upload to server
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/api/tickets/upload-screenshot', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    form.value.screenshot_url = response.data.url
  } catch (error) {
    console.error('Error uploading screenshot:', error)
    alert('Failed to upload screenshot')
  }
}

async function submitTicket() {
  loading.value = true
  
  try {
    await api.post('/api/tickets', {
      ticket_type: form.value.ticket_type,
      family_id: form.value.family_id || null,
      title: form.value.title,
      description: form.value.description,
      screenshot_url: form.value.screenshot_url || null
    })
    
    alert('Ticket submitted successfully!')
    router.push('/support/my-tickets')
  } catch (error) {
    console.error('Error submitting ticket:', error)
    alert('Failed to submit ticket')
  } finally {
    loading.value = false
  }
}
</script>
```

### 2. Vue Component - My Tickets

**`frontend/src/views/Support/MyTickets.vue`:**

```vue
<template>
  <div class="max-w-4xl mx-auto p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">My Support Tickets</h1>
      <button
        @click="$router.push('/support/submit')"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        + New Ticket
      </button>
    </div>
    
    <!-- Filter -->
    <div class="mb-6">
      <select v-model="statusFilter" @change="loadTickets" class="p-2 border rounded">
        <option value="">All Statuses</option>
        <option value="pending">Pending</option>
        <option value="reviewing">Reviewing</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
        <option value="resolved">Resolved</option>
      </select>
    </div>
    
    <!-- Tickets List -->
    <div class="space-y-4">
      <div
        v-for="ticket in tickets"
        :key="ticket.id"
        class="border rounded p-4 hover:shadow-lg transition cursor-pointer"
        @click="viewTicket(ticket.id)"
      >
        <div class="flex justify-between items-start mb-2">
          <div>
            <h3 class="font-semibold text-lg">{{ ticket.title }}</h3>
            <div class="flex gap-2 mt-2">
              <span :class="getTypeClass(ticket.ticket_type)" class="px-2 py-1 rounded text-xs">
                {{ ticket.ticket_type }}
              </span>
              <span :class="getStatusClass(ticket.status)" class="px-2 py-1 rounded text-xs">
                {{ ticket.status }}
              </span>
              <span v-if="ticket.is_rewarded" class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                🎁 Rewarded: +{{ ticket.reward_slots }} slots
              </span>
            </div>
          </div>
          <span class="text-sm text-gray-500">
            {{ formatDate(ticket.created_at) }}
          </span>
        </div>
        
        <p class="text-gray-600 text-sm line-clamp-2">{{ ticket.description }}</p>
        
        <div v-if="ticket.admin_notes" class="mt-3 p-3 bg-gray-50 rounded">
          <p class="text-xs text-gray-500 mb-1">Admin Notes:</p>
          <p class="text-sm">{{ ticket.admin_notes }}</p>
        </div>
      </div>
      
      <div v-if="tickets.length === 0" class="text-center py-12 text-gray-500">
        No tickets found. Submit your first ticket!
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const tickets = ref([])
const statusFilter = ref('')

onMounted(() => {
  loadTickets()
})

async function loadTickets() {
  try {
    const params = statusFilter.value ? { status: statusFilter.value } : {}
    const response = await api.get('/api/tickets/my-tickets', { params })
    tickets.value = response.data
  } catch (error) {
    console.error('Error loading tickets:', error)
  }
}

function viewTicket(ticketId: string) {
  router.push(`/support/tickets/${ticketId}`)
}

function getTypeClass(type: string) {
  const classes = {
    feature: 'bg-purple-100 text-purple-800',
    bug: 'bg-red-100 text-red-800',
    issue: 'bg-blue-100 text-blue-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

function getStatusClass(status: string) {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    reviewing: 'bg-blue-100 text-blue-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    resolved: 'bg-gray-100 text-gray-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString()
}
</script>
```

### 3. Admin Panel - Ticket Management

**`frontend/src/views/Admin/TicketManagement.vue`:**

```vue
<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold mb-6">Ticket Management</h1>
    
    <!-- Filters -->
    <div class="flex gap-4 mb-6">
      <select v-model="filters.status" @change="loadTickets" class="p-2 border rounded">
        <option value="">All Statuses</option>
        <option value="pending">Pending</option>
        <option value="reviewing">Reviewing</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
      </select>
      
      <select v-model="filters.type" @change="loadTickets" class="p-2 border rounded">
        <option value="">All Types</option>
        <option value="feature">Features</option>
        <option value="bug">Bugs</option>
        <option value="issue">Issues</option>
      </select>
      
      <select v-model="filters.priority" @change="loadTickets" class="p-2 border rounded">
        <option value="">All Priorities</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
        <option value="critical">Critical</option>
      </select>
    </div>
    
    <!-- Tickets Table -->
    <div class="bg-white rounded shadow overflow-x-auto">
      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left">Title</th>
            <th class="px-4 py-3 text-left">Type</th>
            <th class="px-4 py-3 text-left">Status</th>
            <th class="px-4 py-3 text-left">Priority</th>
            <th class="px-4 py-3 text-left">User</th>
            <th class="px-4 py-3 text-left">Date</th>
            <th class="px-4 py-3 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ticket in tickets" :key="ticket.id" class="border-t hover:bg-gray-50">
            <td class="px-4 py-3">
              <div class="font-medium">{{ ticket.title }}</div>
              <div class="text-sm text-gray-500">{{ ticket.description.substring(0, 60) }}...</div>
            </td>
            <td class="px-4 py-3">
              <span :class="getTypeClass(ticket.ticket_type)" class="px-2 py-1 rounded text-xs">
                {{ ticket.ticket_type }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span :class="getStatusClass(ticket.status)" class="px-2 py-1 rounded text-xs">
                {{ ticket.status }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span :class="getPriorityClass(ticket.priority)" class="px-2 py-1 rounded text-xs">
                {{ ticket.priority }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm">{{ ticket.user_id }}</td>
            <td class="px-4 py-3 text-sm">{{ formatDate(ticket.created_at) }}</td>
            <td class="px-4 py-3">
              <button
                @click="openRewardModal(ticket)"
                :disabled="ticket.is_rewarded"
                class="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:bg-gray-300"
              >
                {{ ticket.is_rewarded ? `Rewarded (${ticket.reward_slots})` : 'Reward' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Reward Modal -->
    <div v-if="showRewardModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h2 class="text-xl font-bold mb-4">Reward Ticket</h2>
        
        <div class="mb-4">
          <p class="text-sm text-gray-600 mb-2">{{ selectedTicket?.title }}</p>
          <p class="text-xs text-gray-500">Type: {{ selectedTicket?.ticket_type }}</p>
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Reward Slots (1-15)</label>
          <input
            v-model.number="rewardForm.slots"
            type="number"
            min="1"
            max="15"
            class="w-full p-2 border rounded"
          />
          <p class="text-xs text-gray-500 mt-1">Default: 10 slots. Max: 15 slots.</p>
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Admin Notes</label>
          <textarea
            v-model="rewardForm.notes"
            rows="3"
            class="w-full p-2 border rounded"
            placeholder="Optional notes for the user..."
          ></textarea>
        </div>
        
        <div class="flex gap-3">
          <button
            @click="submitReward"
            class="flex-1 bg-green-600 text-white py-2 rounded hover:bg-green-700"
          >
            Confirm Reward
          </button>
          <button
            @click="closeRewardModal"
            class="flex-1 bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const tickets = ref([])
const filters = ref({
  status: '',
  type: '',
  priority: ''
})

const showRewardModal = ref(false)
const selectedTicket = ref(null)
const rewardForm = ref({
  slots: 10,
  notes: ''
})

onMounted(() => {
  loadTickets()
})

async function loadTickets() {
  try {
    const response = await api.get('/api/tickets/admin/all', { params: filters.value })
    tickets.value = response.data
  } catch (error) {
    console.error('Error loading tickets:', error)
  }
}

function openRewardModal(ticket: any) {
  selectedTicket.value = ticket
  rewardForm.value = {
    slots: 10,
    notes: ''
  }
  showRewardModal.value = true
}

function closeRewardModal() {
  showRewardModal.value = false
  selectedTicket.value = null
}

async function submitReward() {
  try {
    await api.post(`/api/tickets/admin/${selectedTicket.value.id}/reward`, {
      ticket_id: selectedTicket.value.id,
      reward_slots: rewardForm.value.slots,
      admin_notes: rewardForm.value.notes
    })
    
    alert(`Successfully rewarded ${rewardForm.value.slots} slots!`)
    closeRewardModal()
    loadTickets()
  } catch (error) {
    console.error('Error rewarding ticket:', error)
    alert('Failed to reward ticket')
  }
}

function getTypeClass(type: string) {
  const classes = {
    feature: 'bg-purple-100 text-purple-800',
    bug: 'bg-red-100 text-red-800',
    issue: 'bg-blue-100 text-blue-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

function getStatusClass(status: string) {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    reviewing: 'bg-blue-100 text-blue-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    resolved: 'bg-gray-100 text-gray-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

function getPriorityClass(priority: string) {
  const classes = {
    low: 'bg-gray-100 text-gray-800',
    medium: 'bg-blue-100 text-blue-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString()
}
</script>
```

---

## 🎯 Key Features Summary

### For Users:
✅ Submit feature suggestions, bug reports, or issues
✅ Attach screenshots (up to 5MB)
✅ Link tickets to specific family trees
✅ Track ticket status in real-time
✅ Get rewarded with person slots (1-15 slots)
✅ View reward history

### For Admin:
✅ View all tickets with filters (status, type, priority)
✅ Update ticket status and priority
✅ Add admin notes/comments
✅ Reward users with slots (1-15, adjustable)
✅ Auto-approve critical bugs or good features
✅ Track which tickets have been rewarded

### Reward Logic:
- Default: 10 slots for approved features or critical bugs
- Admin can adjust: 1-15 slots maximum
- Slots automatically added to user's family tree
- Activity log tracks all rewards
- Prevents duplicate rewards for same ticket

---

## 📱 Mobile Considerations

For mobile app (Capacitor), you can also:
- Use native camera to capture screenshots
- Native file picker for uploads
- Push notifications when ticket status changes

---

This feature will greatly enhance user engagement and help you improve the platform! 🎉
