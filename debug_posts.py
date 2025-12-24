from app import create_app, db
from app.models.post import Post

app = create_app()

with app.app_context():
    print("🔍 فحص قاعدة البيانات بالتفصيل:")
    
    # جميع المنشورات
    all_posts = Post.query.all()
    print(f"📦 إجمالي المنشورات في DB: {len(all_posts)}")
    
    for i, post in enumerate(all_posts, 1):
        print(f"\n{i}. المنشور ID: {post.id}")
        print(f"   📝 العنوان: '{post.title}'")
        
        # معالجة المحتوى إذا كان None
        content_preview = "لا يوجد محتوى"
        if post.content:
            if len(post.content) > 50:
                content_preview = post.content[:50] + "..."
            else:
                content_preview = post.content
        print(f"   📄 المحتوى: '{content_preview}'")
        
        print(f"   🖼️  الصورة: {post.image_path}")
        print(f"   🎥 الفيديو: {post.video_path}")
        print(f"   🏷️  النوع: {post.post_type}")
        print(f"   📢 منشور: {post.is_published}")
        print(f"   👤 user_id: {post.user_id}")
        print(f"   📅 تاريخ الإنشاء: {post.created_at}")
    
    # المنشورات المنشورة فقط
    published_posts = Post.query.filter_by(is_published=True).all()
    print(f"\n✅ المنشورات المنشورة (is_published=True): {len(published_posts)}")
    
    for post in published_posts:
        print(f"   - ID: {post.id}, العنوان: '{post.title}', النوع: {post.post_type}")