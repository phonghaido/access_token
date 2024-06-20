import os
import argon2
import datetime

POSTGRES_DATABASE_CONNECTION = os.getenv("POSTGRES_DATABASE_CONNECTION")
TOKEN_NAME_LENGTH_LIMIT = 64
TOKEN_NAME_REGEX = "^[a-zA-Z0-9][a-zA-Z0-9\\-]*$"
TOKEN_TTL = datetime.timedelta(days=3 * 30)
MAXIMUM_TOKEN_NUMBER = 60
PASSWORD_HASHER = argon2.PasswordHasher()