from pokemon_api import (
    get_pokemon_info,
    get_pokemon_evo
)

from interface import get_user_input

from models import Pokemon
import pprint
import json
# In the output include the evolutions and the level they happen at. Maybe even an item if an item is required?

def main():
    #Getting input from user around pokemon and generation of pokemon
    pokemon, gen = get_user_input()
    #Retrieving Pokemon Info
    pokemon_info = get_pokemon_info(pokemon_name)
    #Retrieving evolution data for pokemon
    evo_data = get_pokemon_evo(pokemon_info["id"])
    #Building pokemon object
    my_pokemon = Pokemon(pokemon_info, evo_data)
    #Displaying Pokemon
    my_pokemon.display_info()

if __name__ == "__main__":
    main()
