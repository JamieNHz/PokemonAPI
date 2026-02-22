from auth import hash_password, verify_password
#Input functions


def get_gen_input(all_gen):
    i = 1
    
    while True:
        #Looping round all items in dictionary in order to print out all available generations for user to pick
        for g in all_gen:
            print(f"{i}: {g}")

            i+=1
        #Prompting user for generation input
        choice = int(input("Enter generation of Pokemon from selection: "))

        #Removing one so it's able
        choice-=1
        #Validating user input
        if choice > -1 and choice < len(all_gen):
            #Assigning the choice to the gen variable to pass back
            gen = all_gen[choice]
            break
            
        else:
            print("Please enter a valid input ranging from 1-19")

    #returning chosen pokemona and pokemon gen
    return gen

def get_pokemon_input():
    #Prompting user for pokemon input
    pokemon = input("Enter name of Pokemon: ")
    # Validating user input to ensure it's not empty and only contains letters
    if not pokemon:
        print("Please enter a valid Pokemon name")
    elif not pokemon.isalpha():
        print("Please enter a valid Pokemon name (letters only)")
    else:
        return pokemon

def login_user(repo):
    print(" \n=== Login ===")
    while True:
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()
        # Retrieve user data from the database using the provided username
        user_data = repo.get_user_by_username(username)
        if user_data and verify_password(password, user_data[2]):
            print(f"Welcome back, {username}!")
            return user_data[0]  # Return the UserID for the logged-in user
                
        print("Invalid username or password.")
        choice = input("Do you want to try again? (y/n): ").lower()
        if choice != 'y':
            break
                
    return None

def register_user(repo):
    # Prompting user for registration details and validating input
    print(" \n=== Register ===")
    # Implementing a loop to allow users to correct their input if registration fails due to validation errors or existing username
    sec_run = False
    while True:
        if sec_run:
            choice = input("Do you want to quit registration? (y/n): ").lower()
            if choice == 'q':
                break
        username = input("Enter a username: ").strip()
        password = input("Enter a password: ").strip()
        confirm_password = input("Confirm your password: ").strip()
        # Validating user input for registration, including password confirmation, password length, and checking for existing username in the database
        if password != confirm_password:
            print("Passwords do not match. Please try again.")
            sec_run = True
            continue
        elif len(password) < 6:
            print("Password must be at least 6 characters long. Please try again.")
            sec_run = True
            continue
        elif repo.get_user_by_username(username):
            print("Username already exists. Please choose a different username.")
            sec_run = True
            continue
        else:
            # If all validations pass, hash the password and add the new user to the database
            password_hash = hash_password(password)
            repo.add_user(username, password_hash)
            print(f"User {username} registered successfully!")
            return repo.get_user_by_username(username)[0]  # Return the UserID for the newly registered user
    return None
        
    
    