# Nutrigence - Food Intelligence Platform

> Initial work for Nutrigence Project. We'll add separate repositories or directories as needed - UI Database Middleware etc.

## 🚀 Project Overview

Nutrigence is a comprehensive food intelligence platform that helps restaurants, distributors, retailers, and manufacturers quickly search, compare, and select food products that align with nutrition guidelines.

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **Location**: `frontend/`
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Key Features**:
  - Product search and comparison
  - Wishlist management with groups
  - Cart functionality
  - User authentication (Google OAuth)
  - Responsive design

### Backend (FastAPI + Python)
- **Location**: `backend/`
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **Key Features**:
  - RESTful API endpoints
  - User authentication and authorization
  - Product data management
  - Wishlist and cart APIs
  - ETL pipeline for data processing

## 🛠️ Key Features

### 🔍 Product Intelligence
- Product search and filtering
- Nutrition guideline compliance checking
- Smart snack identification


### 🔐 Authentication
- Google OAuth integration
- JWT-based authentication
- Automatic token refresh
- Secure session management

### 📊 Data Management
- ETL pipeline for product data
- Comprehensive nutrition information
- Allergen tracking
- Dietary claim support

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**For macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**For Windows:**
```bash
setup.bat
```

### Option 2: Manual Setup

#### Prerequisites
- Node.js 20+
- Python 3.9+
- PostgreSQL
- Git

#### Step-by-step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Mendon
   ```

2. **Set up environment files**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Frontend  
   cp frontend/.env.example frontend/.env
   ```

3. **Set up database**
   ```bash
   # Using Docker (recommended)
   docker run --name nutrigence-postgres -e POSTGRES_DB=nutrigence_db -e POSTGRES_USER=nutrigence_user -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
   ```

4. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python api.py
   ```

5. **Set up frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Visit the application**
   - Frontend: http://localhost:5173
   - Backend API docs: http://localhost:8000/docs

📚 **For detailed setup instructions, see [LOCAL_DEVELOPMENT_SETUP.md](LOCAL_DEVELOPMENT_SETUP.md)**

## 📁 Project Structure

```
nutrigence/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── features/       # Feature-specific components
│   │   ├── contexts/       # React contexts
│   │   └── utils/          # Utility functions
│   └── public/             # Static assets
├── backend/                 # FastAPI backend application
│   ├── api.py              # Main API entry point
│   ├── auth.py             # Authentication logic
│   ├── db_scripts/         # Database setup and migrations
│   ├── etl_pipeline/       # Data processing pipeline
│   └── requirements.txt    # Python dependencies
├── deployment/             # Deployment configurations
└── docker-compose.yml      # Docker setup
```

## 🔧 Development

### Environment Variables
Create `.env` files in both frontend and backend directories with appropriate configuration.

### Database Migrations
Run database scripts in `backend/db_scripts/` to set up the database schema.

### ETL Pipeline
The ETL pipeline in `backend/etl_pipeline/` handles data processing and loading.

## 📝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

Mendon Group. 2025. All rights reserved.
