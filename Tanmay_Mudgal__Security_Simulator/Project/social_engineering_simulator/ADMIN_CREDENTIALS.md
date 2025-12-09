# 🔐 RBAC Admin Credentials

## Admin Account Access

**Username:** `admin`  
**Password:** `Admin@2025!`  
**Email:** `admin@secsimulator.local`  
**Role:** GLOBAL_ADMIN

---

## Login URL

```
http://localhost:5000/login
```

After logging in, access the admin dashboard at:
```
http://localhost:5000/admin
```

--- 

## Security Recommendations

> [!CAUTION]
> **IMPORTANT**: Change the default password immediately after first login in production environments!

### To change admin password:

1. Log in as admin
2. Navigate to profile settings (when implemented)
3. Update password

Or manually update in database:
```python
from werkzeug.security import generate_password_hash
new_password_hash = generate_password_hash('YourNewPassword123!')
# Update in database
```

---

## Available Admin Roles

### GLOBAL_ADMIN
- **Full system access**
- Manage all organizations
- Manage all users
- Assign roles
- View global analytics
- Access: `/admin/*`

### ORG_ADMIN
- **Organization-level access**
- Manage users within organization
- Create users in organization  
- Manage campaigns
- View organization analytics
- Access: `/admin/org/*`

### LEARNER
- **Regular user access**
- Access learning modules
- Take assessments
- View personal dashboard

---

## Quick Start Guide

1. **Login as Admin**
   - Go to http://localhost:5000/login
   - Enter credentials above

2. **Access Admin Dashboard**
   - Click on "Admin" link (if available in nav)
   - Or navigate directly to http://localhost:5000/admin

3. **Manage Users**
   - Go to http://localhost:5000/admin/users
   - Select role from dropdown
   - Click "Assign" to update user role

4. **Create Org Admin**
   - Assign ORG_ADMIN role to existing user
   - They can now access `/admin/org`

---

## Testing RBAC

### Test Scenarios

**Test 1: Admin Access**
1. Login as `admin`
2. Visit `/admin` - Should succeed ✅
3. Visit `/admin/users` - Should succeed ✅  
4. Visit `/admin/organizations` - Should succeed ✅

**Test 2: Org Admin Access**
1. Create test user and assign ORG_ADMIN role
2. Login with that user
3. Visit `/admin` - Should get 403 ❌
4. Visit `/admin/org` - Should succeed ✅
5. Visit `/admin/users` - Should succeed (filtered to org) ✅

**Test 3: Learner Access**
1. Login as regular user (LEARNER role)
2. Visit `/admin` - Should get 403 ❌
3. Visit `/admin/org` - Should get 403 ❌
4. Visit learning modules - Should succeed ✅

---

## Troubleshooting

### Can't login as admin
- Check database: `SELECT * FROM users WHERE username='admin';`
- Verify role assignment: `SELECT * FROM user_roles WHERE user_id=(SELECT user_id FROM users WHERE username='admin');`
- Re-run migration: `Get-Content migrations/setup_rbac_admin.sql | mysql -u root -p1604 social_engineering_db`

### Getting 403 errors
- Check if user has role assigned
- Verify role has required permissions
- Check logs for detailed error messages

### Role assignment not working
- Ensure admin blueprint is registered
- Check browser console for JavaScript errors
- Verify API endpoint is accessible

---

## API Endpoints

### User Management
- `GET /admin/users` - List all users (with role filter for org admins)
- `POST /admin/users/<id>/role` - Assign role to user

### Organization Management
- `GET /admin/organizations` - List all organizations (GLOBAL_ADMIN only)

### Dashboards
- `GET /admin` - Global admin dashboard (GLOBAL_ADMIN only)
- `GET /admin/org` - Organization admin dashboard (ORG_ADMIN only)
- `GET /admin/analytics` - Global analytics (GLOBAL_ADMIN only)
- `GET /admin/org/reports` - Organization reports (ORG_ADMIN only)

---

## Next Steps

1. ✅ Login with admin credentials
2. ✅ Explore admin dashboard  
3. ✅ Test user role assignment
4. ✅ Create organization admin user
5. ⚠️ Change default password
6. ⚠️ Create additional admin users as needed

**System is ready for role-based access control!** 🎉
