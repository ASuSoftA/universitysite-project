from app import create_app
from app.models.post import Post
from app.models.like import Like

app = create_app()

with app.app_context():
    print("🧪 اختبار تفاعل المستخدمين:")
    
    # اختبار الإعجاب على منشور
    post = Post.query.first()
    if post:
        print(f"📝 المنشور: {post.title or 'بدون عنوان'}")
        print(f"👍 عدد الإعجابات: {len(post.likes)}")
        
        # إضافة إعجاب تجريبي
        new_like = Like(post_id=post.id, user_ip='127.0.0.1')
        try:
            from app import db
            db.session.add(new_like)
            db.session.commit()
            print("✅ تم إضافة إعجاب تجريبي")
            print(f"👍 عدد الإعجابات الجديد: {len(post.likes)}")
        except Exception as e:
            print(f"❌ خطأ في إضافة الإعجاب: {e}")
    else:
        print("❌ لا توجد منشورات للاختبار")
        
        