# app/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import List

class MoveSchema(BaseModel):
    model_config = ConfigDict(frozen=True) # Immutable!
    name: str
    level: int

class PokemonSchema(BaseModel):
    model_config = ConfigDict(frozen=True) # Immutable!
    id: int
    name: str
    gen: str
    types: List[str]
    forms: List[str]
    abilities: List[str]
    evolution_line: List[str]
    moves: List[MoveSchema]

class TeamSchema(BaseModel):
    model_config = ConfigDict(frozen=True) # Immutable!
    name: str
    generation: str
    members: List[PokemonSchema] = []
    max_size: int = 6

class TeamCreate(BaseModel):
    team_name: str         
    generation: str        
    pokemon_names: List[str]

# schemas end