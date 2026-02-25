import pyodbc
import time
import os
from models import Team, Pokemon
from pokemon_api import get_pokemon_evo, get_pokemon_info
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Retrieve database connection details from environment variables
server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_PASSWORD")

def get_db_connection(target_db="master"):
    # Pull credentials from the .env variables Docker provides
    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={target_db};"
        f"UID={os.getenv('SQL_USER')};"
        f"PWD={os.getenv('SQL_PASSWORD')};"
        "Encrypt=yes;" # Standard for Driver 18
        "TrustServerCertificate=yes;" # This bypasses the error you see
    )
    # Implementing a retry mechanism to handle potential connection issues when the SQL Server container is still starting up
    max_retries = 6
    retry_delay = 10  # Seconds to wait between attempts

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Connecting to SQL Server (Attempt {attempt}/{max_retries})...")
            conn = pyodbc.connect(connection_string)
            print("Successfully connected to SQL Server!")
            
            return conn
        except Exception as e:
            print(f"SQL Not ready yet: {e}")
            time.sleep(retry_delay)
    
    print("Could not connect to SQL Server after multiple attempts. Please check your Docker setup and ensure the SQL Server container is running.")
    return None

def intialize_db(conn):
    # Create the database if it doesn't exist and set up the connection to use it
    cursor = conn.cursor()
    # We need to temporarily enable autocommit to create the database, then switch back to manual commit mode
    conn.autocommit = True
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'PokemonDB') BEGIN CREATE DATABASE PokemonDB END")
    # After creating the database, we can switch back to manual commit mode for our operations
    conn.autocommit = False

    # Now we can switch to using the new database for our operations
    cursor.execute("USE PokemonDB")
    # Create the Users table if it doesn't exist
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Users]') AND type in (N'U'))
        BEGIN
            CREATE TABLE Users (
                UserID INT PRIMARY KEY IDENTITY(1,1),
                Username NVARCHAR(50) UNIQUE NOT NULL,
                PasswordHash VARBINARY(MAX) NOT NULL,
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        END
    """)
    
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Teams]') AND type in (N'U'))
        BEGIN
            CREATE TABLE Teams (
                TeamID INT PRIMARY KEY IDENTITY(1,1),
                UserID INT FOREIGN KEY REFERENCES Users(UserID) ON DELETE CASCADE,
                TeamName NVARCHAR(100),
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        END
    """)

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[TeamMembers]') AND type in (N'U'))
        BEGIN
            CREATE TABLE TeamMembers (
                MemberID INT PRIMARY KEY IDENTITY(1,1),
                TeamID INT FOREIGN KEY REFERENCES Teams(TeamID) ON DELETE CASCADE,
                PokeApiID INT NOT NULL,
                SlotNumber INT CHECK (SlotNumber BETWEEN 1 AND 6)
            )
        END
    """)
    # Commit the changes to the database and close the cursor
    conn.commit()
    cursor.close()

class PokemonRepository:
    # This class will handle all database interactions related to Pokemon teams and users

    # Initialize the repository with a database connection
    def __init__(self, conn):
        self.conn = conn
        
    # Method to add a new user to the database
    def add_user(self, username, password_hash):
        cursor = self.conn.cursor()
        # We attempt to insert a new user into the Users table. If the username already exists or there's any other issue, we catch the exception, print an error message, and roll back the transaction to maintain database integrity. Finally, we ensure that the cursor is closed after the operation.
        try:
            cursor.execute("INSERT INTO Users (Username, PasswordHash) VALUES (?, ?)", (username, password_hash))
            self.conn.commit()
        except Exception as e:
            print(f"Error adding user to database: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

     # Method to retrieve a user by their username (for authentication purposes)
    def get_user_by_username(self, username):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT UserID, Username, PasswordHash FROM Users WHERE Username = ?", (username,))
            user_data = cursor.fetchone()
        # If there's an error during the database query, we catch the exception, print an error message, and set user_data to None to indicate that the retrieval was unsuccessful
        except Exception as e:
            print(f"Error retrieving user from database: {e}")
            user_data = None
        finally:
            cursor.close()
        return user_data

    # Method to retrieve a user's team from the database

    def get_team_by_user(self, userID):
        cursor = self.conn.cursor()
        team_data = []
        try:
            cursor.execute("""
                SELECT t.TeamID, t.TeamName, tm.PokeApiID, tm.SlotNumber
                FROM Teams t
                JOIN TeamMembers tm ON t.TeamID = tm.TeamID
                WHERE t.UserID = ?
            """, (userID,))
            team_data = cursor.fetchall()
            if team_data:
                rehydrated_team = self.rehydrate_team(team_data)
        except Exception as e:
            print(f"Error retrieving team from database: {e}")
        finally:
            cursor.close()
        return rehydrated_team
    
    # Method to add a team to the database for a specific user
    
    def add_team(self, userID, team_object):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Teams (UserID, TeamName) 
                OUTPUT INSERTED.TeamID 
                VALUES (?, ?)
            """, (userID, team_object.name))

            team_id = cursor.fetchone()[0]  # Get the generated TeamID

            for idx, pokemon in enumerate(team_object.members):
                cursor.execute("""INSERT INTO TeamMembers (TeamID, PokeApiID, SlotNumber)
                                VALUES (?, ?, ?)
                               """, (team_id, pokemon.id, idx + 1))

            
            self.conn.commit()
            
            print(f"Team '{team_object.name}' added successfully for user ID {userID}!")
        
        # In case of any error during the insertion process, we catch the exception, print an error message, and roll back the transaction to maintain database integrity
        except Exception as e:
            print(f"Error adding team to database: {e}")
            self.conn.rollback()
            

        finally:
            cursor.close()

   
    def rehydrate_team(self, team_data):
        # This function takes raw team data from the database and converts it back into a Team object
        if not team_data:
            return None # Return None if no team data is found for the user
        team_name = team_data[0][1] # Assuming all rows have the same team name
        team = Team(team_name)
        for row in team_data:
            # Each row contains: TeamID, TeamName, PokeApiID, SlotNumber
            poke_id = row[2]
            pokemon_info = get_pokemon_info(poke_id)
            pokemon_evo = get_pokemon_evo(pokemon_info["species"]["url"])
            pokemon_obj = Pokemon(pokemon_info, pokemon_evo, "red-blue")
            # We add the rehydrated Pokemon object to the team using the add_pokemon method, which will handle adding it to the members list and ensuring we don't exceed the maximum team size
            team.add_pokemon(pokemon_obj)
        # After processing all rows, we return the fully rehydrated Team object, which now contains all the Pokemon members as actual objects with their data populated from the API
        return team
    