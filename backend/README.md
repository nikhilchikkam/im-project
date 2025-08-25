# Backend Documentation

This directory contains the FastAPI backend for the Nutrigence application, providing APIs for product data, user authentication, cart/wishlist management, and Neo4j graph database operations.

## 🏗️ Architecture Overview

The backend is built with **FastAPI** and uses:
- **PostgreSQL** for relational data (products, users, cart, wishlist)
- **Neo4j** for graph data (product hierarchies)
- **JWT** for authentication
- **DigitalOcean Spaces** for file storage

## 📁 Directory Structure

### Core API Files
- **`api.py`** - Main FastAPI application with product endpoints
- **`auth_api.py`** - User authentication and authorization endpoints
- **`cart_wishlist_api.py`** - Shopping cart and wishlist management
- **`neo4j_api.py`** - Graph database operations for product hierarchies
- **`auth.py`** - Authentication utilities and database models

### Data Processing
- **`etl_pipeline/`** - ETL scripts for data processing and loading
  - `data_processing/` - Data transformation and enrichment scripts
  - `initial_load/` - Initial data loading scripts
  - `reference_files/` - Configuration and mapping files

### Database Scripts
- **`db scripts/`** - Miscellaneous database utilities and scripts
  - Product data loaders, allergen mappings, nutrition standardization
  - One-time data processing and cleanup scripts
  - **Note**: These are development utilities, not part of regular workflow

### Graph Database
- **`neo4j scripts/`** - Neo4j database operations
  - `fetch_hierarchies_by_gtin.py` - Fetches product hierarchies from OneWorldSync API
  - `load_hierarchies_to_neo4j.py` - Loads hierarchies into Neo4j database
  - `csv_to_neo4j_loader.py` - Loads product data from CSV to Neo4j
  - `split_batch_29.py` - Utility to split large data files

### Development Scripts
- **`scripts/`** - Miscellaneous development and utility scripts
  - Data analysis, testing, and debugging scripts
  - **Note**: These are development utilities, not part of regular workflow

## 🔌 Main APIs

### 1. Product API (`api.py`)

**Base URL**: `/api`

#### Endpoints

##### `GET /api/products`
Fetches products from the database with comprehensive filtering and pagination.

**Query Parameters**:
- `class_title` (string) - Filter by product class
- `family_title` (list) - Filter by product family (multiple values)
- `search_term` (string) - Search in product names
- `is_smart_snack` (boolean) - Filter by smart snack status
- `is_good_choice` (string) - Filter by good choice status
- `recommended_ok` (string) - Filter by recommendation status
- `limit` (int, default: 12) - Number of products per page
- `offset` (int, default: 0) - Pagination offset

**Response**:
```json
{
  "total": 1500,
  "limit": 12,
  "offset": 0,
  "products": [
    {
      "gtin": "00041303019337",
      "name": "Product Name",
      "normalized_name": "normalized name",
      "description": "Product description",
      "brand": "Brand Name",
      "product_type": "Food",
      "gpc_code": "10000000",
      "class_title": "Beverages",
      "family_title": "Soft Drinks",
      "is_smart_snack": true,
      "nova_label": 1,
      "is_good_choice": "Yes",
      "recommended_ok": "Recommended",
      "image_urls": ["url1", "url2"]
    }
  ]
}
```

##### `GET /api/products/{gtin}`
Fetches detailed information for a specific product by GTIN.

**Response**:
```json
{
  "gtin": "00041303019337",
  "name": "Product Name",
  "description": "Detailed product description",
  "brand": "Brand Name",
  "product_type": "Food",
  "gpc_code": "10000000",
  "class_title": "Beverages",
  "family_title": "Soft Drinks",
  "is_smart_snack": true,
  "nova_label": 1,
  "is_good_choice": "Yes",
  "recommended_ok": "Recommended",
  "image_urls": ["url1", "url2"],
  "nutrition": {
    "calories": 150,
    "protein": 5.0,
    "fat": 2.0,
    "carbohydrates": 30.0
  }
}
```

### 2. Authentication API (`auth_api.py`)

**Base URL**: `/api/auth`

#### Endpoints

##### `POST /api/auth/magic-link`
Sends a magic link to the user's email for passwordless authentication.

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "message": "Magic link sent to your email",
  "email": "user@example.com"
}
```

##### `POST /api/auth/signup`
Creates a new user account and sends a magic link.

**Request Body**:
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Company Inc",
  "phone": "+1234567890",
  "business_id": "BIZ123"
}
```

##### `GET /api/auth/verify`
Verifies the magic link token and logs the user in.

**Query Parameters**:
- `token` (string) - Magic link token

**Response**:
```json
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": true
  }
}
```

##### `POST /api/auth/refresh`
Refreshes the access token using a refresh token.

**Request Body**:
```json
{
  "refresh_token": "refresh_token_here"
}
```

##### `GET /api/auth/google/url`
Gets the Google OAuth URL for authentication.

##### `GET /api/auth/apple/url`
Gets the Apple OAuth URL for authentication.

##### `GET /api/auth/google/callback`
Handles Google OAuth callback.

