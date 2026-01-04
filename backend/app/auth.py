import bcrypt

def hash_password(password: str) -> str:
    password_bytes = password.encode()
    password_hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return password_hashed.decode()

def check_password(password: str, password_hashed: str) -> bool:
    password_bytes = password.encode()
    password_hashed_bytes = password_hashed.encode()
    return bcrypt.checkpw(password_bytes, password_hashed_bytes)


