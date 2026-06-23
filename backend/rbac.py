"""
Role-Based Access Control (RBAC) Utilities
"""

from fastapi import HTTPException, status
from database import get_db
from models import FamilyRole
from bson import ObjectId

# ============================================
# ROLE CHECKING FUNCTIONS
# ============================================

async def get_user_role_in_family(user_id: str, family_id: str) -> str:
    """Get user's role in a specific family tree"""
    db = get_db()
    member = await db.family_members.find_one({
        "family_id": ObjectId(family_id),
        "user_id": ObjectId(user_id)
    })
    
    if not member:
        return None
    
    return member["role"]

async def check_family_membership(user_id: str, family_id: str):
    """Check if user is a member of the family"""
    role = await get_user_role_in_family(user_id, family_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this family tree"
        )
    return role

async def check_admin_role(user_id: str, family_id: str):
    """Check if user is an admin of the family"""
    role = await get_user_role_in_family(user_id, family_id)
    if role != FamilyRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for this action"
        )
    return True

async def check_admin_or_editor_role(user_id: str, family_id: str):
    """Check if user is an admin or editor"""
    role = await get_user_role_in_family(user_id, family_id)
    if role not in [FamilyRole.ADMIN, FamilyRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Editor role required for this action"
        )
    return role

async def can_invite_role(inviter_role: str, invitee_role: str) -> bool:
    """
    Check if inviter can invite someone with the specified role
    - Admin can invite: Admin, Editor, Viewer
    - Editor can invite: Editor, Viewer
    - Viewer cannot invite anyone
    """
    if inviter_role == FamilyRole.ADMIN:
        return True
    elif inviter_role == FamilyRole.EDITOR:
        return invitee_role in [FamilyRole.EDITOR, FamilyRole.VIEWER]
    else:
        return False

async def check_admin_limit(family_id: str) -> int:
    """Check current number of admins in family (max 5)"""
    db = get_db()
    admin_count = await db.family_members.count_documents({
        "family_id": ObjectId(family_id),
        "role": FamilyRole.ADMIN
    })
    return admin_count

async def check_can_remove_admin(family_id: str) -> bool:
    """Check if an admin can be removed (must keep at least 1)"""
    admin_count = await check_admin_limit(family_id)
    return admin_count > 1

async def validate_admin_addition(family_id: str):
    """Validate that adding an admin won't exceed limit"""
    admin_count = await check_admin_limit(family_id)
    if admin_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 admins allowed per family tree"
        )

# ============================================
# PERMISSION DEFINITIONS
# ============================================

class Permissions:
    """Permission definitions for each role"""
    
    ADMIN = {
        "can_update_family": True,
        "can_delete_family": True,
        "can_add_person": True,
        "can_edit_person": True,
        "can_delete_person": True,
        "can_invite_admin": True,
        "can_invite_editor": True,
        "can_invite_viewer": True,
        "can_remove_member": True,
        "can_transfer_admin": True,
        "can_purchase_plan": True,
        "can_manage_subscription": True,
        "can_generate_pdf": True,
        "can_view_logs": True
    }
    
    EDITOR = {
        "can_update_family": True,
        "can_delete_family": False,
        "can_add_person": True,
        "can_edit_person": True,
        "can_delete_person": True,
        "can_invite_admin": False,
        "can_invite_editor": True,
        "can_invite_viewer": True,
        "can_remove_member": False,
        "can_transfer_admin": False,
        "can_purchase_plan": False,
        "can_manage_subscription": False,
        "can_generate_pdf": True,
        "can_view_logs": True
    }
    
    VIEWER = {
        "can_update_family": False,
        "can_delete_family": False,
        "can_add_person": False,
        "can_edit_person": False,
        "can_delete_person": False,
        "can_invite_admin": False,
        "can_invite_editor": False,
        "can_invite_viewer": False,
        "can_remove_member": False,
        "can_transfer_admin": False,
        "can_purchase_plan": False,
        "can_manage_subscription": False,
        "can_generate_pdf": False,
        "can_view_logs": False
    }
    
    @staticmethod
    def get_permissions(role: str) -> dict:
        """Get permissions for a specific role"""
        if role == FamilyRole.ADMIN:
            return Permissions.ADMIN
        elif role == FamilyRole.EDITOR:
            return Permissions.EDITOR
        elif role == FamilyRole.VIEWER:
            return Permissions.VIEWER
        return {}
    
    @staticmethod
    def check_permission(role: str, permission: str) -> bool:
        """Check if role has a specific permission"""
        permissions = Permissions.get_permissions(role)
        return permissions.get(permission, False)
