#app\module\post.py
from app import db
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, BooleanField, SelectField
from wtforms.validators import Optional
from app.models.faculty import Faculty  

class PostImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(200), nullable=True)
    video_path = db.Column(db.String(200), nullable=True)
    post_type = db.Column(db.String(20), default='text')
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp()) 
    images = db.relationship('PostImage', backref='post', lazy=True, cascade='all, delete-orphan')
    
     # 🔥 الكلية
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)
    faculty = db.relationship('Faculty', backref='posts')

    # المفاتيح الخارجية مع تحديد explicit foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # العلاقات مع explicit foreign keys
    # likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan', 
    #                       foreign_keys='Like.post_id')
    likes = db.relationship('Like', backref='post', lazy='dynamic')
    
    def __repr__(self):
        return f'<Post {self.title}>'


class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_ip = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # المفاتيح الخارجية مع explicit foreign keys
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # إضافة user_id
    
    def __repr__(self):
        return f'<Like post_id={self.post_id} ip={self.user_ip}>'
    