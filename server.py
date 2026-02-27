from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from database import PokemonRepository, get_db_connection
from auth import hash_password, verify_password

app = FastAPI(title="Pokemon Team Builder API")

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