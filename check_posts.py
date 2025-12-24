from app import create_app
from app.models.post import Post

app = create_app()

with app.app_context():
    print("🔍 التحقق من المنشورات في قاعدة البيانات:")
    
    posts = Post.query.all()
    print(f"عدد المنشورات: {len(posts)}")
    
    for i, post in enumerate(posts, 1):
        print(f"{i}. ID: {post.id}, العنوان: '{post.title}', النشر: {post.is_published}")
    
    if posts:
        print(f"\n🎯 يمكنك استخدام post_id: {posts[0].id} للاختبار")
    else:
        print("\n❌ لا توجد منشورات! أضف منشوراً أولاً")