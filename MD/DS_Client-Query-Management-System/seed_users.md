# seed_users.py

## Purpose

This script inserts the project's demo client and support accounts into the existing `users` table. Run `init_schema.py` first so the database and table exist.

## Functions

### `hash_password(password)`

Encodes the password as UTF-8 and returns its SHA-256 hash as text. This matches the hashing approach in the main app. For real accounts, use a password-specific hashing method such as bcrypt or Argon2 instead.

### `seed_demo_users_standalone()`

Connects to the project database and attempts to add the demo accounts. It reports when an account was added or already exists, commits the inserts, and closes its connection. Other errors are printed so they are not silently ignored.

Run the script from the project folder:

```powershell
python seed_users.py
```

The demo credentials are intended only for local testing. Replace or remove them before deployment.
