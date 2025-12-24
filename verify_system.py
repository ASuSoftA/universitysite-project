from app import create_app
from app.models.post import Post, Like

app = create_app()

with app.app_context():
    print("✅ التحقق من نظام الإعجاب:")
    
    posts = Post.query.all()
    for post in posts:
        print(f"📝 المنشور {post.id}: '{post.title}'")
        print(f"   👍 الإعجابات: {len(post.likes)}")
        
        for like in post.likes:
            print(f"      - IP: {like.user_ip}, التاريخ: {like.created_at}")
    
    print("\n🎯 النظام جاهز للتفاعل!")