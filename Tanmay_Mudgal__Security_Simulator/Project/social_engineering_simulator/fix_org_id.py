from app import create_app, db
from app.models import Organization, User

app = create_app()

with app.app_context():
    with open("fix_org_output_v2.txt", "w", encoding="utf-8") as f:
        f.write("--- Existing Organizations ---\n")
        orgs = Organization.query.all()
        for org in orgs:
            f.write(f"ID: {org.org_id} | Name: {org.name}\n")
            
        f.write("\n--- Updating 'Theguy' ---\n")
        user = User.query.filter_by(username='Theguy').first()
        if user:
            if not user.org_id:
                # Assign to first available org or create one if none exist
                if orgs:
                    target_org = orgs[0]
                    user.org_id = target_org.org_id
                    f.write(f"Assigning to Org: {target_org.name} (ID: {target_org.org_id})\n")
                    db.session.commit()
                    f.write("Update committed.\n")
                else:
                    f.write("No organizations found! Please create one first.\n")
            else:
                f.write(f"User already has Org ID: {user.org_id}\n")
        else:
            f.write("User 'Theguy' not found.\n")
