# 🔐 Role-Based Access Control (RBAC) Guide

## 📋 Overview

Complete role-based access control system for Family Tree application with strict permission rules.

---

## 👥 Role Definitions

### 🔴 Admin Role
**Maximum:** 5 admins per family tree  
**Minimum:** 1 admin per family tree (always required)

**Permissions:**
- ✅ **Full access to everything**
- ✅ Purchase/upgrade subscription plans
- ✅ Update family tree details
- ✅ Add/edit/delete persons
- ✅ Manage relationships
- ✅ Generate PDFs (all templates)
- ✅ Invite members with any role (admin, editor, viewer)
- ✅ Transfer admin role to other members
- ✅ Remove members (except last admin)
- ✅ Delete family tree
- ✅ View activity logs
- ✅ Manage subscriptions

**Constraints:**
- Cannot remove the last admin (minimum 1 required)
- Maximum 5 admins allowed per family tree
- Admin role is transferable

---

### 🟡 Editor Role
**No limit** on number of editors

**Permissions:**
- ✅ Update family tree details (name, description)
- ✅ Add new persons
- ✅ Edit person details
- ✅ Delete persons
- ✅ Manage relationships
- ✅ Generate PDFs (standard templates)
- ✅ Invite members with **Editor or Viewer role ONLY** (cannot invite admins)
- ✅ View activity logs

**Restrictions:**
- ❌ Cannot purchase/upgrade plans
- ❌ Cannot invite admin users
- ❌ Cannot delete family tree
- ❌ Cannot remove members
- ❌ Cannot access subscription settings
- ❌ Cannot transfer admin role

---

### 🟢 Viewer Role
**No limit** on number of viewers

**Permissions:**
- ✅ View family tree details
- ✅ View person details
- ✅ View relationships
- ✅ View tree visualization
- ✅ Search persons

**Restrictions:**
- ❌ Cannot update anything
- ❌ Cannot add/edit/delete persons
- ❌ Cannot generate PDFs
- ❌ Cannot invite anyone
- ❌ Cannot purchase plans
- ❌ Cannot access settings

---

## 🛒 Subscription Purchase Rules

### Who Can Purchase?
**ONLY Admin users** can purchase subscription plans.

### Purchase Flow:

1. **User must be admin of at least one family tree**
2. **When clicking "Purchase Plan":**
   - System shows dropdown to select family tree
   - **Only family trees where user is admin are shown**
   - User cannot select family trees where they are editor/viewer
3. **User selects family tree** from dropdown
4. **User selects plan and payment method**
5. **Payment is processed**
6. **Subscription is applied to the selected family tree**

### Example Scenarios:

**Scenario 1:**
- User A is admin of "Smith Family" and "Johnson Family"
- User A clicks "Purchase Plan"
- Dropdown shows: "Smith Family", "Johnson Family"
- User A selects "Smith Family" and purchases Standard plan
- Only "Smith Family" gets upgraded to Standard plan

**Scenario 2:**
- User B is editor of "Brown Family" and admin of "Davis Family"
- User B clicks "Purchase Plan"
- Dropdown shows: "Davis Family" ONLY (not "Brown Family")
- User B can only purchase for "Davis Family"

**Scenario 3:**
- User C is viewer of "Miller Family" and editor of "Wilson Family"
- User C does not see "Purchase Plan" button at all
- No admin access = no purchase option

---

## 🔄 Admin Role Management

### Admin Role Transfer

**Who can transfer admin role?**
- Only existing admins

**Process:**
1. Admin goes to Family Settings → Members
2. Clicks on a member (editor or viewer)
3. Selects "Promote to Admin"
4. System checks if admin limit (5) is reached
5. If not reached, member becomes admin
6. Original admin can then demote themselves if desired

**Constraints:**
- Cannot demote last admin (minimum 1 always required)
- Maximum 5 admins per family tree
- Can only promote existing members (must already be in family)

### Removing Last Admin Protection

```javascript
// Example: Trying to remove last admin
if (family.admins.length === 1 && removingUser.role === 'admin') {
  throw Error("Cannot remove the last admin. Transfer admin role first.");
}
```

