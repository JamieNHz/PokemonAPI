from fastapi import FastAPI, HTTPException, status, Depends, APIRouter, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from database import PokemonRepository, get_db_connection, intialize_db
from auth import hash_password, verify_password, create_access_token
import jwt
from fastapi.security import OAuth2PasswordBearer
# Tells FastAPI where to get token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """The Bouncer: Intercepts the token, validates it, and extracts the user_id."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Crack open the token using our secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Extract the user ID (we will store it under the standard "sub" subject key)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        return int(user_id_str) # Hand the clean user_id to the endpoint!
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise credentials_exception

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
    access_token = create_access_token(data={"sub": str(db_user_id)})
    # We return the access token to the client, which they can use for authenticated requests to protected endpoints. The token includes the user ID in its payload, allowing us to identify the user in future requests.
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

# This endpoint allows users to create a new Pokemon team by providing a team name and a list of Pokemon names. It validates the Pokemon names against the PokeAPI and returns the corresponding Pokemon IDs if they are valid. If any of the provided Pokemon names are invalid, it raises an HTTP 400 error with a message indicating which name was invalid. --- IGNORE ---
@app.post("/team")
def create_team(
    team_data: TeamCreate, # 👈 Expects a clean JSON body now
    current_user_id: int = Depends(get_current_user), # 👈 THE BOUNCER!
    repo: PokemonRepository = Depends(get_repo)
):
    valid_pokemon_ids = []
    for name in pokemon_names:
        pokemon_info = get_pokemon_info(name)
        if pokemon_info:
            valid_pokemon_ids.append(pokemon_info['id'])
        else:
            raise HTTPException(status_code=400, detail=f"Invalid Pokemon name: {name}")
        
    return {"message": f"Team '{team_name}' created with Pokemon IDs: {valid_pokemon_ids}"}

# This endpoint retrieves the Pokemon team associated with a specific user ID. It uses the repository to fetch the team data from the database. If no team is found for the given user ID, it raises a 404 error. Otherwise, it returns the team data in the response. --- IGNORE ---
@app.get("/team/")
def get_team(current_user_id: int = Depends(get_current_user), repo: PokemonRepository = Depends(get_repo)):
    team = repo.get_team_by_user(current_user_id)
    # If no team is found for the given user ID, we raise a 404 error to indicate that the resource was not found. Otherwise, we return the team data in the response.
    if not team:
        raise HTTPException(status_code=404, detail="Team not found for this user")
    return {"team": team.todict()}


@app.get("/")
def read_root():
    return {"message": "Welcome to the Pokemon Team Builder API! Go to /docs to test the endpoints."}