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
    
    def create_invoice(self, node_name: str, amount_sats: int, description: str) -> Optional[Dict]:
        """Create a Lightning invoice (Stage 2 functionality preview)"""
        # This will be implemented in Stage 2
        return {
            'success': False,
            'error': 'Invoice creation will be implemented in Stage 2',
            'stage': 'Stage 2: Commerce Core'
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

