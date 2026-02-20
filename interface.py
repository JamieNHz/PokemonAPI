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

    return pokemon
