from pokemon_api import (
    get_pokemon_info,
    get_pokemon_evo,
    get_pokemon_gen
)

from interface import get_user_input

from models import Pokemon

def main():
    pokemon_info = []
    #Calling get pokemon gen function to collect all available generations
    all_gen_url = get_pokemon_gen()

    # Convert keys to a list, then grab index 0
    all_gen = list(all_gen_url.keys())


    #Validating pokemon name, checking if pokemon name has returned anything.
    while not pokemon_info:
        #Getting input from user around pokemon and generation of pokemon
        pokemon, gen = get_user_input(all_gen)
        #Retrieving Pokemon Info
        pokemon_info = get_pokemon_info(pokemon)

        if pokemon_info:
            #Retrieving evolution data for pokemon
            evo_data = get_pokemon_evo(pokemon_info["id"])
        else:
            print("Invalid Pokemon")
    #Building pokemon object
    my_pokemon = Pokemon(pokemon_info, evo_data)
    #Displaying Pokemon
    my_pokemon.display_info()

if __name__ == "__main__":
    main()
