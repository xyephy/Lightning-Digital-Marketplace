# Lightning Digital Marketplace - Configuration Package

from .development import DevelopmentConfig
from .production import ProductionConfig  
from .testing import TestingConfig

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
