import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from auth import get_db, get_current_user, User

# Pydantic models for request bodies
class CartItemRequest(BaseModel):
    gtin: str
    quantity: int = 1

class WishlistItemRequest(BaseModel):
    gtin: str

class AddToWishlistRequest(BaseModel):
    gtin: str
    group_id: Optional[int] = None  # If not provided, use default wishlist

class CartUpdateRequest(BaseModel):
    gtin: str
    quantity: int

# Wishlist Groups Models
class WishlistGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

class WishlistGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class WishlistGroupItems(BaseModel):
    gtins: List[str]

router = APIRouter(prefix="/api", tags=["cart-wishlist"])

# Cart Endpoints
@router.get("/cart")
async def get_cart_items(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all cart items for the current user"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("""
                SELECT ci.*, p.name, p.normalized_name, p.image_urls, p.product_type, p.description
                FROM cart_items ci
                LEFT JOIN products_with_nutrition p ON ci.gtin = p.gtin
                WHERE ci.user_id = :user_id
                ORDER BY ci.added_at DESC
            """)
            result = db.execute(query, {"user_id": current_user.id}).fetchall()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("""
                SELECT ci.*, p.name, p.normalized_name, p.image_urls, p.product_type, p.description
                FROM cart_items ci
                LEFT JOIN products_with_nutrition p ON ci.gtin = p.gtin
                WHERE ci.user_id = %s
                ORDER BY ci.added_at DESC
            """, (current_user.id,))
            result = cur.fetchall()
            cur.close()
        
        cart_items = []
        for row in result:
            item = dict(row)
            cart_items.append({
                "id": item["id"],
                "gtin": item["gtin"],
                "quantity": item["quantity"],
                "added_at": item["added_at"],
                "product": {
                    "name": item["name"],
                    "normalized_name": item.get("normalized_name", ""),
                    "image_urls": item["image_urls"],
                    "product_type": item["product_type"],
                    "description": item["description"]
                }
            })
        
        return {"items": cart_items, "total_items": len(cart_items)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cart items: {str(e)}")

@router.post("/cart/add")
async def add_to_cart(
    request: CartItemRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Add a product to cart"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("""
                INSERT INTO cart_items (user_id, gtin, quantity)
                VALUES (:user_id, :gtin, :quantity)
                ON CONFLICT (user_id, gtin) 
                DO UPDATE SET quantity = cart_items.quantity + :quantity
                RETURNING *
            """)
            result = db.execute(query, {
                "user_id": current_user.id,
                "gtin": request.gtin,
                "quantity": request.quantity
            }).fetchone()
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("""
                INSERT INTO cart_items (user_id, gtin, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, gtin) 
                DO UPDATE SET quantity = cart_items.quantity + %s
                RETURNING *
            """, (current_user.id, request.gtin, request.quantity, request.quantity))
            result = cur.fetchone()
            db.commit()
            cur.close()
        
        return {"message": "Product added to cart successfully", "item": dict(result)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to cart: {str(e)}")

@router.put("/cart/update")
async def update_cart_item(
    request: CartUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    try:
        if request.quantity <= 0:
            # Remove item if quantity is 0 or negative
            return await remove_from_cart(request.gtin, current_user, db)
        
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("""
                UPDATE cart_items 
                SET quantity = :quantity 
                WHERE user_id = :user_id AND gtin = :gtin
                RETURNING *
            """)
            result = db.execute(query, {
                "user_id": current_user.id,
                "gtin": request.gtin,
                "quantity": request.quantity
            }).fetchone()
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("""
                UPDATE cart_items 
                SET quantity = %s 
                WHERE user_id = %s AND gtin = %s
                RETURNING *
            """, (request.quantity, current_user.id, request.gtin))
            result = cur.fetchone()
            db.commit()
            cur.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        return {"message": "Cart item updated successfully", "item": dict(result)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update cart item: {str(e)}")

@router.delete("/cart/remove")
async def remove_from_cart(
    request: WishlistItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("""
                DELETE FROM cart_items 
                WHERE user_id = :user_id AND gtin = :gtin
                RETURNING *
            """)
            result = db.execute(query, {
                "user_id": current_user.id,
                "gtin": request.gtin
            }).fetchone()
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("""
                DELETE FROM cart_items 
                WHERE user_id = %s AND gtin = %s
                RETURNING *
            """, (current_user.id, request.gtin))
            result = cur.fetchone()
            db.commit()
            cur.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        return {"message": "Item removed from cart successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from cart: {str(e)}")

@router.delete("/cart/clear")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from cart"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("DELETE FROM cart_items WHERE user_id = :user_id")
            db.execute(query, {"user_id": current_user.id})
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("DELETE FROM cart_items WHERE user_id = %s", (current_user.id,))
            db.commit()
            cur.close()
        
        return {"message": "Cart cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cart: {str(e)}")

# Wishlist Endpoints
@router.get("/wishlist")
async def get_wishlist_items(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all wishlist items for the current user (no duplicates)"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("""
                SELECT DISTINCT ON (wi.gtin) 
                    wi.id, wi.gtin, wi.added_at, wi.group_id,
                    p.name, p.normalized_name, p.image_urls, p.product_type, p.family_title, p.description, p.is_smart_snack, p.nova_label, p.is_good_choice
                FROM wishlist_items wi
                LEFT JOIN products_with_nutrition p ON wi.gtin = p.gtin
                WHERE wi.user_id = :user_id
                ORDER BY wi.gtin, wi.added_at DESC
            """)
            result = db.execute(query, {"user_id": current_user.id}).fetchall()
            
            # Get group information for each item
            wishlist_items = []
            for row in result:
                # Get all groups this item belongs to
                group_query = text("""
                    SELECT wg.id, wg.name 
                    FROM wishlist_items wi
                    JOIN wishlist_groups wg ON wi.group_id = wg.id
                    WHERE wi.user_id = :user_id AND wi.gtin = :gtin AND wi.group_id IS NOT NULL
                """)
                groups = db.execute(group_query, {"user_id": current_user.id, "gtin": row.gtin}).fetchall()
                
                item = dict(row)
                wishlist_items.append({
                    "id": item["id"],
                    "gtin": item["gtin"],
                    "added_at": item["added_at"],
                    "group_id": item["group_id"],
                    "groups": [{"id": g.id, "name": g.name} for g in groups],
                    "product": {
                        "name": item["name"],
                        "normalized_name": item.get("normalized_name", ""),
                        "image_urls": item["image_urls"],
                        "product_type": item["product_type"],
                        "family_title": item.get("family_title", ""),
                        "description": item["description"],
                        "is_smart_snack": item["is_smart_snack"],
                        "nova_label": item["nova_label"],
                        "is_good_choice": item["is_good_choice"]
                    }
                })
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("""
                SELECT DISTINCT ON (wi.gtin) 
                    wi.id, wi.gtin, wi.added_at, wi.group_id,
                    p.name, p.normalized_name, p.image_urls, p.product_type, p.family_title, p.description, p.is_smart_snack, p.nova_label, p.is_good_choice
                FROM wishlist_items wi
                LEFT JOIN products_with_nutrition p ON wi.gtin = p.gtin
                WHERE wi.user_id = %s
                ORDER BY wi.gtin, wi.added_at DESC
            """, (current_user.id,))
            result = cur.fetchall()
            
            # Get group information for each item
            wishlist_items = []
            for row in result:
                # Get all groups this item belongs to
                cur.execute("""
                    SELECT wg.id, wg.name 
                    FROM wishlist_items wi
                    JOIN wishlist_groups wg ON wi.group_id = wg.id
                    WHERE wi.user_id = %s AND wi.gtin = %s AND wi.group_id IS NOT NULL
                """, (current_user.id, row['gtin']))
                groups = cur.fetchall()
                
                item = dict(row)
                wishlist_items.append({
                    "id": item["id"],
                    "gtin": item["gtin"],
                    "added_at": item["added_at"],
                    "group_id": item["group_id"],
                    "groups": [{"id": g['id'], "name": g['name']} for g in groups],
                    "product": {
                        "name": item["name"],
                        "normalized_name": item.get("normalized_name", ""),
                        "image_urls": item["image_urls"],
                        "product_type": item["product_type"],
                        "family_title": item.get("family_title", ""),
                        "description": item["description"],
                        "is_smart_snack": item["is_smart_snack"],
                        "nova_label": item["nova_label"],
                        "is_good_choice": item["is_good_choice"]
                    }
                })
            cur.close()
        
        return {"items": wishlist_items, "total_items": len(wishlist_items)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch wishlist items: {str(e)}")

@router.post("/wishlist/add")
async def add_to_wishlist(
    request: AddToWishlistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a product to wishlist"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            # First check if item already exists in main wishlist (group_id IS NULL)
            check_query = text("""
                SELECT id FROM wishlist_items 
                WHERE user_id = :user_id AND gtin = :gtin AND group_id IS NULL
            """)
            existing = db.execute(check_query, {
                "user_id": current_user.id,
                "gtin": request.gtin
            }).fetchone()
            
            if existing:
                return {"message": "Product already in wishlist"}
            
            # Add to main wishlist (group_id IS NULL)
            query = text("""
                INSERT INTO wishlist_items (user_id, gtin, group_id)
                VALUES (:user_id, :gtin, NULL)
                RETURNING *
            """)
            result = db.execute(query, {
                "user_id": current_user.id,
                "gtin": request.gtin
            }).fetchone()
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            
            # First check if item already exists in main wishlist (group_id IS NULL)
            cur.execute("""
                SELECT id FROM wishlist_items 
                WHERE user_id = %s AND gtin = %s AND group_id IS NULL
            """, (current_user.id, request.gtin))
            existing = cur.fetchone()
            
            if existing:
                cur.close()
                return {"message": "Product already in wishlist"}
            
            # Add to main wishlist (group_id IS NULL)
            cur.execute("""
                INSERT INTO wishlist_items (user_id, gtin, group_id)
                VALUES (%s, %s, NULL)
                RETURNING *
            """, (current_user.id, request.gtin))
            result = cur.fetchone()
            db.commit()
            cur.close()
        
        if not result:
            return {"message": "Product already in wishlist"}
        
        return {"message": "Product added to wishlist successfully", "item": dict(result)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to wishlist: {str(e)}")

@router.delete("/wishlist/remove")
async def remove_from_wishlist(
    request: WishlistItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from wishlist (and all groups)"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            # First check what groups this item is in
            check_query = text("""
                SELECT wi.id, wi.group_id, wg.name as group_name 
                FROM wishlist_items wi 
                LEFT JOIN wishlist_groups wg ON wi.group_id = wg.id 
                WHERE wi.user_id = :user_id AND wi.gtin = :gtin
            """)
            items = db.execute(check_query, {"user_id": current_user.id, "gtin": request.gtin}).fetchall()
            
            if not items:
                raise HTTPException(status_code=404, detail="Wishlist item not found")
            
            # Get group names for the response
            group_names = []
            for item in items:
                if item.group_id is not None and item.group_name:
                    group_names.append(item.group_name)
            
            # Remove all instances of this item (from main wishlist and all groups)
            delete_query = text("DELETE FROM wishlist_items WHERE user_id = :user_id AND gtin = :gtin")
            db.execute(delete_query, {"user_id": current_user.id, "gtin": request.gtin})
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            
            # First check what groups this item is in
            cur.execute("""
                SELECT wi.id, wi.group_id, wg.name as group_name 
                FROM wishlist_items wi 
                LEFT JOIN wishlist_groups wg ON wi.group_id = wg.id 
                WHERE wi.user_id = %s AND wi.gtin = %s
            """, (current_user.id, request.gtin))
            items = cur.fetchall()
            
            if not items:
                cur.close()
                raise HTTPException(status_code=404, detail="Wishlist item not found")
            
            # Get group names for the response
            group_names = []
            for item in items:
                if item['group_id'] is not None and item['group_name']:
                    group_names.append(item['group_name'])
            
            # Remove all instances of this item (from main wishlist and all groups)
            cur.execute("DELETE FROM wishlist_items WHERE user_id = %s AND gtin = %s", 
                       (current_user.id, request.gtin))
            db.commit()
            cur.close()
        
        # Return information about what was removed
        response_data = {"message": "Item removed from wishlist successfully"}
        if group_names:
            response_data["removed_from_groups"] = group_names
            response_data["message"] = f"Item removed from wishlist and {len(group_names)} group(s): {', '.join(group_names)}"
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from wishlist: {str(e)}")

@router.delete("/wishlist/clear")
async def clear_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from wishlist"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("DELETE FROM wishlist_items WHERE user_id = :user_id")
            db.execute(query, {"user_id": current_user.id})
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("DELETE FROM wishlist_items WHERE user_id = %s", (current_user.id,))
            db.commit()
            cur.close()
        
        return {"message": "Wishlist cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear wishlist: {str(e)}")

# Utility endpoint to check if product is in cart/wishlist
@router.get("/product/{gtin}/status")
async def get_product_status(
    gtin: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if a product is in cart and/or wishlist"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            cart_query = text("SELECT quantity FROM cart_items WHERE user_id = :user_id AND gtin = :gtin")
            wishlist_query = text("SELECT id FROM wishlist_items WHERE user_id = :user_id AND gtin = :gtin")
            
            cart_result = db.execute(cart_query, {"user_id": current_user.id, "gtin": gtin}).fetchone()
            wishlist_result = db.execute(wishlist_query, {"user_id": current_user.id, "gtin": gtin}).fetchone()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("SELECT quantity FROM cart_items WHERE user_id = %s AND gtin = %s", (current_user.id, gtin))
            cart_result = cur.fetchone()
            cur.execute("SELECT id FROM wishlist_items WHERE user_id = %s AND gtin = %s", (current_user.id, gtin))
            wishlist_result = cur.fetchone()
            cur.close()
        
        return {
            "gtin": gtin,
            "in_cart": cart_result is not None,
            "cart_quantity": cart_result[0] if cart_result else 0,
            "in_wishlist": wishlist_result is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get product status: {str(e)}")

# Wishlist Groups Endpoints
@router.get("/wishlist-groups")
async def get_wishlist_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all wishlist groups for the current user"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("""
                SELECT 
                    wg.id,
                    wg.name,
                    wg.description,
                    wg.is_public,
                    wg.created_at,
                    wg.updated_at,
                    COUNT(DISTINCT wgm.user_id) as member_count,
                    COUNT(DISTINCT wi.gtin) as item_count,
                    CASE WHEN wgm2.role = 'owner' THEN true ELSE false END as is_owner,
                    COALESCE(wgm2.role, 'member') as user_role
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id
                LEFT JOIN wishlist_items wi ON wg.id = wi.group_id
                LEFT JOIN wishlist_group_members wgm2 ON wg.id = wgm2.group_id AND wgm2.user_id = :user_id
                WHERE wg.user_id = :user_id OR wgm2.user_id = :user_id
                GROUP BY wg.id, wg.name, wg.description, wg.is_public, wg.created_at, wg.updated_at, wgm2.role
                ORDER BY wg.updated_at DESC
            """)
            result = db.execute(query, {"user_id": current_user.id}).fetchall()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("""
                SELECT 
                    wg.id,
                    wg.name,
                    wg.description,
                    wg.is_public,
                    wg.created_at,
                    wg.updated_at,
                    COUNT(DISTINCT wgm.user_id) as member_count,
                    COUNT(DISTINCT wi.gtin) as item_count,
                    CASE WHEN wgm2.role = 'owner' THEN true ELSE false END as is_owner,
                    COALESCE(wgm2.role, 'member') as user_role
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id
                LEFT JOIN wishlist_items wi ON wg.id = wi.group_id
                LEFT JOIN wishlist_group_members wgm2 ON wg.id = wgm2.group_id AND wgm2.user_id = %s
                WHERE wg.user_id = %s OR wgm2.user_id = %s
                GROUP BY wg.id, wg.name, wg.description, wg.is_public, wg.created_at, wg.updated_at, wgm2.role
                ORDER BY wg.updated_at DESC
            """, (current_user.id, current_user.id, current_user.id))
            result = cur.fetchall()
            cur.close()
        
        groups = []
        for row in result:
            if hasattr(row, 'id'):
                # SQLAlchemy result
                groups.append({
                    "id": row.id,
                    "name": row.name,
                    "description": row.description,
                    "is_public": row.is_public,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                    "member_count": row.member_count,
                    "item_count": row.item_count,
                    "is_owner": row.is_owner,
                    "user_role": row.user_role
                })
            else:
                # psycopg2 result
                groups.append({
                    "id": row['id'],
                    "name": row['name'],
                    "description": row['description'],
                    "is_public": row['is_public'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at'],
                    "member_count": row['member_count'],
                    "item_count": row['item_count'],
                    "is_owner": row['is_owner'],
                    "user_role": row['user_role']
                })
        
        return groups
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch wishlist groups: {str(e)}")

@router.post("/wishlist-groups")
async def create_wishlist_group(
    group_data: WishlistGroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new wishlist group"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            # Check if group with same name already exists for this user
            existing_query = text("SELECT id FROM wishlist_groups WHERE user_id = :user_id AND name = :name")
            existing = db.execute(existing_query, {"user_id": current_user.id, "name": group_data.name}).fetchone()
            
            if existing:
                raise HTTPException(status_code=400, detail="A wishlist group with this name already exists")
            
            # Create the group
            create_query = text("""
                INSERT INTO wishlist_groups (user_id, name, description, is_public, created_at, updated_at)
                VALUES (:user_id, :name, :description, :is_public, NOW(), NOW())
                RETURNING id, name, description, is_public, created_at, updated_at
            """)
            
            result = db.execute(create_query, {
                "user_id": current_user.id,
                "name": group_data.name,
                "description": group_data.description,
                "is_public": group_data.is_public
            })
            
            group_row = result.fetchone()
            
            # Add user as owner of the group
            member_query = text("""
                INSERT INTO wishlist_group_members (group_id, user_id, role, joined_at)
                VALUES (:group_id, :user_id, 'owner', NOW())
            """)
            
            db.execute(member_query, {
                "group_id": group_row.id,
                "user_id": current_user.id
            })
            
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            
            # Check if group with same name already exists for this user
            cur.execute("SELECT id FROM wishlist_groups WHERE user_id = %s AND name = %s", 
                       (current_user.id, group_data.name))
            existing = cur.fetchone()
            
            if existing:
                cur.close()
                raise HTTPException(status_code=400, detail="A wishlist group with this name already exists")
            
            # Create the group
            cur.execute("""
                INSERT INTO wishlist_groups (user_id, name, description, is_public, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                RETURNING id, name, description, is_public, created_at, updated_at
            """, (current_user.id, group_data.name, group_data.description, group_data.is_public))
            
            group_row = cur.fetchone()
            
            # Add user as owner of the group
            cur.execute("""
                INSERT INTO wishlist_group_members (group_id, user_id, role, joined_at)
                VALUES (%s, %s, 'owner', NOW())
            """, (group_row['id'], current_user.id))
            
            db.commit()
            cur.close()
        
        # Handle both SQLAlchemy and psycopg2 results
        if hasattr(group_row, 'id'):
            # SQLAlchemy result
            return {
                "id": group_row.id,
                "name": group_row.name,
                "description": group_row.description,
                "is_public": group_row.is_public,
                "created_at": group_row.created_at,
                "updated_at": group_row.updated_at,
                "member_count": 1,
                "item_count": 0,
                "is_owner": True,
                "user_role": "owner"
            }
        else:
            # psycopg2 result
            return {
                "id": group_row['id'],
                "name": group_row['name'],
                "description": group_row['description'],
                "is_public": group_row['is_public'],
                "created_at": group_row['created_at'],
                "updated_at": group_row['updated_at'],
                "member_count": 1,
                "item_count": 0,
                "is_owner": True,
                "user_role": "owner"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create wishlist group: {str(e)}")

@router.delete("/wishlist-groups/{group_id}")
async def delete_wishlist_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a wishlist group"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            # Check if user owns the group
            check_query = text("SELECT user_id FROM wishlist_groups WHERE id = :group_id")
            group = db.execute(check_query, {"group_id": group_id}).fetchone()
            
            if not group:
                raise HTTPException(status_code=404, detail="Wishlist group not found")
            
            if group.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="You can only delete your own wishlist groups")
            
            # Delete the group (cascade will handle members and items)
            delete_query = text("DELETE FROM wishlist_groups WHERE id = :group_id")
            db.execute(delete_query, {"group_id": group_id})
            
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            
            # Check if user owns the group
            cur.execute("SELECT user_id FROM wishlist_groups WHERE id = %s", (group_id,))
            group = cur.fetchone()
            
            if not group:
                cur.close()
                raise HTTPException(status_code=404, detail="Wishlist group not found")
            
            if group['user_id'] != current_user.id:
                cur.close()
                raise HTTPException(status_code=403, detail="You can only delete your own wishlist groups")
            
            # Delete the group (cascade will handle members and items)
            cur.execute("DELETE FROM wishlist_groups WHERE id = %s", (group_id,))
            
            db.commit()
            cur.close()
        
        return {"message": "Wishlist group deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete wishlist group: {str(e)}")

@router.post("/wishlist-groups/{group_id}/add-items")
async def add_items_to_group(
    group_id: int,
    items_data: WishlistGroupItems,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add items to a wishlist group"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            # Check if user has access to the group
            access_query = text("""
                SELECT wg.id, wgm.role
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id AND wgm.user_id = :user_id
                WHERE wg.id = :group_id AND (wg.user_id = :user_id OR wgm.user_id = :user_id)
            """)
            
            access = db.execute(access_query, {"group_id": group_id, "user_id": current_user.id}).fetchone()
            
            if not access:
                raise HTTPException(status_code=404, detail="Wishlist group not found or access denied")
            
            # Check if user has write permission (owner or admin)
            if access.role not in ['owner', 'admin']:
                raise HTTPException(status_code=403, detail="You don't have permission to add items to this group")
            
            added_count = 0
            skipped_count = 0
            
            for gtin in items_data.gtins:
                try:
                    # Check if item already exists in the group
                    existing_in_group_query = text("SELECT id FROM wishlist_items WHERE group_id = :group_id AND gtin = :gtin")
                    existing_in_group = db.execute(existing_in_group_query, {"group_id": group_id, "gtin": gtin}).fetchone()
                    
                    if existing_in_group:
                        skipped_count += 1
                        continue
                    
                    # Check if item exists in user's wishlist (without group)
                    existing_wishlist_query = text("SELECT id FROM wishlist_items WHERE user_id = :user_id AND gtin = :gtin AND group_id IS NULL")
                    existing_wishlist = db.execute(existing_wishlist_query, {"user_id": current_user.id, "gtin": gtin}).fetchone()
                    
                    if not existing_wishlist:
                        # Item doesn't exist in wishlist, add it to main wishlist first
                        insert_wishlist_query = text("""
                            INSERT INTO wishlist_items (user_id, gtin, added_at)
                            VALUES (:user_id, :gtin, NOW())
                        """)
                        
                        db.execute(insert_wishlist_query, {
                            "user_id": current_user.id,
                            "gtin": gtin
                        })
                    
                    # Add item to the group (separate record)
                    insert_group_query = text("""
                        INSERT INTO wishlist_items (user_id, gtin, group_id, added_at)
                        VALUES (:user_id, :gtin, :group_id, NOW())
                    """)
                    
                    db.execute(insert_group_query, {
                        "user_id": current_user.id,
                        "gtin": gtin,
                        "group_id": group_id
                    })
                    
                    added_count += 1
                    
                except Exception as e:
                    print(f"Error adding item {gtin}: {e}")
                    skipped_count += 1
                    continue
            
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            
            # Check if user has access to the group
            cur.execute("""
                SELECT wg.id, wgm.role
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id AND wgm.user_id = %s
                WHERE wg.id = %s AND (wg.user_id = %s OR wgm.user_id = %s)
            """, (current_user.id, group_id, current_user.id, current_user.id))
            
            access = cur.fetchone()
            
            if not access:
                cur.close()
                raise HTTPException(status_code=404, detail="Wishlist group not found or access denied")
            
            # Check if user has write permission (owner or admin)
            if access['role'] not in ['owner', 'admin']:
                cur.close()
                raise HTTPException(status_code=403, detail="You don't have permission to add items to this group")
            
            added_count = 0
            skipped_count = 0
            
            for gtin in items_data.gtins:
                try:
                    # Check if item already exists in the group
                    cur.execute("SELECT id FROM wishlist_items WHERE group_id = %s AND gtin = %s", 
                               (group_id, gtin))
                    existing_in_group = cur.fetchone()
                    
                    if existing_in_group:
                        skipped_count += 1
                        continue
                    
                    # Check if item exists in user's wishlist (without group)
                    cur.execute("SELECT id FROM wishlist_items WHERE user_id = %s AND gtin = %s AND group_id IS NULL", 
                               (current_user.id, gtin))
                    existing_wishlist = cur.fetchone()
                    
                    if not existing_wishlist:
                        # Item doesn't exist in wishlist, add it to main wishlist first
                        cur.execute("""
                            INSERT INTO wishlist_items (user_id, gtin, added_at)
                            VALUES (%s, %s, NOW())
                        """, (current_user.id, gtin))
                    
                    # Add item to the group (separate record)
                    cur.execute("""
                        INSERT INTO wishlist_items (user_id, gtin, group_id, added_at)
                        VALUES (%s, %s, %s, NOW())
                    """, (current_user.id, gtin, group_id))
                    
                    added_count += 1
                    
                except Exception as e:
                    print(f"Error adding item {gtin}: {e}")
                    skipped_count += 1
                    continue
            
            db.commit()
            cur.close()
        
        return {
            "message": f"Successfully added {added_count} items to the wishlist group",
            "added_count": added_count,
            "skipped_count": skipped_count,
            "total_requested": len(items_data.gtins)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add items to group: {str(e)}")

@router.delete("/wishlist-groups/{group_id}/remove-items")
async def remove_items_from_group(
    group_id: int,
    items_data: WishlistGroupItems,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove items from a wishlist group"""
    
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            # Check if user has access to the group
            access_query = text("""
                SELECT wg.id, wgm.role
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id AND wgm.user_id = :user_id
                WHERE wg.id = :group_id AND (wg.user_id = :owner_id OR wgm.user_id = :member_id)
            """)
            
            access = db.execute(access_query, {
                "user_id": current_user.id,
                "group_id": group_id,
                "owner_id": current_user.id,
                "member_id": current_user.id
            }).fetchone()
            
            if not access:
                raise HTTPException(status_code=404, detail="Wishlist group not found or access denied")
            
            # Check if user has write permission (owner or admin)
            if access.role not in ['owner', 'admin']:
                raise HTTPException(status_code=403, detail="You don't have permission to remove items from this group")
            
            removed_count = 0
            skipped_count = 0
            
            for gtin in items_data.gtins:
                try:
                    # Remove item from the group
                    delete_query = text("""
                        DELETE FROM wishlist_items 
                        WHERE user_id = :user_id AND gtin = :gtin AND group_id = :group_id
                    """)
                    
                    result = db.execute(delete_query, {
                        "user_id": current_user.id,
                        "gtin": gtin,
                        "group_id": group_id
                    })
                    
                    if result.rowcount > 0:
                        removed_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    print(f"Error removing item {gtin}: {e}")
                    skipped_count += 1
                    continue
            
            db.commit()
        else:
            # psycopg2 connection
            cur = db.cursor()
            
            # Check if user has access to the group
            cur.execute("""
                SELECT wg.id, wgm.role
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id AND wgm.user_id = %s
                WHERE wg.id = %s AND (wg.user_id = %s OR wgm.user_id = %s)
            """, (current_user.id, group_id, current_user.id, current_user.id))
            
            access = cur.fetchone()
            
            if not access:
                cur.close()
                raise HTTPException(status_code=404, detail="Wishlist group not found or access denied")
            
            # Check if user has write permission (owner or admin)
            if access['role'] not in ['owner', 'admin']:
                cur.close()
                raise HTTPException(status_code=403, detail="You don't have permission to remove items from this group")
            
            removed_count = 0
            skipped_count = 0
            
            for gtin in items_data.gtins:
                try:
                    # Remove item from the group
                    cur.execute("""
                        DELETE FROM wishlist_items 
                        WHERE user_id = %s AND gtin = %s AND group_id = %s
                    """, (current_user.id, gtin, group_id))
                    
                    if cur.rowcount > 0:
                        removed_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    print(f"Error removing item {gtin}: {e}")
                    skipped_count += 1
                    continue
            
            db.commit()
            cur.close()
        
        return {
            "message": f"Successfully removed {removed_count} items from the wishlist group",
            "removed_count": removed_count,
            "skipped_count": skipped_count,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove items from group: {str(e)}")

@router.put("/wishlist-groups/{group_id}")
async def update_wishlist_group(
    group_id: int,
    group_data: WishlistGroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a wishlist group"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            # Check if user has access to the group
            access_query = text("""
                SELECT wg.id, wgm.role
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id AND wgm.user_id = :user_id
                WHERE wg.id = :group_id AND (wg.user_id = :owner_id OR wgm.user_id = :member_id)
            """)
            
            access = db.execute(access_query, {
                "user_id": current_user.id,
                "group_id": group_id,
                "owner_id": current_user.id,
                "member_id": current_user.id
            }).fetchone()
            
            if not access:
                raise HTTPException(status_code=404, detail="Wishlist group not found or access denied")
            
            # Check if user has write permission (owner or admin)
            if access.role not in ['owner', 'admin']:
                raise HTTPException(status_code=403, detail="You don't have permission to update this group")
            
            # Check if name is being changed and if it conflicts with existing group
            if group_data.name:
                existing_query = text("""
                    SELECT id FROM wishlist_groups 
                    WHERE user_id = :user_id AND name = :name AND id != :group_id
                """)
                existing = db.execute(existing_query, {
                    "user_id": current_user.id,
                    "name": group_data.name,
                    "group_id": group_id
                }).fetchone()
                
                if existing:
                    raise HTTPException(status_code=400, detail="A wishlist group with this name already exists")
            
            # Build update query dynamically
            update_fields = []
            update_params = {"group_id": group_id}
            
            if group_data.name is not None:
                update_fields.append("name = :name")
                update_params["name"] = group_data.name
            
            if group_data.description is not None:
                update_fields.append("description = :description")
                update_params["description"] = group_data.description
            
            if group_data.is_public is not None:
                update_fields.append("is_public = :is_public")
                update_params["is_public"] = group_data.is_public
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            update_fields.append("updated_at = NOW()")
            
            update_query = text(f"""
                UPDATE wishlist_groups 
                SET {', '.join(update_fields)}
                WHERE id = :group_id
                RETURNING id, name, description, is_public, created_at, updated_at
            """)
            
            result = db.execute(update_query, update_params).fetchone()
            db.commit()
            
        else:
            # psycopg2 connection
            cur = db.cursor()
            
            # Check if user has access to the group
            cur.execute("""
                SELECT wg.id, wgm.role
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id AND wgm.user_id = %s
                WHERE wg.id = %s AND (wg.user_id = %s OR wgm.user_id = %s)
            """, (current_user.id, group_id, current_user.id, current_user.id))
            
            access = cur.fetchone()
            
            if not access:
                cur.close()
                raise HTTPException(status_code=404, detail="Wishlist group not found or access denied")
            
            # Check if user has write permission (owner or admin)
            if access['role'] not in ['owner', 'admin']:
                cur.close()
                raise HTTPException(status_code=403, detail="You don't have permission to update this group")
            
            # Check if name is being changed and if it conflicts with existing group
            if group_data.name:
                cur.execute("""
                    SELECT id FROM wishlist_groups 
                    WHERE user_id = %s AND name = %s AND id != %s
                """, (current_user.id, group_data.name, group_id))
                existing = cur.fetchone()
                
                if existing:
                    cur.close()
                    raise HTTPException(status_code=400, detail="A wishlist group with this name already exists")
            
            # Build update query dynamically
            update_fields = []
            update_params = []
            
            if group_data.name is not None:
                update_fields.append("name = %s")
                update_params.append(group_data.name)
            
            if group_data.description is not None:
                update_fields.append("description = %s")
                update_params.append(group_data.description)
            
            if group_data.is_public is not None:
                update_fields.append("is_public = %s")
                update_params.append(group_data.is_public)
            
            if not update_fields:
                cur.close()
                raise HTTPException(status_code=400, detail="No fields to update")
            
            update_fields.append("updated_at = NOW()")
            
            # Add group_id at the end for WHERE clause
            update_params.append(group_id)
            
            update_query = f"""
                UPDATE wishlist_groups 
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id, name, description, is_public, created_at, updated_at
            """
            
            print(f"Debug - Update query: {update_query}")
            print(f"Debug - Update params: {update_params}")
            
            cur.execute(update_query, update_params)
            result = cur.fetchone()
            db.commit()
            cur.close()
        
        # Handle both SQLAlchemy and psycopg2 results
        if hasattr(result, 'id'):
            # SQLAlchemy result
            return {
                "id": result.id,
                "name": result.name,
                "description": result.description,
                "is_public": result.is_public,
                "created_at": result.created_at,
                "updated_at": result.updated_at
            }
        else:
            # psycopg2 result
            return {
                "id": result['id'],
                "name": result['name'],
                "description": result['description'],
                "is_public": result['is_public'],
                "created_at": result['created_at'],
                "updated_at": result['updated_at']
            }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update wishlist group: {str(e)}")

@router.get("/wishlist-groups/{group_id}")
async def get_wishlist_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific wishlist group by ID"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("""
                SELECT wg.*, 
                       COUNT(DISTINCT wgm2.user_id) as member_count,
                       COUNT(DISTINCT wi.id) as item_count,
                       wgm.role as user_role,
                       CASE WHEN wg.user_id = :user_id THEN true ELSE false END as is_owner
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id AND wgm.user_id = :user_id
                LEFT JOIN wishlist_group_members wgm2 ON wg.id = wgm2.group_id
                LEFT JOIN wishlist_items wi ON wg.id = wi.group_id
                WHERE wg.id = :group_id AND (wg.user_id = :user_id OR wgm.user_id = :user_id)
                GROUP BY wg.id, wgm.role
            """)
            result = db.execute(query, {
                "group_id": group_id,
                "user_id": current_user.id
            }).fetchone()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("""
                SELECT wg.*, 
                       COUNT(DISTINCT wgm2.user_id) as member_count,
                       COUNT(DISTINCT wi.id) as item_count,
                       wgm.role as user_role,
                       CASE WHEN wg.user_id = %s THEN true ELSE false END as is_owner
                FROM wishlist_groups wg
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id AND wgm.user_id = %s
                LEFT JOIN wishlist_group_members wgm2 ON wg.id = wgm2.group_id
                LEFT JOIN wishlist_items wi ON wg.id = wi.group_id
                WHERE wg.id = %s AND (wg.user_id = %s OR wgm.user_id = %s)
                GROUP BY wg.id, wgm.role
            """, (current_user.id, current_user.id, group_id, current_user.id, current_user.id))
            result = cur.fetchone()
            cur.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Wishlist group not found or access denied")
        
        return {
            "id": result["id"],
            "name": result["name"],
            "description": result["description"],
            "is_public": result["is_public"],
            "created_at": result["created_at"],
            "updated_at": result["updated_at"],
            "member_count": result["member_count"],
            "item_count": result["item_count"],
            "user_role": result["user_role"],
            "is_owner": result["is_owner"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching wishlist group {group_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch wishlist group: {str(e)}")

@router.get("/wishlist-groups/{group_id}/items")
async def get_group_items(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all items in a specific wishlist group"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("""
                SELECT wi.*, p.name, p.normalized_name, p.image_urls, p.product_type, p.family_title, p.description, p.is_smart_snack, p.nova_label, p.is_good_choice
                FROM wishlist_items wi
                LEFT JOIN products_with_nutrition p ON wi.gtin = p.gtin
                LEFT JOIN wishlist_groups wg ON wi.group_id = wg.id
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id AND wgm.user_id = :user_id
                WHERE wi.group_id = :group_id AND (wg.user_id = :user_id OR wgm.user_id = :user_id)
                ORDER BY wi.added_at DESC
            """)
            result = db.execute(query, {
                "group_id": group_id,
                "user_id": current_user.id
            }).fetchall()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("""
                SELECT wi.*, p.name, p.normalized_name, p.image_urls, p.product_type, p.family_title, p.description, p.is_smart_snack, p.nova_label, p.is_good_choice
                FROM wishlist_items wi
                LEFT JOIN products_with_nutrition p ON wi.gtin = p.gtin
                LEFT JOIN wishlist_groups wg ON wi.group_id = wg.id
                LEFT JOIN wishlist_group_members wgm ON wg.id = wgm.group_id AND wgm.user_id = %s
                WHERE wi.group_id = %s AND (wg.user_id = %s OR wgm.user_id = %s)
                ORDER BY wi.added_at DESC
            """, (current_user.id, group_id, current_user.id, current_user.id))
            result = cur.fetchall()
            cur.close()
        
        group_items = []
        for row in result:
            item = dict(row)
            group_items.append({
                "id": item["id"],
                "gtin": item["gtin"],
                "added_at": item["added_at"],
                "product": {
                    "name": item["name"],
                    "normalized_name": item.get("normalized_name", ""),
                    "image_urls": item["image_urls"],
                    "product_type": item["product_type"],
                    "family_title": item.get("family_title", ""),
                    "description": item["description"],
                    "is_smart_snack": item["is_smart_snack"],
                    "nova_label": item["nova_label"],
                    "is_good_choice": item["is_good_choice"]
                }
            })
        
        return {"items": group_items, "total_items": len(group_items)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch group items: {str(e)}") 