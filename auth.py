import bcrypt

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