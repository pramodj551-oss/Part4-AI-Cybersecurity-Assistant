"""Generate a PBKDF2-SHA256 password hash for AUTH_PASSWORD_HASH."""

from __future__ import annotations

import getpass
import os
import sys


def get_password() -> str:
    # Allow non-interactive passing via environment variable if needed
    env_pass = os.getenv("AUTH_PASSWORD")
    if env_pass:
        return env_pass

    password = getpass.getpass("Password: ")
    confirmation = getpass.getpass("Confirm password: ")

    if not password:
        sys.exit("Error: Password cannot be empty.")
    if password != confirmation:
        sys.exit("Error: Passwords do not match.")

    return password


def main() -> None:
    password = get_password()

    # Import locally to keep utility decoupled until execution
    from src.auth import hash_password

    iterations = int(os.getenv("AUTH_PBKDF2_ITERATIONS", "600000"))
    password_hash = hash_password(password, iterations=iterations)

    print(f"\nAUTH_PASSWORD_HASH={password_hash}")


if __name__ == "__main__":
    main()
