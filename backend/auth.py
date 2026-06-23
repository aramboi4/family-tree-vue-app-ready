import os
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Request
from config import settings
from database import get_db
from bson import ObjectId

# ============================================
# PASSWORD HASHING
# ============================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# ============================================
# JWT TOKEN MANAGEMENT
# ============================================

def get_jwt_secret() -> str:
    """Get JWT secret from environment"""
    return os.environ.get("JWT_SECRET", settings.JWT_SECRET)

def create_access_token(user_id: str, email: str) -> str:
    """Create access token (15 minutes)"""
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access"
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """Create refresh token (7 days)"""
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh"
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=settings.JWT_ALGORITHM)

# ============================================
# GET CURRENT USER
# ============================================

async def get_current_user(request: Request) -> dict:
    """Get current authenticated user from token"""
    db = get_db()
    
    # Try to get token from cookie first, then from Authorization header
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[settings.JWT_ALGORITHM])
        
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])}, {"password_hash": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        user["_id"] = str(user["_id"])
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# ============================================
# BRUTE FORCE PROTECTION
# ============================================

async def check_brute_force(identifier: str) -> bool:
    """Check if an identifier is locked out due to too many failed attempts"""
    db = get_db()
    attempt = await db.login_attempts.find_one({"identifier": identifier})
    
    if not attempt:
        return False
    
    # Check if locked out (5 attempts = 15 min lockout)
    if attempt["failed_count"] >= 5:
        lockout_time = attempt["last_attempt"] + timedelta(minutes=15)
        if datetime.now(timezone.utc) < lockout_time:
            return True
        else:
            # Lockout expired, reset
            await db.login_attempts.delete_one({"identifier": identifier})
            return False
    
    return False

async def record_failed_login(identifier: str):
    """Record a failed login attempt"""
    db = get_db()
    await db.login_attempts.update_one(
        {"identifier": identifier},
        {
            "$inc": {"failed_count": 1},
            "$set": {"last_attempt": datetime.now(timezone.utc)}
        },
        upsert=True
    )

async def clear_failed_login(identifier: str):
    """Clear failed login attempts after successful login"""
    db = get_db()
    await db.login_attempts.delete_one({"identifier": identifier})
