# Local Development Setup Guide

This guide will help you set up the Nutrigence project on your local machine for development.

## 🚀 Quick Setup (5 minutes)

### Prerequisites Check

First, make sure you have these installed:

```bash
# Check Node.js (should be v20+)
node --version

# Check Python (should be 3.9+)
python --version

# Check if you have Git
git --version
```

If any are missing, install them:
- **Node.js**: Download from [nodejs.org](https://nodejs.org/)
- **Python**: Download from [python.org](https://www.python.org/downloads/)
- **Git**: Download from [git-scm.com](https://git-scm.com/downloads)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Mendon

# Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Database Setup

**Option A: Use Docker (Recommended for quick setup)**

```bash
# Install Docker Desktop from docker.com if you haven't
# Then run:
docker run --name nutrigence-postgres -e POSTGRES_DB=nutrigence_db -e POSTGRES_USER=nutrigence_user -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
```

**Option B: Install PostgreSQL locally**

- **Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- **macOS**: `brew install postgresql && brew services start postgresql`
- **Linux**: `sudo apt install postgresql postgresql-contrib`

Then create the database:
```bash
psql -U postgres
CREATE DATABASE nutrigence_db;
CREATE USER nutrigence_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE nutrigence_db TO nutrigence_user;
\q
```

### 3. Backend Setup

```bash
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

# Update .env file with your database URL
# If using Docker: DATABASE_URL=postgresql://nutrigence_user:password@localhost:5432/nutrigence_db
# If using local PostgreSQL: DATABASE_URL=postgresql://nutrigence_user:password@localhost:5432/nutrigence_db

# Start the backend
python api.py
```

### 4. Frontend Setup

```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Start the frontend
npm run dev
```

### 5. Verify Setup

- Backend should be running on: http://localhost:8000
- Frontend should be running on: http://localhost:5173
- Visit http://localhost:5173 in your browser

## 🔧 Detailed Setup

### Environment Configuration

#### Backend Environment (backend/.env)

```bash
# Database
DATABASE_URL=postgresql://nutrigence_user:password@localhost:5432/nutrigence_db

# JWT Settings
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Development Settings
ENVIRONMENT=development
FRONTEND_URL=http://localhost:5173

# Optional: Google OAuth (if you want to test authentication)
# GOOGLE_CLIENT_ID=your-google-client-id
# GOOGLE_CLIENT_SECRET=your-google-client-secret

# Optional: Email (for magic links)
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password
# MAIL_FROM=your-email@gmail.com
# MAIL_PORT=587
# MAIL_SERVER=smtp.gmail.com
```

#### Frontend Environment (frontend/.env)

```bash
# API Configuration
VITE_API_URL=http://localhost:8000

# Development
VITE_ENVIRONMENT=development

# Optional: Google OAuth
# VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### Database Schema Setup

If you need to set up the database schema:

```bash
cd backend/db_scripts

# Run the main setup script
python main.py

# Or run individual scripts if needed
python product_loader.py
python nutrition_loader.py
python serving_loader.py
```

### Sample Data (Optional)

To load sample data for testing:

```bash
cd backend/db_scripts
python main.py --sample-data
```

## 🐳 Docker Alternative Setup

If you prefer using Docker for everything:

### 1. Install Docker Desktop

Download from [docker.com](https://www.docker.com/products/docker-desktop)

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: nutrigence_db
      POSTGRES_USER: nutrigence_user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://nutrigence_user:password@postgres:5432/nutrigence_db
      - JWT_SECRET_KEY=your-super-secret-key
      - ENVIRONMENT=development
      - FRONTEND_URL=http://localhost:5173
    depends_on:
      - postgres
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

### 3. Run with Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔍 Troubleshooting

### Common Issues

#### 1. "Port already in use" Error

```bash
# Find what's using the port
# Windows:
netstat -ano | findstr :8000
# macOS/Linux:
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### 2. Database Connection Issues

```bash
# Test database connection
psql -h localhost -U nutrigence_user -d nutrigence_db

# If using Docker, check if container is running
docker ps | grep postgres
```

#### 3. Python Dependencies Issues

```bash
# Reinstall dependencies
pip uninstall -r requirements.txt
pip install -r requirements.txt

# Or try with --force-reinstall
pip install -r requirements.txt --force-reinstall
```

#### 4. Node.js Issues

```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### 5. Virtual Environment Issues

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# If activation fails, recreate the environment
rm -rf venv
python -m venv venv
# Then activate again
```

### Environment-Specific Solutions

#### Windows

- Use `venv\Scripts\activate` for virtual environment
- Ensure PostgreSQL is in your PATH
- Use Windows PowerShell or Command Prompt

#### macOS

- Use Homebrew for package management
- Install Xcode Command Line Tools: `xcode-select --install`
- Use `source venv/bin/activate` for virtual environment

#### Linux

- Install system dependencies: `sudo apt install python3-dev libpq-dev`
- Use `source venv/bin/activate` for virtual environment
- Ensure proper file permissions

## 🧪 Testing Your Setup

### 1. Backend Health Check

Visit: http://localhost:8000/docs

You should see the FastAPI documentation page.

### 2. Frontend Health Check

Visit: http://localhost:5173

You should see the Nutrigence application.

### 3. API Test

```bash
# Test the products endpoint
curl http://localhost:8000/api/products?limit=5
```

### 4. Database Test

```bash
# Connect to database
psql -h localhost -U nutrigence_user -d nutrigence_db

# Check tables
\dt

# Exit
\q
```

## 📝 Development Workflow

### Daily Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python api.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Database (if using Docker)
docker start nutrigence-postgres
```

### Making Changes

1. **Backend Changes**: The server will auto-reload on file changes
2. **Frontend Changes**: Vite will hot-reload automatically
3. **Database Changes**: Restart the backend after schema changes

### Useful Commands

```bash
# Backend
python api.py                    # Start backend
pip install package-name         # Install new dependency
pip freeze > requirements.txt    # Update requirements

# Frontend
npm run dev                      # Start development server
npm run build                    # Build for production
npm run lint                     # Run linter
npm install package-name         # Install new dependency

# Database
docker start nutrigence-postgres # Start database
docker stop nutrigence-postgres  # Stop database
```

## 🚀 Next Steps

Once your local setup is working:

1. **Explore the codebase**: Check out the main components and pages
2. **Read the documentation**: Review `CUSTOM_HOOKS_DOCUMENTATION.md`
3. **Make a small change**: Try modifying a component or adding a feature
4. **Run tests**: If there are tests, run them to ensure everything works
5. **Check the API**: Explore the FastAPI docs at http://localhost:8000/docs

## 🤝 Getting Help

If you run into issues:

1. Check this troubleshooting section
2. Look at the project's README.md
3. Check the browser console for frontend errors
4. Check the terminal for backend errors
5. Ask the team for help

---

**Happy coding! 🎉**
