# Server.py start
from typing import List
from fastapi import FastAPI, HTTPException, status, Depends, APIRouter, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from app.database import PokemonRepository, get_db_connection, intialize_db
from app.auth import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
import jwt
from fastapi.security import OAuth2PasswordBearer
from app.pokemon_api import get_pokemon_info, get_pokemon_gen, get_pokemon_evo
from app.models import Pokemon, Team
from app.schemas import TeamSchema, TeamCreate
from app.services import build_pokemon_schema, is_pokemon_in_generation

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
    # We return the access token to the client, which they can use for authenticated requests to protected endpoints.
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@app.post("/team")
def create_team(
    team_data: TeamCreate, 
    current_user_id: int = Depends(get_current_user), 
    repo: PokemonRepository = Depends(get_repo) 
):
    generations = get_pokemon_gen()
    if team_data.generation not in generations:
        raise HTTPException(status_code=400, detail=f"Invalid generation. Valid options are: {', '.join(generations.keys())}")
    
    if len(team_data.pokemon_names) > 6:
        raise HTTPException(status_code=400, detail="A team cannot exceed 6 Pokémon.")

    pokemon_members = []
    
    # 1. Transform all external data into immutable schemas
    for name in team_data.pokemon_names:      
        pokemon_info = get_pokemon_info(name)
        if not pokemon_info:
            raise HTTPException(status_code=400, detail=f"Invalid Pokemon name: {name}")
        
        if not is_pokemon_in_generation(pokemon_info["moves"], team_data.generation):
            raise HTTPException(
                status_code=400, 
                detail=f"{name.capitalize()} does not exist in {team_data.generation}. Please check your team and try again."
            )
            
        evo_data = get_pokemon_evo(pokemon_info["species"]["url"])
        
        # Build the immutable Pydantic model
        poke_schema = build_pokemon_schema(pokemon_info, evo_data, team_data.generation)
        
        # Note: You'll need to move your `check_gen` logic into a service function or validation step here
        # For brevity, assuming it passes:
        pokemon_members.append(poke_schema)

    # 2. Create the immutable Team object all at once
    poke_team = TeamSchema(
        name=team_data.team_name,
        generation=team_data.generation,
        members=pokemon_members
    )

    # Because Pydantic allows dot notation (poke_team.name), your repo.add_team will still work as expected.
    repo.add_team(current_user_id, poke_team)
        
    return {"message": f"Team '{poke_team.name}' created successfully, all {len(poke_team.members)} Pokemon added!"}

@app.get("/team")
def get_team(current_user_id: int = Depends(get_current_user), repo: PokemonRepository = Depends(get_repo)):
    team = repo.get_team_by_user(current_user_id)
    # If no team is found for the given user ID, we raise a 404 error to indicate that the resource was not found. Otherwise, we return the team data in the response.
    if not team:
        raise HTTPException(status_code=404, detail="Team not found for this user")
    return {"team": team.to_dict()}


@app.get("/")
def read_root():
    return {"message": "Welcome to the Pokemon Team Builder API! Go to /docs to test the endpoints."}

# Server.py end