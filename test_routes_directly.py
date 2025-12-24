from app import create_app
import requests

app = create_app()

def test_route(method, url, data=None):
    try:
        with app.test_client() as client:
            if method == 'POST':
                response = client.post(url, json=data or {})
            else:
                response = client.get(url)
            
            print(f"{method} {url} -> {response.status_code}")
            print(f"Response: {response.get_json()}")
            return response.status_code == 200
            
    except Exception as e:
        print(f"Error: {e}")
        return False

# اختبار routes
print("🔍 اختبار routes مباشرة:")
test_route('POST', '/like/1')
test_route('POST', '/share/1')