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

## 🏗️ Architecture & Development Roadmap

This project is actively evolving from a standalone CLI tool into a fully containerized, production-ready microservice. Below is the phased implementation plan focusing on Site Reliability Engineering (SRE) and scalable architecture principles.

### Phase 1: Container Foundation
- [x] Add `Dockerfile` for the core Python application.
- [x] Create `docker-compose.yml` to orchestrate multi-container services.
- [x] Configure isolated container networking.
- [x] Implement persistent volumes for the SQL Server container.
- [x] Decouple configuration using environment variables (`.env`).

### Phase 2: Database Layer
- [x] Design relational database schema (Users, Pokemon, UserPokemon).
- [x] Add automated migration or startup DB initialization scripts.
- [ ] Implement a clean Repository Pattern layer for database access.

### Phase 3: Authentication & Security
- [ ] Implement password hashing (bcrypt/argon2).
- [ ] Create secure user registration and login endpoints.
- [ ] Implement JWT generation and validation middleware.
- [ ] Protect specific Pokémon data routes with required authentication.

### Phase 4: Domain & Data Handling
- [ ] Create immutable domain models (User, Pokemon).
- [ ] Implement data transformation logic (mapping over manual loops).
- [ ] Architect data isolation (store and retrieve Pokémon data strictly per user).

### Phase 5: Production-Level SRE Improvements
- [ ] Implement structured logging for observability.
- [ ] Build application health check endpoints (SLI monitoring).
- [ ] Add native Docker healthchecks.
- [ ] Implement a robust, global error handling strategy.
- [ ] Build a basic CI pipeline for automated building and testing.

### 🚀 Optional Stretch Goals (Scaling)
- [ ] Integrate a Redis container for rapid data caching.
- [ ] Implement Role-Based Access Control (Admin vs Standard User).
- [ ] Add API rate limiting to prevent abuse.
- [ ] Architect a background job container for asynchronous tasks.
