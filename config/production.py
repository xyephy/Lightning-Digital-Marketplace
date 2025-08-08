"""
Lightning Digital Marketplace - Production Configuration
Stage 4: Production Ready
"""

import os

class ProductionConfig:
    """Production environment configuration"""
    
    # Flask Configuration
    DEBUG = False
    TESTING = False
    _secret_key = os.getenv('SECRET_KEY')
    if not _secret_key:
        # Only raise error when config is actually used, not during import
        SECRET_KEY = None
    else:
        SECRET_KEY = _secret_key
    
    @classmethod
    def validate(cls):
        """Validate production configuration before use"""
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is required in production")
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required in production")
    
    # Lightning Configuration - Production
    LIGHTNING_BACKEND = os.getenv('LIGHTNING_BACKEND', 'phoenix')
    LIGHTNING_NETWORK = os.getenv('LIGHTNING_NETWORK', 'mainnet')
    
    # Phoenix Configuration
    PHOENIX_API_TOKEN = os.getenv('PHOENIX_API_TOKEN')
    PHOENIX_API_URL = os.getenv('PHOENIX_API_URL', 'https://api.phoenix.acinq.co/v1')
    
    # Breeze Configuration
    BREEZE_API_KEY = os.getenv('BREEZE_API_KEY')
    BREEZE_SEED = os.getenv('BREEZE_SEED')
    
    # LND Configuration
    LND_HOST = os.getenv('LND_HOST')
    LND_PORT = os.getenv('LND_PORT', '8080')
    LND_CERT_PATH = os.getenv('LND_CERT_PATH')
    LND_MACAROON_PATH = os.getenv('LND_MACAROON_PATH')
    
    # Core Lightning Configuration
    CLN_HOST = os.getenv('CLN_HOST')
    CLN_PORT = os.getenv('CLN_PORT', '3001')
    CLN_CERT_PATH = os.getenv('CLN_CERT_PATH')
    
    # Database Configuration (Production)
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        DATABASE_URL = None  # Will be validated when config is used
    
    # Security Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    
    # Production Features
    ENABLE_DEBUG_ENDPOINTS = False
    LOG_LEVEL = 'INFO'
    SIMULATE_PAYMENTS = False  # Real payments only in production
    
    # WebSocket Configuration
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_LOGGER = False
    SOCKETIO_ENGINEIO_LOGGER = False
    
    # Performance Configuration
    GUNICORN_WORKERS = int(os.getenv('GUNICORN_WORKERS', '4'))
    GUNICORN_BIND = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
    
    # Monitoring Configuration
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    
    # Cache Configuration
    REDIS_URL = os.getenv('REDIS_URL')
    CACHE_TYPE = 'redis' if REDIS_URL else 'simple'
    
    @staticmethod
    def validate_production_config():
        """Validate that all required production configurations are set"""
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        
        # Add backend-specific required variables
        lightning_backend = os.getenv('LIGHTNING_BACKEND', 'phoenix')
        
        if lightning_backend == 'phoenix':
            required_vars.extend(['PHOENIX_API_TOKEN'])
        elif lightning_backend == 'breeze':
            required_vars.extend(['BREEZE_API_KEY', 'BREEZE_SEED'])
        elif lightning_backend == 'lnd_rest':
            required_vars.extend(['LND_HOST', 'LND_MACAROON_PATH'])
        elif lightning_backend == 'cln_rest':
            required_vars.extend(['CLN_HOST'])
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Required environment variables missing: {', '.join(missing_vars)}")
        
        return True
    
    @staticmethod
    def get_config_info():
        """Get configuration information (safe for logging)"""
        return {
            'environment': 'production',
            'debug': False,
            'lightning_backend': os.getenv('LIGHTNING_BACKEND', 'phoenix'),
            'network': os.getenv('LIGHTNING_NETWORK', 'mainnet'),
            'database': 'postgresql' if 'postgresql' in os.getenv('DATABASE_URL', '') else 'other',
            'features': {
                'debug_endpoints': False,
                'payment_simulation': False,
                'metrics_enabled': os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
            }
        }

