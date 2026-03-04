# ⚡️ Pokémon Team Builder API

A fully containerized, RESTful API built with **FastAPI** and **SQL Server**. This backend service allows users to securely register, authenticate via JWT, and build custom Pokémon teams that are validated in real-time against the public PokéAPI.

## 🚀 Developer Highlights
This project was built with a focus on modern backend architecture, security, and zero-dependency deployment:
- **Two-Tier Architecture:** Complete separation of concerns between the application logic (FastAPI) and the data layer (Microsoft SQL Server), orchestrated via Docker Compose.
- **Robust Security:** Implements JWT (JSON Web Token) authentication with bcrypt password hashing. Routes are protected via dependency injection ("Bouncer" pattern).
- **Data Validation:** Utilizes Pydantic models for strict, fail-fast request payload validation, preventing malformed data from ever hitting the application logic.
- **External API Orchestration:** Dynamically communicates with the external PokéAPI to validate Pokémon existence and game-generation legality before saving to the database.
- **Containerized Testing:** Includes a fully isolated, containerized integration test suite that tests the entire user lifecycle without requiring local Python environments.

## 🛠 Tech Stack
* **Framework:** FastAPI (Python)
* **Database:** Microsoft SQL Server (Dockerized)
* **Authentication:** PyJWT & passlib (bcrypt)
* **Infrastructure:** Docker & Docker Compose
* **External Integrations:** PokéAPI

## 📦 Quick Start (Zero-Dependency Setup)

**Prerequisites:** You must have [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running. No local Python installation is required.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JamieNHZ/PokemonAPI.git
   cd PokemonAPI
   ```

2. **Set up your environment variables:**
   Copy the example environment file to create your active `.env` file:
   ```bash
   cp cp.env .env
   ```

3. **Spin up the backend:**
   ```bash
   docker-compose up --build -d
   ```

4. **Explore the API:**
   The API will be live at `http://localhost:8000`. 
   FastAPI automatically generates interactive Swagger UI documentation. Visit:
   👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

## 🧪 Running the Integration Tests

This project includes a fully containerized integration test script (`test_api.py`) that simulates a complete user journey (Register ➔ Login ➔ Extract JWT ➔ Create Team ➔ Fetch Team).

To run the automated test suite against the live Docker network, open your terminal and run:

```bash
docker-compose --profile testing run --rm integration-test
```
*(This command spins up a temporary test container, executes the HTTP requests against the API, prints the JSON responses, and cleanly deletes itself upon completion.)*

## 📡 Core Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/register` | Creates a new user in the SQL database. | No |
| `POST` | `/login` | Verifies credentials and returns a JWT access token. | No |
| `POST` | `/team` | Validates and saves a new Pokémon team to the database. | **Yes** |
| `GET`  | `/team` | Retrieves the authenticated user's saved team. | **Yes** |

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
- [x] Implement a clean Repository Pattern layer for database access.

### Phase 3: Authentication & Security
- [x] Implement password hashing (bcrypt/argon2).
- [x] Create secure user registration and login endpoints.
- [x] Implement JWT generation and validation middleware.
- [x] Protect specific Pokémon data routes with required authentication.

### Phase 4: Domain & Data Handling
- [ ] Create immutable domain models (User, Pokemon).
- [ ] Implement data transformation logic (mapping over manual loops).
- [ ] Architect data isolation (store and retrieve Pokémon data strictly per user).

### Phase 5: Production Level Improvements
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
