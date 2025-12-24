from app.extensions import db
from datetime import datetime

class Suggestion(db.Model):
    __tablename__ = 'suggestions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # suggestion or complaint
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # يمكن أن يكون فارغ
    sender_name = db.Column(db.String(100), nullable=True)  # اسم المرسل (اختياري)
    sender_email = db.Column(db.String(100), nullable=True)  # البريد الإلكتروني (اختياري)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)
    faculty = db.relationship('Faculty', backref='suggestions')

    # العلاقة مع المستخدم
    user = db.relationship('User', backref='suggestions')

    def __repr__(self):
        return f'<Suggestion {self.title}>'

