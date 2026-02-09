import requests

def test_workflow():
    base_url = 'http://127.0.0.1:8000/api'
    login_data = {'email': 'admin@example.com', 'password': 'admin123'}
    token = requests.post(f'{base_url}/auth/login/', json=login_data).json()['access']
    headers = {'Authorization': f'Bearer {token}'}

    print("--- Testing Check-In ---")
    checkin_data = {
        'check_in_lat': 27.7,
        'check_in_lng': 85.3,
        'location_in': 'Kathmandu',
        'check_in_note': 'Morning Session'
    }
    resp = requests.post(f'{base_url}/attendance/checkin/', json=checkin_data, headers=headers)
    print("Check-In Status:", resp.status_code)
    print("Check-In Response:", resp.text)

    if resp.status_code == 201:
        print("\n--- Testing Status (after Check-In) ---")
        status_resp = requests.get(f'{base_url}/attendance/status/', headers=headers)
        print("Status:", status_resp.json())

        print("\n--- Testing Check-Out ---")
        checkout_data = {
            'check_out_lat': 27.7,
            'check_out_lng': 85.3,
            'location_out': 'Kathmandu',
            'check_out_note': 'Finished shift'
        }
        resp = requests.patch(f'{base_url}/attendance/checkout/', json=checkout_data, headers=headers)
        print("Check-Out Status:", resp.status_code)
        print("Check-Out Response:", resp.json())

        print("\n--- Final Status ---")
        status_resp = requests.get(f'{base_url}/attendance/status/', headers=headers)
        print("Final Status is_checked_in:", status_resp.json()['is_checked_in'])

if __name__ == "__main__":
    test_workflow()
