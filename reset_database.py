import os
from app import create_app, db
from app.models.user import User
from app.models.post import Post
from app.models.faculty import Faculty 

app = create_app()

with app.app_context():
    # حذف ملف قاعدة البيانات إذا كان موجوداً
    if os.path.exists('site.db'):
        try:
            os.remove('site.db')
            print("🗑️  تم حذف قاعدة البيانات القديمة")
        except Exception as e:
            print(f"❌ خطأ في حذف قاعدة البيانات: {e}")
    
    # إنشاء الجداول الجديدة
    db.create_all()
    print("✅ تم إنشاء الجداول الجديدة")
    
    # إنشاء مستخدم مدير
    #admin_user = User(username='admin', is_admin=True)
    #admin_user.set_password('admin123')
    #db.session.add(admin_user)
    #print("✅ تم إنشاء المستخدم admin")
    
    admin = User(
    username='admin',
    profile_image='default_profile.png',
    is_admin=True,
    is_super_admin=True,   # ← مدير مطلق
    is_active=True,
    can_post=True,
    can_upload_books=True,
    faculty=None           # لا حاجة لتعيين كلية، لأنه المدير المطلق
)
    print("✅ تم إنشاء المستخدم admin")
    admin.set_password('admin199')
    db.session.add(admin)
    
    faculty = Faculty.query.filter_by(name='كلية الحاسوب').first()

    # إنشاء منشور تجريبي بدون عنوان
    test_post = Post(
        content='هذا منشور تجريبي بدون عنوان للتجربة',
        user_id=1,
        is_published=True,
        
    )
    db.session.add(test_post)
    
    # منشور تجريبي بصورة فقط
    test_post2 = Post(
        post_type='image',
        user_id=1,
        is_published=True,
      
    )
    db.session.add(test_post2)
    
    db.session.commit()
    print("✅ تم إنشاء منشورات تجريبية")
    print("🎉 تم إعادة تهيئة قاعدة البيانات بنجاح!")
    print("🔑 بيانات الدخول: admin / admin123")