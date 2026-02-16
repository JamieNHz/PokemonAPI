from pokemon_api import (
    get_pokemon_info,
    get_pokemon_evo
)

from models import Pokemon
import pprint
import json
# In the output include the evolutions and the level they happen at. Maybe even an item if an item is required?

def main():
    pokemon_name = "Pikachu"
    pokemon_info = get_pokemon_info(pokemon_name)
    print(f"{pokemon_info['id']} is this showing id??")
    evo_data = get_pokemon_evo(pokemon_info["id"])
    my_pokemon = Pokemon(pokemon_info, evo_data)
    my_pokemon.display_info()

if __name__ == "__main__":
    main()
