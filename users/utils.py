import random
import hashlib
import secrets


def generate_code():
    code = int(''.join([str(random.randint(0, 10)) for _ in range(4)]))
    return code


def generate_ref():
    # Generate a random string
    random_string = secrets.token_hex(16)
    # Convert the string to bytes
    message = random_string.encode('utf-8')
    # Create an MD5 hash object
    md5_hash = hashlib.md5()
    # Update the hash object with the message
    md5_hash.update(message)
    # Get the hexadecimal representation of the hash
    return md5_hash.hexdigest()
