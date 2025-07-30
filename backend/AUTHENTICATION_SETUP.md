# Authentication Setup Guide

This guide will help you set up the authentication system with magic links and OAuth providers.

## Backend Setup

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-in-production
MAGIC_LINK_SECRET_KEY=your-magic-link-secret-key-change-in-production

# Email Configuration (for magic links)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@nutrigence.app
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Frontend URL (for magic links)
FRONTEND_URL=http://localhost:5173

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Apple OAuth Configuration (optional)
APPLE_CLIENT_ID=your-apple-client-id
APPLE_TEAM_ID=your-apple-team-id
APPLE_KEY_ID=your-apple-key-id
APPLE_PRIVATE_KEY=your-apple-private-key
APPLE_REDIRECT_URI=http://localhost:8000/api/auth/apple/callback

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### 3. Email Setup (for Magic Links)

For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in `MAIL_PASSWORD`

### 4. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Set Application Type to "Web application"
6. Add authorized redirect URIs:
   - `http://localhost:8000/api/auth/google/callback` (development)
   - `https://yourdomain.com/api/auth/google/callback` (production)
7. Copy the Client ID and Client Secret to your `.env` file

### 5. Apple OAuth Setup (Optional)

1. Go to [Apple Developer Console](https://developer.apple.com/)
2. Create an App ID
3. Enable Sign In with Apple
4. Create a Services ID
5. Generate a private key
6. Add the configuration to your `.env` file

## Frontend Setup

### 1. Environment Variables

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### 2. Update API Base URL

The frontend is configured to use relative URLs for API calls, which will work with the current setup.

## Running the Application

### Backend

```bash
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm run dev
```

## Authentication Flow

### Magic Link Flow

1. User enters email on login page
2. Backend sends magic link to user's email
3. User clicks link in email
4. Frontend verifies token with backend
5. User is logged in with JWT tokens

### Google OAuth Flow

1. User clicks "Continue with Google"
2. User is redirected to Google OAuth
3. User authorizes the application
4. Google redirects back with authorization code
5. Backend exchanges code for tokens
6. User is logged in with JWT tokens

### Apple OAuth Flow

1. User clicks "Continue with Apple"
2. User is redirected to Apple OAuth
3. User authorizes the application
4. Apple redirects back with authorization code
5. Backend exchanges code for tokens
6. User is logged in with JWT tokens

## API Endpoints

### Authentication Endpoints

- `POST /api/auth/magic-link` - Send magic link
- `GET /api/auth/verify?token=<token>` - Verify magic link
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/google/url` - Get Google OAuth URL
- `POST /api/auth/google/callback` - Handle Google OAuth callback
- `GET /api/auth/apple/url` - Get Apple OAuth URL
- `POST /api/auth/apple/callback` - Handle Apple OAuth callback
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user
- `PUT /api/auth/profile` - Update user profile

## Security Considerations

1. **JWT Secret**: Use a strong, random secret key
2. **Magic Link Secret**: Use a different strong secret for magic links
3. **HTTPS**: Always use HTTPS in production
4. **Token Expiration**: Access tokens expire in 30 minutes, refresh tokens in 7 days
5. **Email Security**: Use app passwords for email authentication
6. **OAuth Secrets**: Keep OAuth client secrets secure

## Production Deployment

1. Update all URLs to use your production domain
2. Set up proper email service (SendGrid, AWS SES, etc.)
3. Configure CORS for your production domain
4. Use environment-specific secrets
5. Set up proper logging and monitoring
6. Configure rate limiting for authentication endpoints 