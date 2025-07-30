# 🚀 DigitalOcean Deployment Guide

## **Required Code Changes for Production**

### **1. Backend Environment Variables**

Create `backend/.env` with these production values:

```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# JWT & Security (Generate strong secrets!)
SECRET_KEY=your-production-secret-key-here
MAGIC_LINK_SECRET_KEY=your-production-magic-link-secret

# Email Configuration (for magic links)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@nutrigence.app
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# OAuth (if using)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
APPLE_CLIENT_ID=your-apple-client-id
APPLE_TEAM_ID=your-apple-team-id
APPLE_KEY_ID=your-apple-key-id
APPLE_PRIVATE_KEY=your-apple-private-key

# API Base URL
API_BASE_URL=https://your-do-app.ondigitalocean.app

# Environment
ENVIRONMENT=production

# Frontend URL
FRONTEND_URL=https://nutrigence.app
```

### **2. Frontend Environment Variables**

Create `frontend/.env.production`:

```bash
VITE_API_URL=https://your-do-app.ondigitalocean.app
```

### **3. Database Setup**

Run these scripts in order:

```bash
# 1. Create all tables
cd backend
python setup_database.py

# 2. Verify tables exist
python -c "
from auth import get_db
db = get_db()
cursor = db.cursor()
cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\'')
tables = [row['table_name'] for row in cursor.fetchall()]
print('Tables:', tables)
db.close()
"
```

### **4. Security Checklist**

✅ **Generate Strong Secrets**:
```bash
# Use these commands to generate secure keys
python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"
python -c "import secrets; print('MAGIC_LINK_SECRET_KEY:', secrets.token_urlsafe(32))"
```

✅ **Email Configuration**:
- Use Gmail App Password (not regular password)
- Enable 2FA on Gmail account
- Generate App Password in Google Account settings

✅ **OAuth Setup** (if using):
- Configure Google OAuth in Google Cloud Console
- Add production domain to authorized origins
- Update redirect URIs

### **5. DigitalOcean App Platform Configuration**

**Backend Service**:
```yaml
# app.yaml
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-repo
    branch: main
  run_command: uvicorn api:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: ${DATABASE_URL}
  - key: SECRET_KEY
    value: ${SECRET_KEY}
  - key: MAGIC_LINK_SECRET_KEY
    value: ${MAGIC_LINK_SECRET_KEY}
  - key: MAIL_USERNAME
    value: ${MAIL_USERNAME}
  - key: MAIL_PASSWORD
    value: ${MAIL_PASSWORD}
  - key: MAIL_FROM
    value: ${MAIL_FROM}
  - key: MAIL_SERVER
    value: ${MAIL_SERVER}
  - key: MAIL_PORT
    value: ${MAIL_PORT}
  - key: ENVIRONMENT
    value: production
  - key: FRONTEND_URL
    value: ${FRONTEND_URL}
```

**Frontend Service**:
```yaml
- name: frontend
  source_dir: /frontend
  github:
    repo: your-repo
    branch: main
  run_command: npm run build && npx serve -s dist -l $PORT
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: VITE_API_URL
    value: ${VITE_API_URL}
```

### **6. Required Dependencies**

**Backend Requirements** (`backend/requirements.txt`):
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
PyJWT==2.8.0
itsdangerous==2.1.2
authlib==1.2.1
fastapi-mail==1.4.1
pydantic[email]==2.5.0
neo4j==5.15.0
```

**Frontend Dependencies** (`frontend/package.json`):
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.1",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.10"
  }
}
```

### **7. Build Commands**

**Backend**:
```bash
cd backend
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install
npm run build
```

### **8. Health Check Endpoints**

Add these to verify deployment:

```python
# backend/api.py
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/health")
def api_health_check():
    return {"status": "healthy", "api": "working"}
```

### **9. CORS Configuration**

The backend already includes CORS configuration for:
- `http://localhost:5173` (development)
- `https://nutrigence-app-d2jla.ondigitalocean.app` (production)
- `https://nutrigence.app` (custom domain)

### **10. Environment-Specific Code**

The code has been updated to:
- ✅ Only include test endpoints in development
- ✅ Use environment variables for API URLs
- ✅ Handle production vs development configurations
- ✅ Remove debug logging in production

### **11. Deployment Steps**

1. **Prepare Environment**:
   ```bash
   # Generate secrets
   python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"
   python -c "import secrets; print('MAGIC_LINK_SECRET_KEY:', secrets.token_urlsafe(32))"
   ```

2. **Set up Database**:
   ```bash
   cd backend
   python setup_database.py
   ```

3. **Configure DigitalOcean**:
   - Create App Platform project
   - Connect GitHub repository
   - Set environment variables
   - Deploy

4. **Verify Deployment**:
   ```bash
   # Test health endpoints
   curl https://your-app.ondigitalocean.app/health
   curl https://your-app.ondigitalocean.app/api/health
   ```

### **12. Post-Deployment Verification**

✅ **Test Authentication**:
- Sign up with magic link
- Login/logout functionality
- Token refresh

✅ **Test Cart & Wishlist**:
- Add/remove items
- Quantity updates
- Wishlist groups

✅ **Test API Endpoints**:
- Products listing
- Product details
- Nutrition/allergen data

### **13. Monitoring & Logs**

- Monitor DigitalOcean App Platform logs
- Set up error tracking (Sentry recommended)
- Monitor database performance
- Check email delivery for magic links

### **14. Security Best Practices**

✅ **Secrets Management**:
- Use DigitalOcean App Platform secrets
- Never commit `.env` files
- Rotate secrets regularly

✅ **HTTPS**:
- DigitalOcean provides automatic HTTPS
- Verify SSL certificates

✅ **Database Security**:
- Use connection pooling
- Restrict database access
- Regular backups

### **15. Troubleshooting**

**Common Issues**:
1. **CORS Errors**: Check CORS configuration in `api.py`
2. **Database Connection**: Verify `DATABASE_URL` format
3. **Email Not Sending**: Check SMTP credentials
4. **Token Issues**: Verify `SECRET_KEY` is set
5. **Build Failures**: Check Node.js/Python versions

**Debug Commands**:
```bash
# Check environment variables
echo $DATABASE_URL
echo $SECRET_KEY

# Test database connection
python -c "from auth import get_db; db = get_db(); print('DB OK')"

# Check logs
doctl apps logs your-app-id
``` 