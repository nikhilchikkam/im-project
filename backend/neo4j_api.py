import os
from fastapi import APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

load_dotenv(dotenv_path="db scripts/.env")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter(prefix="/api/neo4j", tags=["neo4j"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/hierarchy/{gtin}")
def get_product_hierarchy(gtin: str, db: Session = Depends(get_db)):
    """
    Fetch full hierarchy (ancestors and descendants) for a product from product_hierarchies table.
    Returns nodes (unique GTINs) and relationships (edges).
    """
    try:
        # Recursive CTE for descendants
        descendants_cte = """
        WITH RECURSIVE descendants AS (
            SELECT start_id, end_id, type, level, quantity
            FROM product_hierarchies
            WHERE start_id = :gtin
            UNION ALL
            SELECT ph.start_id, ph.end_id, ph.type, ph.level, ph.quantity
            FROM product_hierarchies ph
            INNER JOIN descendants d ON ph.start_id = d.end_id
        )
        SELECT * FROM descendants
        """
        # Recursive CTE for ancestors
        ancestors_cte = """
        WITH RECURSIVE ancestors AS (
            SELECT start_id, end_id, type, level, quantity
            FROM product_hierarchies
            WHERE end_id = :gtin
            UNION ALL
            SELECT ph.start_id, ph.end_id, ph.type, ph.level, ph.quantity
            FROM product_hierarchies ph
            INNER JOIN ancestors a ON ph.end_id = a.start_id
        )
        SELECT * FROM ancestors
        """
        # Run both queries and combine results
        descendants = db.execute(text(descendants_cte), {"gtin": gtin}).fetchall()
        ancestors = db.execute(text(ancestors_cte), {"gtin": gtin}).fetchall()
        all_rels = descendants + ancestors
        # Remove duplicates
        seen = set()
        relationships = []
        gtins = set([gtin])
        for row in all_rels:
            rel_key = (row.start_id, row.end_id, row.type, row.level, row.quantity)
            if rel_key not in seen:
                seen.add(rel_key)
                relationships.append({
                    "source": row.start_id,
                    "target": row.end_id,
                    "type": row.type,
                    "level": row.level,
                    "quantity": row.quantity
                })
                gtins.add(row.start_id)
                gtins.add(row.end_id)
        nodes = [{"gtin": g} for g in gtins]
        return {"nodes": nodes, "relationships": relationships}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch hierarchy: {str(e)}")

@router.get("/test-connection")
def test_neo4j_connection():
    return {"status": "neo4j connection disabled"} 