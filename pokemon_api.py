# pokemon_api.py start
import requests
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from database import PokemonRepository
from auth import hash_password, verify_password
import pyodbc
from your_db_module import get_db_connection # Adjust import as needed
db_conn = get_db_connection("master")
repo = PokemonRepository(db_conn)

app = FastAPI(title="Pokemon Team Builder API")

base_url = "https://pokeapi.co/api/v2/"

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCredentials):
    """Creates a new user in the SQL Database."""
    
    # 
    existing_user = repo.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    #
    hashed_pw = hash_password(user.password)

    # 
    success = repo.add_user(user.username, hashed_pw)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {"message": f"User {user.username} successfully registered!"}

@app.post("/login")
def login_user(user: UserCredentials):
    """Verifies user credentials."""
    
    # Retrieve user data from the database using the provided username
    user_data = repo.get_user_by_username(user.username)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # user_data is a tuple: (UserID, Username, PasswordHash)
    db_user_id = user_data[0]
    db_password_hash = user_data[2]

    # Verify the provided plain text password against the stored hashed password
    if not verify_password(user.password, db_password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")
    # If we reach this point, the login is successful
    return {
        "message": "Login successful!",
        "user_id": db_user_id
    }

def get_pokemon_info(name):
    url = f"{base_url}/pokemon/{name}"
    response = requests.get(url)

    if response.status_code == 200:
        pokemon_data = response.json()
        return pokemon_data
    else:
        print(f"Failed to retrieve data {response.status_code}")

def get_pokemon_evo(url):
    species_request = requests.get(url)

    if species_request.status_code == 200:
        evo_id = species_request.json()
        evo_response = requests.get(evo_id["evolution_chain"]["url"])
        pokemon_evo = evo_response.json()
        return pokemon_evo
    else:
        print(f"Failed to retrieve data {species_request.status_code}")

def get_pokemon_gen():
    url = f"{base_url}/version-group/?limit=20"
    all_groups = [] # This is where we will store every result

    while url:
        response = requests.get(url)
        data = response.json()
        
        # 1. Add the results from THIS page to our master list
        all_groups.extend(data["results"])
        
        # 2. Update the URL to the 'next' page link provided by the API
        url = data["next"] 
        
        print(f"Fetched {len(all_groups)} groups so far...")

    version_dict = {group["name"]: group["url"] for group in all_groups}

    return version_dict

# pokemon_api.py ends here. The functions defined in this file are responsible for interacting with the PokeAPI to retrieve information about Pokemon, their evolutions, and the available generations. These functions will be used by other parts of the application, such as the main logic and database interactions, to build the functionality of the Pokemon team builder application.

