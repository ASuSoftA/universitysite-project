from app import create_app
import requests

app = create_app()

test_urls = [
    ('POST', '/like/1'),
    ('POST', '/share/1'),
    ('GET', '/'),
]

with app.test_client() as client:
    print("🔍 اختبار الـ routes:")
    
    for method, url in test_urls:
        if method == 'POST':
            response = client.post(url, json={})
        else:
            response = client.get(url)
        
        print(f"{method} {url} -> {response.status_code} {response.status}")
        
        if response.status_code == 405:
            print(f"   ❌ Method Not Allowed! تأكد من methods=['POST']")
        elif response.status_code == 200:
            print(f"   ✅ يعمل بشكل صحيح")
        else:
            print(f"   ⚠️  حالة غير متوقعة: {response.status_code}")