##### `GET /api/auth/apple/callback`
Handles Apple OAuth callback.

### 3. Cart & Wishlist API (`cart_wishlist_api.py`)

**Base URL**: `/api`

#### Cart Endpoints

##### `GET /api/cart`
Gets all cart items for the current user.

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "gtin": "00041303019337",
      "quantity": 2,
      "added_at": "2024-01-01T12:00:00Z",
      "product": {
        "name": "Product Name",
        "normalized_name": "normalized name",
        "image_urls": ["url1", "url2"],
        "product_type": "Food",
        "description": "Product description"
      }
    }
  ],
  "total_items": 1
}
```

##### `POST /api/cart/add`
Adds a product to the cart.

**Request Body**:
```json
{
  "gtin": "00041303019337",
  "quantity": 2
}
```

##### `PUT /api/cart/update`
Updates the quantity of a cart item.

**Request Body**:
```json
{
  "gtin": "00041303019337",
  "quantity": 3
}
```

##### `DELETE /api/cart/remove/{gtin}`
Removes a product from the cart.

##### `DELETE /api/cart/clear`
Clears all items from the cart.

#### Wishlist Endpoints

##### `GET /api/wishlist`
Gets all wishlist items for the current user.

##### `POST /api/wishlist/add`
Adds a product to the wishlist.

**Request Body**:
```json
{
  "gtin": "00041303019337",
  "group_id": 1
}
```

##### `DELETE /api/wishlist/remove/{gtin}`
Removes a product from the wishlist.

##### `GET /api/wishlist/groups`
Gets all wishlist groups for the current user.

##### `POST /api/wishlist/groups`
Creates a new wishlist group.

**Request Body**:
```json
{
  "name": "My Wishlist",
  "description": "Personal wishlist",
  "is_public": false
}
```

##### `PUT /api/wishlist/groups/{group_id}`
Updates a wishlist group.

##### `DELETE /api/wishlist/groups/{group_id}`
Deletes a wishlist group.

##### `POST /api/wishlist/groups/{group_id}/items`
Adds multiple products to a wishlist group.

**Request Body**:
```json
{
  "gtins": ["00041303019337", "00041303019338"]
}
```

### 4. Neo4j API (`neo4j_api.py`)

**Base URL**: `/api/neo4j`

#### Endpoints

##### `GET /api/neo4j/hierarchy/{gtin}`
Fetches the complete product hierarchy (ancestors and descendants) for a given GTIN.

**Response**:
```json
{
  "nodes": [
    {
      "gtin": "00041303019337",
      "name": "Product Name",
      "image_urls": ["url1", "url2"],
      "product_type": "Food",
      "description": "Product description"
    }
  ],
  "relationships": [
    {
      "parent_gtin": "10041303019334",
      "child_gtin": "00041303019337",
      "type": "CONTAINS",
      "level": 1,
      "quantity": "12"
    }
  ]
}
```

##### `GET /api/neo4j/ancestors/{gtin}`
Fetches all ancestor products (parent hierarchy) for a given GTIN.

##### `GET /api/neo4j/descendants/{gtin}`
Fetches all descendant products (child hierarchy) for a given GTIN.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Authentication
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (for magic links)
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_FROM=your_email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com

# OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
APPLE_CLIENT_ID=your_apple_client_id
APPLE_TEAM_ID=your_apple_team_id
APPLE_KEY_ID=your_apple_key_id
APPLE_PRIVATE_KEY=your_apple_private_key

# Frontend
FRONTEND_URL=https://your-frontend-domain.com

# DigitalOcean Spaces
DO_SPACES_KEY=your_spaces_key
DO_SPACES_SECRET=your_spaces_secret
DO_SPACES_BUCKET=your_bucket_name
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com

# OneWorldSync API
ONEWORLDSYNC_API_KEY=your_api_key
ONEWORLDSYNC_API_SECRET=your_api_secret

# Environment
ENVIRONMENT=production
```


### Neo4j Graph Structure

#### Nodes
- **Product**: `{gtin: string}`

#### Relationships
- **CONTAINS**: `(parent:Product)-[:CONTAINS {quantity: string, level: int}]->(child:Product)`

## 🔒 Security

### Authentication
- JWT-based authentication with access and refresh tokens
- Magic link authentication for passwordless login
- OAuth integration with Google and Apple
- Token refresh mechanism

### Authorization
- Protected endpoints require valid JWT tokens
- User-specific data access (cart, wishlist)
- Role-based access control (future enhancement)

### CORS
- Configured to allow requests from specified frontend domains
- Supports local development and production environments

## 📈 Performance

### Database Optimization
- Indexed queries on frequently accessed fields
- Pagination for large result sets
- Efficient JOIN operations

### Caching
- Consider implementing Redis for session storage
- Query result caching for frequently accessed data

### Monitoring
- Logging for all API endpoints
- Error tracking and monitoring
- Performance metrics collection


## 📝 Logging

### Log Levels
- `INFO` - General application flow
- `WARNING` - Potential issues
- `ERROR` - Error conditions
- `DEBUG` - Detailed debugging information