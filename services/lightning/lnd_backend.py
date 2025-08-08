"""
Lightning Digital Marketplace - LND Backend
Stage 4: Production Ready

LND REST API Lightning service implementation
"""

from services.lightning.lightning_factory import LightningServiceInterface
from typing import Dict, Any
import requests
import os
import base64
from datetime import datetime, timedelta

class LNDRestService(LightningServiceInterface):
    """LND REST API Lightning service"""
    
    def __init__(self):
        self.host = os.getenv('LND_HOST', 'localhost')
        self.port = os.getenv('LND_PORT', '8080')
        self.cert_path = os.getenv('LND_CERT_PATH')
        self.macaroon_path = os.getenv('LND_MACAROON_PATH')
        self.network = os.getenv('LIGHTNING_NETWORK', 'mainnet')
        
        self.base_url = f"https://{self.host}:{self.port}/v1"
        
        # Load TLS certificate and macaroon
        self.cert_file = self._load_cert()
        self.macaroon = self._load_macaroon()
        
        if not self.macaroon:
            raise ValueError("LND_MACAROON_PATH not found or invalid")
    
    def _load_cert(self) -> str:
        """Load LND TLS certificate"""
        try:
            if self.cert_path and os.path.exists(self.cert_path):
                return self.cert_path
            return False  # Use verify=False for requests
        except Exception:
            return False
    
    def _load_macaroon(self) -> str:
        """Load LND macaroon for authentication"""
        try:
            if not self.macaroon_path or not os.path.exists(self.macaroon_path):
                return None
            
            with open(self.macaroon_path, 'rb') as f:
                macaroon_bytes = f.read()
                return base64.b64encode(macaroon_bytes).decode('ascii')
        except Exception as e:
            print(f"Error loading macaroon: {e}")
            return None
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """Make authenticated request to LND REST API"""
        try:
            headers = {
                'Grpc-Metadata-macaroon': self.macaroon,
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}{endpoint}"
            
            # Use cert file if available, otherwise skip verification (for development)
            verify = self.cert_file if self.cert_file else False
            
            if method == 'GET':
                response = requests.get(url, headers=headers, verify=verify, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, verify=verify, timeout=30)
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
                    'error': f"LND API error: {response.status_code} - {response.text}",
                    'status_code': response.status_code
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"LND API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"LND API error: {str(e)}"
            }
    
    def get_node_info(self) -> Dict[str, Any]:
        """Get Lightning node information"""
        try:
            result = self._make_request('/getinfo')
            
            if result['success']:
                data = result['data']
                return {
                    'success': True,
                    'backend': 'lnd_rest',
                    'node_info': {
                        'alias': data.get('alias', 'LND Node'),
                        'identity_pubkey': data.get('identity_pubkey', ''),
                        'num_active_channels': int(data.get('num_active_channels', 0)),
                        'num_peers': int(data.get('num_peers', 0)),
                        'block_height': int(data.get('block_height', 0)),
                        'synced_to_chain': data.get('synced_to_chain', False),
                        'version': data.get('version', 'LND'),
                        'network': data.get('chains', [{}])[0].get('network', self.network)
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'backend': 'lnd_rest'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"LND backend error: {str(e)}",
                'backend': 'lnd_rest'
            }
    
    def create_invoice(self, amount_sats: int, description: str, expiry_seconds: int = 900) -> Dict[str, Any]:
        """Create a Lightning invoice"""
        try:
            data = {
                'value': amount_sats,
                'memo': description,
                'expiry': expiry_seconds
            }
            
            result = self._make_request('/invoices', 'POST', data)
            
            if result['success']:
                invoice_data = result['data']
                expires_at = datetime.now() + timedelta(seconds=expiry_seconds)
                
                return {
                    'success': True,
                    'backend': 'lnd_rest',
                    'payment_request': invoice_data['payment_request'],
                    'payment_hash': invoice_data['r_hash'],
                    'amount_sats': amount_sats,
                    'description': description,
                    'expires_at': expires_at.isoformat(),
                    'expiry_seconds': expiry_seconds,
                    'network': self.network,
                    'add_index': invoice_data.get('add_index')
                }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'backend': 'lnd_rest'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create LND invoice: {str(e)}",
                'backend': 'lnd_rest'
            }
    
    def check_invoice(self, payment_hash: str) -> Dict[str, Any]:
        """Check if invoice has been paid"""
        try:
            # Convert hex payment hash to base64 for LND API
            payment_hash_b64 = base64.b64encode(bytes.fromhex(payment_hash)).decode('ascii')
            
            result = self._make_request(f'/invoice/{payment_hash_b64}')
            
            if result['success']:
                invoice_data = result['data']
                state = invoice_data.get('state', 'OPEN')
                
                if state == 'SETTLED':
                    return {
                        'success': True,
                        'backend': 'lnd_rest',
                        'payment_hash': payment_hash,
                        'status': 'paid',
                        'paid_at': datetime.fromtimestamp(int(invoice_data.get('settle_date', 0))).isoformat(),
                        'payment_preimage': invoice_data.get('r_preimage'),
                        'amount_received_sats': int(invoice_data.get('amt_paid_sat', 0))
                    }
                elif state == 'CANCELED':
                    return {
                        'success': True,
                        'backend': 'lnd_rest',
                        'payment_hash': payment_hash,
                        'status': 'cancelled'
                    }
                else:
                    return {
                        'success': True,
                        'backend': 'lnd_rest',
                        'payment_hash': payment_hash,
                        'status': 'pending'
                    }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'backend': 'lnd_rest'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to check LND invoice: {str(e)}",
                'backend': 'lnd_rest'
            }
    
    def get_balance(self) -> Dict[str, Any]:
        """Get wallet balance"""
        try:
            # Get wallet balance
            wallet_result = self._make_request('/balance/blockchain')
            channel_result = self._make_request('/balance/channels')
            
            if wallet_result['success'] and channel_result['success']:
                wallet_data = wallet_result['data']
                channel_data = channel_result['data']
                
                return {
                    'success': True,
                    'backend': 'lnd_rest',
                    'balance': {
                        'total_balance_sats': int(wallet_data.get('total_balance', 0)),
                        'confirmed_balance_sats': int(wallet_data.get('confirmed_balance', 0)),
                        'unconfirmed_balance_sats': int(wallet_data.get('unconfirmed_balance', 0)),
                        'channel_balance_sats': int(channel_data.get('balance', 0)),
                        'channel_pending_sats': int(channel_data.get('pending_open_balance', 0))
                    },
                    'network': self.network
                }
            else:
                error = wallet_result.get('error') or channel_result.get('error')
                return {
                    'success': False,
                    'error': error,
                    'backend': 'lnd_rest'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to get LND balance: {str(e)}",
                'backend': 'lnd_rest'
            }
    
    def pay_invoice(self, payment_request: str) -> Dict[str, Any]:
        """Pay a Lightning invoice"""
        try:
            data = {
                'payment_request': payment_request
            }
            
            result = self._make_request('/channels/transactions', 'POST', data)
            
            if result['success']:
                payment_data = result['data']
                
                return {
                    'success': True,
                    'backend': 'lnd_rest',
                    'payment_hash': payment_data.get('payment_hash'),
                    'payment_preimage': payment_data.get('payment_preimage'),
                    'fee_paid_sats': int(payment_data.get('payment_route', {}).get('total_fees', 0)),
                    'route_hops': len(payment_data.get('payment_route', {}).get('hops', [])),
                    'paid_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': result['error'],
                    'backend': 'lnd_rest'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to pay LND invoice: {str(e)}",
                'backend': 'lnd_rest'
            }

