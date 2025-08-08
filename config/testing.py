"""
Lightning Digital Marketplace - Testing Configuration
Stage 4: Production Ready
"""

import os

class TestingConfig:
    """Testing environment configuration"""
    
    # Flask Configuration
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    
    # Lightning Configuration - Testing (Mock)
    LIGHTNING_BACKEND = os.getenv('TEST_LIGHTNING_BACKEND', 'polar')
    LIGHTNING_NETWORK = 'regtest'
    
    # Mock Polar Configuration
    POLAR_API_URL = 'http://localhost:8080'
    POLAR_NETWORK = '17'
    POLAR_ALICE_PORT = 8081
    POLAR_BOB_PORT = 8082
    POLAR_CAROL_PORT = 8083
    
    # Test Database Configuration
    DATABASE_URL = 'sqlite:///:memory:'  # In-memory database for tests
    
    # Security Configuration
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']
    
    # Testing Features
    ENABLE_DEBUG_ENDPOINTS = True
    LOG_LEVEL = 'DEBUG'
    SIMULATE_PAYMENTS = True  # Always simulate payments in tests
    MOCK_LIGHTNING_RESPONSES = True  # Mock all Lightning API responses
    
    # WebSocket Configuration
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_LOGGER = False
    SOCKETIO_ENGINEIO_LOGGER = False
    
    # Test Performance Configuration
    PAYMENT_CHECK_INTERVAL = 1  # Faster checks for tests
    INVOICE_EXPIRY_SECONDS = 60  # Shorter expiry for tests
    
    @staticmethod
    def get_config_info():
        """Get configuration information for testing"""
        return {
            'environment': 'testing',
            'debug': True,
            'lightning_backend': 'mock',
            'network': 'regtest',
            'database': 'memory',
            'features': {
                'debug_endpoints': True,
                'payment_simulation': True,
                'mock_responses': True,
                'fast_timeouts': True
            }
        }

