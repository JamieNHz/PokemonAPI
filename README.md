# ⚡️ Python Pokédex & Evolution Tracker

A modular CLI application that interfaces with the PokeAPI to provide detailed Pokémon data, including version-specific move sets and full evolution chain discovery.

## 🚀 Developer Highlights (DevEx)
This project was built with a focus on **Separation of Concerns** and **Maintainable Architecture**:
- **Modular Design:** Logic is split across `api`, `models`, and `interface` modules.
- **Dynamic Filtering:** Implements `any()` iterators to validate Pokémon availability across different game generations.
- **Recursive Data Parsing:** Navigates complex, nested JSON trees to reconstruct linear evolution paths.
- **Robust Input Handling:** Feature-rich CLI with input validation and dynamic menu generation.



## 🛠 Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/JamieNHZ/PokemonAPI.git](https://github.com/JamieNHZ/PokemonAPI.git)
   cd PokemonAPI
