import hashlib
import datetime
import jwt

def encrypt_password(raw_password):
    salt = hashlib.sha256()
    salt.update(raw_password.encode('utf-8'))
    salt_bytes = salt.digest()

    hashed_password = hashlib.sha256()
    hashed_password.update(raw_password.encode('utf-8') + salt_bytes)
    hashed_password_bytes = hashed_password.digest()

    return hashed_password_bytes.hex()

def users_encode_token(payload: dict):
    """
    The function `admin_users_encode_token` encodes a payload dictionary into a JSON Web Token (JWT)
    using the "admin_key" as the secret key and the HS256 algorithm, with the expiration time set to 7
    days from the current UTC time.

    :param payload: The payload is a dictionary that contains the data to be encoded into the token. It
    can include any key-value pairs that you want to include in the token
    :type payload: dict
    :return: a token encoded using the JWT (JSON Web Token) library.
    """
    payload["exp"] = datetime.datetime.now(
        tz=datetime.timezone.utc
    ) + datetime.timedelta(days=7)
    token = jwt.encode(payload, "user_key", algorithm="HS256")
    return token

def admin_encode_token(payload: dict):
    """
    The function `admin_users_encode_token` encodes a payload dictionary into a JSON Web Token (JWT)
    using the "admin_key" as the secret key and the HS256 algorithm, with the expiration time set to 7
    days from the current UTC time.

    :param payload: The payload is a dictionary that contains the data to be encoded into the token. It
    can include any key-value pairs that you want to include in the token
    :type payload: dict
    :return: a token encoded using the JWT (JSON Web Token) library.
    """
    payload["exp"] = datetime.datetime.now(
        tz=datetime.timezone.utc
    ) + datetime.timedelta(days=7)
    token = jwt.encode(payload, "admin_key", algorithm="HS256")
    return token