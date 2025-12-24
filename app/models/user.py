from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.faculty import Faculty

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    profile_image = db.Column(db.String(200), default='default_profile.png')
    is_admin = db.Column(db.Boolean, default=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    can_post = db.Column(db.Boolean, default=False)  # ✅ صلاحية إضافة المنشورات
    can_upload_books = db.Column(db.Boolean, default=False)  # صلاحية رفع الكتب
     # حقل الكلية
    #faculty = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # في User
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)
    faculty = db.relationship('Faculty', backref='users')

    # العلاقات
    posts = db.relationship('Post', backref='author', lazy=True, foreign_keys='Post.user_id')
    likes = db.relationship('Like', backref='user', lazy=True, foreign_keys='Like.user_id')
    
    def can_create_posts(self):
        return self.is_admin or self.can_post  # ✅ المديرين يمكنهم دائماً، الآخرون حسب الصلاحية
    
    def can_upload_to_library(self):
        return self.is_admin or self.can_upload_books   # ← NEW
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
  
    def __repr__(self):
        # نستخدم اسم الكلية إذا موجود
        faculty_name = self.faculty.name if self.faculty else "بدون كلية"
        return f'<User {self.username} - {faculty_name}>'
