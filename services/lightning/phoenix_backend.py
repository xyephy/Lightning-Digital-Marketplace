"""
Lightning Digital Marketplace - Phoenix Backend
Stage 4: Production Ready

Phoenix Wallet Lightning service implementation
"""

from services.lightning.lightning_factory import LightningServiceInterface
from typing import Dict, Any
import requests
import os
from datetime import datetime, timedelta

class PhoenixLightningService(LightningServiceInterface):
    """Phoenix Wallet Lightning service"""
    
    def __init__(self):
        self.api_token = os.getenv('PHOENIX_API_TOKEN')
        self.api_url = os.getenv('PHOENIX_API_URL', 'https://api.phoenix.acinq.co/v1')
        self.network = os.getenv('LIGHTNING_NETWORK', 'mainnet')
        
        if not self.api_token:
            raise ValueError("PHOENIX_API_TOKEN environment variable is required")
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """Make authenticated request to Phoenix API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.api_url}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"Phoenix API error: {response.status_code} - {response.text}",
                    'status_code': response.status_code
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Phoenix API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Phoenix API error: {str(e)}"
            }
    
    def get_node_info(self) -> Dict[str, Any]:
        """Get Lightning node information"""
        try:
            result = self._make_request('/info')
            
            if result['success']:
                data = result['data']
                return {
                    'success': True,
                    'backend': 'phoenix',
                    'node_info': {
                        'alias': data.get('alias', 'Phoenix Wallet'),
                        'identity_pubkey': data.get('node_id', ''),
                        'num_active_channels': data.get('num_channels', 0),
                        'num_peers': data.get('num_peers', 0),
                        'block_height': data.get('block_height', 0),
                        'synced_to_chain': data.get('synced_to_chain', True),
                        'version': data.get('version', 'Phoenix'),
                        'network': self.network
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'backend': 'phoenix'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Phoenix backend error: {str(e)}",
                'backend': 'phoenix'
            }
    
    def create_invoice(self, amount_sats: int, description: str, expiry_seconds: int = 900) -> Dict[str, Any]:
        """Create a Lightning invoice"""
        try:
            data = {
                'amount_msat': amount_sats * 1000,  # Convert sats to millisats
                'description': description,
                'expiry': expiry_seconds
            }
            
            result = self._make_request('/createinvoice', 'POST', data)
            
            if result['success']:
                invoice_data = result['data']
                expires_at = datetime.now() + timedelta(seconds=expiry_seconds)
                
                return {
                    'success': True,
                    'backend': 'phoenix',
                    'payment_request': invoice_data['bolt11'],
                    'payment_hash': invoice_data['payment_hash'],
                    'amount_sats': amount_sats,
                    'description': description,
                    'expires_at': expires_at.isoformat(),
                    'expiry_seconds': expiry_seconds,
                    'network': self.network
                }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'backend': 'phoenix'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create Phoenix invoice: {str(e)}",
                'backend': 'phoenix'
            }
    
    def check_invoice(self, payment_hash: str) -> Dict[str, Any]:
        """Check if invoice has been paid"""
        try:
            result = self._make_request(f'/checkinvoice/{payment_hash}')
            
            if result['success']:
                invoice_data = result['data']
                status = invoice_data.get('status', 'pending')
                
                if status == 'paid':
                    return {
                        'success': True,
                        'backend': 'phoenix',
                        'payment_hash': payment_hash,
                        'status': 'paid',
                        'paid_at': invoice_data.get('paid_at'),
                        'payment_preimage': invoice_data.get('payment_preimage'),
                        'amount_received_sats': invoice_data.get('amount_msat', 0) // 1000
                    }
                else:
                    return {
                        'success': True,
                        'backend': 'phoenix',
                        'payment_hash': payment_hash,
                        'status': status
                    }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'backend': 'phoenix'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to check Phoenix invoice: {str(e)}",
                'backend': 'phoenix'
            }
    
    def get_balance(self) -> Dict[str, Any]:
        """Get wallet balance"""
        try:
            result = self._make_request('/balance')
            
            if result['success']:
                balance_data = result['data']
                
                return {
                    'success': True,
                    'backend': 'phoenix',
                    'balance': {
                        'total_balance_sats': balance_data.get('balance_msat', 0) // 1000,
                        'confirmed_balance_sats': balance_data.get('confirmed_msat', 0) // 1000,
                        'unconfirmed_balance_sats': balance_data.get('unconfirmed_msat', 0) // 1000,
                        'channel_balance_sats': balance_data.get('channel_msat', 0) // 1000,
                        'channel_pending_sats': balance_data.get('pending_msat', 0) // 1000
                    },
                    'network': self.network
                }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'backend': 'phoenix'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to get Phoenix balance: {str(e)}",
                'backend': 'phoenix'
            }
    
    def pay_invoice(self, payment_request: str) -> Dict[str, Any]:
        """Pay a Lightning invoice"""
        try:
            data = {
                'bolt11': payment_request
            }
            
            result = self._make_request('/payinvoice', 'POST', data)
            
            if result['success']:
                payment_data = result['data']
                
                return {
                    'success': True,
                    'backend': 'phoenix',
                    'payment_hash': payment_data['payment_hash'],
                    'payment_preimage': payment_data['payment_preimage'],
                    'fee_paid_sats': payment_data.get('fee_msat', 0) // 1000,
                    'route_hops': payment_data.get('route_hops', 0),
                    'paid_at': payment_data.get('paid_at', datetime.now().isoformat())
                }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'backend': 'phoenix'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to pay Phoenix invoice: {str(e)}",
                'backend': 'phoenix'
            }
