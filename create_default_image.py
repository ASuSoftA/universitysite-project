# create_default_image.py
from PIL import Image, ImageDraw
import os

# إنشاء صورة بروفايل افتراضية
img = Image.new('RGB', (200, 200), color='#3498db')
draw = ImageDraw.Draw(img)

# رسم دائرة بيضاء في المنتصف
draw.ellipse((50, 50, 150, 150), fill='white')

# رسم وجه smiley بسيط
draw.ellipse((80, 80, 120, 120), fill='#3498db')  # عيون
draw.arc((70, 100, 130, 140), 0, 180, fill='white', width=5)  # ابتسامة

# حفظ الصورة
os.makedirs('app/static/images', exist_ok=True)
img.save('app/static/images/default_profile.png')
print("✅ تم إنشاء الصورة الافتراضية: app/static/images/default_profile.png")