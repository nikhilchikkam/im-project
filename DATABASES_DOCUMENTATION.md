# Databases Documentation
## Nutrigence Database Systems

### 📋 Table of Contents
1. [Overview](#overview)
2. [PostgreSQL Database](#postgresql-database)
3. [Neo4j Graph Database](#neo4j-graph-database)
4. [Database Schema](#database-schema)
5. [Performance Optimization](#performance-optimization)
6. [Backup & Recovery](#backup--recovery)
7. [Monitoring](#monitoring)
8. [Maintenance](#maintenance)

---

## Overview

The Nutrigence platform uses two database systems:
- **PostgreSQL**: Primary relational database for user data, products, and business logic
- **Neo4j**: Graph database for product hierarchies and relationships

### 🎯 Key Features
- **Dual Database Architecture**: Relational + Graph database design
- **Data Integrity**: Proper constraints and relationships
- **Performance Optimization**: Strategic indexing and query optimization
- **Scalability**: Designed for growth and high performance
- **Backup & Recovery**: Comprehensive data protection

---

## PostgreSQL Database

### 🗄️ Primary Database

#### Connection Configuration
```python
# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

#### Core Tables
- **users**: User authentication and profile data
- **cart_items**: Shopping cart functionality
- **wishlist_items**: User wishlists with group organization
- **wishlist_groups**: Wishlist group management
- **products**: Product data from OneWorldSync
- **product_allergen**: Allergen information
- **product_nutrition**: Nutritional data
- **product_diet_claims**: Diet and health claims
- **product_images**: Product image URLs

### 🔗 Table Relationships

#### Entity Relationship Diagram
```
users (1) ──── (many) cart_items
users (1) ──── (many) wishlist_items
users (1) ──── (many) wishlist_groups
wishlist_groups (1) ──── (many) wishlist_items
products (1) ──── (many) product_allergen
products (1) ──── (many) product_nutrition
products (1) ──── (many) product_diet_claims
products (1) ──── (many) product_images
```

#### Foreign Key Constraints
```sql
-- Cart items reference users
ALTER TABLE cart_items 
ADD CONSTRAINT fk_cart_items_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Wishlist items reference users and groups
ALTER TABLE wishlist_items 
ADD CONSTRAINT fk_wishlist_items_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE wishlist_items 
ADD CONSTRAINT fk_wishlist_items_group 
FOREIGN KEY (group_id) REFERENCES wishlist_groups(id) ON DELETE CASCADE;

-- Product-related tables reference products
ALTER TABLE product_allergen 
ADD CONSTRAINT fk_product_allergen_product 
FOREIGN KEY (gtin) REFERENCES products(gtin) ON DELETE CASCADE;
```

---

## Neo4j Graph Database

### 🌳 Graph Database

#### Connection Configuration
```python
# Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

from neo4j import GraphDatabase

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
```

#### Graph Schema
- **Nodes**: Products, Categories, Brands, Segments
- **Relationships**: CONTAINS, BELONGS_TO, SIMILAR_TO
- **Properties**: Product attributes, category information

### 🔗 Graph Relationships

#### Product Hierarchy
```cypher
// Product hierarchy structure
(Product)-[:BELONGS_TO]->(Brick)
(Brick)-[:BELONGS_TO]->(Family)
(Family)-[:BELONGS_TO]->(Class)
(Class)-[:BELONGS_TO]->(Segment)
```

#### Similar Products
```cypher
// Similar product relationships
(Product1)-[:SIMILAR_TO {score: 0.85}]->(Product2)
(Product1)-[:SIMILAR_TO {score: 0.72}]->(Product3)
```

---

## Database Schema

### 📊 PostgreSQL Schema

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    phone VARCHAR(20),
    business_id VARCHAR(100),
    auth_provider VARCHAR(20) NOT NULL DEFAULT 'email',
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Products Table
```sql
CREATE TABLE products (
    gtin VARCHAR(50) PRIMARY KEY,
    name VARCHAR(500),
    description TEXT,
    ingredients TEXT,
    brand VARCHAR(255),
    product_type VARCHAR(100),
    is_consumer_unit BOOLEAN,
    gpc_code VARCHAR(50),
    class_title VARCHAR(255),
    family_title VARCHAR(255),
    is_smart_snack BOOLEAN,
    nova_label VARCHAR(50),
    is_good_choice VARCHAR(10),
    recommended_ok VARCHAR(10),
    image_urls JSONB,
    raw_data TEXT,
    last_updated TIMESTAMP DEFAULT NOW()
);
```

#### Cart Items Table
```sql
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    gtin VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, gtin),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### Wishlist Items Table
```sql
CREATE TABLE wishlist_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    gtin VARCHAR(50) NOT NULL,
    group_id INTEGER,
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, gtin),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES wishlist_groups(id) ON DELETE CASCADE
);
```

### 🌐 Neo4j Schema

#### Product Nodes
```cypher
// Create product node
CREATE (p:Product {
    gtin: "1234567890123",
    name: "Organic Apple Juice",
    brand: "Organic Brand",
    class_title: "Beverages",
    family_title: "Juices"
})
```

#### Category Nodes
```cypher
// Create category hierarchy
CREATE (s:Segment {id: "10000000", title: "Food & Beverages"})
CREATE (c:Class {id: "10000001", title: "Beverages"})
CREATE (f:Family {id: "10000002", title: "Juices"})
CREATE (b:Brick {id: "10000003", title: "Apple Juice"})
```

#### Relationships
```cypher
// Create hierarchy relationships
CREATE (s)-[:CONTAINS]->(c)
CREATE (c)-[:CONTAINS]->(f)
CREATE (f)-[:CONTAINS]->(b)
CREATE (b)-[:CONTAINS]->(p)
```

---

## Performance Optimization

### ⚡ PostgreSQL Optimization

#### Strategic Indexing
```sql
-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_auth_provider ON users(auth_provider);

-- Cart indexes
CREATE INDEX idx_cart_items_user_id ON cart_items(user_id);
CREATE INDEX idx_cart_items_gtin ON cart_items(gtin);

-- Wishlist indexes
CREATE INDEX idx_wishlist_items_user_id ON wishlist_items(user_id);
CREATE INDEX idx_wishlist_items_gtin ON wishlist_items(gtin);
CREATE INDEX idx_wishlist_items_group_id ON wishlist_items(group_id);

-- Product indexes
CREATE INDEX idx_products_gpc_code ON products(gpc_code);
CREATE INDEX idx_products_class_title ON products(class_title);
CREATE INDEX idx_products_family_title ON products(family_title);
CREATE INDEX idx_products_is_smart_snack ON products(is_smart_snack);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_name ON products USING gin(to_tsvector('english', name));
```

#### Query Optimization
```sql
-- Optimized product search query
SELECT p.*, 
       array_agg(DISTINCT pa.allergen_name) as allergens,
       array_agg(DISTINCT pdc.claim_name) as diet_claims
FROM products p
LEFT JOIN product_allergen pa ON p.gtin = pa.gtin
LEFT JOIN product_diet_claims pdc ON p.gtin = pdc.gtin
WHERE p.class_title = $1 
  AND p.is_smart_snack = $2
GROUP BY p.gtin
ORDER BY p.name
LIMIT $3 OFFSET $4;
```

### 🚀 Neo4j Optimization

#### Index Optimization
```cypher
// Create indexes for better performance
CREATE INDEX product_gtin_index FOR (p:Product) ON (p.gtin);
CREATE INDEX category_id_index FOR (c:Category) ON (c.id);
CREATE INDEX category_title_index FOR (c:Category) ON (c.title);
```

#### Query Optimization
```cypher
// Optimized hierarchy query
MATCH (p:Product {gtin: $gtin})-[:BELONGS_TO*]->(c:Category)
RETURN c.id as category_id, c.title as category_title, c.level as level
ORDER BY c.level;
```

---

## Backup & Recovery

### 💾 PostgreSQL Backup

#### Automated Backups
```bash
#!/bin/bash
# PostgreSQL backup script

BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="nutrigence"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump -h localhost -U postgres -d $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

#### Recovery Process
```bash
# Restore from backup
gunzip -c backup_20240115_103000.sql.gz | psql -h localhost -U postgres -d nutrigence
```

### 🔄 Neo4j Backup

#### Neo4j Backup
```bash
#!/bin/bash
# Neo4j backup script

BACKUP_DIR="/backups/neo4j"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup using neo4j-admin
neo4j-admin database backup neo4j --to-path=$BACKUP_DIR/backup_$DATE
```

---

## Monitoring

### 📊 PostgreSQL Monitoring

#### Performance Queries
```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

#### Connection Monitoring
```sql
-- Check active connections
SELECT 
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query_start
FROM pg_stat_activity
WHERE state = 'active';
```

### 📈 Neo4j Monitoring

#### Performance Monitoring
```cypher
// Check database statistics
CALL dbms.queryJmx("neo4j.metrics:name=neo4j.page_cache.*") YIELD attributes
RETURN attributes;

// Check memory usage
CALL dbms.queryJmx("java.lang:type=Memory") YIELD attributes
RETURN attributes;
```

---

## Maintenance

### 🔧 PostgreSQL Maintenance

#### Regular Maintenance
```sql
-- Update table statistics
ANALYZE;

-- Vacuum tables
VACUUM ANALYZE products;
VACUUM ANALYZE users;
VACUUM ANALYZE cart_items;
VACUUM ANALYZE wishlist_items;

-- Reindex tables
REINDEX TABLE products;
REINDEX TABLE users;
```

#### Data Cleanup
```sql
-- Clean up old cart items (older than 30 days)
DELETE FROM cart_items 
WHERE added_at < NOW() - INTERVAL '30 days';

-- Clean up old wishlist items (older than 90 days)
DELETE FROM wishlist_items 
WHERE added_at < NOW() - INTERVAL '90 days';
```

### 🛠️ Neo4j Maintenance

#### Graph Maintenance
```cypher
// Remove orphaned nodes
MATCH (n)
WHERE NOT (n)--()
DELETE n;

// Update node properties
MATCH (p:Product)
WHERE p.last_updated IS NULL
SET p.last_updated = datetime()
RETURN count(p);
```

---

## 🎯 Key Takeaways

### 🏗️ Database Design Excellence
1. **Dual Database Architecture**: Relational + Graph for optimal data modeling
2. **Performance Optimization**: Strategic indexing and query optimization
3. **Data Integrity**: Proper constraints and relationships
4. **Scalability**: Designed for growth and high performance

### 🔧 Technical Implementation
1. **PostgreSQL**: Robust relational database for business data
2. **Neo4j**: Efficient graph database for hierarchical relationships
3. **Backup & Recovery**: Comprehensive data protection strategies
4. **Monitoring**: Real-time performance and health monitoring

### 📈 Operational Features
1. **Maintenance**: Regular optimization and cleanup procedures
2. **Performance**: Optimized queries and indexing strategies
3. **Reliability**: Backup and recovery procedures
4. **Monitoring**: Comprehensive performance tracking

---

*This database documentation provides a comprehensive overview of the database systems, including schema design, optimization strategies, and maintenance procedures. For specific implementation details, refer to the individual database files and their inline documentation.*

**Last Updated**: January 2025  
**Version**: 1.0  
**Maintained By**: Database Administration Team
