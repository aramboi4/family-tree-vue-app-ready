"""
Family Tree FastAPI Backend
Main application entry point
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime, timezone
from bson import ObjectId
import secrets
import os
import uuid

from config import settings
from database import connect_db, disconnect_db, get_db
from models import *
from rbac import (
    check_family_membership,
    check_admin_role,
    check_admin_or_editor_role,
    can_invite_role,
    check_admin_limit,
    check_can_remove_admin,
    validate_admin_addition,
    Permissions,
    get_user_role_in_family
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    check_brute_force,
    record_failed_login,
    clear_failed_login
)

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Family Tree API",
    description="Family Tree SaaS Application API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ============================================
# CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", settings.FRONTEND_URL)],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# STARTUP & SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB and seed admin"""
    await connect_db()
    await seed_admin()
    await write_test_credentials()

@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from MongoDB"""
    await disconnect_db()

# ============================================
# ADMIN SEEDING
# ============================================

async def seed_admin():
    """Seed admin user if not exists"""
    db = get_db()
    admin_email = os.environ.get("ADMIN_EMAIL", settings.ADMIN_EMAIL)
    admin_password = os.environ.get("ADMIN_PASSWORD", settings.ADMIN_PASSWORD)
    
    existing = await db.users.find_one({"email": admin_email})
    
    if existing is None:
        hashed = hash_password(admin_password)
        await db.users.insert_one({
            "_id": ObjectId(),
            "email": admin_email,
            "password_hash": hashed,
            "full_name": "Admin User",
            "role": UserRole.ADMIN,
            "created_at": datetime.now(timezone.utc)
        })
        print(f"✅ Admin user created: {admin_email}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": hash_password(admin_password)}}
        )
        print(f"✅ Admin password updated: {admin_email}")

async def write_test_credentials():
    """Write test credentials to memory file"""
    admin_email = os.environ.get("ADMIN_EMAIL", settings.ADMIN_EMAIL)
    admin_password = os.environ.get("ADMIN_PASSWORD", settings.ADMIN_PASSWORD)
    
    credentials_content = f"""# Test Credentials

## Admin Account
- Email: {admin_email}
- Password: {admin_password}
- Role: admin

## Auth Endpoints
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me
- POST /api/auth/refresh
- POST /api/auth/forgot-password
- POST /api/auth/reset-password

## Family Endpoints
- GET /api/families
- POST /api/families
- GET /api/families/{{family_id}}
- PUT /api/families/{{family_id}}
- DELETE /api/families/{{family_id}}

