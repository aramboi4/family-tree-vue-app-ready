from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ============================================
# ENUMS
# ============================================

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class FamilyRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class SubscriptionPlan(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

# Plan configurations
PLAN_LIMITS = {
    "free": 50,
    "basic": 200,
    "premium": 1000
}

PLAN_PRICES = {
    "free": 0,
    "basic": 499,  # PHP or your currency
    "premium": 999
}

# ============================================
# SUPPORT TICKET MODELS
# ============================================

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
    family_id: str
    ticket_type: TicketType
    title: str
    description: str
    screenshot_url: Optional[str] = None

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    reward_slots: Optional[int] = None
    admin_notes: Optional[str] = None

class TicketResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    family_id: str
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
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    
    class Config:
        populate_by_name = True

# ============================================
# USER MODELS
# ============================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: str
    full_name: str
    role: UserRole = UserRole.USER
    created_at: datetime
    
    class Config:
        populate_by_name = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ============================================
# FAMILY MODELS
# ============================================

class FamilyCreate(BaseModel):
    name: str
    description: Optional[str] = None

class FamilyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class FamilyResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: Optional[str] = None
    created_by: str
    created_at: datetime
    join_code: str
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE
    person_count: int = 0
    person_limit: int = 50
    
    class Config:
        populate_by_name = True

# ============================================
# PERSON MODELS
# ============================================

class PersonCreate(BaseModel):
    family_id: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    nickname: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    birth_place: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    facebook_url: Optional[str] = None
    is_deceased: bool = False
    photo_gallery: Optional[List[str]] = []
    father_id: Optional[str] = None  # Reference to father person
    mother_id: Optional[str] = None  # Reference to mother person
    spouse_ids: Optional[List[str]] = []  # List of spouse person IDs

class PersonUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    birth_place: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    facebook_url: Optional[str] = None
    is_deceased: Optional[bool] = None
    photo_gallery: Optional[List[str]] = None
    father_id: Optional[str] = None
    mother_id: Optional[str] = None
    spouse_ids: Optional[List[str]] = None

class PersonResponse(BaseModel):
    id: str = Field(alias="_id")
    family_id: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    nickname: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    birth_place: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    facebook_url: Optional[str] = None
    is_deceased: bool = False
    generation_level: int = 0
    photo_gallery: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

# ============================================
# MEMBER MANAGEMENT MODELS
# ============================================

class MemberInvite(BaseModel):
    family_id: str
    email: EmailStr
    role: FamilyRole

class MemberUpdate(BaseModel):
    role: FamilyRole

class MemberResponse(BaseModel):
    id: str = Field(alias="_id")
    family_id: str
    user_id: str
    role: FamilyRole
    joined_at: datetime
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    
    class Config:


# ============================================
# SUBSCRIPTION MODELS
# ============================================

class SubscriptionCreate(BaseModel):
    family_id: str
    plan: SubscriptionPlan
    payment_method: str  # "gcash", "maya", "instapay"
    payment_reference: str

class SubscriptionResponse(BaseModel):
    id: str = Field(alias="_id")
    family_id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool = False
    ticket_reward_slots: int = 0
    
    class Config:
        populate_by_name = True

class PlanUpgrade(BaseModel):
    new_plan: SubscriptionPlan
    payment_method: str
    payment_reference: str

        populate_by_name = True
