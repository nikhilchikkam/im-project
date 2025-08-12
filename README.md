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
- Advanced product search and filtering
- Nutrition guideline compliance checking
- Product comparison tools
- Smart snack identification

### 👥 Team Collaboration
- Shared wishlists and product lists
- Group-based organization
- Real-time collaboration features

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

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL
- Docker (optional)

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python api.py
```

### Database Setup
```bash
cd backend/db_scripts
python setup_database.py
```

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

---

**Built with ❤️ by the Mendon Group team**
