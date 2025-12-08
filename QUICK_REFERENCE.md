# 🚀 QUICK REFERENCE: Users Table Cleanup

## ⚡ Execute These Commands

### 1️⃣ Clean the Users Table

```sql
USE FlightBookingDB;
TRUNCATE TABLE Users;
```

### 2️⃣ Verify It's Empty

```sql
SELECT COUNT(*) FROM Users;
-- Expected: 0
```

### 3️⃣ View Live Data Anytime

```sql
SELECT * FROM Users;
-- Shows only real user registrations
```

---

## 📋 What Was Done

| Task                   | Status       | Command                          |
| ---------------------- | ------------ | -------------------------------- |
| Delete all users       | ✅ Ready     | `TRUNCATE TABLE Users;`          |
| Reset auto-increment   | ✅ Automatic | Part of TRUNCATE                 |
| Ensure live data only  | ✅ Built-in  | Application controls             |
| Create monitoring view | ✅ Ready     | `SELECT * FROM Live_Users_View;` |

---

## 🔒 Live Data Protection

### How It Works:

```
User Registration → Website Form → api_server.py → MySQL Database
```

### Why It's Secure:

- ✅ No hardcoded test users after TRUNCATE
- ✅ UNIQUE email constraint prevents duplicates
- ✅ AUTO_INCREMENT ensures unique IDs
- ✅ CURRENT_TIMESTAMP tracks registration time
- ✅ Only api_server.py can insert users

---

## 📊 Quick Verification Queries

```sql
-- Total live users
SELECT COUNT(*) FROM Users;

-- Recent registrations (last 10)
SELECT user_id, name, email, registration_date
FROM Users
ORDER BY registration_date DESC
LIMIT 10;

-- Active users (logged in last 30 days)
SELECT COUNT(*) FROM Users
WHERE last_login_date >= DATE_SUB(NOW(), INTERVAL 30 DAY);

-- Users who never logged in
SELECT COUNT(*) FROM Users
WHERE last_login_date IS NULL;
```

---

## 🎯 Files Created

1. **clear_users_table.sql** - Complete cleanup script
2. **USERS_TABLE_CLEANUP_GUIDE.md** - Full documentation
3. **QUICK_REFERENCE.md** - This file

---

## ⚠️ Important Notes

- `TRUNCATE` is **permanent** - cannot be undone
- Always backup before running on production
- After TRUNCATE, only website registrations create users
- `SELECT * FROM Users` **always** shows current live data

---

## 🔄 Regular Maintenance

**Weekly Check:**

```sql
SELECT
    COUNT(*) as total_users,
    COUNT(CASE WHEN last_login_date IS NOT NULL THEN 1 END) as logged_in_users,
    COUNT(CASE WHEN last_login_date IS NULL THEN 1 END) as never_logged_in
FROM Users;
```

**Find inactive users (>90 days):**

```sql
SELECT name, email, last_login_date
FROM Users
WHERE last_login_date < DATE_SUB(NOW(), INTERVAL 90 DAY)
   OR last_login_date IS NULL;
```

---

## 💡 Pro Tips

1. **Before cleanup**: Take a backup

   ```sql
   CREATE TABLE Users_Backup AS SELECT * FROM Users;
   ```

2. **After cleanup**: Monitor first registration

   ```sql
   SELECT * FROM Users WHERE user_id = 1;
   ```

3. **Check application**: Ensure api_server.py is running
   ```bash
   python api_server.py
   ```

---

## ✅ Final Checklist

- [ ] Backup current Users table (if needed)
- [ ] Run `TRUNCATE TABLE Users;`
- [ ] Verify table is empty (`COUNT(*) = 0`)
- [ ] Test registration through website
- [ ] Confirm new user appears with `SELECT * FROM Users;`
- [ ] Check registration_date is current timestamp

**Done! Your Users table now contains ONLY live data! 🎉**
