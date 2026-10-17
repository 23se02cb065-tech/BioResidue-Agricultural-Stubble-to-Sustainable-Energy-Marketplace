import os
from dotenv import load_dotenv

# Load env variables from a .env file if it exists
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret-key-change-in-production')
    
    # PostgreSQL by default, fallback to SQLite locally
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'app.db')
    )
    
    # In sqlite, pg-specific or decimal features are handled gracefully
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ChromaDB configuration
    CHROMA_PERSIST_DIRECTORY = os.environ.get(
        'CHROMA_DB_DIR',
        os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'chroma_db')
    )
    
    # JWT expiration in seconds (default: 1 day)
    JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))
