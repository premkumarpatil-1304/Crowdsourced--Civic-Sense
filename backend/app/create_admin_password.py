from passlib.context import CryptContext

# The password you want to hash
plain_password = "prempatil"

# Initialize the same password context as your application
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password
hashed_password = pwd_context.hash(plain_password)

print(f"Plain Password: {plain_password}")
print(f"Hashed Password: {hashed_password}")