---

## 📊 Database Schema Updates

### Family Members Table with Constraints

```sql
-- Update Family Members Table
ALTER TABLE family_members
ADD CONSTRAINT check_admin_count 
CHECK (
  -- Ensure at least 1 admin exists
  (SELECT COUNT(*) FROM family_members 
   WHERE family_id = family_members.family_id 
   AND role = 'admin') >= 1
);

-- Admin Role Limits Table
CREATE TABLE family_admin_limits (
    family_id VARCHAR(36) PRIMARY KEY,
    admin_count INT DEFAULT 0,
    max_admins INT DEFAULT 5,
    min_admins INT DEFAULT 1,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    CONSTRAINT check_admin_limits CHECK (admin_count <= max_admins AND admin_count >= min_admins)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Trigger to update admin count
DELIMITER //
CREATE TRIGGER update_admin_count_insert
AFTER INSERT ON family_members
FOR EACH ROW
BEGIN
    IF NEW.role = 'admin' THEN
        INSERT INTO family_admin_limits (family_id, admin_count)
        VALUES (NEW.family_id, 1)
        ON DUPLICATE KEY UPDATE admin_count = admin_count + 1;
    END IF;
END//

CREATE TRIGGER update_admin_count_update
AFTER UPDATE ON family_members
FOR EACH ROW
BEGIN
    IF NEW.role = 'admin' AND OLD.role != 'admin' THEN
        INSERT INTO family_admin_limits (family_id, admin_count)
        VALUES (NEW.family_id, 1)
        ON DUPLICATE KEY UPDATE admin_count = admin_count + 1;
    ELSEIF OLD.role = 'admin' AND NEW.role != 'admin' THEN
        UPDATE family_admin_limits 
        SET admin_count = admin_count - 1
        WHERE family_id = NEW.family_id;
    END IF;
END//

CREATE TRIGGER update_admin_count_delete
AFTER DELETE ON family_members
FOR EACH ROW
BEGIN
    IF OLD.role = 'admin' THEN
        UPDATE family_admin_limits 
        SET admin_count = admin_count - 1
        WHERE family_id = OLD.family_id;
    END IF;
END//
DELIMITER ;
```

---

## 🔧 Backend Implementation

### 1. Permission Middleware

**`backend/app/middleware/permissions.py`:**

```python
from fastapi import HTTPException, Depends, status
from typing import Callable
from app.database import get_db
from app.utils.auth import get_current_user

class FamilyPermissions:
    """Check user permissions for family operations"""
    
    @staticmethod
    async def is_admin(family_id: str, user_id: str, db) -> bool:
        member = await db.family_members.find_one({
            "family_id": family_id,
            "user_id": user_id,
            "role": "admin"
        })
        return member is not None
    
    @staticmethod
    async def is_editor_or_above(family_id: str, user_id: str, db) -> bool:
        member = await db.family_members.find_one({
            "family_id": family_id,
            "user_id": user_id,
            "role": {"$in": ["admin", "editor"]}
        })
        return member is not None
    
    @staticmethod
    async def is_member(family_id: str, user_id: str, db) -> bool:
        member = await db.family_members.find_one({
            "family_id": family_id,
            "user_id": user_id
        })
        return member is not None
    
    @staticmethod
    async def can_invite_role(family_id: str, user_id: str, target_role: str, db) -> bool:
        """Check if user can invite someone with target_role"""
        member = await db.family_members.find_one({
            "family_id": family_id,
            "user_id": user_id
        })
        
        if not member:
            return False
        
        user_role = member["role"]
        
        # Viewers cannot invite
        if user_role == "viewer":
            return False
        
        # Editors can only invite editors or viewers
        if user_role == "editor" and target_role == "admin":
            return False
        
        # Admins can invite anyone
        return True
    
    @staticmethod
    async def get_admin_count(family_id: str, db) -> int:
        """Get current admin count for family"""
        count = await db.family_members.count_documents({
            "family_id": family_id,
            "role": "admin"
        })
        return count
    
    @staticmethod
    async def can_add_admin(family_id: str, db) -> bool:
        """Check if family can have more admins (max 5)"""
        count = await FamilyPermissions.get_admin_count(family_id, db)
        return count < 5
    
    @staticmethod
    async def can_remove_admin(family_id: str, db) -> bool:
        """Check if admin can be removed (must have at least 1)"""
        count = await FamilyPermissions.get_admin_count(family_id, db)
        return count > 1

# Dependency functions
def require_admin(family_id: str):
    """Require admin role for the family"""
    async def check_admin(
        current_user: dict = Depends(get_current_user),
        db = Depends(get_db)
    ):
        if not await FamilyPermissions.is_admin(family_id, current_user["id"], db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required"
            )
        return current_user
    return check_admin

def require_editor_or_above(family_id: str):
    """Require editor or admin role"""
    async def check_editor(
        current_user: dict = Depends(get_current_user),
        db = Depends(get_db)
    ):
        if not await FamilyPermissions.is_editor_or_above(family_id, current_user["id"], db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Editor or Admin role required"
            )
        return current_user
    return check_editor

def require_member(family_id: str):
    """Require any membership (viewer, editor, or admin)"""
    async def check_member(
        current_user: dict = Depends(get_current_user),
        db = Depends(get_db)
    ):
        if not await FamilyPermissions.is_member(family_id, current_user["id"], db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Family membership required"
            )
        return current_user
    return check_member
```

