"""
Script to create/update admin user with correct password
"""
from app import create_app, db
from app.models import User, Role, UserRole
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

with app.app_context():
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    
    # Password
    password = 'admin123'
    password_hash = generate_password_hash(password)
    
    print(f"Generated hash for password '{password}':")
    print(password_hash)
    print()
    
    if admin:
        print(f"Admin user found (ID: {admin.user_id})")
        print(f"Updating password...")
        admin.password = password_hash
    else:
        print("Admin user not found. Creating new admin user...")
        admin = User(
            username='admin',
            password=password_hash,
            email='admin@secsimulator.local',
            organization='System',
            account_type='Admin',
            created_date=datetime.utcnow(),
            total_score=0,
            vulnerability_level='Low'
        )
        db.session.add(admin)
        db.session.flush()
    
    # Commit changes
    db.session.commit()
    
    # Verify
    admin = User.query.filter_by(username='admin').first()
    print(f"\n✅ Admin user ready!")
    print(f"Username: {admin.username}")
    print(f"Email: {admin.email}")
    print(f"User ID: {admin.user_id}")
    print(f"Password: {password}")
    
    # Check role assignment
    user_role = UserRole.query.filter_by(user_id=admin.user_id).first()
    if user_role:
        role = Role.query.get(user_role.role_id)
        print(f"Role: {role.role_name if role else 'None'}")
    else:
        print("Role: Not assigned")
        # Assign GLOBAL_ADMIN role
        global_admin_role = Role.query.filter_by(role_name='GLOBAL_ADMIN').first()
        if global_admin_role:
            new_user_role = UserRole(
                user_id=admin.user_id,
                role_id=global_admin_role.role_id,
                assigned_date=datetime.utcnow()
            )
            db.session.add(new_user_role)
            db.session.commit()
            print(f"✅ Assigned GLOBAL_ADMIN role")
    
    print(f"\n🔐 Login credentials:")
    print(f"   Username: admin")
    print(f"   Password: {password}")
