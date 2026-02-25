#Importing pokemon api functions
from pokemon_api import (
    get_pokemon_info,
    get_pokemon_evo,
    get_pokemon_gen
)
#Importing interface function
from interface import get_gen_input, get_pokemon_input, login_user, register_user

from database import get_db_connection, intialize_db, PokemonRepository

#Importing module function
from models import Pokemon, Team

import pprint

def main(db_conn, repo, user_id):
    get_team = PokemonRepository.get_team_by_user(repo, user_id)
    
    if(get_team):
        print("You already have a team saved. Please delete your existing team before creating a new one.")
        get_team.display_team()
    else:
        print("Let's build your Pokemon team!")
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
        my_team = Team(team_name, gen) 

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
                    my_team.add_pokemon(my_pokemon)
                    #Displaying Pokemon
                    my_pokemon.display_info()
                    team_counter += 1
                else:
                    # If the pokemon doesn't exist in the generation chosen, prompt user to try again or quit
                    print("Invalid Pokemon for the selected generation")
                    
            else:
                print("Invalid Pokemon")
            # Prompting user to add another pokemon or quit
            option = input("Enter q to quit or any other key to continue adding: ").lower()
            if option == "q" or team_counter >= team_max_size:
                break

        repo.add_team(user_id, my_team)
        my_team.display_team()
    #Displaying team
        
        

if __name__ == "__main__":
    db_conn = None
    # Implementing a retry mechanism to handle potential connection issues when the SQL Server container is still starting up
    try:
        db_conn = get_db_connection("master")
        if db_conn:
            intialize_db(db_conn)  # Ensure the database and tables are set up
            repo = PokemonRepository(db_conn)  # Create a repository instance for database operations
            print("Database connection established successfully!")
            while True:
                # Starting the main application logic
                print("\nWelcome to the Pokemon Team Builder!")
                print("1. Login")
                print("2. Register")
                choice = input("Select an option (1 or 2): ")
                # Initialize user_id to None before the login/register process
                user_id = None
                if choice == "1":
                    user_id = login_user(repo)
                elif choice == "2":
                    user_id = register_user(repo)
                
                if user_id:
                    main(db_conn, repo, user_id)  # Pass the database connection and user_id to the main function
                    break  # Exit after the main function completes
                else:
                    exit_choice = input("Login or registration failed. Do you want to try again? (y/n): ").lower()
                    if exit_choice != 'y':
                        print("Exiting the application. Please try again later.")
                        break
                    else:
                        print("Login or registration failed. Please try again.")
        else:
            print("Failed to establish a database connection. Please check your Docker setup and ensure the SQL Server container is running.")
    except Exception as e:
        print(f"Failed to connect to the database. Please check your Docker setup and ensure the SQL Server container is running. Error: {e}")
    finally:
        if db_conn:
            db_conn.close()
            print("Database connection closed.")
