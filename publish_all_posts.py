from app import create_app, db
from app.models.post import Post

app = create_app()

with app.app_context():
    print("📝 جعل جميع المنشورات منشورة...")
    
    # جعل جميع المنشورات منشورة
    posts = Post.query.all()
    for post in posts:
        post.is_published = True
    
    db.session.commit()
    print(f"✅ تم نشر {len(posts)} منشور")
    
    # التحقق
    published_count = Post.query.filter_by(is_published=True).count()
    print(f"📊 المنشورات المنشورة الآن: {published_count}")