# إنشاء ملف test_db.py
from app import create_app, db
from app.models.post import Post, Like
from app.models.user import User

app = create_app()

with app.app_context():
    print("عدد المنشورات:", Post.query.count())
    print("عدد الإعجابات:", Like.query.count())
    print("عدد المستخدمين:", User.query.count())