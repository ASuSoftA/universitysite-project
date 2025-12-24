from app import create_app

app = create_app()

test_urls = [
    ('POST', '/like/1'),
    ('POST', '/share/1'),
    ('GET', '/'),
]

print("🔍 اختبار الـ routes باستخدام test_client:")

with app.test_client() as client:
    for method, url in test_urls:
        try:
            if method == 'POST':
                response = client.post(url, json={})
            else:
                response = client.get(url)
            
            print(f"{method} {url} -> {response.status_code} {response.status}")
            
            if response.status_code == 405:
                print(f"   ❌ Method Not Allowed! - تأكد من methods=['POST']")
            elif response.status_code == 200:
                print(f"   ✅ يعمل بشكل صحيح")
                if response.is_json:
                    print(f"   📦 Response: {response.get_json()}")
            elif response.status_code == 404:
                print(f"   ❌ Not Found - قد يكون post_id غير موجود")
            else:
                print(f"   ⚠️  حالة غير متوقعة: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 خطأ أثناء الاختبار: {e}")

print("\n🎯 إذا ظهر Method Not Allowed, المشكلة في تعريف الـ routes")
print("🎯 إذا ظهر Not Found, المشكلة في وجود المنشورات في DB")