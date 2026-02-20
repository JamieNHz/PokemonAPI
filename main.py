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
    team_max_size = 6
    team_counter = 0
    # Convert keys to a list, then grab index 0
    all_gen = list(all_gen_url.keys())
    gen = get_gen_input(all_gen)
    #Asking user for team name and confirming input
    while True:
        team_name = input("Enter a name for your team: ")
        confirm = input(f"Confirm team name '{team_name}'? (y/n): ").lower()
        if confirm == 'y':
            break
    #Creating team object to hold pokemon
    my_team = Team(team_name) 

    #Validating pokemon name, checking if pokemon name has returned anything.
    while team_counter < 7:
        #Getting input for pokemon name
        pokemon = get_pokemon_input()
        #Grabbing pokemon if exists
        pokemon_info = get_pokemon_info(pokemon)
        
        #Checking if the generation chosen exists within the pokemon object

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
                #Creating pokemon object to hold all data and passing in generation for move filtering
                my_pokemon = Pokemon(pokemon_info, evo_data, gen)
                my_team.add_pokemon(my_pokemon.name)
                #Displaying Pokemon
                my_pokemon.display_info()
                team_counter += 1
            else:
                # If the pokemon doesn't exist in the generation chosen, prompt user to try again or quit
                print("Invalid Pokemon")
                
        else:
            print("Invalid Pokemon")
        # Prompting user to add another pokemon or quit
        option = input("Enter q to quit or any other key to continue adding: ").lower()
        if option == "q":
            break
    #Displaying team
    my_team.display_team()
        

if __name__ == "__main__":
    main()