### 2. Update Payment Routes

**`backend/app/routes/payments.py` (Update):**

```python
@router.get("/user/admin-families")
async def get_user_admin_families(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get all families where current user is admin
    Used for purchase plan dropdown
    """
    # Find all family memberships where user is admin
    admin_memberships = await db.family_members.find({
        "user_id": current_user["id"],
        "role": "admin"
    }).to_list(100)
    
    family_ids = [m["family_id"] for m in admin_memberships]
    
    # Get family details
    families = await db.families.find({
        "_id": {"$in": family_ids}
    }).to_list(100)
    
    # Add current subscription info
    result = []
    for family in families:
        subscription = await db.family_subscriptions.find_one({
            "family_id": family["_id"]
        }) or {
            "plan": "free",
            "person_limit": 50
        }
        
        result.append({
            "id": family["_id"],
            "name": family["name"],
            "current_plan": subscription.get("plan", "free"),
            "person_count": family.get("person_count", 0),
            "person_limit": subscription.get("person_limit", 50)
        })
    
    return result

@router.post("/family/{family_id}/subscribe")
async def create_subscription_payment(
    family_id: str,
    payment_request: CreatePaymentRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create a payment for family subscription
    ONLY ADMINS can purchase subscriptions
    """
    # Check if user is admin of this family
    is_admin = await FamilyPermissions.is_admin(family_id, current_user["id"], db)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family admins can purchase subscription plans"
        )
    
    # ... rest of payment logic
```

### 3. Role Management Routes

**`backend/app/routes/roles.py`:**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.permissions import FamilyPermissions, require_admin, require_editor_or_above
from app.database import get_db
from app.utils.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

class UpdateRoleRequest(BaseModel):
    user_id: str
    new_role: str  # 'admin', 'editor', 'viewer'

class InviteMemberRequest(BaseModel):
    email: str
    role: str

@router.get("/family/{family_id}/members")
async def get_family_members(
    family_id: str,
    current_user: dict = Depends(require_member(family_id)),
    db = Depends(get_db)
):
    """Get all members of a family"""
    members = await db.family_members.find({
        "family_id": family_id
    }).to_list(100)
    
    # Get user details
    user_ids = [m["user_id"] for m in members]
    users = await db.users.find({
        "_id": {"$in": user_ids}
    }).to_list(100)
    
    # Combine data
    user_map = {u["_id"]: u for u in users}
    result = []
    for member in members:
        user = user_map.get(member["user_id"], {})
        result.append({
            "user_id": member["user_id"],
            "email": user.get("email", ""),
            "full_name": user.get("full_name", ""),
            "role": member["role"],
            "joined_at": member["joined_at"]
        })
    
    return result

