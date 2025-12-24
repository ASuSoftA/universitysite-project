# create_default_profile.py
from PIL import Image, ImageDraw
import os

# إنشاء صورة افتراضية
img = Image.new('RGB', (200, 200), color='#007bff')
draw = ImageDraw.Draw(img)
draw.ellipse((50, 50, 150, 150), fill='#ffffff', outline='#007bff')
draw.text((75, 85), "👤", font=None, fill='#007bff')

# حفظ الصورة
os.makedirs('app/static/images', exist_ok=True)
img.save('app/static/images/default_profile.png')
print("✅ تم إنشاء صورة البروفايل الافتراضية")
