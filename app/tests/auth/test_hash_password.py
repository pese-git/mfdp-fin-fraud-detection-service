import pytest
from src.auth.hash_password import HashPassword

hash_password = HashPassword()


def test_create_hash() -> None:
    password = "mysecurepassword"
    hashed = hash_password.create_hash(password)

    assert hashed is not None
    assert hashed != password  # Убедитесь, что пароли не хранятся в открытом виде
    assert len(hashed) > len(password)  # Хэш длиннее, чем исходный пароль


def test_verify_hash() -> None:
    password = "anothersecurepassword"
    hashed = hash_password.create_hash(password)

    # Убедимся, что хэш соответствует паролю
    assert hash_password.verify_hash(password, hashed)

    # Проверьте, что неправильные пароли не проходят проверку
    assert not hash_password.verify_hash("wrongpassword", hashed)
    assert not hash_password.verify_hash(
        "AnotherSecurePassword", hashed
    )  # Чувствительность к регистру
