from app import create_app

app = create_app()

def test_static_file(filename):
    try:
        with app.test_client() as client:
            response = client.get(f'/static/js/{filename}')
            print(f"{filename} -> {response.status_code}")
            if response.status_code == 200:
                print("✅ الملف موجود ويعمل")
            else:
                print("❌ الملف غير موجود")
    except Exception as e:
        print(f"Error testing {filename}: {e}")

print("🔍 اختبار ملفات Static:")
test_static_file('debug_buttons.js')
test_static_file('likes.js')
test_static_file('shares.js')