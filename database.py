import pyodbc
import time
import os
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
    def __init__(self, conn):
        self.conn = conn

    def add_user(self, username, password_hash):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Users (Username, PasswordHash) VALUES (?, ?)", (username, password_hash))
        self.conn.commit()
        cursor.close()

    def get_team_by_user(self, userID):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.TeamID, t.TeamName, tm.PokeApiID, tm.SlotNumber
            FROM Teams t
            JOIN TeamMembers tm ON t.TeamID = tm.TeamID
            WHERE t.UserID = ?
        """, (userID,))
        team_data = cursor.fetchall()
        cursor.close()
        return team_data