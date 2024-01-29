import hashlib

def encrypt_password(raw_password):
    """
    Encrypts the raw password using SHA-256.

    Parameters:
    - raw_password: The password to be hashed.

    Returns:
    - The hashed password.
    """
    # Use a unique salt for each password (you can also use a fixed salt)
    salt = hashlib.sha256()
    salt.update(raw_password.encode('utf-8'))
    salt_bytes = salt.digest()

    # Hash the password with the salt using SHA-256
    hashed_password = hashlib.sha256()
    hashed_password.update(raw_password.encode('utf-8') + salt_bytes)
    hashed_password_bytes = hashed_password.digest()

    # Return the hashed password as a hexadecimal string
    return hashed_password_bytes.hex()
