# API Documentation
## Nutrigence FastAPI Backend

### 📋 Table of Contents
1. [Overview](#overview)
2. [API Architecture](#api-architecture)
3. [Authentication System](#authentication-system)
4. [Core Endpoints](#core-endpoints)
5. [Product Endpoints](#product-endpoints)
6. [Cart & Wishlist Endpoints](#cart--wishlist-endpoints)
7. [User Management Endpoints](#user-management-endpoints)
8. [Neo4j Graph Endpoints](#neo4j-graph-endpoints)
9. [Error Handling](#error-handling)
10. [Rate Limiting & Security](#rate-limiting--security)
11. [Testing & Development](#testing--development)
12. [Deployment & Monitoring](#deployment--monitoring)

---

## Overview

The Nutrigence API is built with FastAPI, providing a comprehensive REST API for the food intelligence platform. The API handles authentication, product management, user data, and integrates with both PostgreSQL and Neo4j databases.

### 🎯 Key Features
- **RESTful API Design**: Standard REST endpoints with proper HTTP methods
- **JWT Authentication**: Secure token-based authentication with refresh mechanism
- **OAuth Integration**: Google and Apple OAuth support
- **Database Integration**: PostgreSQL for relational data, Neo4j for graph relationships
- **Comprehensive Error Handling**: Detailed error responses with proper HTTP status codes
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Automatic Documentation**: OpenAPI/Swagger documentation

---

## API Architecture

### 🏗️ Project Structure
```
backend/
├── api.py                 # Main FastAPI application entry point
├── auth.py                # Authentication logic and JWT handling
├── auth_api.py            # Authentication API endpoints
├── cart_wishlist_api.py   # Cart and wishlist API endpoints
├── neo4j_api.py           # Neo4j graph database API
├── requirements.txt       # Python dependencies
├── Procfile              # Production deployment configuration
└── .env                  # Environment variables
```

### 🔧 Technology Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary relational database
- **Neo4j**: Graph database for hierarchical relationships
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment

### 🌐 Base URL Configuration
```python
# Production
BASE_URL = "https://nutrigence.app/im-project-backend"

# Development
BASE_URL = "http://localhost:8000"
```

---

## Authentication System

### 🔐 JWT Token Configuration

#### Token Settings
```python
# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Magic Link Configuration
MAGIC_LINK_SECRET_KEY = os.getenv("MAGIC_LINK_SECRET_KEY", "magic-link-secret-key")
MAGIC_LINK_EXPIRE_MINUTES = 15
```

#### Token Types
1. **Access Token**: Short-lived (30 min), used for API calls
2. **Refresh Token**: Long-lived (7 days), used to get new access tokens
3. **Magic Link Token**: Short-lived (15 min), for passwordless login

### 🔄 Authentication Endpoints

#### 1. Email/Password Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Acme Corp",
    "auth_provider": "email",
    "is_verified": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### 2. User Registration
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "company_name": "Tech Corp"
}
```

#### 3. Token Refresh
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 4. Magic Link Authentication
```http
POST /api/auth/magic-link
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Magic link sent to your email"
}
```

#### 5. Magic Link Verification
```http
POST /api/auth/verify
Content-Type: application/json

{
  "token": "magic-link-token-from-email"
}
```

#### 6. Google OAuth
```http
GET /api/auth/google/url
```

**Response:**
```json
{
  "url": "https://accounts.google.com/oauth/authorize?..."
}
```

```http
POST /api/auth/google/callback
Content-Type: application/json

{
  "code": "authorization-code-from-google"
}
```

#### 7. Apple OAuth
```http
GET /api/auth/apple/url
```

**Response:**
```json
{
  "url": "https://appleid.apple.com/auth/authorize?..."
}
```

```http
POST /api/auth/apple/callback
Content-Type: application/json

{
  "code": "authorization-code-from-apple"
}
```

### 🔒 Security Features

#### Token Validation
```python
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

#### CORS Configuration
```python
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
```

---

## Core Endpoints

### 🏠 Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### 📊 API Documentation
```http
GET /docs
```
- Swagger UI documentation
- Interactive API testing interface

```http
GET /redoc
```
- ReDoc documentation
- Alternative documentation format

---

## Product Endpoints

### 🔍 Product Search & Filtering

#### Get Products
```http
GET /api/products?search_term=organic&class_title=Beverages&family_title=Juices&is_smart_snack=true&limit=12&offset=0
```

**Query Parameters:**
- `search_term` (string): Search in product name and description
- `class_title` (string): Filter by product class
- `family_title` (array): Filter by product family (multiple values supported)
- `is_smart_snack` (boolean): Filter smart snacks
- `is_good_choice` (string): Filter good choice products
- `recommended_ok` (string): Filter recommended products
- `limit` (integer): Number of products per page (default: 12)
- `offset` (integer): Pagination offset (default: 0)

**Response:**
```json
{
  "total": 150,
  "limit": 12,
  "offset": 0,
  "products": [
    {
      "gtin": "1234567890123",
      "name": "Organic Apple Juice",
      "normalized_name": "organic apple juice",
      "description": "Pure organic apple juice",
      "brand": "Organic Brand",
      "product_type": "Beverage",
      "gpc_code": "10000001",
      "class_title": "Beverages",
      "family_title": "Juices",
      "is_smart_snack": true,
      "nova_label": "1",
      "is_good_choice": "Yes",
      "recommended_ok": "Recommended",
      "image_urls": [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg"
      ]
    }
  ]
}
```

#### Get Product by GTIN
```http
GET /api/products/{gtin}
```

**Response:**
```json
{
  "gtin": "1234567890123",
  "name": "Organic Apple Juice",
  "description": "Pure organic apple juice",
  "ingredients": "Organic apple juice, vitamin C",
  "brand": "Organic Brand",
  "product_type": "Beverage",
  "nutrition": {
    "calories": 120,
    "protein": 0,
    "fat": 0,
    "carbohydrates": 30
  },
  "allergens": ["None"],
  "diet_claims": ["Organic", "Gluten-Free"],
  "image_urls": [...],
  "hierarchy": {
    "class": "Beverages",
    "family": "Juices",
    "brick": "Apple Juice"
  }
}
```

### 🏷️ Product Categories

#### Get Product Categories
```http
GET /api/categories
```

**Response:**
```json
{
  "categories": [
    {
      "class_title": "Beverages",
      "families": [
        {
          "family_title": "Juices",
          "count": 150
        },
        {
          "family_title": "Sodas",
          "count": 200
        }
      ]
    }
  ]
}
```

---

## Cart & Wishlist Endpoints

### 🛒 Cart Management

#### Get Cart Items
```http
GET /api/cart
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "gtin": "1234567890123",
      "quantity": 2,
      "added_at": "2024-01-15T10:30:00Z",
      "product": {
        "name": "Organic Apple Juice",
        "normalized_name": "organic apple juice",
        "image_urls": [...],
        "product_type": "Beverage",
        "description": "Pure organic apple juice"
      }
    }
  ],
  "total_items": 1
}
```

#### Add Item to Cart
```http
POST /api/cart/add
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "gtin": "1234567890123",
  "quantity": 2
}
```

**Response:**
```json
{
  "message": "Product added to cart successfully",
  "item": {
    "id": 1,
    "user_id": 1,
    "gtin": "1234567890123",
    "quantity": 2,
    "added_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Update Cart Item
```http
PUT /api/cart/update
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "gtin": "1234567890123",
  "quantity": 3
}
```

#### Remove Item from Cart
```http
DELETE /api/cart/remove
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "gtin": "1234567890123"
}
```

#### Clear Cart
```http
DELETE /api/cart/clear
Authorization: Bearer {access_token}
```

### ❤️ Wishlist Management

#### Get Wishlist Items
```http
GET /api/wishlist
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "gtin": "1234567890123",
      "added_at": "2024-01-15T10:30:00Z",
      "groups": [
        {
          "id": 1,
          "name": "Healthy Snacks"
        }
      ],
      "product": {
        "name": "Organic Apple Juice",
        "normalized_name": "organic apple juice",
        "image_urls": [...],
        "product_type": "Beverage",
        "family_title": "Juices",
        "description": "Pure organic apple juice",
        "is_smart_snack": true,
        "nova_label": "1",
        "is_good_choice": "Yes"
      }
    }
  ],
  "total_items": 1
}
```

#### Add Item to Wishlist
```http
POST /api/wishlist/add
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "gtin": "1234567890123",
  "group_id": 1
}
```

#### Remove Item from Wishlist
```http
DELETE /api/wishlist/remove
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "gtin": "1234567890123"
}
```

#### Clear Wishlist
```http
DELETE /api/wishlist/clear
Authorization: Bearer {access_token}
```

### 📁 Wishlist Groups

#### Get Wishlist Groups
```http
GET /api/wishlist-groups
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "groups": [
    {
      "id": 1,
      "name": "Healthy Snacks",
      "description": "Nutritious snack options",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "item_count": 5
    }
  ]
}
```

#### Create Wishlist Group
```http
POST /api/wishlist-groups
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "New Group",
  "description": "Group description"
}
```

#### Update Wishlist Group
```http
PUT /api/wishlist-groups/{id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Updated Group Name",
  "description": "Updated description"
}
```

#### Delete Wishlist Group
```http
DELETE /api/wishlist-groups/{id}
Authorization: Bearer {access_token}
```

#### Add Items to Group
```http
POST /api/wishlist-groups/{id}/add
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "gtins": ["1234567890123", "9876543210987"]
}
```

#### Remove Items from Group
```http
DELETE /api/wishlist-groups/{id}/remove
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "gtins": ["1234567890123"]
}
```

### 🔍 Product Status Check
```http
GET /api/product/{gtin}/status
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "gtin": "1234567890123",
  "in_cart": true,
  "cart_quantity": 2,
  "in_wishlist": true
}
```

---

## User Management Endpoints

### 👤 User Profile

#### Get User Profile
```http
GET /api/user/profile
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Acme Corp",
  "phone": "+1234567890",
  "business_id": "BIZ123",
  "auth_provider": "email",
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Update User Profile
```http
PUT /api/user/profile
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith",
  "company_name": "New Corp",
  "phone": "+1234567890"
}
```

