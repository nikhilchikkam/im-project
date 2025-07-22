import os
from fastapi import APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from neo4j import GraphDatabase

load_dotenv(dotenv_path="db scripts/.env")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/api/neo4j", tags=["neo4j"])

def get_neo4j_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

@router.get("/hierarchy/{gtin}")
def get_product_hierarchy(gtin: str, db: Session = Depends(get_db)):
    """
    Fetch full hierarchy (ancestors and descendants) for a product from Neo4j, enrich nodes with product names/images from PostgreSQL.
    """
    try:
        cypher = """
        MATCH path1 = (root:Product)-[:CONTAINS*]->(p:Product {gtin: $gtin})
        RETURN path1 as result
        UNION
        MATCH path2 = (p:Product {gtin: $gtin})-[:CONTAINS*]->(child:Product)
        RETURN path2 as result
        UNION
        MATCH (p:Product {gtin: $gtin})
        RETURN p as result
        """
        driver = get_neo4j_driver()
        nodes = set()
        relationships = set()
        with driver.session() as session:
            result = session.run(cypher, gtin=gtin)
            for record in result:
                path = record.get("result")
                if hasattr(path, 'nodes'):
                    for node in path.nodes:
                        nodes.add(node.get('gtin'))
                    for rel in path.relationships:
                        relationships.add((
                            rel.start_node.get('gtin'),
                            rel.end_node.get('gtin'),
                            rel.type,
                            rel.get('level'),
                            rel.get('quantity')
                        ))
                elif hasattr(path, 'get'):
                    nodes.add(path.get('gtin'))
        driver.close()
        # Remove None/empty gtins
        gtins = [g for g in nodes if g]
        # Query PostgreSQL for product names/images
        if gtins:
            placeholders = ','.join([f':gtin{i}' for i in range(len(gtins))])
            sql = text(f"""
                SELECT gtin, name, image_urls
                FROM products_with_nutrition
                WHERE gtin IN ({placeholders})
            """)
            params = {f'gtin{i}': g for i, g in enumerate(gtins)}
            result = db.execute(sql, params).fetchall()
            details = {r.gtin: {"name": r.name, "image_urls": r.image_urls} for r in result}
        else:
            details = {}
        # Enrich nodes
        nodes_list = []
        for gtin in gtins:
            node = {"gtin": gtin}
            if gtin in details:
                node["name"] = details[gtin]["name"]
                node["image_urls"] = details[gtin]["image_urls"]
            nodes_list.append(node)
        relationships_list = [
            {"source": s, "target": t, "type": typ, "level": lvl, "quantity": qty}
            for (s, t, typ, lvl, qty) in relationships
        ]
        return {"nodes": nodes_list, "relationships": relationships_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch hierarchy: {str(e)}")

@router.get("/test-connection")
def test_neo4j_connection():
    return {"status": "neo4j connection enabled"} 