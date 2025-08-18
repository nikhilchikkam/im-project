# Hierarchy & Neo4j Documentation
## Nutrigence Product Hierarchy System

### 📋 Table of Contents
1. [Overview](#overview)
2. [Hierarchy Architecture](#hierarchy-architecture)
3. [Neo4j Implementation](#neo4j-implementation)
4. [Graph Schema](#graph-schema)
5. [API Endpoints](#api-endpoints)
6. [Query Patterns](#query-patterns)
7. [Performance Optimization](#performance-optimization)
8. [Maintenance](#maintenance)

---

## Overview

The Nutrigence hierarchy system uses Neo4j graph database to model product relationships and hierarchical structures. This enables efficient product categorization, similarity analysis, and relationship queries.

### 🎯 Key Features
- **Product Hierarchy**: Multi-level product categorization
- **Similarity Analysis**: Product relationship mapping
- **Graph Queries**: Efficient relationship traversal
- **Visualization**: Interactive hierarchy graphs
- **Performance**: Optimized graph queries and indexing

---

## Hierarchy Architecture

### 🌳 Hierarchy Levels

#### GPC (Global Product Classification) Structure
```
Segment (Level 1)
├── Class (Level 2)
    ├── Family (Level 3)
        ├── Brick (Level 4)
            └── Product (Level 5)
```

#### Example Hierarchy
```
Food & Beverages (Segment)
├── Beverages (Class)
    ├── Juices (Family)
        ├── Apple Juice (Brick)
            ├── Organic Apple Juice (Product)
            ├── Regular Apple Juice (Product)
            └── Apple Cider (Product)
        └── Orange Juice (Brick)
            ├── Fresh Orange Juice (Product)
            └── Concentrated Orange Juice (Product)
    └── Sodas (Family)
        ├── Cola (Brick)
        └── Lemon-Lime (Brick)
```

### 🔗 Relationship Types

#### Hierarchy Relationships
- **CONTAINS**: Parent-child relationships in hierarchy
- **BELONGS_TO**: Product membership in categories
- **SIMILAR_TO**: Product similarity relationships
- **REPLACES**: Product substitution relationships

---

## Neo4j Implementation

### 🚀 Connection Management

#### Neo4j Driver Setup
```python
from neo4j import GraphDatabase
import os

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        self.driver.close()
    
    def verify_connectivity(self):
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Neo4j connection failed: {str(e)}")
            return False
```

#### Session Management
```python
def get_session():
    """Get Neo4j session with proper error handling"""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        return driver.session()
    except Exception as e:
        print(f"Failed to create Neo4j session: {str(e)}")
        return None
```

---

## Graph Schema

### 📊 Node Types

#### Product Nodes
```cypher
// Product node structure
CREATE (p:Product {
    gtin: "1234567890123",
    name: "Organic Apple Juice",
    brand: "Organic Brand",
    class_title: "Beverages",
    family_title: "Juices",
    brick_title: "Apple Juice",
    segment_title: "Food & Beverages",
    is_smart_snack: true,
    nova_label: "1",
    is_good_choice: "Yes"
})
```

#### Category Nodes
```cypher
// Segment node
CREATE (s:Segment {
    id: "10000000",
    title: "Food & Beverages",
    level: 1
})

// Class node
CREATE (c:Class {
    id: "10000001",
    title: "Beverages",
    level: 2
})

// Family node
CREATE (f:Family {
    id: "10000002",
    title: "Juices",
    level: 3
})

// Brick node
CREATE (b:Brick {
    id: "10000003",
    title: "Apple Juice",
    level: 4
})
```

### 🔗 Relationship Types

#### Hierarchy Relationships
```cypher
// Create hierarchy relationships
CREATE (s:Segment {id: "10000000", title: "Food & Beverages"})
CREATE (c:Class {id: "10000001", title: "Beverages"})
CREATE (f:Family {id: "10000002", title: "Juices"})
CREATE (b:Brick {id: "10000003", title: "Apple Juice"})

// Connect hierarchy
CREATE (s)-[:CONTAINS]->(c)
CREATE (c)-[:CONTAINS]->(f)
CREATE (f)-[:CONTAINS]->(b)
```

#### Product Relationships
```cypher
// Product belongs to brick
CREATE (p:Product {gtin: "1234567890123", name: "Organic Apple Juice"})
CREATE (b:Brick {id: "10000003", title: "Apple Juice"})
CREATE (p)-[:BELONGS_TO]->(b)

// Similar products
CREATE (p1:Product {gtin: "1234567890123", name: "Organic Apple Juice"})
CREATE (p2:Product {gtin: "9876543210987", name: "Regular Apple Juice"})
CREATE (p1)-[:SIMILAR_TO {score: 0.85}]->(p2)
```

---

## API Endpoints

### 🌐 Hierarchy API

#### Get Product Hierarchy
```python
@app.get("/api/hierarchy/{gtin}")
async def get_product_hierarchy(gtin: str):
    """Get complete hierarchy for a product"""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Product {gtin: $gtin})-[:BELONGS_TO*]->(c:Category)
            RETURN c.id as category_id, c.title as category_title, c.level as level
            ORDER BY c.level
        """, gtin=gtin)
        
        hierarchy = [record.data() for record in result]
        return {"gtin": gtin, "hierarchy": hierarchy}
```

#### Get Related Products
```python
@app.get("/api/hierarchy/{gtin}/related")
async def get_related_products(gtin: str, limit: int = 10):
    """Get related products based on hierarchy"""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Product {gtin: $gtin})-[:BELONGS_TO]->(b:Brick)
            MATCH (b)<-[:BELONGS_TO]-(related:Product)
            WHERE related.gtin <> $gtin
            RETURN related.gtin as gtin, related.name as name, 
                   related.brand as brand, related.is_smart_snack as is_smart_snack
            LIMIT $limit
        """, gtin=gtin, limit=limit)
        
        related_products = [record.data() for record in result]
        return {"related_products": related_products}
```

#### Search Hierarchy
```python
@app.get("/api/hierarchy/search")
async def search_hierarchy(term: str, level: int = None):
    """Search hierarchy by term and optional level"""
    with driver.session() as session:
        query = """
            MATCH (c:Category)
            WHERE toLower(c.title) CONTAINS toLower($term)
        """
        
        if level:
            query += " AND c.level = $level"
            
        query += """
            RETURN c.id as id, c.title as title, c.level as level,
                   size((c)<-[:BELONGS_TO]-()) as product_count
            ORDER BY c.level, c.title
        """
        
        result = session.run(query, term=term, level=level)
        results = [record.data() for record in result]
        return {"results": results}
```

---

## Query Patterns

### 🔍 Common Queries

#### Get Product Categories
```cypher
// Get all categories for a product
MATCH (p:Product {gtin: "1234567890123"})-[:BELONGS_TO*]->(c:Category)
RETURN c.id as category_id, c.title as category_title, c.level as level
ORDER BY c.level;
```

#### Find Similar Products
```cypher
// Find products in the same category
MATCH (p:Product {gtin: "1234567890123"})-[:BELONGS_TO]->(b:Brick)
MATCH (b)<-[:BELONGS_TO]-(similar:Product)
WHERE similar.gtin <> "1234567890123"
RETURN similar.gtin as gtin, similar.name as name, similar.brand as brand
LIMIT 10;
```

#### Hierarchy Navigation
```cypher
// Navigate up the hierarchy
MATCH (p:Product {gtin: "1234567890123"})-[:BELONGS_TO*]->(c:Category)
RETURN c.title as category, c.level as level
ORDER BY c.level DESC;

// Navigate down the hierarchy
MATCH (s:Segment {title: "Food & Beverages"})-[:CONTAINS*]->(c:Category)
RETURN c.title as category, c.level as level
ORDER BY c.level;
```

#### Product Recommendations
```cypher
// Get product recommendations based on hierarchy
MATCH (p:Product {gtin: "1234567890123"})-[:BELONGS_TO]->(b:Brick)
MATCH (b)<-[:BELONGS_TO]-(recommended:Product)
WHERE recommended.gtin <> "1234567890123"
  AND recommended.is_smart_snack = true
RETURN recommended.gtin as gtin, recommended.name as name,
       recommended.is_good_choice as is_good_choice
ORDER BY recommended.is_good_choice DESC
LIMIT 5;
```

---

## Performance Optimization

### ⚡ Indexing Strategy

#### Node Indexes
```cypher
// Create indexes for better performance
CREATE INDEX product_gtin_index FOR (p:Product) ON (p.gtin);
CREATE INDEX product_name_index FOR (p:Product) ON (p.name);
CREATE INDEX category_id_index FOR (c:Category) ON (c.id);
CREATE INDEX category_title_index FOR (c:Category) ON (c.title);
CREATE INDEX category_level_index FOR (c:Category) ON (c.level);
```

#### Relationship Indexes
```cypher
// Create relationship indexes
CREATE INDEX contains_relationship_index FOR ()-[r:CONTAINS]-() ON (r);
CREATE INDEX belongs_to_relationship_index FOR ()-[r:BELONGS_TO]-() ON (r);
CREATE INDEX similar_to_relationship_index FOR ()-[r:SIMILAR_TO]-() ON (r);
```

### 🚀 Query Optimization

#### Optimized Hierarchy Query
```cypher
// Use parameterized queries for better performance
MATCH (p:Product {gtin: $gtin})-[:BELONGS_TO*]->(c:Category)
USING INDEX p:Product(gtin)
RETURN c.id as category_id, c.title as category_title, c.level as level
ORDER BY c.level;
```

#### Efficient Similarity Search
```cypher
// Optimized similarity search with limits
MATCH (p:Product {gtin: $gtin})-[:BELONGS_TO]->(b:Brick)
MATCH (b)<-[:BELONGS_TO]-(similar:Product)
WHERE similar.gtin <> $gtin
USING INDEX p:Product(gtin)
USING INDEX similar:Product(gtin)
RETURN similar.gtin as gtin, similar.name as name
LIMIT $limit;
```

---

## Maintenance

### 🔧 Graph Maintenance

#### Data Cleanup
```cypher
// Remove orphaned nodes
MATCH (n)
WHERE NOT (n)--()
DELETE n;

// Remove duplicate relationships
MATCH (a)-[r:CONTAINS]->(b)
WITH a, b, collect(r) as rels
WHERE size(rels) > 1
UNWIND tail(rels) as rel
DELETE rel;
```

#### Index Maintenance
```cypher
// Check index usage
SHOW INDEXES;

// Drop unused indexes
DROP INDEX product_name_index IF EXISTS;

// Create new indexes as needed
CREATE INDEX product_brand_index FOR (p:Product) ON (p.brand);
```

### 📊 Monitoring Queries

#### Graph Statistics
```cypher
// Get graph statistics
MATCH (n)
RETURN labels(n) as node_type, count(n) as count
ORDER BY count DESC;

// Get relationship statistics
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC;
```

#### Performance Monitoring
```cypher
// Check query performance
CALL dbms.queryJmx("neo4j.metrics:name=neo4j.page_cache.*") YIELD attributes
RETURN attributes;

// Monitor memory usage
CALL dbms.queryJmx("java.lang:type=Memory") YIELD attributes
RETURN attributes;
```

---

## 🎯 Key Takeaways

### 🏗️ Architecture Excellence
1. **Graph Database Design**: Efficient relationship modeling with Neo4j
2. **Hierarchy Management**: Multi-level product categorization
3. **Performance Optimization**: Strategic indexing and query optimization
4. **Scalable Design**: Efficient graph traversal and relationship queries

### 🔧 Technical Implementation
1. **Neo4j Integration**: Robust graph database implementation
2. **Query Optimization**: Efficient Cypher query patterns
3. **Index Management**: Strategic indexing for performance
4. **API Design**: RESTful endpoints for hierarchy operations

### 📈 Operational Features
1. **Maintenance**: Regular graph cleanup and optimization
2. **Monitoring**: Performance tracking and health monitoring
3. **Scalability**: Efficient handling of large product hierarchies
4. **Flexibility**: Dynamic relationship modeling and queries

---

*This hierarchy and Neo4j documentation provides a comprehensive overview of the graph database implementation, including schema design, query patterns, and optimization strategies. For specific implementation details, refer to the individual Neo4j files and their inline documentation.*

**Last Updated**: January 2025  
**Version**: 1.0  
**Maintained By**: Graph Database Team
