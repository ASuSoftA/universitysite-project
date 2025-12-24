# test_upload.py
from app import create_app
from app.utils.helpers import save_uploaded_file

app = create_app()

with app.app_context():
    print("✅ تم تحميل دالة save_uploaded_file بنجاح")
    print("📁 جاهز لرفع الملفات")