from app import create_app,db
from app.models import User, Role, UserRole

app = create_app()

with app.app_context():
    with open("debug_output_v2.txt", "w", encoding="utf-8") as f:
        username = "Theguy"
        user = User.query.filter_by(username=username).first()
        
        if not user:
            f.write(f"User {username} not found\n")
        else:
            f.write(f"User: {user.username} (ID: {user.user_id})\n")
            f.write(f"Org ID: {user.org_id}\n")
            
            f.write("\n--- Roles via user.roles relationship ---\n")
            for ur in user.roles:
                f.write(f"UserRole Entry: {ur}\n")
                # Manually fetch role to see what it points to
                role = Role.query.get(ur.role_id)
                f.write(f" -> Points to Role: {role.role_name} (ID: {role.role_id})\n")
                
            f.write("\n--- Direct Property Check ---\n")
            try:
                f.write(f"user.role: {user.role}\n")
                if user.role:
                    f.write(f"user.role.role_name: {user.role.role_name}\n")
            except Exception as e:
                f.write(f"Error checking user.role: {e}\n")
                
            f.write(f"is_org_admin(): {user.is_org_admin()}\n")
            
            # Check available roles
            f.write("\n--- All Available Roles ---\n")
            roles = Role.query.all()
            for r in roles:
                f.write(f"ID: {r.role_id} | Name: {r.role_name}\n")
