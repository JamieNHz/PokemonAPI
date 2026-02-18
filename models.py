class Pokemon:
    def __init__(self, data, evo_data, gen):
        # 1. Basic Info
        self.name = data["name"].capitalize()
        self.id = data["id"]
        self.gen = gen
        
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
                    detail["version_group"]["name"] == gen and
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
        print(f"Moves ({self.gen} Level-up):")
        for move in self.moves:
            print(f" Lvl {move['level']:>2} - {move['name'].title()}")
        print(f"{'='*30}\n")