@router.put("/family/{family_id}/members/role")
async def update_member_role(
    family_id: str,
    role_request: UpdateRoleRequest,
    current_user: dict = Depends(require_admin(family_id)),
    db = Depends(get_db)
):
    """
    Update a member's role (Admin only)
    
    Rules:
    - Only admins can change roles
    - Cannot demote last admin
    - Maximum 5 admins per family
    """
    target_user_id = role_request.user_id
    new_role = role_request.new_role
    
    if new_role not in ["admin", "editor", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Get current member info
    member = await db.family_members.find_one({
        "family_id": family_id,
        "user_id": target_user_id
    })
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    current_role = member["role"]
    
    # Check if trying to demote last admin
    if current_role == "admin" and new_role != "admin":
        if not await FamilyPermissions.can_remove_admin(family_id, db):
            raise HTTPException(
                status_code=400,
                detail="Cannot demote the last admin. Promote another user to admin first."
            )
    
    # Check if promoting to admin exceeds limit
    if new_role == "admin" and current_role != "admin":
        if not await FamilyPermissions.can_add_admin(family_id, db):
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 admins allowed per family tree"
            )
    
    # Update role
    await db.family_members.update_one(
        {"family_id": family_id, "user_id": target_user_id},
        {"$set": {"role": new_role}}
    )
    
    # Log activity
    await db.activity_log.insert_one({
        "_id": str(uuid.uuid4()),
        "family_id": family_id,
        "user_id": current_user["id"],
        "action": "role_updated",
        "details": f"Changed {member.get('email', target_user_id)} role from {current_role} to {new_role}",
        "created_at": datetime.utcnow()
    })
    
    return {"message": "Role updated successfully", "new_role": new_role}

