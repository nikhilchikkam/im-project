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
- **Docker** - For containerized deployment
- **VS Code** - Recommended IDE with extensions for React and Python
- **Postman** - For API testing

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
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/nutrigence_db

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth (if using)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Configuration (for magic links)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com

# Neo4j Configuration (if using)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password

# Environment
ENVIRONMENT=development
FRONTEND_URL=http://localhost:5173
```

#### Frontend Environment (`.env` in `frontend/` directory)

```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# Google OAuth (if using)
VITE_GOOGLE_CLIENT_ID=your-google-client-id

# Environment
VITE_ENVIRONMENT=development
```

### 3. Database Setup

#### PostgreSQL Installation

**Windows:**
1. Download PostgreSQL from the official website
2. Run the installer and follow the setup wizard
3. Remember the password you set for the `postgres` user
4. Add PostgreSQL to your system PATH

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE nutrigence_db;
CREATE USER nutrigence_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nutrigence_db TO nutrigence_user;
\q
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
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database scripts (if available)
cd db_scripts
python main.py
cd ..

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
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Neo4j** - Graph database (optional)
- **JWT** - Authentication tokens
- **Pydantic** - Data validation

#### 2. Database Schema

The application uses several database tables:

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

#### 3. Build Commands

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Linting
npm run lint
```

## 🐳 Docker Setup (Optional)

If you prefer using Docker:

### 1. Install Docker

Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)

### 2. Docker Compose

Create a `docker-compose.yml` file in the root directory:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: nutrigence_db
      POSTGRES_USER: nutrigence_user
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  neo4j:
    image: neo4j:5.0
    environment:
      NEO4J_AUTH: neo4j/your-neo4j-password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://nutrigence_user:your_password@postgres:5432/nutrigence_db
    depends_on:
      - postgres
      - neo4j

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
  neo4j_data:
```

### 3. Run with Docker

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Issues

**Problem**: Cannot connect to PostgreSQL
**Solution**:
- Verify PostgreSQL is running
- Check connection string in `.env`
- Ensure database and user exist
- Verify firewall settings

#### 2. Python Dependencies

**Problem**: Import errors or missing packages
**Solution**:
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt
pip install -r requirements.txt

# Check Python version
python --version
```

#### 3. Node.js Issues

**Problem**: npm install fails
**Solution**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 4. Port Conflicts

**Problem**: Port already in use
**Solution**:
```bash
# Find process using port
# Windows:
netstat -ano | findstr :8000
# macOS/Linux:
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Environment-Specific Issues

#### Windows

- Use `venv\Scripts\activate` for virtual environment
- Ensure PostgreSQL is in PATH
- Use Windows-compatible line endings

#### macOS

- Use Homebrew for package management
- Ensure Xcode Command Line Tools are installed
- Use `source venv/bin/activate` for virtual environment

#### Linux

- Install system dependencies: `sudo apt install python3-dev libpq-dev`
- Use `source venv/bin/activate` for virtual environment
- Ensure proper file permissions

## 📊 Data Loading

### Initial Data Setup

The project includes scripts for loading initial data:

```bash
cd backend/db_scripts

# Load product data
python product_loader.py

# Load nutrition data
python nutrition_loader.py

# Load serving data
python serving_loader.py
```

### Sample Data

If you need sample data for testing:

```bash
# Run database setup with sample data
python main.py --sample-data
```

## 🔐 Authentication Setup

### Google OAuth (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:5173/auth/callback`
   - `https://yourdomain.com/auth/callback`
6. Copy Client ID and Secret to environment variables

### JWT Configuration

Generate a secure JWT secret:

```python
import secrets
print(secrets.token_urlsafe(32))
```

## 🚀 Deployment

### Production Environment Variables

```bash
# Backend
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET_KEY=your-production-secret

# Frontend
VITE_API_URL=https://your-api-domain.com
VITE_ENVIRONMENT=production
```

### Build for Production

```bash
# Backend
cd backend
pip install -r requirements.txt
python api.py

# Frontend
cd frontend
npm run build
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 🤝 Support

If you encounter issues during setup:

1. Check the troubleshooting section above
2. Review the project's README.md
3. Check GitHub issues for similar problems
4. Contact the development team

---

**Note**: This setup guide assumes you have basic knowledge of command line tools and development environments. If you're new to any of these technologies, consider reviewing their official documentation first.
