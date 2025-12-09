"""
Assign GLOBAL_ADMIN role to admin user
Run this AFTER registering the admin user through the web interface
"""
import os
import sys

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Role, UserRole
from datetime import datetime

app = create_app()

with app.app_context():
    # Find admin user
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("❌ Admin user not found!")
        print("Please register 'admin' user at http://localhost:5000/register first")
        sys.exit(1)
    
    print(f"✅ Found admin user (ID: {admin.user_id})")
    
    # Find GLOBAL_ADMIN role
    global_admin_role = Role.query.filter_by(role_name='GLOBAL_ADMIN').first()
    
    if not global_admin_role:
        print("❌ GLOBAL_ADMIN role not found in database!")
        sys.exit(1)
    
    print(f"✅ Found GLOBAL_ADMIN role (ID: {global_admin_role.role_id})")
    
    # Check if already assigned
    existing = UserRole.query.filter_by(
        user_id=admin.user_id,
        role_id=global_admin_role.role_id
    ).first()
    
    if existing:
        print("✅ Admin user already has GLOBAL_ADMIN role!")
    else:
        # Assign role
        user_role = UserRole(
            user_id=admin.user_id,
            role_id=global_admin_role.role_id,
            assigned_date=datetime.utcnow()
        )
        db.session.add(user_role)
        db.session.commit()
        print("✅ Assigned GLOBAL_ADMIN role to admin user!")
    
    print("\n🎉 Admin setup complete!")
    print(f"   Username: {admin.username}")
    print(f"   Email: {admin.email}")
    print(f"   Role: GLOBAL_ADMIN")
    print(f"\n🔗 Login at: http://localhost:5000/login")
    print(f"🔗 Admin dashboard: http://localhost:5000/admin")
