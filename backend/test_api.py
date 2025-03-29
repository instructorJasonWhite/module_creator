import json

import requests


def test_api():
    # Base URL
    base_url = "http://localhost:8000/api/v1"

    # Login to get token
    login_data = {"username": "admin", "password": "admin"}

    try:
        # Login
        response = requests.post(f"{base_url}/auth/login", data=login_data)
        response.raise_for_status()
        token = response.json()["access_token"]

        # Set up headers with token
        headers = {"Authorization": f"Bearer {token}"}

        # Test system stats endpoint
        response = requests.get(f"{base_url}/system/stats", headers=headers)
        response.raise_for_status()
        stats = response.json()

        print("System Stats:")
        print(json.dumps(stats, indent=2))

        # Test model settings endpoint
        response = requests.get(f"{base_url}/system/models", headers=headers)
        response.raise_for_status()
        models = response.json()

        print("\nModel Settings:")
        print(json.dumps(models, indent=2))

        # Test token usage endpoint
        response = requests.get(f"{base_url}/system/token-usage", headers=headers)
        response.raise_for_status()
        usage = response.json()

        print("\nToken Usage:")
        print(json.dumps(usage, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e.response, "text"):
            print(f"Response: {e.response.text}")


if __name__ == "__main__":
    test_api()