## Person Endpoints
- GET /api/families/{{family_id}}/persons
- POST /api/persons
- GET /api/persons/{{person_id}}
- PUT /api/persons/{{person_id}}
- DELETE /api/persons/{{person_id}}
"""
    
    os.makedirs("/app/memory", exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write(credentials_content)
    
    print("✅ Test credentials written to /app/memory/test_credentials.md")

# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Family Tree API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "family-tree-api"}

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, response: Response):
    """Register a new user"""
    db = get_db()
    
    # Normalize email
    email = user_data.email.lower()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = ObjectId()
    hashed_password = hash_password(user_data.password)
    
    new_user = {
        "_id": user_id,
        "email": email,
        "full_name": user_data.full_name,
        "password_hash": hashed_password,
        "role": UserRole.USER,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(new_user)
    
    # Create tokens
    access_token = create_access_token(str(user_id), email)
    refresh_token = create_refresh_token(str(user_id))
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800,
        path="/"
    )
    
    return {
        "_id": str(user_id),
        "email": email,
        "full_name": user_data.full_name,
        "role": UserRole.USER,
        "created_at": new_user["created_at"]
    }

@app.post("/api/auth/login")
async def login(user_data: UserLogin, request: Request, response: Response):
    """Login and get access token"""
    db = get_db()
    
    # Normalize email
    email = user_data.email.lower()
    
    # Check brute force
    client_ip = request.client.host
    identifier = f"{client_ip}:{email}"
    
    if await check_brute_force(identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again in 15 minutes."
        )
    
    # Get user from database
    user = await db.users.find_one({"email": email})
    
    if not user or not verify_password(user_data.password, user["password_hash"]):
        await record_failed_login(identifier)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Clear failed attempts
    await clear_failed_login(identifier)
    
    # Create tokens
    user_id = str(user["_id"])
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800,
        path="/"
    )
    
    return {
        "_id": user_id,
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "created_at": user["created_at"]
    }

@app.post("/api/auth/logout")
async def logout(response: Response):
    """Logout and clear cookies"""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me")
async def get_me(request: Request, current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/api/auth/refresh")
async def refresh_token(request: Request, response: Response):
    """Refresh access token"""
    import jwt
    from auth import get_jwt_secret
    
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    try:
        payload = jwt.decode(refresh_token, get_jwt_secret(), algorithms=[settings.JWT_ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Get user
        db = get_db()
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Create new access token
        access_token = create_access_token(str(user["_id"]), user["email"])
        
        # Set new cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=900,
            path="/"
        )
        
        return {"message": "Token refreshed"}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.post("/api/auth/forgot-password")
async def forgot_password(email: EmailStr):
    """Request password reset"""
    db = get_db()
    
    # Normalize email
    email = email.lower()
    
    user = await db.users.find_one({"email": email})
    if not user:
        # Don't reveal if user exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    await db.password_reset_tokens.insert_one({
        "token": reset_token,
        "user_id": user["_id"],
        "expires_at": expires_at,
        "used": False
    })
    
    # In production, send email here
    # For now, just log it
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
    print(f"🔗 Password reset link: {reset_link}")
    
    return {"message": "If the email exists, a reset link has been sent"}

@app.post("/api/auth/reset-password")
async def reset_password(token: str, new_password: str):
    """Reset password using token"""
    db = get_db()
    
    # Find token
    reset_token = await db.password_reset_tokens.find_one({"token": token, "used": False})
    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Check expiration
    if datetime.now(timezone.utc) > reset_token["expires_at"]:
        raise HTTPException(status_code=400, detail="Token has expired")
    
    # Update password
    hashed_password = hash_password(new_password)
    await db.users.update_one(
        {"_id": reset_token["user_id"]},
        {"$set": {"password_hash": hashed_password}}
    )
    
    # Mark token as used
    await db.password_reset_tokens.update_one(
        {"token": token},
        {"$set": {"used": True}}
    )
    
    return {"message": "Password reset successful"}

# ============================================
# FAMILY ENDPOINTS
# ============================================

@app.get("/api/families")
async def list_families(current_user: dict = Depends(get_current_user)):
    """List all families the user is a member of"""
    db = get_db()
    
    # Find all family memberships
    memberships = await db.family_members.find({"user_id": current_user["_id"]}).to_list(100)
    family_ids = [m["family_id"] for m in memberships]
    
    # Get families
    families = await db.families.find({"_id": {"$in": family_ids}}).to_list(100)
    
    result = []
    for family in families:
        result.append({
            "_id": str(family["_id"]),
            "name": family["name"],
            "description": family.get("description"),
            "created_by": str(family["created_by"]),
            "created_at": family["created_at"],
            "join_code": family["join_code"],
            "subscription_plan": family.get("subscription_plan", "free"),
            "person_count": family.get("person_count", 0),
            "person_limit": family.get("person_limit", 50)
        })
    
    return result

@app.post("/api/families", status_code=status.HTTP_201_CREATED)
async def create_family(family_data: FamilyCreate, current_user: dict = Depends(get_current_user)):
    """Create a new family tree"""
    db = get_db()
    
    family_id = ObjectId()
    join_code = str(uuid.uuid4())[:8].upper()
    
    # Create family
    new_family = {
        "_id": family_id,
        "name": family_data.name,
        "description": family_data.description,
        "created_by": ObjectId(current_user["_id"]),
        "created_at": datetime.now(timezone.utc),
        "join_code": join_code,
        "subscription_plan": SubscriptionPlan.FREE,
        "person_count": 0,
        "person_limit": 50
    }
    
    await db.families.insert_one(new_family)
    
    # Add creator as admin member
    await db.family_members.insert_one({
        "_id": ObjectId(),
        "family_id": family_id,
        "user_id": ObjectId(current_user["_id"]),
        "role": FamilyRole.ADMIN,
        "joined_at": datetime.now(timezone.utc)
    })
    
    return {
        "_id": str(family_id),
        "name": new_family["name"],
        "description": new_family["description"],
        "created_by": str(new_family["created_by"]),
        "created_at": new_family["created_at"],
        "join_code": join_code,
        "subscription_plan": SubscriptionPlan.FREE,
        "person_count": 0,
        "person_limit": 50
    }

@app.get("/api/families/{family_id}")
async def get_family(family_id: str, current_user: dict = Depends(get_current_user)):
    """Get family details"""
    db = get_db()
    
    # Check if user is a member
    member = await db.family_members.find_one({
        "family_id": ObjectId(family_id),
        "user_id": ObjectId(current_user["_id"])
    })
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this family"
        )
    
    family = await db.families.find_one({"_id": ObjectId(family_id)})
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found"
        )
    
    return {
        "_id": str(family["_id"]),
        "name": family["name"],
        "description": family.get("description"),
        "created_by": str(family["created_by"]),
        "created_at": family["created_at"],
        "join_code": family["join_code"],
        "subscription_plan": family.get("subscription_plan", "free"),
        "person_count": family.get("person_count", 0),
        "person_limit": family.get("person_limit", 50),
        "user_role": member["role"]
    }

@app.put("/api/families/{family_id}")
async def update_family(
    family_id: str,
    family_data: FamilyUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update family details (admin or editor only)"""
    db = get_db()
    
    # Check if user is admin or editor
    member = await db.family_members.find_one({
        "family_id": ObjectId(family_id),
        "user_id": ObjectId(current_user["_id"])
    })
    
    if not member or member["role"] not in [FamilyRole.ADMIN, FamilyRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or editor role required"
        )
    
    # Update family
    update_fields = {}
    if family_data.name:
        update_fields["name"] = family_data.name
    if family_data.description is not None:
        update_fields["description"] = family_data.description
    
    if update_fields:
        await db.families.update_one(
            {"_id": ObjectId(family_id)},
            {"$set": update_fields}
        )
    
    return await get_family(family_id, current_user)

