# app/services.py
from app.schemas import PokemonSchema, MoveSchema

def build_pokemon_schema(data: dict, evo_data: dict, gen: str) -> PokemonSchema:
    """Takes raw PokeAPI JSON and builds an immutable Pydantic model."""
    
    types = [t["type"]["name"] for t in data["types"]]
    forms = [f["name"] for f in data["forms"]]
    abilities = [a["ability"]["name"] for a in data["abilities"]]
    
    moves = []
    for m in data["moves"]:
        for detail in m["version_group_details"]:
            if (detail["move_learn_method"]["name"] == "level-up" and 
                detail["version_group"]["name"] == gen and
                detail["level_learned_at"] > 1):
                moves.append(MoveSchema(name=m["move"]["name"], level=detail["level_learned_at"]))
    
    moves.sort(key=lambda x: x.level)

    evolution_line = []
    current_stage = evo_data["chain"]
    while current_stage:
        evolution_line.append(current_stage["species"]["name"].capitalize())
        if current_stage['evolves_to']:
            current_stage = current_stage["evolves_to"][0]
        else:
            current_stage = None

    return PokemonSchema(
        id=data["id"],
        name=data["name"].capitalize(),
        gen=gen,
        types=types,
        forms=forms,
        abilities=abilities,
        evolution_line=evolution_line,
        moves=moves
    )