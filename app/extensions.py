from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
import os
import secrets

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# تعريف photos ككائن فارغ لتجنب الأخطاء
class MockPhotos:
    def save(self, file):
        return save_file(file, 'app/static/uploads/images', ['jpg', 'jpeg', 'png', 'gif'])

photos = MockPhotos()

# دوال تحميل الملفات البديلة
def save_file(file, folder, allowed_extensions):
    print(f"محاولة الحفظ في: {folder}")
    if file and file.filename:
        filename = secure_filename(file.filename)
        if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            unique_filename = f"{secrets.token_hex(8)}_{filename}"
            
            # إصلاح المسار - إزالة "app/" المكرر
            if folder.startswith('app/'):
                folder = folder[4:]  # إزالة "app/" من البداية
            
            file_path = os.path.join(folder, unique_filename)
            os.makedirs(folder, exist_ok=True)
            file.save(file_path)
            return unique_filename
    return None

def delete_file(filename, folder):
    if filename:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)