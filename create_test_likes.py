from app import create_app
from app.models.post import Post, Like
from app.models.user import User

app = create_app()

with app.app_context():
    print("➕ إنشاء إعجابات تجريبية...")
    
    # الحصول على أول منشور
    post = Post.query.first()
    if not post:
        print("❌ لا توجد منشورات! يجب إنشاء منشور أولاً")
        # إنشاء منشور تجريبي
        user = User.query.first()
        if user:
            post = Post(
                title="منشور تجريبي",
                content="هذا منشور للتجربة",
                user_id=user.id,
                is_published=True
            )
            from app import db
            db.session.add(post)
            db.session.commit()
            print("✅ تم إنشاء منشور تجريبي")
    
    if post:
        # إضافة إعجابات تجريبية
        test_ips = ['127.0.0.1', '192.168.1.1', '10.0.0.1']
        
        for ip in test_ips:
            # التحقق إذا كان الإعجاب موجوداً already
            existing_like = Like.query.filter_by(post_id=post.id, user_ip=ip).first()
            if not existing_like:
                new_like = Like(post_id=post.id, user_ip=ip)
                from app import db
                db.session.add(new_like)
                print(f"✅ تم إضافة إعجاب من IP: {ip}")
        
        db.session.commit()
        print(f"👍 عدد الإعجابات الآن: {len(post.likes)}")
    else:
        print("❌ لا يمكن إنشاء إعجابات بدون منشورات")