import os
from datetime import date

class Config:
    # App configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Valentine's Day (change as needed)
    VALENTINES_DATE = date(2026, 2, 9)
    
    # Database configuration
    DATABASE_PATH = 'database.db'
    
    # Encryption key (in production, use environment variable)
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')