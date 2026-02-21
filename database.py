import pyodbc
import time
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Retrieve database connection details from environment variables
server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_PASSWORD")

def get_db_connection():
    # Pull credentials from the .env variables Docker provides
    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
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