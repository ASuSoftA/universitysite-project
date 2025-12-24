# list_routes.py
from app import create_app

app = create_app()

print("📋 قائمة جميع الـ routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint} -> {rule.rule}")

print("\n🔍 البحث عن endpoint 'main.index':")
for rule in app.url_map.iter_rules():
    if 'main.index' in rule.endpoint:
        print(f"✅ موجود: {rule.endpoint} -> {rule.rule}")