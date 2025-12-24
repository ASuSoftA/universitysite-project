from app import create_app, db
from app.models.post import Post

app = create_app()

with app.app_context():
    print("🔍 التحقق من بنية قاعدة البيانات:")
    
    # التحقق من المنشورات
    posts = Post.query.all()
    print(f"عدد المنشورات: {len(posts)}")
    
    for post in posts:
        print(f"📝 المنشور {post.id}:")
        print(f"   العنوان: {post.title}")
        print(f"   المحتوى: {post.content}")
        print(f"   نوع المنشور: {post.post_type}")
        print(f"   الصورة: {post.image_path}")
        print(f"   الفيديو: {post.video_path}")
        print("---")