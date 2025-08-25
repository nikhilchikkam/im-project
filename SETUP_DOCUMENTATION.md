# Nutrigence Project Setup Guide

This guide provides step-by-step instructions for setting up the Nutrigence project on a new device.

## 📋 Prerequisites

Before setting up the project, ensure you have the following installed:

### Required Software
- **Node.js** (v20.x or higher) - [Download here](https://nodejs.org/)
- **Python** (3.9 or higher) - [Download here](https://www.python.org/downloads/)
- **PostgreSQL** (v12 or higher) - [Download here](https://www.postgresql.org/download/)
- **Git** - [Download here](https://git-scm.com/downloads)

### Optional Software
- **VS Code** - Recommended IDE with extensions for React and Python

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Mendon
```

### 2. Environment Setup

Create environment files for both frontend and backend:

#### Backend Environment (`.env` in `backend/` directory)

```bash
ONEWORLDSYNC_APP_ID=
ONEWORLDSYNC_SECRET_KEY=
ONEWORLDSYNC_USER_GLN=
ONEWORLDSYNC_CONTENT1_API_URL=https://content1-api.1worldsync.com


# JWT Configuration (generate these with generate_secrets.py)
SECRET_KEY=
MAGIC_LINK_SECRET_KEY=

# Email Configuration (Gmail)
MAIL_USERNAME=noreply.mendon@gmail.com
MAIL_PASSWORD=
MAIL_FROM=Nutrigence App <noreply@nutrigence.app>
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_TLS=True
MAIL_SSL=False

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=


# Database Configuration
DATABASE_URL=

# JWT Configuration (generate these with generate_secrets.py)
SECRET_KEY=
MAGIC_LINK_SECRET_KEY=


# Frontend URL
FRONTEND_URL=http://localhost:5173


# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=
NEO4J_PASSWORD=

# DigitalOcean Spaces Configuration
SPACES_REGION=sfo3
SPACES_BUCKET=nutrigence-etl
SPACES_SECRET_KEY=/iBQhJ+jWk2FyRkLZTbyCVh2RjTdlmoSy4G+E/MdoMY
SPACES_ACCESS_KEY=DO00CAZ6LEZBMXA7WV4X

# OneWorldSync Configuration
OWS_BATCH_SIZE=1000
OWS_MAX_RETRIES=3
OWS_RETRY_DELAY=5

# ETL Configuration
ETL_BATCH_SIZE=1000
ETL_MAX_WORKERS=4

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=etl_pipeline.log

# API Configuration
API_DELAY=0.1 
```

### 3. Database Setup

#### PostgreSQL Installation


```

### 4. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate


# Install dependencies
pip install -r requirements.txt


# Start the backend server
python api.py
```

The backend should now be running on `http://localhost:8000`

### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend should now be running on `http://localhost:5173`

## 🔧 Detailed Setup Instructions

### Backend Configuration

#### 1. Python Environment

The backend uses Python 3.9+ with the following key dependencies:

- **FastAPI** - Web framework
- **PostgreSQL** - Primary database
- **Neo4j** - Graph database (optional)
- **JWT** - Authentication tokens

#### 2. Database Schema

The application uses several database tables like:

- `users` - User accounts and authentication
- `products` - Product information and nutrition data
- `cart_items` - Shopping cart items
- `wishlist_items` - Wishlist items
- `wishlist_groups` - Wishlist organization

#### 3. API Endpoints

Key API endpoints:

- `GET /api/products` - Product search and filtering
- `POST /api/auth/login` - User authentication
- `GET /api/cart` - Cart operations
- `GET /api/wishlist` - Wishlist operations

### Frontend Configuration

#### 1. React Application

The frontend is built with:

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **React Router** - Navigation

#### 2. Key Dependencies

```json
{
  "react": "^19.1.0",
  "react-dom": "^19.1.0",
  "react-router-dom": "^7.6.2",
  "lucide-react": "^0.514.0",
  "clsx": "^2.1.1"
}
```