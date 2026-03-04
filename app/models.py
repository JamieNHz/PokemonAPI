#models.py start
class Pokemon:
    def __init__(self, data, evo_data = None, gen=None):
        # 1. Basic Info
        self.name = data["name"].capitalize()
        self.id = data["id"]
        #self.gen = gen
        self.types = [t["type"]["name"] for t in data["types"]]
        self.forms = [f["name"] for f in data["forms"]]
        self.abilities = [a["ability"]["name"] for a in data["abilities"]]
        # 2. Extract Types (into a simple list of strings)
        if gen and evo_data:
            self.gen = gen  
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
            
            
            # 4. Extract Level-Up Moves (specifically for Red-Blue as an example)
            self.moves = []
            for m in data["moves"]:
                for detail in m["version_group_details"]:
                    if (detail["move_learn_method"]["name"] == "level-up" and 
                        detail["version_group"]["name"] == gen and
                        detail["level_learned_at"] > 1):
                        self.moves.append({
                            "name": m["move"]["name"],
                            "level": detail["level_learned_at"]
                        })
            
            # Sort moves by level
            self.moves.sort(key=lambda x: x["level"])
        else:
            self.evolution_line = []
            self.moves = data["moves"]
    """
    def display_info(self):
        # This method prints out all the relevant information about the Pokemon in a nicely formatted way, including its name, ID, types, forms, evolution line, abilities, and level-up moves for the specified generation. The output is designed to be clear and visually appealing for users who want to see the details of their chosen Pokemon.
        print(f"\n{'='*30}")
        print(f"#{self.id:03} : {self.name}")
        print(f"Type: {' / '.join(self.types).title()}")
        print(f"Forms: {' / '.join(self.forms).title()}")
        print(f"Evolutions: { ' -> ' .join(self.evolution_line)}")
        print(f"Abilities: {', '.join(self.abilities).title()}")
        print("-" * 30)
        print(f"Moves ({self.gen} Level-up):")
        for move in self.moves:
            print(f" Lvl {move['level']:>2} - {move['name'].title()}")
        print(f"{'='*30}\n")
    """
    def to_dict(self):
        # This method converts the Pokemon object into a dictionary format, which is useful for serialization (e.g., when storing in a database or sending as JSON in an API response). It includes all relevant attributes of the Pokemon, such as name, ID, types, forms, evolution line, abilities, and moves.
        return {
            "name": self.name,
            "id": self.id,
            "types": self.types,
            "forms": self.forms,
            "evolution_line": self.evolution_line,
            "abilities": self.abilities,
            "moves": self.moves
        }
    # This method is for checking whether the pokemon exists within this generation
    def check_gen(self, target_gen):
        pok_exists = []
        pok_exists = any(
                    group["version_group"]["name"] == target_gen
                    for move in self.moves
                    for group in move["version_group_details"]
                    )
        return pok_exists

class Team:
    def __init__(self, name, gen):
          self.name = name
          self.gen = gen
          self.members = [] # List to hold all pokemon in the team
          self.max_size = 6
    def add_pokemon(self, pokemon, first_add=True):
         #adds a pokemon as long as team isn't full
        if len(self.members) < self.max_size:
              self.members.append(pokemon)
              if first_add:
                print(f"{pokemon.name} has been added to {self.name}")
              return True
        else:
            print(f"{self.name} is already full, please remove, or swap an existing pokemon")
            return False

    def display_team(self):
        #Displaying full team, including name, and pokemon type
        print(f"\n{'='*30}")
        print(f"🏆 {self.name.upper()} 🏆")
        print(f"Generation: {self.gen}")
        print(f"{'='*30}")

        if not self.members:
             print("Your team is currently empty")
             return
        
        for i, pkmn in enumerate(self.members, 1):
             print(f"{i}: {pkmn.name} | Type: {'/'.join(pkmn.types).title()}")
        print(f"{'='*30}\n")

    # This method converts the Team object into a dictionary format, which is useful for serialization (e.g., when storing in a database or sending as JSON in an API response). It includes the team name, generation, and a list of members where each member is also converted to a dictionary using their own to_dict method.
    def to_dict(self):
        return {
            "name": self.name,
            "generation": self.gen,
            # Loop through the objects and turn them into dictionaries too!
            "members": [pokemon.to_dict() for pokemon in self.members] 
        }
#models.py ends here. This file defines the core data structures for the Pokemon team builder application, including the Pokemon class, which encapsulates all relevant information about a Pokemon, and the Team class, which manages a collection of Pokemon and provides methods for adding members and displaying the team. These classes will be used throughout the application to create and manage Pokemon teams based on user input and data retrieved from the PokeAPI.