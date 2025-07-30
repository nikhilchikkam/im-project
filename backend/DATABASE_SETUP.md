# Database Setup for Authentication

This guide will help you set up the PostgreSQL database for the authentication system.

## Prerequisites

1. **PostgreSQL Database** - Make sure you have a PostgreSQL database running
2. **Database Connection** - You need the connection details (host, port, database name, username, password)
3. **Python Environment** - Make sure you have the required Python packages installed

## Step 1: Install Dependencies

First, install the required Python packages:

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

Create or update your `.env` file in the `backend/db scripts/` directory with your database connection:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Example for local PostgreSQL:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/nutrigence_db

# Example for DigitalOcean managed database:
# DATABASE_URL=postgresql://doadmin:password@host:25060/defaultdb?sslmode=require
```

## Step 3: Create the Users Table

Run the database setup script to create the users table:

```bash
cd backend/db scripts
python create_users_table.py
```

This script will:
- Create the `users` table with all necessary columns
- Add an index on the email column for faster lookups
- Create a trigger to automatically update the `updated_at` timestamp
- Display the table structure for verification

### Expected Output:

```
🚀 Setting up authentication database...
==================================================
🔧 Creating users table...
🔧 Creating email index...
🔧 Creating trigger function...
🔧 Creating update trigger...
✅ Users table created successfully!

📋 Table structure:
--------------------------------------------------------------------------------
Column Name         Data Type       Nullable   Default
--------------------------------------------------------------------------------
id                 integer         NO         nextval('users_id_seq'::regclass)
email              character varying NO        NULL
first_name         character varying YES       NULL
last_name          character varying YES       NULL
company_name       character varying YES       NULL
phone              character varying YES       NULL
business_id        character varying YES       NULL
auth_provider      character varying NO        'email'::character varying
is_verified        boolean         YES        false
created_at         timestamp without time zone YES       now()
updated_at         timestamp without time zone YES       now()

👥 Current users in database: 0

✅ Database setup complete!

📝 Next steps:
1. Configure your .env file with email settings
2. Set up Google OAuth credentials
3. Test the authentication system
```

## Step 4: Test the Database Setup

Run the test script to verify everything is working:

```bash
cd backend/db scripts
python test_auth_system.py
```

This script will:
- Check if all required environment variables are set
- Test the database connection
- Verify the users table exists
- Test user creation functionality
- Test API endpoints (if the server is running)

### Expected Output:

```
🧪 Testing Authentication System
==================================================
🔍 Checking environment variables...
✅ DATABASE_URL: Set
✅ SECRET_KEY: Set
✅ MAGIC_LINK_SECRET_KEY: Set
✅ MAIL_USERNAME: Set
✅ MAIL_PASSWORD: Set
✅ MAIL_FROM: Set
✅ FRONTEND_URL: Set

🔍 Testing database connection...
✅ Users table exists
✅ Found 0 users in database

🔍 Testing user creation...
✅ Test user created/updated: ID 1, Email: test@example.com
   Verified: False

🔍 Testing magic link endpoint...
❌ Could not connect to API server
   Make sure the backend server is running on http://localhost:8000

==================================================
📊 Test Results Summary:
   Environment Variables: ✅
   Database Connection: ✅
   User Creation: ✅
   Magic Link API: ❌
   Google OAuth API: ❌

✅ Core authentication system is ready!
⚠️  API tests failed - make sure the backend server is running
```

## Step 5: Database Schema Details

The `users` table has the following structure:

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NO | Auto-increment | Primary key |
| `email` | VARCHAR(255) | NO | NULL | Unique email address |
| `first_name` | VARCHAR(100) | YES | NULL | User's first name |
| `last_name` | VARCHAR(100) | YES | NULL | User's last name |
| `company_name` | VARCHAR(255) | YES | NULL | Company name (for business accounts) |
| `phone` | VARCHAR(20) | YES | NULL | Phone number |
| `business_id` | VARCHAR(100) | YES | NULL | Business registration number/Tax ID/SSN |
| `auth_provider` | VARCHAR(20) | NO | 'email' | Authentication provider ('email', 'google', 'apple') |
| `is_verified` | BOOLEAN | YES | false | Whether the user's email is verified |
| `created_at` | TIMESTAMP | YES | NOW() | Account creation timestamp |
| `updated_at` | TIMESTAMP | YES | NOW() | Last update timestamp (auto-updated) |

### Indexes:
- Primary key index on `id`
- Unique index on `email` for fast lookups

### Triggers:
- `update_users_updated_at` - Automatically updates `updated_at` when a row is modified

## Step 6: Manual Database Verification

You can also verify the setup manually using `psql`:

```sql
-- Connect to your database
psql -h host -p port -U username -d database_name

-- Check if the table exists
\dt users

-- View table structure
\d users

-- Check for any existing users
SELECT COUNT(*) FROM users;

-- View sample data (if any)
SELECT id, email, auth_provider, is_verified, created_at 
FROM users 
LIMIT 5;
```

## Troubleshooting

### Common Issues:

1. **Connection Error**: 
   - Verify your `DATABASE_URL` is correct
   - Check if PostgreSQL is running
   - Ensure the database exists

2. **Permission Error**:
   - Make sure your database user has CREATE TABLE permissions
   - Check if the user can create indexes and triggers

3. **Table Already Exists**:
   - The script uses `CREATE TABLE IF NOT EXISTS`, so it's safe to run multiple times
   - If you need to recreate the table, drop it first: `DROP TABLE IF EXISTS users;`

4. **Environment Variables Missing**:
   - Make sure your `.env` file is in the correct location (`backend/db scripts/.env`)
   - Check that all required variables are set

### Database Connection Examples:

**Local PostgreSQL:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/nutrigence_db
```

**DigitalOcean Managed Database:**
```env
DATABASE_URL=postgresql://doadmin:password@host:25060/defaultdb?sslmode=require
```

**Heroku PostgreSQL:**
```env
DATABASE_URL=postgresql://username:password@host:port/database_name
```

## Next Steps

After setting up the database:

1. **Configure Email Settings** - Set up SMTP for magic links
2. **Set up OAuth Providers** - Configure Google and Apple OAuth
3. **Test the Authentication System** - Try creating accounts and logging in
4. **Deploy to Production** - Update environment variables for production

The database is now ready to support the authentication system! 