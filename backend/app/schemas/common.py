from typing import Annotated

from pydantic import AfterValidator, StringConstraints


def validate_password_characters(password: str) -> str:
    has_letter = any("A" <= character <= "Z" or "a" <= character <= "z" for character in password)
    has_number = any("0" <= character <= "9" for character in password)
    if not has_letter or not has_number:
        raise ValueError("Password must include at least one letter and one number")
    return password


Password = Annotated[
    str,
    StringConstraints(
        min_length=12,
        max_length=128,
    ),
    AfterValidator(validate_password_characters),
]
