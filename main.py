from pokemon_api import (
    get_pokemon_info,
    get_pokemon_evo
)
import pprint
import json
# In the output include the evolutions and the level they happen at. Maybe even an item if an item is required?
class Pokemon:
    def __init__(self, data, evo_data):
        # 1. Basic Info
        self.name = data["name"].capitalize()
        self.id = data["id"]
        
        # 2. Extract Types (into a simple list of strings)
        self.types = [t["type"]["name"] for t in data["types"]]

        self.forms = [f["name"] for f in data["forms"]]
        current_stage = evo_data["chain"]
        self.evolution_line = []
        while current_stage:
            name = current_stage["species"]["name"].capitalize()
            # 1. Dig for the evolution level
            # We check if details exist (the first pokemon has None/Empty)
            details = current_stage["evolution_details"]
            if details:
                det = details[0]
                trigger = det["trigger"]["name"]
                if trigger == "level-up" and det["min_level"]:
                    self.evolution_line.append(f"{name} (Lvl {det['min_level']})")
                    
                elif trigger == "use-item":
                        item = det["item"]["name"].replace("-", " ").title()
                        self.evolution_line.append(f"{name} ({item})")

                elif trigger == "trade":
                        self.evolution_line.append(f"{name} (Trade)")
            else:
                self.evolution_line.append(name)

            if current_stage['evolves_to']:

                current_stage = current_stage["evolves_to"][0]
            else:

                current_stage = None
        
        # 3. Extract Abilities
        self.abilities = [a["ability"]["name"] for a in data["abilities"]]
        
        # 4. Extract Level-Up Moves (specifically for Red-Blue as an example)
        self.moves = []
        for m in data["moves"]:
            for detail in m["version_group_details"]:
                if (detail["move_learn_method"]["name"] == "level-up" and 
                    detail["version_group"]["name"] == "emerald" and
                    detail["level_learned_at"] > 2):
                    self.moves.append({
                        "name": m["move"]["name"],
                        "level": detail["level_learned_at"]
                    })
        
        # Sort moves by level
        self.moves.sort(key=lambda x: x["level"])

    def display_info(self):
        """Prints a neat summary of the Pokemon"""
        print(f"\n{'='*30}")
        print(f"#{self.id:03} : {self.name}")
        print(f"Type: {' / '.join(self.types).title()}")
        print(f"Forms: {' / '.join(self.forms).title()}")
        print(f"Evolutions: { ' -> ' .join(self.evolution_line)}")
        print(f"Abilities: {', '.join(self.abilities).title()}")
        print("-" * 30)
        print("Moves (Red/Blue Level-up):")
        for move in self.moves:
            print(f" Lvl {move['level']:>2} - {move['name'].title()}")
        print(f"{'='*30}\n")





#def get_version_groups():

pokemon_name = "Pikachu"
pokemon_info = get_pokemon_info(pokemon_name)
print(f"{pokemon_info['id']} is this showing id??")
evo_data = get_pokemon_evo(pokemon_info["id"])
my_pokemon = Pokemon(pokemon_info, evo_data)
my_pokemon.display_info()



"""
for held in pokemon_info["held_items"]:
    item_name = held["item"]["name"]
    pprint.pprint(item_name)
print("Showing moves --------- ")
red_blue_moves = []

for move in pokemon_info["moves"]:
    for deet in move["version_group_details"]:
        if (deet["move_learn_method"]["name"] == "level-up" and 
            deet["version_group"]["name"] == "red-blue"):
            # Store as a tuple: (level, name)
            red_blue_moves.append((deet["level_learned_at"], move["move"]["name"]))

# Sort the list by the first item (the level)
for level, name in sorted(red_blue_moves):
    print(f"Lvl {level}: {name}")

print("\nShowing abilities --------- ")
for ability in pokemon_info["abilities"]:
    item_name = ability["ability"]["name"]
    print(f"Name: {item_name}")
    

print("\n Showing abilities ---------" )

type_count = len(pokemon_info["types"])
type = pokemon_info["types"][0]["type"]["name"]
if type_count == 2:
    type2 = pokemon_info["types"][1]["type"]["name"]
    print(f"This Pokémon is both {type} and {type2} types")
else:
    print(f"This Pokémon only is {type} type.")

        

if pokemon_info:
    print(f"Name: {pokemon_info["name"]}")
    print(f"Id: {pokemon_info["id"]}")
    print(f"Height: {pokemon_info["height"]}")
    print(f"Weight: {pokemon_info["weight"]}")
"""