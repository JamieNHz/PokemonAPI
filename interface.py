#Input functions

def get_user_input():
    is_running = True
    #Prompting user for pokemon input
    pokemon = input("Enter name of Pokemon: ")
    while is_running:
        #Prompting user for generation input
        gen = int(input("Enter generation of Pokemon (1-19): "))

        #Validating user input
        if gen > 0 and gen < 20:
            is_running = False
        else:
            print("Please enter a valid input ranging from 1-19")

    return pokemon, gen