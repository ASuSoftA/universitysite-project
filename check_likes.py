from app import create_app
from app.models.post import Like, Post  # ✅ الاستيراد الصحيح

app = create_app()

with app.app_context():
    print("🔍 التحقق من جدول الإعجابات:")
    
    # التحقق من وجود الجدول
    likes_count = Like.query.count()
    print(f"عدد الإعجابات في النظام: {likes_count}")
    
    # عرض بعض الإعجابات إذا وجدت
    likes = Like.query.limit(5).all()
    for like in likes:
        print(f"👍 الإعجاب {like.id}: المنشور {like.post_id}, IP: {like.user_ip}")
    
    # التحقق من المنشورات
    posts = Post.query.all()
    print(f"\n📝 عدد المنشورات: {len(posts)}")
    for post in posts:
        print(f"   - المنشور {post.id}: '{post.title}' - الإعجابات: {len(post.likes)}")