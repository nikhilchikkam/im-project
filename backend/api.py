import os
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from neo4j_api import router as neo4j_router
from auth_api import router as auth_router
from cart_wishlist_api import router as cart_wishlist_router
from wishlist_groups_api import router as wishlist_groups_router
from auth import get_db

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # for local development
        "https://nutrigence-app-d2jla.ondigitalocean.app",  # for production
        "https://nutrigence.app",  # custom domain
        os.getenv("FRONTEND_URL", "https://nutrigence.app")  # from environment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(neo4j_router)
app.include_router(auth_router)
app.include_router(cart_wishlist_router)
app.include_router(wishlist_groups_router)

# Only include test router in development
if os.getenv("ENVIRONMENT", "production") == "development":
    from test_auth_endpoint import router as test_auth_router
    app.include_router(test_auth_router)

# Test endpoint for debugging (only in development)
if os.getenv("ENVIRONMENT", "production") == "development":
    @app.get("/api/test-db")
    def test_database(db: Session = Depends(get_db)):
        """Test database connection and wishlist tables"""
        try:
            # Test basic connection
            result = db.execute(text("SELECT 1 as test")).fetchone()
            
            # Check if wishlist_groups table exists
            table_check = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'wishlist_groups'
            """)).fetchone()
            
            # Count wishlist groups
            if table_check:
                count_result = db.execute(text("SELECT COUNT(*) as count FROM wishlist_groups")).fetchone()
                wishlist_count = count_result.count if count_result else 0
            else:
                wishlist_count = "Table not found"
            
            return {
                "database_connection": "Working",
                "wishlist_groups_table": "Exists" if table_check else "Not found",
                "wishlist_groups_count": wishlist_count,
                "test_query": result.test if result else "Failed"
            }
        except Exception as e:
            return {
                "error": str(e),
                "database_connection": "Failed"
            }

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/products")
def get_products(db: Session = Depends(get_db), class_title: str = None, family_title: list[str] = Query(None), search_term: str = None, is_smart_snack: bool = None, is_good_choice: str = None, recommended_ok: str = None, limit: int = 12, offset: int = 0):
    """
    Fetch products from the database.
    This endpoint retrieves a list of all products with nutrition data, optionally filtered by class_title, family_title (multi), search term, is_smart_snack, is_good_choice, recommended_ok, with pagination support.
    Returns pagination metadata: total, limit, offset, and products.
    """
    try:
        base_query = "SELECT gtin, name, normalized_name, description, brand, product_type, gpc_code, class_title, family_title, is_smart_snack, nova_label, is_good_choice, recommended_ok, image_urls FROM products_with_nutrition"
        count_query = "SELECT COUNT(*) FROM products_with_nutrition"
        conditions = []
        params = {}

        if class_title:
            conditions.append("class_title = :class_title")
            params['class_title'] = class_title
        if family_title:
            conditions.append(f"family_title IN :family_titles")
            params['family_titles'] = tuple(family_title)
        if search_term:
            conditions.append("name ILIKE :search_term")
            params['search_term'] = f"%{search_term}%"
        if is_smart_snack is not None:
            conditions.append("is_smart_snack = :is_smart_snack")
            params['is_smart_snack'] = is_smart_snack
        if is_good_choice is not None:
            conditions.append("is_good_choice = :is_good_choice")
            params['is_good_choice'] = is_good_choice
        if recommended_ok is not None:
            conditions.append("recommended_ok = :recommended_ok")
            params['recommended_ok'] = recommended_ok


        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        base_query += where_clause
        count_query += where_clause
        base_query += " ORDER BY name ASC LIMIT :limit OFFSET :offset"
        params['limit'] = limit
        params['offset'] = offset
        query = text(base_query)
        count_q = text(count_query)

        products_result = db.execute(query, params).fetchall()
        total = db.execute(count_q, params).scalar()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "products": [
                {"gtin": p.gtin, "name": p.name, "normalized_name": p.normalized_name, "description": p.description, "brand": p.brand, "product_type": p.product_type, "gpc_code": p.gpc_code, "class_title": p.class_title, "family_title": p.family_title, "is_smart_snack": p.is_smart_snack, "nova_label": p.nova_label, "is_good_choice": p.is_good_choice, "recommended_ok": getattr(p, 'recommended_ok', None), "image_urls": getattr(p, 'image_urls', None)}
                for p in products_result
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{gtin}")
def get_product_details(gtin: str, db: Session = Depends(get_db)):
    """
    Fetch detailed information for a single product, including nutrition facts.
    """
    try:
        product_query = text("SELECT gtin, name, normalized_name, description, ingredients, brand, product_type, gpc_code, class_title, family_title, is_smart_snack, image_urls FROM products_with_nutrition WHERE gtin = :gtin")
        product = db.execute(product_query, {"gtin": gtin}).fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        nutrition_query = text("""
            SELECT nutrient_code, nutrient_label, value, unit, daily_value_intake_percent
            FROM product_nutrition
            WHERE gtin = :gtin
        """)
        nutrition_info_result = db.execute(nutrition_query, {"gtin": gtin}).fetchall()

        product_dict = dict(product._mapping)
        product_dict['nutrition'] = [dict(n._mapping) for n in nutrition_info_result]

        return product_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/nutrition/{gtin}")
def get_product_nutrition(gtin: str, db: Session = Depends(get_db)):
    """
    Fetch nutrition facts and serving information for a single product, using standardized values and units.
    """
    try:
        # Fetch nutrition details
        nutrition_query = text("""
            SELECT nutrient_code, nutrient_label, value, unit, daily_value_intake_percent, standardized_value, standardized_unit
            FROM product_nutrition
            WHERE gtin = :gtin
        """)
        nutrition_info_result = db.execute(nutrition_query, {"gtin": gtin}).fetchall()
        # Prepare nutrients with standardized values/units, fallback to 'N/A' if missing
        nutrients = []
        for n in nutrition_info_result:
            n_map = dict(n._mapping)
            n_map['standardized_value'] = n_map.get('standardized_value') if n_map.get('standardized_value') not in (None, '', 'null') else None
            n_map['standardized_unit'] = n_map.get('standardized_unit') if n_map.get('standardized_unit') not in (None, '', 'null') else None
            nutrients.append(n_map)

        # Fetch serving information
        serving_query = text("""
            SELECT serving_size_value, serving_size_unit, serving_description, 
                   basis_quantity_value, basis_quantity_unit, basis_quantity_type
            FROM serving
            WHERE gtin = :gtin
        """)
        serving_info = db.execute(serving_query, {"gtin": gtin}).fetchone()

        if not nutrition_info_result and not serving_info:
            raise HTTPException(status_code=404, detail="Nutrition and serving information not found for this product")

        return {
            "serving_info": dict(serving_info._mapping) if serving_info else None,
            "nutrients": nutrients
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/allergens/{gtin}")
def get_product_allergens(gtin: str, db: Session = Depends(get_db)):
    """
    Fetch allergen information for a single product, excluding non-indicative statuses.
    """
    try:
        allergen_query = text("""
            SELECT gtin, allergenspecificationagency, allergenspecificationname, allergentypecode, allergentypename, levelofcontainmentcode, allergenstatement, isallergenrelevantdataprovided
            FROM product_allergen
            WHERE gtin = :gtin
              AND (levelofcontainmentcode IS NULL OR levelofcontainmentcode NOT IN (
                'FREE_FROM',
                'Not Derived From',
                'Not intentionally nor inherently included'
              ))
        """)
        allergen_info_result = db.execute(allergen_query, {"gtin": gtin}).fetchall()
        if not allergen_info_result:
            raise HTTPException(status_code=404, detail="Allergen information not found for this product")
        return [dict(a._mapping) for a in allergen_info_result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/diet_claims/{gtin}")
def get_diet_claims(gtin: str, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT diet_types, claims FROM product_diet_claims WHERE gtin = :gtin
        """)
        result = db.execute(query, {"gtin": gtin}).fetchone()
        if not result:
            return {"gtin": gtin, "diet_types": [], "claims": {}}
        return {
            "gtin": gtin,
            "diet_types": result.diet_types if result.diet_types else [],
            "claims": result.claims if result.claims else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 