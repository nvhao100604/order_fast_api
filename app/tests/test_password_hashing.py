from app.core.security import get_password_hash


hashed_pass = get_password_hash("123456")
print(f"Hashed password is: {hashed_pass}")