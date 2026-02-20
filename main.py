#Importing pokemon api functions
from pokemon_api import (
    get_pokemon_info,
    get_pokemon_evo,
    get_pokemon_gen
)
#Importing interface function
from interface import get_gen_input, get_pokemon_input

#Importing module function
from models import Pokemon, Team

import pprint

def main():
    pokemon_info = []
    #Calling get pokemon gen function to collect all available generations
    all_gen_url = get_pokemon_gen()

    # Convert keys to a list, then grab index 0
    all_gen = list(all_gen_url.keys())
    gen = get_gen_input(all_gen)

    #Validating pokemon name, checking if pokemon name has returned anything.
    while not pokemon_info:
        #Getting input from user around pokemon and generation of pokemon
        pokemon = get_pokemon_input()
        pokemon_info = get_pokemon_info(pokemon)
        
        #Retrieving Pokemon Info
        

        if pokemon_info:
            #Using any iteration to look through object and see if the generation chosen exists within pokemon object
            pok_exists = any(
                group["version_group"]["name"] == gen
                for move in pokemon_info["moves"]
                for group in move["version_group_details"]
                )

            
            if pok_exists:
                #Retrieving evolution data for pokemon - Passing in URL for species in order to retrieve the correct evo tree
                evo_data = get_pokemon_evo(pokemon_info["species"]["url"])
                my_pokemon = Pokemon(pokemon_info, evo_data, gen)
                #Displaying Pokemon
                my_pokemon.display_info()
            else:
                print("Invalid Pokemon")
                option = input("Enter q to quit: ")
        else:
            print("Invalid Pokemon")
            option = input("Enter q to quit: ")

        if option == "q":
            break
        

if __name__ == "__main__":
    main()
