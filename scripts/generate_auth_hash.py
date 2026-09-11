"""Generate a PBKDF2-SHA256 password hash for AUTH_PASSWORD_HASH."""

from __future__ import annotations

import getpass
import os


def main() -> None:
    password = getpass.getpass("Password:River!Cloud7#Mango92")
    confirmation = getpass.getpass("Confirm password:River!Cloud7#Mango92")
    if not password or password != confirmation:
        raise SystemExit("Passwords must be non-empty and match.")

    # Import after interactive validation so this utility has no application side effects.
    from src.auth import hash_password

    iterations = int(os.getenv("AUTH_PBKDF2_ITERATIONS", "600000"))
    print(hash_password(password, iterations=iterations))


if __name__ == "__main__":
    main()
