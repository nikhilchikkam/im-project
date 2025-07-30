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
    """Get all wishlist items for the current user"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("""
                SELECT wi.*, p.name, p.normalized_name, p.image_urls, p.product_type, p.family_title, p.description, p.is_smart_snack, p.nova_label, p.is_good_choice
                FROM wishlist_items wi
                LEFT JOIN products_with_nutrition p ON wi.gtin = p.gtin
                WHERE wi.user_id = :user_id
                ORDER BY wi.added_at DESC
            """)
            result = db.execute(query, {"user_id": current_user.id}).fetchall()
        else:
            # psycopg2 connection
            cur = db.cursor()
            cur.execute("""
                SELECT wi.*, p.name, p.normalized_name, p.image_urls, p.product_type, p.family_title, p.description, p.is_smart_snack, p.nova_label, p.is_good_choice
                FROM wishlist_items wi
                LEFT JOIN products_with_nutrition p ON wi.gtin = p.gtin
                WHERE wi.user_id = %s
                ORDER BY wi.added_at DESC
            """, (current_user.id,))
            result = cur.fetchall()
            cur.close()
        
        wishlist_items = []
        for row in result:
            item = dict(row)
            wishlist_items.append({
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
            query = text("""
                INSERT INTO wishlist_items (user_id, gtin)
                VALUES (:user_id, :gtin)
                ON CONFLICT (user_id, gtin) DO NOTHING
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
                INSERT INTO wishlist_items (user_id, gtin)
                VALUES (%s, %s)
                ON CONFLICT (user_id, gtin) DO NOTHING
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
    """Remove item from wishlist"""
    try:
        if hasattr(db, 'execute'):
            # SQLAlchemy session
            query = text("""
                DELETE FROM wishlist_items 
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
                DELETE FROM wishlist_items 
                WHERE user_id = %s AND gtin = %s
                RETURNING *
            """, (current_user.id, request.gtin))
            result = cur.fetchone()
            db.commit()
            cur.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Wishlist item not found")
        
        return {"message": "Item removed from wishlist successfully"}
        
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