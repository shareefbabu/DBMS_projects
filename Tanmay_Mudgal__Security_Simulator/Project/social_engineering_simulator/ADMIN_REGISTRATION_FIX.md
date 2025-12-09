# Admin Registration Instructions

## Option 1: Register Admin Through Web Interface (Recommended)

1. **Go to Registration Page:**  
   http://localhost:5000/register

2. **Fill in the registration form:**
   - Username: `admin`
   - Password: `admin123` (or any password you prefer)
   - Email: `admin@secsimulator.local`
   - Organization: `System`
   - Account Type: `Admin`

3. **Click Register**

4. **After registration, run this command to assign GLOBAL_ADMIN role:**
   ```bash
   python assign_admin_role.py
   ```

---

## Option 2: Delete Existing Admin and Re-register

If you get "username already exists" error:

1. **Delete the existing admin user:**
   ```sql
   mysql -u root -p1604 social_engineering_db -e "DELETE FROM users WHERE username='admin';"
   ```

2. **Then follow Option 1 steps above**

---

## What This Does

When you register through the web interface:
- Password is automatically hashed correctly by Flask
- User is added to database properly
- Then the script assigns the GLOBAL_ADMIN role

This ensures compatibility with your login system!
