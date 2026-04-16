from fastapi import FastAPI, HTTPException, status, Depends
from contextlib import asynccontextmanager
from pydantic import BaseModel
from app.database import PokemonRepository, get_db_connection, intialize_db
from app.auth import hash_password, verify_password, create_access_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Auth Service: Initializing database schema...")
    db_conn = None
    try:
        db_conn = get_db_connection("master")
        intialize_db(db_conn) # ONLY AUTH DOES THIS
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to the database: {e}")
    yield   
    if db_conn:
        db_conn.close()

app = FastAPI(title="Auth Service API", lifespan=lifespan)

class UserCredentials(BaseModel):
    username: str
    password: str

def get_repo():
    conn = get_db_connection()
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
    existing_user = repo.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_pw = hash_password(user.password)
    success = repo.add_user(user.username, hashed_pw)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return {"message": f"User {user.username} successfully registered!"}

@app.post("/login")
def login_user(user: UserCredentials, repo: PokemonRepository = Depends(get_repo)):
    user_data = repo.get_user_by_username(user.username)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user_id, _, db_password_hash = user_data[0], user_data[1], user_data[2]

    if not verify_password(user.password, db_password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")
        
    access_token = create_access_token(data={"sub": str(db_user_id)})
    return {"access_token": access_token, "token_type": "bearer"}