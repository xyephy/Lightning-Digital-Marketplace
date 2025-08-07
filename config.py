"""
Lightning Digital Marketplace - Configuration Management
Stage 1: Foundation Setup
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Polar Lightning Configuration
    POLAR_API_URL = os.getenv('POLAR_API_URL', 'http://localhost:8080')
    POLAR_NETWORK = os.getenv('POLAR_NETWORK', '17')
    POLAR_ALICE_PORT = int(os.getenv('POLAR_ALICE_PORT', '8081'))
    POLAR_BOB_PORT = int(os.getenv('POLAR_BOB_PORT', '8082'))
    POLAR_CAROL_PORT = int(os.getenv('POLAR_CAROL_PORT', '8083'))
    
    # Lightning Network Configuration
    LIGHTNING_BACKEND = os.getenv('LIGHTNING_BACKEND', 'polar')
    LIGHTNING_NETWORK = os.getenv('LIGHTNING_NETWORK', 'regtest')
    
    # Database Configuration (for future stages)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///marketplace.db')
    
    # Security Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000').split(',')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///test_marketplace.db'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

