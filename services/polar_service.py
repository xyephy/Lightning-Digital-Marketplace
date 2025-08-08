"""
Lightning Digital Marketplace - Polar Lightning Service
Stage 1: Foundation Setup

This service handles connection to Polar Lightning Network nodes.
"""

import requests
import os
import json
from typing import Dict, Optional, Any

class PolarService:
    """Service class for interacting with Polar Lightning Network"""
    
    def __init__(self):
        """Initialize Polar Lightning service"""
        self.base_url = os.getenv('POLAR_API_URL', 'http://localhost:8080')
        self.network = os.getenv('POLAR_NETWORK', '17')
        self.alice_port = int(os.getenv('POLAR_ALICE_PORT', '8081'))
        self.bob_port = int(os.getenv('POLAR_BOB_PORT', '8082'))
        self.carol_port = int(os.getenv('POLAR_CAROL_PORT', '8083'))
        
        # Node configuration
        self.nodes = {
            'alice': {
                'name': 'Alice',
                'port': self.alice_port,
                'host': 'localhost'
            },
            'bob': {
                'name': 'Bob', 
                'port': self.bob_port,
                'host': 'localhost'
            },
            'carol': {
                'name': 'Carol',
                'port': self.carol_port,
                'host': 'localhost'
            }
        }
    
    def get_macaroon_path(self, node_name: str) -> str:
        """Get the macaroon file path for a specific node"""
        user = os.getenv('USER')
        return f"/Users/{user}/.polar/networks/{self.network}/volumes/lnd/{node_name}/data/chain/bitcoin/regtest/admin.macaroon"
    
    def load_macaroon(self, node_name: str) -> Optional[str]:
        """Load macaroon for authentication"""
        try:
            macaroon_path = self.get_macaroon_path(node_name)
            with open(macaroon_path, 'rb') as f:
                macaroon = f.read().hex()
            return macaroon
        except Exception as e:
            print(f"❌ Error loading macaroon for {node_name}: {e}")
            return None
    
    def make_request(self, node_name: str, endpoint: str, method: str = 'GET', data: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Lightning node"""
        try:
            # Get node configuration
            if node_name not in self.nodes:
                raise ValueError(f"Unknown node: {node_name}")
            
            node = self.nodes[node_name]
            macaroon = self.load_macaroon(node_name)
            
            if not macaroon:
                return None
            
            # Setup request
            url = f"https://{node['host']}:{node['port']}{endpoint}"
            headers = {
                'Grpc-Metadata-macaroon': macaroon,
                'Content-Type': 'application/json'
            }
            
            # Make request
            if method == 'GET':
                response = requests.get(url, headers=headers, verify=False, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, verify=False, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Request failed with status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error making request to {node_name}: {e}")
            return None
    
    def get_node_info(self, node_name: str = 'alice') -> Dict[str, Any]:
        """Get information about a Lightning node"""
        try:
            response = self.make_request(node_name, '/v1/getinfo')
            if response:
                return {
                    'success': True,
                    'node_name': node_name,
                    'alias': response.get('alias', 'Unknown'),
                    'identity_pubkey': response.get('identity_pubkey', ''),
                    'num_active_channels': response.get('num_active_channels', 0),
                    'num_peers': response.get('num_peers', 0),
                    'block_height': response.get('block_height', 0),
                    'synced_to_chain': response.get('synced_to_chain', False),
                    'version': response.get('version', 'Unknown')
                }
            else:
                return {
                    'success': False,
                    'error': f'Could not connect to {node_name}',
                    'node_name': node_name
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'node_name': node_name
            }
    
    def get_all_nodes_info(self) -> Dict[str, Any]:
        """Get information about all Lightning nodes"""
        results = {}
        for node_name in self.nodes.keys():
            results[node_name] = self.get_node_info(node_name)
        return results
    
    def create_invoice(self, node: str, amount_sats: int, description: str, expiry: int = 900) -> Dict[str, Any]:
        """Create a Lightning invoice using LND REST API"""
        try:
            node_config = self.nodes.get(node, self.nodes['alice'])
            macaroon_hex = self.load_macaroon(node)
            
            if not macaroon_hex:
                print(f"ERROR: Could not load macaroon for node {node}")
                return {
                    'success': False,
                    'error': f'Could not load macaroon for node {node}'
                }
            
            url = f"https://localhost:{node_config['port']}/v1/invoices"
            headers = {
                'Grpc-Metadata-macaroon': macaroon_hex,
                'Content-Type': 'application/json'
            }
            
            data = {
                'value': amount_sats,
                'memo': description,
                'expiry': expiry
            }
            
            print(f"DEBUG: Creating invoice - URL: {url}")
            print(f"DEBUG: Data: {data}")
            print(f"DEBUG: Headers: {list(headers.keys())}")
            
            response = requests.post(
                url, 
                json=data, 
                headers=headers, 
                verify=False,  # Skip SSL verification for local development
                timeout=10
            )
            
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            
            if response.status_code == 200:
                invoice_data = response.json()
                print(f"SUCCESS: Invoice created - {invoice_data.get('payment_request', '')[:50]}...")
                return {
                    'success': True,
                    'payment_request': invoice_data['payment_request'],
                    'payment_hash': invoice_data.get('r_hash', ''),
                    'add_index': invoice_data.get('add_index', ''),
                    'payment_addr': invoice_data.get('payment_addr', '')
                }
            else:
                error_msg = f'Failed to create invoice: HTTP {response.status_code} - {response.text}'
                print(f"ERROR: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            error_msg = f'Error creating invoice: {str(e)}'
            print(f"ERROR: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def lookup_invoice(self, node: str, payment_hash: str) -> Dict[str, Any]:
        """Check if a Lightning invoice has been paid"""
        try:
            node_config = self.nodes.get(node, self.nodes['alice'])
            macaroon_hex = self.load_macaroon(node)
            
            if not macaroon_hex:
                return {
                    'success': False,
                    'error': f'Could not load macaroon for node {node}'
                }
            
            # Decode base64 payment hash for URL
            import base64
            payment_hash_bytes = base64.b64decode(payment_hash)
            payment_hash_hex = payment_hash_bytes.hex()
            
            url = f"https://localhost:{node_config['port']}/v1/invoice/{payment_hash_hex}"
            headers = {
                'Grpc-Metadata-macaroon': macaroon_hex,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                url, 
                headers=headers, 
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                invoice_data = response.json()
                return {
                    'success': True,
                    'settled': invoice_data.get('settled', False),
                    'state': invoice_data.get('state', 'OPEN'),
                    'value': invoice_data.get('value', 0),
                    'settle_date': invoice_data.get('settle_date', 0),
                    'creation_date': invoice_data.get('creation_date', 0)
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to lookup invoice: HTTP {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error looking up invoice: {str(e)}'
            }
    
    def check_connection_status(self) -> Dict[str, Any]:
        """Check the connection status of all nodes"""
        status = {
            'polar_running': False,
            'nodes_connected': 0,
            'total_nodes': len(self.nodes),
            'node_details': {}
        }
        
        connected_nodes = 0
        for node_name in self.nodes.keys():
            node_info = self.get_node_info(node_name)
            status['node_details'][node_name] = node_info
            
            if node_info['success']:
                connected_nodes += 1
        
        status['nodes_connected'] = connected_nodes
        status['polar_running'] = connected_nodes > 0
        
        return status