@app.delete("/api/families/{family_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_family(family_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a family tree (admin only)"""
    db = get_db()
    
    # Check if user is admin
    member = await db.family_members.find_one({
        "family_id": ObjectId(family_id),
        "user_id": ObjectId(current_user["_id"])
    })
    
    if not member or member["role"] != FamilyRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    
    # Delete family and related data
    await db.families.delete_one({"_id": ObjectId(family_id)})
    await db.family_members.delete_many({"family_id": ObjectId(family_id)})
    await db.persons.delete_many({"family_id": ObjectId(family_id)})
    
    return None

# ============================================


# ============================================
# MEMBER MANAGEMENT ENDPOINTS
# ============================================

@app.get("/api/families/{family_id}/members")
async def list_family_members(family_id: str, current_user: dict = Depends(get_current_user)):
    """List all members of a family tree"""
    db = get_db()
    
    # Check if user is a member
    await check_family_membership(current_user["_id"], family_id)
    
    # Get all members
    members = await db.family_members.find({"family_id": ObjectId(family_id)}).to_list(100)
    
    # Enrich with user data
    result = []
    for member in members:
        user = await db.users.find_one({"_id": member["user_id"]}, {"password_hash": 0})
        result.append({
            "_id": str(member["_id"]),
            "family_id": str(member["family_id"]),
            "user_id": str(member["user_id"]),
            "role": member["role"],
            "joined_at": member["joined_at"],
            "user_email": user.get("email") if user else None,
            "user_name": user.get("full_name") if user else None
        })
    
    return result

@app.post("/api/families/{family_id}/members/invite", status_code=status.HTTP_201_CREATED)
async def invite_member(
    family_id: str,
    invite_data: MemberInvite,
    current_user: dict = Depends(get_current_user)
):
    """Invite a member to the family tree"""
    db = get_db()
    
    # Get inviter's role
    inviter_role = await get_user_role_in_family(current_user["_id"], family_id)
    if not inviter_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this family"
        )
    
    # Check if inviter can invite this role
    if not await can_invite_role(inviter_role, invite_data.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You cannot invite {invite_data.role} members"
        )
    
    # If inviting admin, check admin limit
    if invite_data.role == FamilyRole.ADMIN:
        await validate_admin_addition(family_id)
    
    # Check if user exists
    invitee = await db.users.find_one({"email": invite_data.email.lower()})
    if not invitee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found"
        )
    
    # Check if already a member
    existing_member = await db.family_members.find_one({
        "family_id": ObjectId(family_id),
        "user_id": invitee["_id"]
    })
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this family"
        )
    
    # Add member
    member_id = ObjectId()
    await db.family_members.insert_one({
        "_id": member_id,
        "family_id": ObjectId(family_id),
        "user_id": invitee["_id"],
        "role": invite_data.role,
        "joined_at": datetime.now(timezone.utc)
    })
    
    return {
        "_id": str(member_id),
        "family_id": family_id,
        "user_id": str(invitee["_id"]),
        "role": invite_data.role,
        "joined_at": datetime.now(timezone.utc),
        "user_email": invitee["email"],
        "user_name": invitee.get("full_name")
    }

