from app import create_app, db
from app.models.post import Post
from app.models.user import User

app = create_app()

with app.app_context():
    print("➕ إضافة منشور اختباري...")
    
    # الحصول على أول مستخدم
    user = User.query.first()
    
    if user:
        # إضافة منشور اختباري
        test_post = Post(
            title="منشور اختباري",
            content="هذا منشور اختباري للتأكد من أن النظام يعمل",
            user_id=user.id,
            is_published=True,
            post_type='text'
        )
        
        db.session.add(test_post)
        db.session.commit()
        print("✅ تم إضافة منشور اختباري منشور")
    else:
        print("❌ لا يوجد مستخدمين في النظام")