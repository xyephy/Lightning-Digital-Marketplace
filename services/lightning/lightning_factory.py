"""
Lightning Digital Marketplace - Lightning Factory
Stage 4: Production Ready

Factory pattern for creating different Lightning service backends
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os

class LightningServiceInterface(ABC):
    """Abstract interface for Lightning services"""
    
    @abstractmethod
    def get_node_info(self) -> Dict[str, Any]:
        """Get Lightning node information"""
        pass
    
    @abstractmethod
    def create_invoice(self, amount_sats: int, description: str, expiry_seconds: int = 900) -> Dict[str, Any]:
        """Create a Lightning invoice"""
        pass
    
    @abstractmethod
    def check_invoice(self, payment_hash: str) -> Dict[str, Any]:
        """Check if invoice has been paid"""
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict[str, Any]:
        """Get wallet balance"""
        pass
    
    @abstractmethod
    def pay_invoice(self, payment_request: str) -> Dict[str, Any]:
        """Pay a Lightning invoice"""
        pass

class LightningFactory:
    """Factory for creating Lightning service instances"""
    
    SUPPORTED_BACKENDS = ['polar', 'phoenix', 'breeze', 'lnd_rest', 'cln_rest']
    
    @staticmethod
    def create_service(backend_type: str = None) -> LightningServiceInterface:
        """Create Lightning service based on backend type"""
        
        if backend_type is None:
            backend_type = os.getenv('LIGHTNING_BACKEND', 'polar')
        
        backend_type = backend_type.lower()
        
        if backend_type == 'polar':
            from services.lightning.polar_backend import PolarLightningService
            return PolarLightningService()
        
        elif backend_type == 'phoenix':
            from services.lightning.phoenix_backend import PhoenixLightningService
            return PhoenixLightningService()
        
        elif backend_type == 'breeze':
            from services.lightning.breeze_backend import BreezeLightningService
            return BreezeLightningService()
        
        elif backend_type == 'lnd_rest':
            from services.lightning.lnd_backend import LNDRestService
            return LNDRestService()
        
        elif backend_type == 'cln_rest':
            from services.lightning.cln_backend import CLNRestService
            return CLNRestService()
        
        else:
            raise ValueError(f"Unsupported Lightning backend: {backend_type}. "
                           f"Supported backends: {', '.join(LightningFactory.SUPPORTED_BACKENDS)}")
    
    @staticmethod
    def get_available_backends() -> Dict[str, Dict[str, Any]]:
        """Get information about available backends"""
        return {
            'polar': {
                'name': 'Polar Lightning Network',
                'description': 'Local development Lightning network using Polar',
                'network': 'regtest',
                'production_ready': False,
                'requirements': ['Polar application running']
            },
            'phoenix': {
                'name': 'Phoenix Wallet',
                'description': 'ACINQ Phoenix wallet Lightning backend',
                'network': 'mainnet/testnet',
                'production_ready': True,
                'requirements': ['Phoenix API credentials']
            },
            'breeze': {
                'name': 'Breeze SDK',
                'description': 'Blockstream Breeze Lightning SDK',
                'network': 'mainnet/testnet',
                'production_ready': True,
                'requirements': ['Breeze SDK setup']
            },
            'lnd_rest': {
                'name': 'LND REST API',
                'description': 'Lightning Network Daemon REST API',
                'network': 'mainnet/testnet/regtest',
                'production_ready': True,
                'requirements': ['LND node', 'TLS cert', 'Macaroon']
            },
            'cln_rest': {
                'name': 'Core Lightning REST',
                'description': 'Core Lightning REST API',
                'network': 'mainnet/testnet/regtest',
                'production_ready': True,
                'requirements': ['Core Lightning node', 'REST plugin']
            }
        }
    
    @staticmethod
    def validate_backend_config(backend_type: str) -> Dict[str, Any]:
        """Validate configuration for specified backend"""
        validation_result = {
            'valid': False,
            'backend': backend_type,
            'errors': [],
            'warnings': [],
            'config_found': {}
        }
        
        try:
            if backend_type == 'polar':
                # Check Polar configuration
                polar_url = os.getenv('POLAR_API_URL')
                polar_network = os.getenv('POLAR_NETWORK')
                
                if polar_url:
                    validation_result['config_found']['polar_url'] = polar_url
                else:
                    validation_result['errors'].append('POLAR_API_URL not configured')
                
                if polar_network:
                    validation_result['config_found']['polar_network'] = polar_network
                else:
                    validation_result['warnings'].append('POLAR_NETWORK not configured, using default')
            
            elif backend_type == 'phoenix':
                # Check Phoenix configuration
                phoenix_token = os.getenv('PHOENIX_API_TOKEN')
                phoenix_url = os.getenv('PHOENIX_API_URL')
                
                if not phoenix_token:
                    validation_result['errors'].append('PHOENIX_API_TOKEN not configured')
                if not phoenix_url:
                    validation_result['errors'].append('PHOENIX_API_URL not configured')
                
                if phoenix_token:
                    validation_result['config_found']['phoenix_token'] = '***' + phoenix_token[-4:]
                if phoenix_url:
                    validation_result['config_found']['phoenix_url'] = phoenix_url
            
            elif backend_type == 'breeze':
                # Check Breeze configuration
                breeze_api_key = os.getenv('BREEZE_API_KEY')
                breeze_seed = os.getenv('BREEZE_SEED')
                
                if not breeze_api_key:
                    validation_result['errors'].append('BREEZE_API_KEY not configured')
                if not breeze_seed:
                    validation_result['errors'].append('BREEZE_SEED not configured')
                
                if breeze_api_key:
                    validation_result['config_found']['breeze_api_key'] = '***' + breeze_api_key[-4:]
                if breeze_seed:
                    validation_result['config_found']['breeze_seed'] = 'configured'
            
            elif backend_type == 'lnd_rest':
                # Check LND configuration
                lnd_host = os.getenv('LND_HOST')
                lnd_port = os.getenv('LND_PORT')
                lnd_cert_path = os.getenv('LND_CERT_PATH')
                lnd_macaroon_path = os.getenv('LND_MACAROON_PATH')
                
                if not lnd_host:
                    validation_result['errors'].append('LND_HOST not configured')
                if not lnd_cert_path:
                    validation_result['errors'].append('LND_CERT_PATH not configured')
                if not lnd_macaroon_path:
                    validation_result['errors'].append('LND_MACAROON_PATH not configured')
                
                validation_result['config_found'].update({
                    'lnd_host': lnd_host,
                    'lnd_port': lnd_port or '8080',
                    'lnd_cert_path': lnd_cert_path,
                    'lnd_macaroon_path': lnd_macaroon_path
                })
            
            elif backend_type == 'cln_rest':
                # Check Core Lightning configuration
                cln_host = os.getenv('CLN_HOST')
                cln_port = os.getenv('CLN_PORT')
                cln_cert_path = os.getenv('CLN_CERT_PATH')
                
                if not cln_host:
                    validation_result['errors'].append('CLN_HOST not configured')
                
                validation_result['config_found'].update({
                    'cln_host': cln_host,
                    'cln_port': cln_port or '3001',
                    'cln_cert_path': cln_cert_path
                })
            
            # Set valid flag
            validation_result['valid'] = len(validation_result['errors']) == 0
            
        except Exception as e:
            validation_result['errors'].append(f"Configuration validation error: {str(e)}")
        
        return validation_result
    
    @staticmethod
    def test_backend_connection(backend_type: str) -> Dict[str, Any]:
        """Test connection to specified backend"""
        test_result = {
            'success': False,
            'backend': backend_type,
            'response_time_ms': None,
            'error': None,
            'node_info': None
        }
        
        try:
            import time
            start_time = time.time()
            
            # Create service and test connection
            service = LightningFactory.create_service(backend_type)
            node_info = service.get_node_info()
            
            end_time = time.time()
            test_result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
            
            if node_info.get('success', False):
                test_result['success'] = True
                test_result['node_info'] = node_info
            else:
                test_result['error'] = node_info.get('error', 'Unknown error')
        
        except Exception as e:
            test_result['error'] = str(e)
        
        return test_result