@app.put("/api/families/{family_id}/members/{member_id}")
async def update_member_role(
    family_id: str,
    member_id: str,
    update_data: MemberUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a member's role (Admin only)"""
    db = get_db()
    
    # Only admins can change roles
    await check_admin_role(current_user["_id"], family_id)
    
    # Get the member
    member = await db.family_members.find_one({"_id": ObjectId(member_id)})
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # If promoting to admin, check limit
    if update_data.role == FamilyRole.ADMIN and member["role"] != FamilyRole.ADMIN:
        await validate_admin_addition(family_id)
    
    # If demoting from admin, check if we can remove an admin
    if member["role"] == FamilyRole.ADMIN and update_data.role != FamilyRole.ADMIN:
        if not await check_can_remove_admin(family_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the last admin"
            )
    
    # Update role
    await db.family_members.update_one(
        {"_id": ObjectId(member_id)},
        {"$set": {"role": update_data.role}}
    )
    
    # Return updated member
    updated_member = await db.family_members.find_one({"_id": ObjectId(member_id)})
    user = await db.users.find_one({"_id": updated_member["user_id"]}, {"password_hash": 0})
    
    return {
        "_id": str(updated_member["_id"]),
        "family_id": str(updated_member["family_id"]),
        "user_id": str(updated_member["user_id"]),
        "role": updated_member["role"],
        "joined_at": updated_member["joined_at"],
        "user_email": user.get("email") if user else None,
        "user_name": user.get("full_name") if user else None
    }

@app.delete("/api/families/{family_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    family_id: str,
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a member from the family tree (Admin only)"""
    db = get_db()
    
    # Only admins can remove members
    await check_admin_role(current_user["_id"], family_id)
    
    # Get the member
    member = await db.family_members.find_one({"_id": ObjectId(member_id)})
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Cannot remove the last admin
    if member["role"] == FamilyRole.ADMIN:
        if not await check_can_remove_admin(family_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last admin"
            )
    
    # Remove member
    await db.family_members.delete_one({"_id": ObjectId(member_id)})
    
    return None

@app.get("/api/families/{family_id}/my-role")
async def get_my_role(family_id: str, current_user: dict = Depends(get_current_user)):
    """Get current user's role and permissions in a family"""
    role = await get_user_role_in_family(current_user["_id"], family_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this family"
        )
    
    permissions = Permissions.get_permissions(role)
    
    return {
        "role": role,
        "permissions": permissions
    }

# PERSON ENDPOINTS
# ============================================

@app.get("/api/families/{family_id}/persons")
async def list_persons(family_id: str, current_user: dict = Depends(get_current_user)):
    """List all persons in a family"""
    db = get_db()
    
    # Check if user is a member
    member = await db.family_members.find_one({
        "family_id": ObjectId(family_id),
        "user_id": ObjectId(current_user["_id"])
    })
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this family"
        )
    
    persons = await db.persons.find({"family_id": ObjectId(family_id)}).to_list(1000)
    
    result = []
    for person in persons:
        result.append({
            "_id": str(person["_id"]),
            "family_id": str(person["family_id"]),
            "first_name": person["first_name"],
            "middle_name": person.get("middle_name"),
            "last_name": person["last_name"],
            "nickname": person.get("nickname"),
            "gender": person.get("gender"),
            "birth_date": person.get("birth_date"),
            "death_date": person.get("death_date"),
            "birth_place": person.get("birth_place"),
            "bio": person.get("bio"),
            "profile_image_url": person.get("profile_image_url"),
            "facebook_url": person.get("facebook_url"),
            "is_deceased": person.get("is_deceased", False),
            "generation_level": person.get("generation_level", 0),
            "created_at": person["created_at"],
            "updated_at": person["updated_at"]
        })
    
    return result

@app.post("/api/persons", status_code=status.HTTP_201_CREATED)
async def create_person(person_data: PersonCreate, current_user: dict = Depends(get_current_user)):
    """Create a new person (admin or editor only)"""
    db = get_db()
    
    # Check if user is admin or editor
    member = await db.family_members.find_one({
        "family_id": ObjectId(person_data.family_id),
        "user_id": ObjectId(current_user["_id"])
    })
    
    if not member or member["role"] not in [FamilyRole.ADMIN, FamilyRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or editor role required"
        )
    
    person_id = ObjectId()
    now = datetime.now(timezone.utc)
    
    new_person = {
        "_id": person_id,
        "family_id": ObjectId(person_data.family_id),
        "first_name": person_data.first_name,
        "middle_name": person_data.middle_name,
        "last_name": person_data.last_name,
        "nickname": person_data.nickname,
        "gender": person_data.gender,
        "birth_date": person_data.birth_date,
        "death_date": person_data.death_date,
        "birth_place": person_data.birth_place,
        "bio": person_data.bio,
        "profile_image_url": person_data.profile_image_url,
        "facebook_url": person_data.facebook_url,
        "is_deceased": person_data.is_deceased,
        "photo_gallery": person_data.photo_gallery if person_data.photo_gallery else [],
        "father_id": person_data.father_id,
        "mother_id": person_data.mother_id,
        "spouse_ids": person_data.spouse_ids if person_data.spouse_ids else [],
        "generation_level": 0,
        "created_at": now,
        "updated_at": now
    }
    
    await db.persons.insert_one(new_person)
    
    # Update person count
    await db.families.update_one(
        {"_id": ObjectId(person_data.family_id)},
        {"$inc": {"person_count": 1}}
    )
    
    return {
        "_id": str(person_id),
        "family_id": person_data.family_id,
        **person_data.dict(),
        "generation_level": 0,
        "created_at": now,
        "updated_at": now
    }

@app.get("/api/persons/{person_id}")
async def get_person(person_id: str, current_user: dict = Depends(get_current_user)):
    """Get person details"""
    db = get_db()
    
    person = await db.persons.find_one({"_id": ObjectId(person_id)})
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    # Check if user is a member of the family
    member = await db.family_members.find_one({
        "family_id": person["family_id"],
        "user_id": ObjectId(current_user["_id"])
    })
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this family"
        )
    
    return {
        "_id": str(person["_id"]),
        "family_id": str(person["family_id"]),
        "first_name": person["first_name"],
        "middle_name": person.get("middle_name"),
        "last_name": person["last_name"],
        "nickname": person.get("nickname"),
        "gender": person.get("gender"),
        "birth_date": person.get("birth_date"),
        "death_date": person.get("death_date"),
        "birth_place": person.get("birth_place"),
        "bio": person.get("bio"),
        "profile_image_url": person.get("profile_image_url"),
        "facebook_url": person.get("facebook_url"),
        "is_deceased": person.get("is_deceased", False),
        "generation_level": person.get("generation_level", 0),
        "created_at": person["created_at"],
        "updated_at": person["updated_at"]
    }

