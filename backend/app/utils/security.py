from passlib.context import CryptContext

# Configure bcrypt as the hashing algorithm
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# Hash a plain password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Verify a password during login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )