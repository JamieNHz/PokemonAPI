from fastapi import FastAPI, HTTPException, status, Depends
from contextlib import asynccontextmanager
from pydantic import BaseModel
from database import PokemonRepository, get_db_connection, intialize_db
from auth import hash_password, verify_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up the application. Establishing database connection...")
    db_conn = None
    try:
        # 1. DO ALL SETUP BEFORE YIELDING
        db_conn = get_db_connection("master")
        intialize_db(db_conn) 
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to the database: {e}")
        
    # 2. PAUSE AND RUN THE SERVER
    # (Everything above this line runs on startup. Everything below runs on shutdown)
    yield   

    # 3. TEARDOWN
    print("🛑 Shutting down the application...")
    if db_conn:
        db_conn.close()
        print("Database connection closed.")

app = FastAPI(title="Pokemon Team Builder API", lifespan=lifespan)


class UserCredentials(BaseModel):
    username: str
    password: str

def get_repo():
    """Dependency that creates a fresh database connection per request."""
    conn = get_db_connection() # Or get_db_connection("master"), whatever you currently have
    
    # 👇 THE SILVER BULLET: Force this specific connection into the right room
    cursor = conn.cursor()
    cursor.execute("USE PokemonDB")
    cursor.close()
    
    repo = PokemonRepository(conn)
    try:
        yield repo
    finally:
        conn.close()

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCredentials, repo: PokemonRepository = Depends(get_repo)):
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
def login_user(user: UserCredentials, repo: PokemonRepository = Depends(get_repo)):
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

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pokemon Team Builder API! Go to /docs to test the endpoints."}