@app.put("/api/persons/{person_id}")
async def update_person(
    person_id: str,
    person_data: PersonUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update person details (admin or editor only)"""
    db = get_db()
    
    person = await db.persons.find_one({"_id": ObjectId(person_id)})
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    # Check if user is admin or editor
    member = await db.family_members.find_one({
        "family_id": person["family_id"],
        "user_id": ObjectId(current_user["_id"])
    })
    
    if not member or member["role"] not in [FamilyRole.ADMIN, FamilyRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or editor role required"
        )
    
    # Update person
    update_fields = person_data.dict(exclude_unset=True)
    if update_fields:
        update_fields["updated_at"] = datetime.now(timezone.utc)
        await db.persons.update_one(
            {"_id": ObjectId(person_id)},
            {"$set": update_fields}
        )
    
    return await get_person(person_id, current_user)

@app.delete("/api/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(person_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a person (admin or editor only)"""
    db = get_db()
    
    person = await db.persons.find_one({"_id": ObjectId(person_id)})
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    # Check if user is admin or editor
    member = await db.family_members.find_one({
        "family_id": person["family_id"],
        "user_id": ObjectId(current_user["_id"])
    })
    
    if not member or member["role"] not in [FamilyRole.ADMIN, FamilyRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or editor role required"
        )
    
    # Delete person
    await db.persons.delete_one({"_id": ObjectId(person_id)})
    
    # Update person count
    await db.families.update_one(
        {"_id": person["family_id"]},
        {"$inc": {"person_count": -1}}
    )
    
    return None

# ============================================


# ============================================
# SUPPORT TICKET ENDPOINTS
# ============================================

@app.post("/api/tickets", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a support ticket"""
    db = get_db()
    
    # Verify user is member of family
    await check_family_membership(current_user["_id"], ticket_data.family_id)
    
    ticket_id = ObjectId()
    now = datetime.now(timezone.utc)
    
    new_ticket = {
        "_id": ticket_id,
        "user_id": ObjectId(current_user["_id"]),
        "family_id": ObjectId(ticket_data.family_id),
        "ticket_type": ticket_data.ticket_type,
        "title": ticket_data.title,
        "description": ticket_data.description,
        "screenshot_url": ticket_data.screenshot_url,
        "status": TicketStatus.PENDING,
        "priority": TicketPriority.MEDIUM,
        "reward_slots": 0,
        "is_rewarded": False,
        "admin_notes": None,
        "reviewed_by": None,
        "reviewed_at": None,
        "created_at": now,
        "updated_at": now
    }
    
    await db.support_tickets.insert_one(new_ticket)
    
    return {
        "_id": str(ticket_id),
        "user_id": str(current_user["_id"]),
        "family_id": ticket_data.family_id,
        "ticket_type": ticket_data.ticket_type,
        "title": ticket_data.title,
        "description": ticket_data.description,
        "screenshot_url": ticket_data.screenshot_url,
        "status": TicketStatus.PENDING,
        "priority": TicketPriority.MEDIUM,
        "reward_slots": 0,
        "is_rewarded": False,
        "created_at": now,
        "updated_at": now,
        "user_email": current_user["email"],
        "user_name": current_user["full_name"]
    }

@app.get("/api/tickets")
async def list_tickets(current_user: dict = Depends(get_current_user)):
    """List user's tickets"""
    db = get_db()
    
    # If admin, show all tickets; otherwise show only user's tickets
    if current_user.get("role") == UserRole.ADMIN:
        tickets = await db.support_tickets.find().sort("created_at", -1).to_list(100)
    else:
        tickets = await db.support_tickets.find({
            "user_id": ObjectId(current_user["_id"])
        }).sort("created_at", -1).to_list(100)
    
    result = []
    for ticket in tickets:
        user = await db.users.find_one({"_id": ticket["user_id"]}, {"password_hash": 0})
        result.append({
            "_id": str(ticket["_id"]),
            "user_id": str(ticket["user_id"]),
            "family_id": str(ticket["family_id"]),
            "ticket_type": ticket["ticket_type"],
            "title": ticket["title"],
            "description": ticket["description"],
            "screenshot_url": ticket.get("screenshot_url"),
            "status": ticket["status"],
            "priority": ticket["priority"],
            "reward_slots": ticket["reward_slots"],
            "is_rewarded": ticket["is_rewarded"],
            "admin_notes": ticket.get("admin_notes"),
            "reviewed_by": str(ticket["reviewed_by"]) if ticket.get("reviewed_by") else None,
            "reviewed_at": ticket.get("reviewed_at"),
            "created_at": ticket["created_at"],
            "updated_at": ticket["updated_at"],
            "user_email": user.get("email") if user else None,
            "user_name": user.get("full_name") if user else None
        })
    
    return result

@app.get("/api/tickets/{ticket_id}")
async def get_ticket(ticket_id: str, current_user: dict = Depends(get_current_user)):
    """Get ticket details"""
    db = get_db()
    
    ticket = await db.support_tickets.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Check permissions (admin or ticket owner)
    if current_user.get("role") != UserRole.ADMIN and str(ticket["user_id"]) != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ticket"
        )
    
    user = await db.users.find_one({"_id": ticket["user_id"]}, {"password_hash": 0})
    
    return {
        "_id": str(ticket["_id"]),
        "user_id": str(ticket["user_id"]),
        "family_id": str(ticket["family_id"]),
        "ticket_type": ticket["ticket_type"],
        "title": ticket["title"],
        "description": ticket["description"],
        "screenshot_url": ticket.get("screenshot_url"),
        "status": ticket["status"],
        "priority": ticket["priority"],
        "reward_slots": ticket["reward_slots"],
        "is_rewarded": ticket["is_rewarded"],
        "admin_notes": ticket.get("admin_notes"),
        "reviewed_by": str(ticket["reviewed_by"]) if ticket.get("reviewed_by") else None,
        "reviewed_at": ticket.get("reviewed_at"),
        "created_at": ticket["created_at"],
        "updated_at": ticket["updated_at"],
        "user_email": user.get("email") if user else None,
        "user_name": user.get("full_name") if user else None
    }

@app.put("/api/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    ticket_update: TicketUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update ticket (Admin only for review)"""
    db = get_db()
    
    # Only admins can update tickets
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    
    ticket = await db.support_tickets.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    update_fields = {"updated_at": datetime.now(timezone.utc)}
    
    if ticket_update.status:
        update_fields["status"] = ticket_update.status
        update_fields["reviewed_by"] = ObjectId(current_user["_id"])
        update_fields["reviewed_at"] = datetime.now(timezone.utc)
    
    if ticket_update.priority:
        update_fields["priority"] = ticket_update.priority
    
    if ticket_update.admin_notes:
        update_fields["admin_notes"] = ticket_update.admin_notes
    
    # Handle reward slots
    if ticket_update.reward_slots is not None:
        if not (1 <= ticket_update.reward_slots <= 15):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reward slots must be between 1 and 15"
            )
        
        update_fields["reward_slots"] = ticket_update.reward_slots
        update_fields["is_rewarded"] = True
        
        # Add slots to family's person_limit
        await db.families.update_one(
            {"_id": ticket["family_id"]},
            {"$inc": {"person_limit": ticket_update.reward_slots}}
        )
    
    await db.support_tickets.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$set": update_fields}
    )
    
    return await get_ticket(ticket_id, current_user)