#### Change Password
```http
PUT /api/user/password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

#### Delete Account
```http
DELETE /api/user/account
Authorization: Bearer {access_token}
```

---

## Neo4j Graph Endpoints

### 🌳 Product Hierarchy

#### Get Product Hierarchy
```http
GET /api/hierarchy/{gtin}
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "gtin": "1234567890123",
  "hierarchy": {
    "segments": [
      {
        "id": "10000000",
        "title": "Food & Beverages",
        "level": "segment"
      },
      {
        "id": "10000001",
        "title": "Beverages",
        "level": "class"
      },
      {
        "id": "10000002",
        "title": "Juices",
        "level": "family"
      },
      {
        "id": "10000003",
        "title": "Apple Juice",
        "level": "brick"
      }
    ],
    "relationships": [
      {
        "from": "10000000",
        "to": "10000001",
        "type": "CONTAINS"
      }
    ]
  }
}
```

#### Get Related Products
```http
GET /api/hierarchy/{gtin}/related
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "related_products": [
    {
      "gtin": "9876543210987",
      "name": "Organic Orange Juice",
      "relationship": "same_family",
      "similarity_score": 0.85
    }
  ]
}
```

#### Search Hierarchy
```http
GET /api/hierarchy/search?term=juice
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "results": [
    {
      "id": "10000002",
      "title": "Juices",
      "level": "family",
      "product_count": 150
    }
  ]
}
```

---

## Error Handling

### 📋 Error Response Format

#### Standard Error Response
```json
{
  "detail": "Error message description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/products"
}
```

#### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "error_code": "VALIDATION_ERROR"
}
```

