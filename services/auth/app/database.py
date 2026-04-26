# database.py start
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import time
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Retrieve database connection details from environment variables
server = os.getenv("DATABASE_URL")

def get_db_connection():
    # Pull the perfectly formatted URI from your .env
    database_url = os.getenv("DATABASE_URL")
    
    # Let SQLAlchemy do the heavy lifting of parsing the string
    engine = create_engine(database_url, echo=True)
    
    max_retries = 6
    retry_delay = 10 

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Connecting to Azure SQL via SQLAlchemy (Attempt {attempt}/{max_retries})...")
            # Attempt a raw connection to test the network
            with engine.connect() as conn:
                print("Successfully connected to Azure SQL!")
                return engine
        except OperationalError as e:
            print(f"SQL Not ready yet: {e}")
            time.sleep(retry_delay)
    
    print("Could not connect to Azure SQL. Check your firewall and credentials.")
    return None

def initialize_db(engine):
    # Populating SQL database with table schema for first run
    try:
        # SQLAlchemy manages the connection pool context
        with engine.connect() as connection:
            
            # Create Users table
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Users]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE Users (
                        UserID INT PRIMARY KEY IDENTITY(1,1),
                        Username NVARCHAR(50) UNIQUE NOT NULL,
                        PasswordHash VARBINARY(MAX) NOT NULL,
                        CreatedAt DATETIME DEFAULT GETDATE()
                    )
                END
            """))
            
            # Create Teams table
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Teams]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE Teams (
                        TeamID INT PRIMARY KEY IDENTITY(1,1),
                        UserID INT FOREIGN KEY REFERENCES Users(UserID) ON DELETE CASCADE,
                        TeamName NVARCHAR(100),
                        Generation NVARCHAR(50),
                        CreatedAt DATETIME DEFAULT GETDATE()
                    )
                END
            """))

            # Create TeamMembers table
            connection.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[TeamMembers]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE TeamMembers (
                        MemberID INT PRIMARY KEY IDENTITY(1,1),
                        TeamID INT FOREIGN KEY REFERENCES Teams(TeamID) ON DELETE CASCADE,
                        PokeApiID INT NOT NULL,
                        SlotNumber INT CHECK (SlotNumber BETWEEN 1 AND 6)
                    )
                END
            """))
            
            # Explicitly commit the transaction
            connection.commit()
            print("🚀 Database schema initialized successfully in Azure SQL!")
            
    except Exception as e:
        print(f"❌ Failed to initialize schema: {e}")

class PokemonRepository:
    # This class will handle all database interactions related to Pokemon teams and users

    # Initialize the repository with a database connection
    def __init__(self, conn):
        self.conn = conn
        
    # Method to add a new user to the database
    def add_user(self, username, password_hash):
        
        # We attempt to insert a new user into the Users table. If the username already exists or there's any other issue, we catch the exception, print an error message, and roll back the transaction to maintain database integrity. Finally, we ensure that the cursor is closed after the operation.
        try:
            cursor.execute("INSERT INTO Users (Username, PasswordHash) VALUES (?, ?)", (username, password_hash))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding user to database: {e}")
            self.conn.rollback()
            return False
        finally:
            

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

    
# 