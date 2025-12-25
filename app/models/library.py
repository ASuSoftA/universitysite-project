from app.extensions import db
from datetime import datetime

class LibraryFile(db.Model):
    __tablename__ = "library"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # book, handout, exam, etc.
    course = db.Column(db.String(100))  # اسم المادة
    semester = db.Column(db.String(50))  # الفصل الدراسي
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    download_count = db.Column(db.Integer, default=0)
    file_size = db.Column(db.Integer)  # حجم الملف بالبايت
    is_published = db.Column(db.Boolean, default=True)
    #faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'))  # ✅ الكلية
    #faculty = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)
    faculty = db.relationship('Faculty', backref='libraries')


    # العلاقة مع المستخدم
    uploader = db.relationship('User', backref='uploaded_files')

    def __repr__(self):
        return f'<LibraryFile {self.title}>'
    