import os

basedir = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # إعدادات تحميل الملفات
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # يجب أن يكون ≥ MAX_FILE_SIZE

    # امتدادات مسموحة
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}
    ALLOWED_LIBRARY_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'zip', 'rar'}
