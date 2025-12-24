import os
from app import create_app, db
from app.models.user import User
from app.models.post import Post
from app.models.suggestion import Suggestion

app = create_app()

with app.app_context():
    # حذف قاعدة البيانات القديمة إذا كانت موجودة
    if os.path.exists('site.db'):
        os.remove('site.db')
        print("🗑️ قاعدة البيانات القديمة تم حذفها")

    # إنشاء الجداول الجديدة
    db.create_all()
    print("✅ الجداول الجديدة تم إنشاؤها")

    # إنشاء مستخدم مدير
    admin_user = User(username='admin', is_admin=True)
    admin_user.set_password('admin123')
    db.session.add(admin_user)

    # إنشاء منشورات تجريبية
    test_post = Post(content='هذا منشور تجريبي بدون عنوان', user_id=1, is_published=True)
    test_post2 = Post(post_type='image', user_id=1, is_published=True)
    db.session.add(test_post)
    db.session.add(test_post2)

    db.session.commit()
    print("🎉 تم إعادة تهيئة قاعدة البيانات بنجاح!")
    print("🔑 بيانات الدخول: admin / admin123")
