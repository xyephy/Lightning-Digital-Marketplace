"""
Lightning Digital Marketplace - Development Configuration
Stage 4: Production Ready
"""

import os

class DevelopmentConfig:
    """Development environment configuration"""
    
    # Flask Configuration
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Lightning Configuration - Development (Polar)
    LIGHTNING_BACKEND = os.getenv('LIGHTNING_BACKEND', 'polar')
    LIGHTNING_NETWORK = os.getenv('LIGHTNING_NETWORK', 'regtest')
    
    # Polar Configuration
    POLAR_API_URL = os.getenv('POLAR_API_URL', 'http://localhost:8080')
    POLAR_NETWORK = os.getenv('POLAR_NETWORK', '17')
    POLAR_ALICE_PORT = int(os.getenv('POLAR_ALICE_PORT', '8081'))
    POLAR_BOB_PORT = int(os.getenv('POLAR_BOB_PORT', '8082'))
    POLAR_CAROL_PORT = int(os.getenv('POLAR_CAROL_PORT', '8083'))
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///marketplace_dev.db')
    
    # Security Configuration
    CORS_ORIGINS = ['http://localhost:5000', 'http://localhost:3000', 'http://127.0.0.1:5000']
    
    # Development Features
    ENABLE_DEBUG_ENDPOINTS = True
    LOG_LEVEL = 'DEBUG'
    SIMULATE_PAYMENTS = True  # Enable payment simulation for development
    
    # WebSocket Configuration
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_LOGGER = True
    SOCKETIO_ENGINEIO_LOGGER = True
    
    @staticmethod
    def get_config_info():
        """Get configuration information for debugging"""
        return {
            'environment': 'development',
            'debug': True,
            'lightning_backend': 'polar',
            'network': 'regtest',
            'database': 'sqlite',
            'features': {
                'debug_endpoints': True,
                'payment_simulation': True,
                'verbose_logging': True
            }
        }

