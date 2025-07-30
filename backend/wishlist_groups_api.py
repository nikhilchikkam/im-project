import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from auth import get_current_user, User
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/wishlist-groups", tags=["wishlist-groups"])

# Pydantic models
class WishlistGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

class WishlistGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class WishlistGroupMember(BaseModel):
    user_id: int
    role: str = "member"  # "owner", "admin", "member"

# Test endpoints (for debugging)
@router.get("/test")
async def test_wishlist_groups():
    return {"message": "Wishlist groups API is working"}

@router.get("/test-simple")
async def test_wishlist_groups_simple():
    return {"message": "Simple test endpoint working"}

@router.get("/test-auth")
async def test_wishlist_groups_auth(current_user: User = Depends(get_current_user)):
    return {
        "message": "Authenticated test endpoint working",
        "user_id": current_user.id,
        "user_email": current_user.email
    }

@router.get("/test-auth-simple")
async def test_wishlist_groups_auth_simple(current_user: User = Depends(get_current_user)):
    return {"message": "Authenticated simple test working"}

# Main endpoints
@router.get("/")
async def get_wishlist_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_current_user)):
    """Get all wishlist groups for the current user"""
    try:
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            query = text("""
                SELECT wg.*, 
                       COUNT(DISTINCT wgm.user_id) as member_count,
                       COUNT(DISTINCT wi.id) as item_count
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id
                LEFT JOIN wishlist_items wi ON wg.id = wi.group_id
                WHERE wg.user_id = :user_id OR wg.is_public = true
                GROUP BY wg.id
                ORDER BY wg.created_at DESC
            """)
            result = db.execute(query, {"user_id": current_user.id})
            groups = []
            for row in result:
                group_data = dict(row._mapping)
                groups.append({
                    "id": group_data["id"],
                    "name": group_data["name"],
                    "description": group_data["description"],
                    "is_public": group_data["is_public"],
                    "member_count": group_data["member_count"],
                    "item_count": group_data["item_count"],
                    "created_at": group_data["created_at"],
                    "updated_at": group_data["updated_at"]
                })
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("""
                SELECT wg.*, 
                       COUNT(DISTINCT wgm.user_id) as member_count,
                       COUNT(DISTINCT wi.id) as item_count
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id
                LEFT JOIN wishlist_items wi ON wg.id = wi.group_id
                WHERE wg.user_id = %s OR wg.is_public = true
                GROUP BY wg.id
                ORDER BY wg.created_at DESC
            """, (current_user.id,))
            
            groups = []
            for row in cursor.fetchall():
                group_data = dict(row)
                groups.append({
                    "id": group_data["id"],
                    "name": group_data["name"],
                    "description": group_data["description"],
                    "is_public": group_data["is_public"],
                    "member_count": group_data["member_count"],
                    "item_count": group_data["item_count"],
                    "created_at": group_data["created_at"],
                    "updated_at": group_data["updated_at"]
                })
        
        return {"groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch wishlist groups: {str(e)}")

