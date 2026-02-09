import requests

def debug_logs():
    base_url = 'http://127.0.0.1:8000/api'
    
    # Login
    login_data = {'email': 'admin@example.com', 'password': 'admin123'}
    try:
        resp = requests.post(f'{base_url}/auth/login/', json=login_data)
        token = resp.json().get('access')
        if not token:
            print("Login failed:", resp.text)
            return
    except Exception as e:
        print("Login connection failed:", e)
        return

    # Fetch logs
    headers = {'Authorization': f'Bearer {token}'}
    try:
        print("Fetching logs...")
        resp = requests.get(f'{base_url}/attendance/logs/', headers=headers)
        print("Logs Status Code:", resp.status_code)
        
        print("Fetching status...")
        resp_status = requests.get(f'{base_url}/attendance/status/', headers=headers)
        print("Status Code:", resp_status.status_code)
        if resp_status.status_code == 200:
            print("Status Response:", resp_status.json())
        else:
            print("Status Error:", resp_status.text[:500])
    except Exception as e:
        print("Logs fetch failed:", e)

if __name__ == "__main__":
    debug_logs()
