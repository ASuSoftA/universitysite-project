from app import create_app, db
from app.models.post import Post

app = create_app()

with app.app_context():
    print("🔧 إصلاح العناوين الفارغة...")
    
    posts = Post.query.all()
    for post in posts:
        if post.title is None:
            post.title = ""
            print(f"✅ إصلاح العنوان للمنشور {post.id}")
    
    db.session.commit()
    print("🎉 تم إصلاح جميع العناوين")
    
    # التحقق
    fixed_posts = Post.query.all()
    for post in fixed_posts:
        print(f"📝 المنشور {post.id}: العنوان='{post.title}'")