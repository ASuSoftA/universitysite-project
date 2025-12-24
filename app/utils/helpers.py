# app/utils/helpers.py
import os
from werkzeug.utils import secure_filename
from datetime import datetime

def save_uploaded_file(file, folder, allowed_extensions):
    if file and file.filename:
        # الحصول على الامتداد الأصلي
        original_filename = secure_filename(file.filename)
        name, ext = os.path.splitext(original_filename)
        
        # إذا لم يكن هناك امتداد، نحدده من نوع الملف
        if not ext:
            content_type = file.content_type.lower()
            if 'image' in content_type:
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                else:
                    ext = '.png'
            elif 'video' in content_type:
                if 'mp4' in content_type:
                    ext = '.mp4'
                elif 'mov' in content_type:
                    ext = '.mov'
                elif 'avi' in content_type:
                    ext = '.avi'
                else:
                    ext = '.mp4'
        
        # إنشاء اسم فريد مع الاحتفاظ بالامتداد
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{name}{ext}"
        file_path = os.path.join(folder, unique_filename)
        
        # التأكد من وجود المجلد
        os.makedirs(folder, exist_ok=True)
        
        # حفظ الملف
        file.save(file_path)
        print(f"✅ تم حفظ الملف: {unique_filename}")
        return unique_filename
    
    return None

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions