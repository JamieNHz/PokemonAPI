import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel
from app.database import PokemonRepository, get_db_connection
from app.pokemon_api import get_pokemon_info, get_pokemon_gen, get_pokemon_evo
from app.services import build_pokemon_schema, is_pokemon_in_generation
from app.schemas import TeamSchema, TeamCreate

# Must match Auth service exactly
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]

# Note: The tokenUrl doesn't strictly matter here, it's just for the Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://auth:8000/login")

app = FastAPI(title="Pokemon Domain API")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates the token minted by the Auth service."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return int(user_id_str)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_repo():
    """Connects to the exact same database as Auth."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("USE PokemonDB")
    cursor.close()
    repo = PokemonRepository(conn)
    try:
        yield repo
    finally:
        conn.close()

@app.post("/team")
def create_team(team_data: TeamCreate, current_user_id: int = Depends(get_current_user), repo: PokemonRepository = Depends(get_repo)):
    generations = get_pokemon_gen()
    if team_data.generation not in generations:
        raise HTTPException(status_code=400, detail="Invalid generation.")
    
    if len(team_data.pokemon_names) > 6:
        raise HTTPException(status_code=400, detail="Team exceeds 6 Pokémon.")

    pokemon_members = []
    for name in team_data.pokemon_names:      
        pokemon_info = get_pokemon_info(name)
        if not pokemon_info:
            raise HTTPException(status_code=400, detail=f"Invalid Pokemon: {name}")
        
        if not is_pokemon_in_generation(pokemon_info["moves"], team_data.generation):
            raise HTTPException(status_code=400, detail=f"{name} not in {team_data.generation}.")
            
        evo_data = get_pokemon_evo(pokemon_info["species"]["url"])
        poke_schema = build_pokemon_schema(pokemon_info, evo_data, team_data.generation)
        pokemon_members.append(poke_schema)

    poke_team = TeamSchema(
        name=team_data.team_name,
        generation=team_data.generation,
        members=pokemon_members
    )
    repo.add_team(current_user_id, poke_team)
    return {"message": "Team created successfully!"}

@app.get("/team")
def get_team(current_user_id: int = Depends(get_current_user), repo: PokemonRepository = Depends(get_repo)):
    team = repo.get_team_by_user(current_user_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"team": team}

@app.get("/health")
def health_check():
    """Docker Compose uses this to verify the container is running."""
    return {"status": "healthy"}