@router.post("/family/{family_id}/invite")
async def invite_member(
    family_id: str,
    invite_request: InviteMemberRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Invite a member to family
    
    Rules:
    - Admins can invite anyone (admin, editor, viewer)
    - Editors can only invite editors or viewers
    - Viewers cannot invite
    - Max 5 admins per family
    """
    # Check if user can invite with the specified role
    can_invite = await FamilyPermissions.can_invite_role(
        family_id, 
        current_user["id"], 
        invite_request.role,
        db
    )
    
    if not can_invite:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to invite users with this role"
        )
    
    # Check admin limit if inviting admin
    if invite_request.role == "admin":
        if not await FamilyPermissions.can_add_admin(family_id, db):
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 admins allowed per family tree"
            )
    
    # Create invitation
    invitation = {
        "_id": str(uuid.uuid4()),
        "family_id": family_id,
        "email": invite_request.email,
        "role": invite_request.role,
        "token": str(uuid.uuid4()),
        "invited_by": current_user["id"],
        "invited_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=7),
        "accepted": False
    }
    
    await db.invitations.insert_one(invitation)
    
    # Send invitation email (implement email service)
    # send_invitation_email(invite_request.email, invitation["token"])
    
    return {
        "message": "Invitation sent successfully",
        "invitation_id": invitation["_id"]
    }

@router.delete("/family/{family_id}/members/{user_id}")
async def remove_member(
    family_id: str,
    user_id: str,
    current_user: dict = Depends(require_admin(family_id)),
    db = Depends(get_db)
):
    """
    Remove a member from family (Admin only)
    Cannot remove last admin
    """
    member = await db.family_members.find_one({
        "family_id": family_id,
        "user_id": user_id
    })
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check if trying to remove last admin
    if member["role"] == "admin":
        if not await FamilyPermissions.can_remove_admin(family_id, db):
            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last admin"
            )
    
    # Remove member
    await db.family_members.delete_one({
        "family_id": family_id,
        "user_id": user_id
    })
    
    # Log activity
    await db.activity_log.insert_one({
        "_id": str(uuid.uuid4()),
        "family_id": family_id,
        "user_id": current_user["id"],
        "action": "member_removed",
        "details": f"Removed user {user_id} from family",
        "created_at": datetime.utcnow()
    })
    
    return {"message": "Member removed successfully"}
```

---

## 🎨 Frontend Implementation

### 1. Family Selector for Purchase

**`frontend/src/components/subscription/FamilySelector.vue`:**

```vue
<template>
  <div>
    <label class="block text-sm font-medium mb-2">
      Select Family Tree to Upgrade
    </label>
    <select
      v-model="selectedFamily"
      @change="$emit('update:modelValue', selectedFamily)"
      class="w-full p-3 border rounded-lg"
      required
    >
      <option value="">-- Select a family tree --</option>
      <option
        v-for="family in adminFamilies"
        :key="family.id"
        :value="family.id"
      >
        {{ family.name }} 
        ({{ family.current_plan }} - {{ family.person_count }}/{{ family.person_limit }} persons)
      </option>
    </select>
    
    <p v-if="adminFamilies.length === 0" class="text-sm text-red-600 mt-2">
      You must be an admin of at least one family tree to purchase a plan.
    </p>
    
    <p class="text-xs text-gray-500 mt-2">
      Only family trees where you are an admin are shown.
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const emit = defineEmits(['update:modelValue'])

const adminFamilies = ref([])
const selectedFamily = ref('')

onMounted(async () => {
  await loadAdminFamilies()
})

async function loadAdminFamilies() {
  try {
    const response = await api.get('/api/payments/user/admin-families')
    adminFamilies.value = response.data
  } catch (error) {
    console.error('Error loading admin families:', error)
  }
}
</script>
```

### 2. Role Management Component

**`frontend/src/components/family/MemberManagement.vue`:**

```vue
<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">Family Members</h2>
      <button
        v-if="canInvite"
        @click="showInviteModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        + Invite Member
      </button>
    </div>
    
    <!-- Admin Count Warning -->
    <div v-if="adminCount >= 5" class="bg-yellow-50 border border-yellow-200 rounded p-4 mb-4">
      <p class="text-sm text-yellow-800">
        ⚠️ Maximum admin limit reached (5/5). Remove an admin to add another.
      </p>
    </div>
    
    <!-- Members List -->
    <div class="space-y-4">
      <div
        v-for="member in members"
        :key="member.user_id"
        class="flex justify-between items-center p-4 border rounded-lg"
      >
        <div>
          <p class="font-semibold">{{ member.full_name }}</p>
          <p class="text-sm text-gray-600">{{ member.email }}</p>
          <div class="flex items-center gap-2 mt-2">
            <span :class="getRoleBadgeClass(member.role)" class="px-2 py-1 rounded text-xs font-semibold">
              {{ member.role.toUpperCase() }}
            </span>
            <span class="text-xs text-gray-500">
              Joined {{ formatDate(member.joined_at) }}
            </span>
          </div>
        </div>
        
        <!-- Role Actions (Admin only) -->
        <div v-if="userRole === 'admin' && member.user_id !== currentUserId" class="flex gap-2">
          <!-- Promote to Admin -->
          <button
            v-if="member.role !== 'admin' && adminCount < 5"
            @click="changeRole(member.user_id, 'admin')"
            class="px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200"
            title="Promote to Admin"
          >
            Make Admin
          </button>
          
          <!-- Change to Editor -->
          <button
            v-if="member.role !== 'editor'"
            @click="changeRole(member.user_id, 'editor')"
            class="px-3 py-1 bg-yellow-100 text-yellow-700 rounded text-sm hover:bg-yellow-200"
            title="Change to Editor"
          >
            Make Editor
          </button>
          
          <!-- Change to Viewer -->
          <button
            v-if="member.role !== 'viewer'"
            @click="changeRole(member.user_id, 'viewer')"
            class="px-3 py-1 bg-green-100 text-green-700 rounded text-sm hover:bg-green-200"
            :disabled="member.role === 'admin' && adminCount === 1"
            title="Change to Viewer"
          >
            Make Viewer
          </button>
          
          <!-- Remove Member -->
          <button
            @click="removeMember(member.user_id)"
            :disabled="member.role === 'admin' && adminCount === 1"
            class="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 disabled:bg-gray-300"
            title="Remove Member"
          >
            Remove
          </button>
        </div>
        
        <!-- Last Admin Notice -->
        <div v-if="member.role === 'admin' && adminCount === 1" class="text-xs text-gray-500">
          (Last admin - cannot be removed)
        </div>
      </div>
    </div>
    
    <!-- Invite Modal -->
    <InviteModal
      v-if="showInviteModal"
      :family-id="familyId"
      :user-role="userRole"
      :admin-count="adminCount"
      @close="showInviteModal = false"
      @success="loadMembers"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import InviteModal from './InviteModal.vue'

const props = defineProps<{
  familyId: string
}>()

const members = ref([])
const userRole = ref('viewer')
const currentUserId = ref('')
const showInviteModal = ref(false)

const adminCount = computed(() => {
  return members.value.filter(m => m.role === 'admin').length
})

const canInvite = computed(() => {
  return userRole.value === 'admin' || userRole.value === 'editor'
})

onMounted(async () => {
  await loadMembers()
})

async function loadMembers() {
  try {
    const response = await api.get(`/api/roles/family/${props.familyId}/members`)
    members.value = response.data
    
    // Get current user's role
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
    currentUserId.value = currentUser.id
    const myMembership = members.value.find(m => m.user_id === currentUser.id)
    if (myMembership) {
      userRole.value = myMembership.role
    }
  } catch (error) {
    console.error('Error loading members:', error)
  }
}

async function changeRole(userId: string, newRole: string) {
  const member = members.value.find(m => m.user_id === userId)
  
  // Confirm if demoting last admin
  if (member.role === 'admin' && adminCount.value === 1) {
    alert('Cannot change role of the last admin')
    return
  }
  
  // Confirm if promoting to admin at limit
  if (newRole === 'admin' && adminCount.value >= 5) {
    alert('Maximum 5 admins allowed per family tree')
    return
  }
  
  if (!confirm(`Change ${member.full_name}'s role to ${newRole}?`)) {
    return
  }
  
  try {
    await api.put(`/api/roles/family/${props.familyId}/members/role`, {
      user_id: userId,
      new_role: newRole
    })
    await loadMembers()
  } catch (error) {
    console.error('Error changing role:', error)
    alert(error.response?.data?.detail || 'Failed to change role')
  }
}

async function removeMember(userId: string) {
  const member = members.value.find(m => m.user_id === userId)
  
  if (member.role === 'admin' && adminCount.value === 1) {
    alert('Cannot remove the last admin')
    return
  }
  
  if (!confirm(`Remove ${member.full_name} from this family?`)) {
    return
  }
  
  try {
    await api.delete(`/api/roles/family/${props.familyId}/members/${userId}`)
    await loadMembers()
  } catch (error) {
    console.error('Error removing member:', error)
    alert(error.response?.data?.detail || 'Failed to remove member')
  }
}

function getRoleBadgeClass(role: string) {
  const classes = {
    admin: 'bg-red-100 text-red-800',
    editor: 'bg-yellow-100 text-yellow-800',
    viewer: 'bg-green-100 text-green-800'
  }
  return classes[role] || 'bg-gray-100 text-gray-800'
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString()
}
</script>
```

### 3. Invite Modal with Role Restrictions

**`frontend/src/components/family/InviteModal.vue`:**

```vue
<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full">
      <h2 class="text-xl font-bold mb-4">Invite Member</h2>
      
      <form @submit.prevent="sendInvite">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Email Address</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full p-2 border rounded"
            placeholder="user@example.com"
          />
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Role</label>
          <select v-model="form.role" required class="w-full p-2 border rounded">
            <option value="">Select role...</option>
            <option 
              v-if="userRole === 'admin' && adminCount < 5" 
              value="admin"
            >
              Admin (Full access)
            </option>
            <option value="editor">Editor (Can edit and add)</option>
            <option value="viewer">Viewer (View only)</option>
          </select>
          
          <!-- Role Restrictions Info -->
          <div class="mt-2 text-xs text-gray-600">
            <p v-if="userRole === 'editor'">
              ℹ️ As an editor, you can only invite editors or viewers.
            </p>
            <p v-if="adminCount >= 5">
              ⚠️ Admin limit reached (5/5). Cannot invite more admins.
            </p>
          </div>
        </div>
        
        <!-- Role Permissions Info -->
        <div v-if="form.role" class="mb-4 p-3 bg-blue-50 rounded text-sm">
          <p class="font-semibold mb-1">{{ getRoleLabel(form.role) }} can:</p>
          <ul class="list-disc ml-5 space-y-1">
            <li v-for="perm in getRolePermissions(form.role)" :key="perm">{{ perm }}</li>
          </ul>
        </div>
        
        <div class="flex gap-3">
          <button
            type="button"
            @click="$emit('close')"
            class="flex-1 px-4 py-2 border rounded hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {{ loading ? 'Sending...' : 'Send Invite' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/services/api'

const props = defineProps<{
  familyId: string
  userRole: string
  adminCount: number
}>()

const emit = defineEmits(['close', 'success'])

const form = ref({
  email: '',
  role: ''
})
const loading = ref(false)

async function sendInvite() {
  loading.value = true
  
  try {
    await api.post(`/api/roles/family/${props.familyId}/invite`, {
      email: form.value.email,
      role: form.value.role
    })
    
    alert('Invitation sent successfully!')
    emit('success')
    emit('close')
  } catch (error) {
    console.error('Error sending invite:', error)
    alert(error.response?.data?.detail || 'Failed to send invitation')
  } finally {
    loading.value = false
  }
}

function getRoleLabel(role: string) {
  const labels = {
    admin: 'Admins',
    editor: 'Editors',
    viewer: 'Viewers'
  }
  return labels[role] || role
}

function getRolePermissions(role: string) {
  const permissions = {
    admin: [
      'Full access to everything',
      'Purchase subscription plans',
      'Invite members (any role)',
      'Manage all settings',
      'Delete family tree'
    ],
    editor: [
      'Update family tree details',
      'Add and edit persons',
      'Generate PDFs',
      'Invite editors and viewers'
    ],
    viewer: [
      'View family tree',
      'View person details',
      'View relationships'
    ]
  }
  return permissions[role] || []
}
</script>
```

---

## 📋 Permission Matrix

| Feature | Admin | Editor | Viewer |
|---------|-------|--------|--------|
| **View family tree** | ✅ | ✅ | ✅ |
| **View persons** | ✅ | ✅ | ✅ |
| **Add persons** | ✅ | ✅ | ❌ |
| **Edit persons** | ✅ | ✅ | ❌ |
| **Delete persons** | ✅ | ✅ | ❌ |
| **Update family details** | ✅ | ✅ | ❌ |
| **Generate PDF** | ✅ | ✅ | ❌ |
| **Purchase plan** | ✅ | ❌ | ❌ |
| **Invite admin** | ✅ | ❌ | ❌ |
| **Invite editor** | ✅ | ✅ | ❌ |
| **Invite viewer** | ✅ | ✅ | ❌ |
| **Change roles** | ✅ | ❌ | ❌ |
| **Remove members** | ✅ | ❌ | ❌ |
| **Delete family** | ✅ | ❌ | ❌ |
| **Transfer admin** | ✅ | ❌ | ❌ |

---

## ✅ Implementation Checklist

- [ ] Update database with admin limits table
- [ ] Create permission middleware
- [ ] Update payment routes (admin-only)
- [ ] Create role management routes
- [ ] Add family selector for purchases
- [ ] Create member management UI
- [ ] Add role change functionality
- [ ] Implement invite modal with restrictions
- [ ] Add last admin protection
- [ ] Test admin limit (5 max)
- [ ] Test editor invite restrictions
- [ ] Test viewer no-invite rule

---

## 🎯 Key Rules Summary

1. **Admin Purchase Only**: Only admins can buy plans
2. **Family Selection**: Must select which family tree to upgrade
3. **1-5 Admins**: Minimum 1, maximum 5 admins per family
4. **Editor Limits**: Can only invite editor/viewer (not admin)
5. **Viewer Limits**: Cannot invite anyone
6. **Last Admin Protection**: Cannot remove/demote last admin
7. **Role Transfer**: Admins can transfer role to others

---

**Your Family Tree app now has complete role-based access control! 🔐**