@router.post("/")
async def create_wishlist_group(
    group_data: WishlistGroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_user)
):
    """Create a new wishlist group"""
    try:
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            query = text("""
                INSERT INTO wishlist_groups (name, description, is_public, user_id, created_at, updated_at)
                VALUES (:name, :description, :is_public, :user_id, NOW(), NOW())
                RETURNING *
            """)
            result = db.execute(query, {
                "name": group_data.name,
                "description": group_data.description,
                "is_public": group_data.is_public,
                "user_id": current_user.id
            })
            db.commit()
            new_group = dict(result.fetchone()._mapping)
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO wishlist_groups (name, description, is_public, user_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                RETURNING *
            """, (group_data.name, group_data.description, group_data.is_public, current_user.id))
            new_group = dict(cursor.fetchone())
            db.commit()
        
        return {
            "message": "Wishlist group created successfully",
            "group": {
                "id": new_group["id"],
                "name": new_group["name"],
                "description": new_group["description"],
                "is_public": new_group["is_public"],
                "created_at": new_group["created_at"]
            }
        }
    except Exception as e:
        if hasattr(db, 'rollback'):
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create wishlist group: {str(e)}")

@router.get("/{group_id}")
async def get_wishlist_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_user)
):
    """Get a specific wishlist group"""
    try:
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            query = text("""
                SELECT wg.*, 
                       COUNT(DISTINCT wgm.user_id) as member_count,
                       COUNT(DISTINCT wi.id) as item_count
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id
                LEFT JOIN wishlist_items wi ON wg.id = wi.group_id
                WHERE wg.id = :group_id AND (wg.user_id = :user_id OR wg.is_public = true)
                GROUP BY wg.id
            """)
            result = db.execute(query, {"group_id": group_id, "user_id": current_user.id})
            row = result.fetchone()
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("""
                SELECT wg.*, 
                       COUNT(DISTINCT wgm.user_id) as member_count,
                       COUNT(DISTINCT wi.id) as item_count
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id
                LEFT JOIN wishlist_items wi ON wg.id = wi.group_id
                WHERE wg.id = %s AND (wg.user_id = %s OR wg.is_public = true)
                GROUP BY wg.id
            """, (group_id, current_user.id))
            row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Wishlist group not found")
        
        group_data = dict(row._mapping if hasattr(row, '_mapping') else row)
        return {
            "id": group_data["id"],
            "name": group_data["name"],
            "description": group_data["description"],
            "is_public": group_data["is_public"],
            "member_count": group_data["member_count"],
            "item_count": group_data["item_count"],
            "created_at": group_data["created_at"],
            "updated_at": group_data["updated_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch wishlist group: {str(e)}")

@router.put("/{group_id}")
async def update_wishlist_group(
    group_id: int,
    group_data: WishlistGroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_user)
):
    """Update a wishlist group"""
    try:
        # Check if user owns the group
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            check_query = text("SELECT user_id FROM wishlist_groups WHERE id = :group_id")
            result = db.execute(check_query, {"group_id": group_id})
            row = result.fetchone()
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("SELECT user_id FROM wishlist_groups WHERE id = %s", (group_id,))
            row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Wishlist group not found")
        
        group_user_id = row.user_id if hasattr(row, 'user_id') else row['user_id']
        if group_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this group")
        
        # Build update query
        update_fields = {}
        if group_data.name is not None:
            update_fields["name"] = group_data.name
        if group_data.description is not None:
            update_fields["description"] = group_data.description
        if group_data.is_public is not None:
            update_fields["is_public"] = group_data.is_public
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            set_clause = ", ".join([f"{field} = :{field}" for field in update_fields.keys()])
            query = text(f"UPDATE wishlist_groups SET {set_clause}, updated_at = NOW() WHERE id = :group_id RETURNING *")
            update_fields["group_id"] = group_id
            result = db.execute(query, update_fields)
            db.commit()
            updated_group = dict(result.fetchone()._mapping)
        else:  # psycopg2 connection
            set_clause = ", ".join([f"{field} = %s" for field in update_fields.keys()])
            query = f"UPDATE wishlist_groups SET {set_clause}, updated_at = NOW() WHERE id = %s RETURNING *"
            values = list(update_fields.values()) + [group_id]
            cursor = db.cursor()
            cursor.execute(query, values)
            updated_group = dict(cursor.fetchone())
            db.commit()
        
        return {
            "message": "Wishlist group updated successfully",
            "group": {
                "id": updated_group["id"],
                "name": updated_group["name"],
                "description": updated_group["description"],
                "is_public": updated_group["is_public"],
                "updated_at": updated_group["updated_at"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        if hasattr(db, 'rollback'):
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update wishlist group: {str(e)}")

@router.delete("/{group_id}")
async def delete_wishlist_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_user)
):
    """Delete a wishlist group"""
    try:
        # Check if user owns the group
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            check_query = text("SELECT user_id FROM wishlist_groups WHERE id = :group_id")
            result = db.execute(check_query, {"group_id": group_id})
            row = result.fetchone()
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("SELECT user_id FROM wishlist_groups WHERE id = %s", (group_id,))
            row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Wishlist group not found")
        
        group_user_id = row.user_id if hasattr(row, 'user_id') else row['user_id']
        if group_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this group")
        
        # Delete group (cascade will handle related records)
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            delete_query = text("DELETE FROM wishlist_groups WHERE id = :group_id")
            db.execute(delete_query, {"group_id": group_id})
            db.commit()
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("DELETE FROM wishlist_groups WHERE id = %s", (group_id,))
            db.commit()
        
        return {"message": "Wishlist group deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        if hasattr(db, 'rollback'):
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete wishlist group: {str(e)}")

@router.post("/{group_id}/members")
async def add_group_member(
    group_id: int,
    member_data: WishlistGroupMember,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_user)
):
    """Add a member to a wishlist group"""
    try:
        # Check if user owns the group
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            check_query = text("SELECT user_id FROM wishlist_groups WHERE id = :group_id")
            result = db.execute(check_query, {"group_id": group_id})
            row = result.fetchone()
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("SELECT user_id FROM wishlist_groups WHERE id = %s", (group_id,))
            row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Wishlist group not found")
        
        group_user_id = row.user_id if hasattr(row, 'user_id') else row['user_id']
        if group_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to add members to this group")
        
        # Add member
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            insert_query = text("""
                INSERT INTO wishlist_group_members (group_id, user_id, role, joined_at)
                VALUES (:group_id, :user_id, :role, NOW())
                ON CONFLICT (group_id, user_id) DO UPDATE SET role = :role
            """)
            db.execute(insert_query, {
                "group_id": group_id,
                "user_id": member_data.user_id,
                "role": member_data.role
            })
            db.commit()
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO wishlist_group_members (group_id, user_id, role, joined_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (group_id, user_id) DO UPDATE SET role = %s
            """, (group_id, member_data.user_id, member_data.role, member_data.role))
            db.commit()
        
        return {"message": "Member added to group successfully"}
    except HTTPException:
        raise
    except Exception as e:
        if hasattr(db, 'rollback'):
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add member to group: {str(e)}")

@router.delete("/{group_id}/members/{user_id}")
async def remove_group_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_current_user)
):
    """Remove a member from a wishlist group"""
    try:
        # Check if user owns the group
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            check_query = text("SELECT user_id FROM wishlist_groups WHERE id = :group_id")
            result = db.execute(check_query, {"group_id": group_id})
            row = result.fetchone()
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("SELECT user_id FROM wishlist_groups WHERE id = %s", (group_id,))
            row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Wishlist group not found")
        
        group_user_id = row.user_id if hasattr(row, 'user_id') else row['user_id']
        if group_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to remove members from this group")
        
        # Remove member
        if hasattr(db, 'execute'):  # SQLAlchemy Session
            delete_query = text("DELETE FROM wishlist_group_members WHERE group_id = :group_id AND user_id = :user_id")
            db.execute(delete_query, {"group_id": group_id, "user_id": user_id})
            db.commit()
        else:  # psycopg2 connection
            cursor = db.cursor()
            cursor.execute("DELETE FROM wishlist_group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
            db.commit()
        
        return {"message": "Member removed from group successfully"}
    except HTTPException:
        raise
    except Exception as e:
        if hasattr(db, 'rollback'):
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove member from group: {str(e)}") 