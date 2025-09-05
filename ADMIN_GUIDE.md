# Admin Authentication Guide

## Overview
The Houston Financial Navigator now supports admin accounts with role-based authentication. This guide explains how to create, test, and use admin accounts for demonstration purposes.

## Creating Admin Accounts

### Via Web Interface
1. Navigate to `/register` in your browser
2. Fill out the registration form:
   - **First Name**: Your first name
   - **Last Name**: Your last name
   - **Email**: A valid email address (must be unique)
   - **Password**: A secure password
   - **Account Type**: Select "Admin (For Administrators)"
3. Click "Create Account"
4. You will be automatically logged in and redirected to the admin dashboard at `/admin`

### Via API (for testing/automation)
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "securepassword",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
  }'
```

## Required Fields for Admin Registration

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Unique email address for the admin |
| `password` | string | Yes | Secure password for authentication |
| `first_name` | string | Yes | Admin's first name |
| `last_name` | string | Yes | Admin's last name |
| `role` | string | Yes | Must be set to "admin" for admin accounts |

## Login Flow for Admins

### Automatic Routing
When admins log in, they are automatically routed based on their role:
- **Admin users** → Redirected to `/admin` (Admin Dashboard)
- **Regular users** → Redirected to `/onboarding` or `/dashboard`

### Admin Dashboard Access
- **Route**: `/admin`
- **Protection**: Requires admin role authentication
- **Features**: 
  - Nessie API sandbox for testing
  - Customer and account management tools
  - Financial transaction simulation

## Testing Admin Functionality

### Quick Test Script
A test script is included at `test_admin_auth.py` that verifies:
1. Admin account registration
2. Regular user registration  
3. Admin login with correct role assignment
4. Admin access to protected endpoints
5. Regular user access denial to admin endpoints

Run the test:
```bash
python test_admin_auth.py
```

### Manual Testing Steps

#### 1. Create Admin Account
- Register with role "admin"
- Verify successful creation
- Check automatic redirect to `/admin`

#### 2. Test Admin Access
- Access admin-only endpoints: `/admin/status`
- Use Nessie API features in admin dashboard
- Verify admin functionality works

#### 3. Create Regular User
- Register with role "user" (or leave default)
- Verify normal user flow to `/onboarding`

#### 4. Test Access Protection
- Log in as regular user
- Try to access `/admin` - should be denied
- Verify 403 error for admin-only API endpoints

## Troubleshooting

### Common Issues

#### 1. "Email already registered" Error
**Problem**: Trying to register with an email that's already in use.
**Solution**: Use a different email address or delete the existing user from the database.

#### 2. "Admin access required" Error
**Problem**: Regular user trying to access admin-only resources.
**Solution**: Log in with an admin account or register a new admin account.

#### 3. Role not set correctly
**Problem**: User has no role or incorrect role in database.
**Solution**: Check the database user table and update the role field:
```sql
UPDATE users SET role = 'admin' WHERE email = 'your@email.com';
```

#### 4. Admin dashboard shows 403 error
**Problem**: Authentication not working properly.
**Solutions**:
- Clear browser cookies and log in again
- Check that session cookie is being set
- Verify the FLASK_SECRET environment variable is consistent

#### 5. Frontend routing issues
**Problem**: Admin not redirected to correct page after login.
**Solution**: Check that the user object includes the role field and the login logic handles routing properly.

### Database Schema
The users table includes these fields:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    nessie_customer_id TEXT,
    role TEXT DEFAULT 'user',
    created_at INTEGER
);
```

### API Endpoints

#### Authentication Endpoints
- `POST /auth/register` - Register new user/admin
- `POST /auth/login` - Login user/admin  
- `GET /me` - Get current user info (includes role)
- `POST /auth/logout` - Logout current user

#### Admin-Only Endpoints
- `GET /admin/status` - Admin health check
- `POST /nessie/customers` - Create Nessie customer
- `GET /nessie/customers` - List Nessie customers
- `POST /nessie/customers/{id}/accounts` - Create account
- `GET /nessie/customers/{id}/accounts` - List accounts
- `POST /nessie/accounts/{id}/deposits` - Add deposit
- `POST /nessie/accounts/{id}/purchases` - Add purchase

## Security Notes

1. **Admin Role Assignment**: Only assign admin role to trusted demo accounts
2. **Password Security**: Use strong passwords for admin accounts
3. **Session Management**: Admin sessions use the same JWT token system as regular users
4. **API Protection**: All admin endpoints are protected with role-based access control
5. **Database Security**: Role information is stored securely in the SQLite database

## For Hackathon Judges

### Quick Demo Setup
1. Visit the registration page
2. Create an admin account with your details
3. Select "Admin" from the Account Type dropdown
4. Click "Create Account" - you'll be taken directly to the admin dashboard
5. Test the Nessie API sandbox features

### Demo Features to Highlight
- **Role-based Authentication**: Different user types with appropriate access
- **Admin Dashboard**: Complete Nessie API integration for financial simulation
- **Security**: Proper access control and session management
- **User Experience**: Seamless registration and login flow