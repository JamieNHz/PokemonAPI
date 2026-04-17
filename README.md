# ⚡️ Pokémon Team Builder Microservices

A fully containerized, microservices-based application built with FastAPI, NGINX, and SQL Server. This infrastructure allows users to securely register, authenticate via JWT, and build custom Pokémon teams that are validated in real-time against the public PokéAPI.

## 🚀 Developer Highlights

This project was refactored from a monolith into a production-grade microservice network with a focus on modern infrastructure, security, and zero-dependency deployment:

* **Three-Tier Architecture:** Complete network segmentation. A public-facing NGINX API Gateway routes traffic to private Python backend services, which alone hold the keys to the isolated Microsoft SQL database.
* **Microservice Decoupling:** Identity management (Auth) and domain logic (Pokémon) are completely physically separated into independent containers that scale and fail independently.
* **Robust Security:** Implements stateless JWT authentication. The Auth service issues tokens, and the Pokémon service validates the cryptographic signatures locally without requiring cross-container chatter.
* **Data Validation:** Utilizes Pydantic models for strict, fail-fast request payload validation, preventing malformed data from ever hitting the application logic.
* **External API Orchestration:** Dynamically communicates with the external PokéAPI to validate Pokémon existence and game-generation legality before committing to the database.

## 🛠 Tech Stack

* **API Gateway & Frontend:** NGINX
* **Application Backend:** FastAPI (Python 3.11)
* **Database:** Microsoft Azure SQL Edge (Dockerized)
* **Authentication:** PyJWT & passlib (bcrypt)
* **Infrastructure:** Docker & Docker Compose

## 📦 Quick Start (Zero-Dependency Setup)

**Prerequisites:** You must have Docker Desktop installed and running. No local Python installation is required.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/JamieNHZ/PokemonAPI.git](https://github.com/JamieNHZ/PokemonAPI.git)
    cd PokemonAPI
    ```

2.  **Set up your environment variables:**
    Copy the example environment file to create your active `.env` file, ensuring `SQL_PASSWORD` meets Microsoft's strict complexity requirements:
    ```bash
    cp .env.example .env
    ```

3.  **Spin up the infrastructure:**
    ```bash
    docker-compose up --build -d
    ```

4.  **Explore the Network:**
    The NGINX Gateway is now live on port 80.
    * **Frontend UI:** `http://localhost/`
    * **Auth API Swagger:** `http://localhost:8001/docs`
    * **Pokémon API Swagger:** `http://localhost:8000/docs`

## 📡 Core Endpoints (Routed via NGINX Gateway)

* **POST `/api/auth/register`**
    * **Description:** Creates a new user in the SQL database.
    * **Auth Required:** No

* **POST `/api/auth/login`**
    * **Description:** Verifies credentials against the database and returns a JWT access token.
    * **Auth Required:** No

* **POST `/api/team/`**
    * **Description:** Validates and saves a new Pokémon team to the database.
    * **Auth Required:** Yes (Requires Bearer JWT)

* **GET `/api/team/`**
    * **Description:** Retrieves the authenticated user's saved team.
    * **Auth Required:** Yes (Requires Bearer JWT)

### Phase 1: Container Foundation
- [x] Add `Dockerfile` for the core Python application.
- [x] Create `docker-compose.yml` to orchestrate multi-container services.
- [x] Configure isolated container networking.
- [x] Implement persistent volumes for the SQL Server container.
- [x] Decouple configuration using environment variables (`.env`).

### Phase 2: Database Layer
- [x] Design relational database schema (Users, Pokemon, UserPokemon).
- [x] Add automated migration or startup DB initialization scripts.
- [x] Implement a clean Repository Pattern layer for database access.

### Phase 3: Authentication & Security
- [x] Implement password hashing (bcrypt/argon2).
- [x] Create secure user registration and login endpoints.
- [x] Implement JWT generation and validation middleware.  - [x] Protect specific Pokémon data routes with required authentication.
### Phase 4: Domain & Data Handling
- [x] Create immutable domain models (User, Pokemon).
- [ ] Implement data transformation logic (mapping over manual loops).
- [ ] Architect data isolation (store and retrieve Pokémon data strictly per user).

### Phase 5: Production Level Improvements
- [ ] Implement structured logging for observability.
- [x] Build application health check endpoints (SLI monitoring).
- [x] Add native Docker healthchecks.
- [ ] Implement a robust, global error handling strategy.
- [x] Build a basic CI pipeline for automated building and testing.

### 🚀 Optional Stretch Goals (Scaling)
- [ ] Integrate a Redis container for rapid data caching.
- [ ] Implement Role-Based Access Control (Admin vs Standard User).
- [ ] Add API rate limiting to prevent abuse.
- [ ] Architect a background job container for asynchronous tasks.
