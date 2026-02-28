# auth.py start
import bcrypt
import os
import jwt
from datetime import datetime, timedelta, timezone

def create_access_token(data: dict):
    # We create a copy of the data to encode, which allows us to add additional information (like the expiration time) without modifying the original data dictionary that was passed in. This is a common practice to ensure that the function does not have side effects on the input data.
    to_encode = data.copy()
    
    # Set the expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Sign and create the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to hash a plain text password using bcrypt
def hash_password(plain_text_password):
    password_bytes = plain_text_password.encode('utf-8')

    # Generate a salt and hash the password using bcrypt
    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)

    return hashed_password

def verify_password(plain_text_password, hashed_password):
    # Verify the provided plain text password against the stored hashed password
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)

# auth.py ends here. The functions defined in this file are responsible for securely hashing user passwords and verifying them during login. These functions will be used by the authentication logic in the application to ensure that user credentials are handled securely.