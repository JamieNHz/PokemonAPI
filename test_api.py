#  test_api.py start
import requests
import os

host = os.getenv("API_HOST", "localhost")
baseURL = f"http://{host}:8000/"

def main():
    # 1. Test user registration
    reg_response = requests.post(f"{baseURL}register", json={"username": "testuser", "password": "testpass"})
    print("Registration Response:", reg_response.json())

    # 2. Test user login
    login_response = requests.post(f"{baseURL}login", json={"username": "testuser", "password": "testpass"})
    print("Login Response:", login_response.json())

    # 3. Test team creation (replace 'your_token_here' with the actual token from login response)
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    team_data = {
        "team_name": "My Test Team",
        "generation": "red-blue",
        "pokemon_names": ["bulbasaur", "charmander", "squirtle"]
    }
    team_response = requests.post(f"{baseURL}team", json=team_data, headers=headers)
    print("Team Creation Response:", team_response.json())

    # 4. Test team retrieval
    team_retrieval_response = requests.get(f"{baseURL}team", headers=headers)
    print("Team Retrieval Response:", team_retrieval_response.json())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred during testing: {e}")

# test_api.py end