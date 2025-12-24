from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    print("🔍 التحقق من صلاحيات المستخدمين:")
    
    users = User.query.all()
    for user in users:
        print(f"\n👤 {user.username}:")
        print(f"   - المدير: {user.is_admin}")
        print(f"   - يمكنه النشر: {user.can_post}")
        print(f"   - نشط: {user.is_active}")
        print(f"   - يمكنه إنشاء منشورات: {user.can_create_posts()}")