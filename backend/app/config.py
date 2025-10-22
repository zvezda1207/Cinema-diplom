import os

POSTGRES_DB = os.getenv('POSTGRES_DB', 'cinema')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5434')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')

PG_DSN = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

TOKEN_TTL_SEC = 60 * 60 * 72