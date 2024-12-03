import secrets
import os
from dotenv import load_dotenv, set_key

def generate_secrets():
    secret_key = secrets.token_hex(32)
    jwt_secret_key = secrets.token_hex(32)
    return secret_key, jwt_secret_key

def set_env_variables(secret_key, jwt_secret_key, database_url, env_path='.env'):
    if not os.path.exists(env_path):
        open(env_path, 'a').close()
    load_dotenv(dotenv_path=env_path)
    set_key(env_path, 'SECRET_KEY', secret_key)
    set_key(env_path, 'JWT_SECRET_KEY', jwt_secret_key)
    set_key(env_path, 'DATABASE_URL', database_url)

def main():
    secret_key, jwt_secret_key = generate_secrets()
    database_url = 'mysql+pymysql://root:pass@127.0.0.1:3306/currency_stock_db'
    set_env_variables(secret_key, jwt_secret_key, database_url)
    print("SECRET_KEY, JWT_SECRET_KEY, and DATABASE_URL have been generated and saved to .env")

if __name__ == "__main__":
    main()
