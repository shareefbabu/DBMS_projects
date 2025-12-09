# Query to see current level and module structure
from app import create_app, db
from app.models import PathLevel, LearningModule

app = create_app()
app.app_context().push()

print("Current Levels:")
print("=" * 80)
levels = PathLevel.query.order_by(PathLevel.level_number).all()
for level in levels:
    print(f"\nLevel {level.level_number}: {level.level_name}")
    print(f"  Description: {level.description}")
    print(f"  Unlock Score: {level.unlock_score}")
    
    modules = LearningModule.query.filter_by(level_id=level.level_id).all()
    print(f"  Modules ({len(modules)}):")
    for mod in modules:
        print(f"    - {mod.title} ({mod.category.category_name if mod.category else 'No category'})")
