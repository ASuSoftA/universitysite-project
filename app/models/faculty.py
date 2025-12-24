# app/models/faculty.py
from app import db

class Faculty(db.Model):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False)

    cover_image = db.Column(db.String(200))   # صورة الغلاف
    logo_image = db.Column(db.String(200))    # شعار الكلية
    description = db.Column(db.Text)          # نص تعريفي

    def __repr__(self):
        return f'<Faculty {self.name}>'
