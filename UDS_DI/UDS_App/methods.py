import hashlib
import datetime
import jwt
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from zipfile import ZipFile


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

def zip_files(self, file_paths):
        unique_name = datetime.now().strftime("%Y%m%d%H%M%S")
        zip_file_path = os.path.join("D:/", f'zipped_files_{unique_name}.zip')
        file_names = []

        with ZipFile(zip_file_path, 'w') as zip_file:
            for file_path in file_paths:
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    file_names.append(os.path.basename(file_path))
                    with open(file_path, 'rb') as file_content:
                        arcname = os.path.basename(file_path)
                        print(f"Adding to zip: {file_path} with arcname {arcname}")
                        zip_file.writestr(arcname, file_content.read())

        return zip_file_path, file_names

def send_email(self, to_email, email_subject, email_body, zip_file_path):
    sender_email = 'gibson.25cs@licet.ac.in'
    sender_password = 'NARSELmary1305@'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = email_subject
    body = email_body
    msg.attach(MIMEText(body, 'plain'))
    print(f"Attaching zip file: {zip_file_path}")
    attachment = open(zip_file_path, 'rb')
    part = MIMEBase('application', 'zip')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(zip_file_path))
    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login(sender_email, sender_password)
        # server.sendmail(sender_email, to_email, msg.as_string())
        # server.quit()
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise  # Re-raise the exception for the calling function to handle