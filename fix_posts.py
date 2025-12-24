from app import create_app, db
from app.models.post import Post

app = create_app()

with app.app_context():
    print("🔧 إصلاح المنشورات الحالية...")
    
    posts = Post.query.all()
    for post in posts:
        # إذا كان العنوان None، اجعله string فارغ
        if post.title is None:
            post.title = ""
            print(f"✅ إصلاح العنوان للمنشور {post.id}")
        
        # إذا كان المحتوى None، اجعله string فارغ
        if post.content is None:
            post.content = ""
            print(f"✅ إصلاح المحتوى للمنشور {post.id}")
    
    db.session.commit()
    print("🎉 تم إصلاح جميع المنشورات")
    
    # التحقق
    fixed_posts = Post.query.all()
    for post in fixed_posts:
        print(f"📝 المنشور {post.id}: العنوان='{post.title}', المحتوى='{post.content}'")