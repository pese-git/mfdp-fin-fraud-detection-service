from passlib.context import CryptContext
from typing import cast

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashPassword:
    def create_hash(self, password: str) -> str:
        return cast(str, pwd_context.hash(password))

    def verify_hash(self, plain_password: str, hashed_password: str) -> bool:
        return cast(bool, pwd_context.verify(plain_password, hashed_password))