### 🔢 HTTP Status Codes

#### Success Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return

#### Client Error Codes
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation error

#### Server Error Codes
- `500 Internal Server Error`: Server error
- `502 Bad Gateway`: Gateway error
- `503 Service Unavailable`: Service temporarily unavailable

### 🛡️ Error Handling Implementation

#### Custom Exception Handler
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": get_error_code(exc.status_code),
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "error_code": "VALIDATION_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )
```

---

## Rate Limiting & Security

### 🚦 Rate Limiting

#### Configuration
```python
# Rate limiting settings
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Check rate limits
    if is_rate_limited(client_ip, current_time):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    response = await call_next(request)
    return response
```

### 🔐 Security Headers

#### Security Middleware
```python
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response
```

### 🔍 Input Validation

#### Pydantic Models
```python
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str = None
    last_name: str = None
    company_name: str = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class ProductSearch(BaseModel):
    search_term: str = None
    class_title: str = None
    family_title: list[str] = None
    is_smart_snack: bool = None
    limit: int = 12
    offset: int = 0
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v
```

---

## Testing & Development

### 🧪 API Testing

#### Test Endpoints
```python
# Test authentication
def test_login():
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# Test product search
def test_product_search():
    response = client.get("/api/products?search_term=organic")
    assert response.status_code == 200
    assert "products" in response.json()

# Test protected endpoints
def test_protected_endpoint():
    # Get token first
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Test protected endpoint
    response = client.get("/api/cart", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
```

### 🔧 Development Setup

#### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/nutrigence"
export SECRET_KEY="your-secret-key"
export GOOGLE_CLIENT_ID="your-google-client-id"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"

# Run development server
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

#### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# JWT Authentication
SECRET_KEY=your-secret-key-change-in-production
MAGIC_LINK_SECRET_KEY=magic-link-secret-key

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@nutrigence.app
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://nutrigence.app/auth/google/callback

APPLE_CLIENT_ID=your-apple-client-id
APPLE_TEAM_ID=your-apple-team-id
APPLE_KEY_ID=your-apple-key-id
APPLE_PRIVATE_KEY=your-apple-private-key
APPLE_REDIRECT_URI=https://nutrigence.app/auth/apple/callback

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# CORS
FRONTEND_URL=https://nutrigence.app
ENVIRONMENT=development
```

---

## Deployment & Monitoring

### 🚀 Production Deployment

#### DigitalOcean App Platform
```yaml
# .do/app.yaml
name: nutrigence-api
services:
- name: api
  source_dir: /backend
  github:
    repo: your-repo/nutrigence
    branch: main
  run_command: uvicorn api:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: ${DATABASE_URL}
  - key: SECRET_KEY
    value: ${SECRET_KEY}
  - key: ENVIRONMENT
    value: production
```

#### Procfile Configuration
```
web: uvicorn api:app --host 0.0.0.0 --port 8080
```

### 📊 Monitoring & Logging

#### Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": "connected",
        "neo4j": "connected"
    }
```

#### Logging Configuration
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log API requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response
```

### 🔍 Performance Monitoring

#### Database Query Monitoring
```python
# Monitor slow queries
import time
from functools import wraps

def monitor_query_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        query_time = time.time() - start_time
        
        if query_time > 1.0:  # Log slow queries (>1 second)
            logger.warning(f"Slow query detected: {func.__name__} took {query_time:.3f}s")
        
        return result
    return wrapper
```

#### API Response Time Monitoring
```python
@app.middleware("http")
async def response_time_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add response time header
    response.headers["X-Response-Time"] = str(process_time)
    
    # Log slow responses
    if process_time > 2.0:
        logger.warning(f"Slow response: {request.url.path} took {process_time:.3f}s")
    
    return response
```

---

## 🎯 Key Takeaways

### 🏗️ API Design Excellence
1. **RESTful Design**: Standard REST endpoints with proper HTTP methods
2. **Comprehensive Authentication**: JWT tokens with OAuth integration
3. **Robust Error Handling**: Detailed error responses with proper status codes
4. **Security Focused**: Rate limiting, input validation, and security headers

### 🔧 Technical Implementation
1. **FastAPI Framework**: Modern, fast, and automatic documentation
2. **Database Integration**: PostgreSQL for relational data, Neo4j for graphs
3. **Type Safety**: Pydantic models for data validation
4. **Performance Optimized**: Efficient querying and response handling

### 📈 Scalability Features
1. **Rate Limiting**: Prevents API abuse
2. **Caching**: Response caching for improved performance
3. **Monitoring**: Comprehensive logging and health checks
4. **Deployment Ready**: Production-ready configuration

### 🚀 Development Experience
1. **Auto Documentation**: OpenAPI/Swagger integration
2. **Testing Support**: Comprehensive testing framework
3. **Development Tools**: Hot reload and debugging support
4. **Environment Management**: Flexible configuration system

---

*This API documentation provides a comprehensive overview of the FastAPI backend, including all endpoints, authentication methods, and development practices. For specific implementation details, refer to the individual API files and their inline documentation.*

**Last Updated**: January 2025  
**Version**: 1.0  
**Maintained By**: Backend Development Team