# ============================================
# PDF EXPORT ENDPOINTS
# ============================================

@app.get("/api/families/{family_id}/export/pdf")
async def export_family_tree_pdf(
    family_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Export family tree as PDF (Admin or Editor only)"""
    from fastapi.responses import StreamingResponse
    from pdf_generator import generate_family_tree_pdf
    
    db = get_db()
    
    # Check if user has permission (Admin or Editor)
    role = await get_user_role_in_family(current_user["_id"], family_id)
    if role not in [FamilyRole.ADMIN, FamilyRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Editor role required to export PDF"
        )
    
    # Get family data
    family = await db.families.find_one({"_id": ObjectId(family_id)})
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family not found"
        )
    
    # Get all persons
    persons = await db.persons.find({"family_id": ObjectId(family_id)}).to_list(1000)
    
    # Convert ObjectIds to strings for PDF generator
    family_data = {
        "_id": str(family["_id"]),
        "name": family["name"],
        "description": family.get("description", ""),
        "created_at": family["created_at"].isoformat() if isinstance(family["created_at"], datetime) else str(family["created_at"]),
        "person_count": family.get("person_count", len(persons)),
        "subscription_plan": family.get("subscription_plan", "free"),
        "person_limit": family.get("person_limit", 50),
        "join_code": family.get("join_code", "")
    }
    
    persons_data = []
    for person in persons:
        persons_data.append({
            "first_name": person.get("first_name", ""),
            "middle_name": person.get("middle_name"),
            "last_name": person.get("last_name", ""),
            "nickname": person.get("nickname"),
            "gender": person.get("gender"),
            "birth_date": person.get("birth_date"),
            "death_date": person.get("death_date"),
            "birth_place": person.get("birth_place"),
            "bio": person.get("bio"),
            "is_deceased": person.get("is_deceased", False),
            "generation_level": person.get("generation_level", 0)
        })
    
    # Generate PDF
    pdf_buffer = generate_family_tree_pdf(family_data, persons_data)
    
    # Return as streaming response
    filename = f"{family['name'].replace(' ', '_')}_FamilyTree.pdf"


# ============================================
# PHOTO GALLERY ENDPOINTS
# ============================================

class PhotoAdd(BaseModel):
    photo_url: str

@app.post("/api/persons/{person_id}/photos")
async def add_photo_to_gallery(
    person_id: str,
    photo_data: PhotoAdd,
    current_user: dict = Depends(get_current_user)
):
    """Add photo to person's gallery (Admin or Editor only)"""
    db = get_db()
    
    person = await db.persons.find_one({"_id": ObjectId(person_id)})
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    # Check permission
    role = await get_user_role_in_family(current_user["_id"], str(person["family_id"]))
    if role not in [FamilyRole.ADMIN, FamilyRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Editor role required"
        )
    
    # Add photo to gallery
    await db.persons.update_one(
        {"_id": ObjectId(person_id)},
        {
            "$push": {"photo_gallery": photo_data.photo_url},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )
    
    return {"message": "Photo added to gallery", "photo_url": photo_data.photo_url}

@app.delete("/api/persons/{person_id}/photos")
async def remove_photo_from_gallery(
    person_id: str,
    photo_url: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove photo from person's gallery (Admin or Editor only)"""
    db = get_db()
    
    person = await db.persons.find_one({"_id": ObjectId(person_id)})
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    # Check permission
    role = await get_user_role_in_family(current_user["_id"], str(person["family_id"]))
    if role not in [FamilyRole.ADMIN, FamilyRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Editor role required"
        )
    
    # Remove photo from gallery
    await db.persons.update_one(
        {"_id": ObjectId(person_id)},
        {
            "$pull": {"photo_gallery": photo_url},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )
    
    return {"message": "Photo removed from gallery"}

@app.get("/api/persons/{person_id}/photos")
async def get_person_photos(
    person_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all photos from person's gallery"""
    db = get_db()
    
    person = await db.persons.find_one({"_id": ObjectId(person_id)})
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    # Check if user has access to family
    await check_family_membership(current_user["_id"], str(person["family_id"]))
    
    return {
        "person_id": person_id,
        "photos": person.get("photo_gallery", [])
    }

# ============================================
# RELATIONSHIP MAPPING ENDPOINTS
# ============================================

class RelationshipAdd(BaseModel):
    relationship_type: str  # "father", "mother", "spouse", "child"
    related_person_id: str

@app.post("/api/persons/{person_id}/relationships")
async def add_relationship(
    person_id: str,
    relationship_data: RelationshipAdd,
    current_user: dict = Depends(get_current_user)
):
    """Add relationship between persons (Admin or Editor only)"""
    db = get_db()
    
    person = await db.persons.find_one({"_id": ObjectId(person_id)})
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    related_person = await db.persons.find_one({"_id": ObjectId(relationship_data.related_person_id)})
    if not related_person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Related person not found"
        )
    
    # Check permission
    role = await get_user_role_in_family(current_user["_id"], str(person["family_id"]))
    if role not in [FamilyRole.ADMIN, FamilyRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Editor role required"
        )
    
    # Add relationship based on type
    update_query = {"$set": {"updated_at": datetime.now(timezone.utc)}}
    
    if relationship_data.relationship_type == "father":
        update_query["$set"]["father_id"] = relationship_data.related_person_id
    elif relationship_data.relationship_type == "mother":
        update_query["$set"]["mother_id"] = relationship_data.related_person_id
    elif relationship_data.relationship_type == "spouse":
        update_query["$addToSet"] = {"spouse_ids": relationship_data.related_person_id}
        # Add reciprocal relationship
        await db.persons.update_one(
            {"_id": ObjectId(relationship_data.related_person_id)},
            {"$addToSet": {"spouse_ids": person_id}}
        )
    elif relationship_data.relationship_type == "child":
        # Set this person as parent of the related person
        if person.get("gender") == "male":
            await db.persons.update_one(
                {"_id": ObjectId(relationship_data.related_person_id)},
                {"$set": {"father_id": person_id, "updated_at": datetime.now(timezone.utc)}}
            )
        elif person.get("gender") == "female":
            await db.persons.update_one(
                {"_id": ObjectId(relationship_data.related_person_id)},
                {"$set": {"mother_id": person_id, "updated_at": datetime.now(timezone.utc)}}
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid relationship type. Use: father, mother, spouse, or child"
        )
    
    await db.persons.update_one({"_id": ObjectId(person_id)}, update_query)
    
    return {
        "message": f"{relationship_data.relationship_type.title()} relationship added",
        "person_id": person_id,
        "related_person_id": relationship_data.related_person_id
    }

@app.get("/api/persons/{person_id}/relationships")
async def get_person_relationships(
    person_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all relationships for a person"""
    db = get_db()
    
    person = await db.persons.find_one({"_id": ObjectId(person_id)})
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    # Check access
    await check_family_membership(current_user["_id"], str(person["family_id"]))
    
    relationships = {
        "person_id": person_id,
        "father": None,
        "mother": None,
        "spouses": [],
        "children": []
    }
    
    # Get father
    if person.get("father_id"):
        try:
            father = await db.persons.find_one({"_id": ObjectId(person["father_id"])})
            if father:
                relationships["father"] = {
                    "id": person["father_id"],
                    "name": f"{father['first_name']} {father['last_name']}"
                }
        except:
            pass
    
    # Get mother
    if person.get("mother_id"):
        try:
            mother = await db.persons.find_one({"_id": ObjectId(person["mother_id"])})
            if mother:
                relationships["mother"] = {
                    "id": person["mother_id"],
                    "name": f"{mother['first_name']} {mother['last_name']}"
                }
        except:
            pass
    
    # Get spouses
    if person.get("spouse_ids"):
        for spouse_id in person["spouse_ids"]:
            spouse = await db.persons.find_one({"_id": ObjectId(spouse_id)})
            if spouse:
                relationships["spouses"].append({
                    "id": str(spouse["_id"]),
                    "name": f"{spouse['first_name']} {spouse['last_name']}"
                })
    
    # Get children (persons who have this person as parent)
    children = await db.persons.find({
        "$or": [
            {"father_id": person_id},
            {"mother_id": person_id}
        ]
    }).to_list(100)
    
    for child in children:
        relationships["children"].append({
            "id": str(child["_id"]),
            "name": f"{child['first_name']} {child['last_name']}"
        })
    
    return relationships

@app.get("/api/families/{family_id}/tree")
async def get_family_tree_structure(
    family_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get complete family tree structure with relationships"""
    db = get_db()
    
    # Check access
    await check_family_membership(current_user["_id"], family_id)
    
    # Get all persons in family
    persons = await db.persons.find({"family_id": ObjectId(family_id)}).to_list(1000)
    
    tree_data = []
    for person in persons:
        tree_data.append({
            "id": str(person["_id"]),
            "first_name": person["first_name"],
            "last_name": person["last_name"],
            "gender": person.get("gender"),
            "birth_date": person.get("birth_date"),
            "is_deceased": person.get("is_deceased", False),
            "father_id": person.get("father_id"),
            "mother_id": person.get("mother_id"),
            "spouse_ids": person.get("spouse_ids", []),
            "generation_level": person.get("generation_level", 0)
        })
    
    return {
        "family_id": family_id,
        "total_persons": len(tree_data),
        "persons": tree_data
    }

# ============================================
# RUN APP
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
