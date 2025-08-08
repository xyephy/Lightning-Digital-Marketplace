# 🚀 Production Lightning APIs

This guide provides **real Lightning APIs** that developers can use in their hackathon projects, portfolio applications, and learning experiments. All APIs listed here are production-ready services with actual Lightning Network integration.

## 🎯 Quick Start Recommendations

| **Experience Level** | **Recommended API** | **Why Choose This** |
|---------------------|--------------------|--------------------|
| **Beginner** | LNbits | Free demo instance, no signup required |
| **Intermediate** | Strike | Fiat integration, excellent docs |
| **Advanced** | OpenNode | Production-grade, used by real businesses |
| **Expert** | Voltage | Your own Lightning node in the cloud |

---

## 1. 🟢 LNbits - Best for Beginners

**Perfect for hackathons and learning - get started in 5 minutes!**

### Why LNbits?
- ✅ **Free demo instance** available at `demo.lnbits.com`
- ✅ **No signup required** for testing
- ✅ **Real Lightning transactions** on Bitcoin testnet/mainnet
- ✅ **Open source** - you can run your own instance
- ✅ **Active community** and great documentation

### Setup Instructions

#### Option 1: Use Demo Instance (Easiest)
1. Go to https://demo.lnbits.com
2. Click "Add a new wallet"
3. Copy your **Admin Key** and **Invoice Key**
4. Set environment variables:
   ```bash
   export LNBITS_API_URL="https://demo.lnbits.com"
   export LNBITS_ADMIN_KEY="your_admin_key_here"
   export LNBITS_INVOICE_KEY="your_invoice_key_here"
   ```

#### Option 2: Run Locally with Docker
```bash
# Run your own LNbits instance
docker run -p 5000:5000 lnbits/lnbits:latest

# Or use docker-compose
wget https://raw.githubusercontent.com/lnbits/lnbits/main/docker-compose.yml
docker-compose up -d
```

### Implementation Example
```python
import requests
from datetime import datetime, timedelta
from typing import Dict, Any

class LNbitsLightningService:
    """Real LNbits API - Works with demo.lnbits.com"""
    
    def __init__(self):
        self.api_url = os.getenv('LNBITS_API_URL', 'https://demo.lnbits.com')
        self.admin_key = os.getenv('LNBITS_ADMIN_KEY')
        self.invoice_key = os.getenv('LNBITS_INVOICE_KEY')
        
        if not self.admin_key or not self.invoice_key:
            raise ValueError("LNbits API keys are required. Get them from demo.lnbits.com")
    
    def create_invoice(self, amount_sats: int, description: str) -> Dict[str, Any]:
        """Create a real Lightning invoice"""
        try:
            headers = {
                'X-Api-Key': self.invoice_key,
                'Content-Type': 'application/json'
            }
            
            data = {
                'out': False,  # Incoming payment
                'amount': amount_sats,
                'memo': description,
                'unit': 'sat'
            }
            
            response = requests.post(
                f'{self.api_url}/api/v1/payments',
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    'success': True,
                    'backend': 'lnbits',
                    'payment_request': result['payment_request'],
                    'payment_hash': result['payment_hash'],
                    'amount_sats': amount_sats,
                    'checking_id': result['checking_id'],
                    'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'LNbits API error: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'LNbits request failed: {str(e)}'
            }
    
    def check_payment_status(self, checking_id: str) -> Dict[str, Any]:
        """Check if payment has been received"""
        try:
            headers = {'X-Api-Key': self.invoice_key}
            
            response = requests.get(
                f'{self.api_url}/api/v1/payments/{checking_id}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'backend': 'lnbits',
                    'status': 'paid' if result['paid'] else 'pending',
                    'paid_at': result.get('time'),
                    'amount_received_sats': abs(result.get('amount', 0)) // 1000,
                    'fee_sats': result.get('fee', 0) // 1000
                }
            else:
                return {
                    'success': False,
                    'error': f'Payment check failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Status check failed: {str(e)}'
            }
    
    def get_balance(self) -> Dict[str, Any]:
        """Get wallet balance"""
        try:
            headers = {'X-Api-Key': self.admin_key}
            
            response = requests.get(
                f'{self.api_url}/api/v1/wallet',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                balance_msat = result.get('balance', 0)
                return {
                    'success': True,
                    'backend': 'lnbits',
                    'balance_sats': balance_msat // 1000,
                    'balance_msat': balance_msat
                }
            else:
                return {
                    'success': False,
                    'error': f'Balance check failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Balance request failed: {str(e)}'
            }
```

### Resources
- **Website**: https://lnbits.com
- **Demo**: https://demo.lnbits.com
- **Documentation**: https://github.com/lnbits/lnbits
- **API Docs**: https://demo.lnbits.com/docs

---

## 2. 🟡 Strike API - Lightning + Fiat Integration

**Perfect for developers wanting to build real-world payment applications**

### Why Strike?
- ✅ **Free sandbox environment** for development
- ✅ **Fiat integration** (USD/EUR) - unique learning opportunity
- ✅ **Professional API** used by real businesses
- ✅ **Excellent documentation** and developer support
- ✅ **Lightning + traditional banking** bridge

### Setup Instructions

1. **Sign up for developer account**: https://developer.strike.me
2. **Get your sandbox API key** from the dashboard
3. **Set environment variables**:
   ```bash
   export STRIKE_API_KEY="your_sandbox_api_key"
   export STRIKE_ENV="sandbox"
   ```

### Implementation Example
```python
import requests
from typing import Dict, Any
from datetime import datetime

class StrikeLightningService:
    """Strike API - Real Lightning with fiat integration"""
    
    def __init__(self):
        self.api_key = os.getenv('STRIKE_API_KEY')
        self.environment = os.getenv('STRIKE_ENV', 'sandbox')
        
        if self.environment == 'sandbox':
            self.api_url = 'https://api.strike.me/v1'
        else:
            self.api_url = 'https://api.strike.me/v1'
        
        if not self.api_key:
            raise ValueError("STRIKE_API_KEY is required. Get it from developer.strike.me")
    
    def create_invoice(self, amount_sats: int, description: str) -> Dict[str, Any]:
        """Create Strike Lightning invoice"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Convert sats to USD (Strike works in fiat)
            btc_amount = amount_sats / 100_000_000
            # In production, get current rate from Strike rates API
            usd_amount = round(btc_amount * 35000, 2)  # Approximate rate
            
            data = {
                'amount': {
                    'amount': str(usd_amount),
                    'currency': 'USD'
                },
                'description': description
            }
            
            response = requests.post(
                f'{self.api_url}/invoices',
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'backend': 'strike',
                    'payment_request': result['lnInvoice'],
                    'invoice_id': result['invoiceId'],
                    'amount_sats': amount_sats,
                    'amount_usd': usd_amount,
                    'expires_at': result.get('created') + result.get('expirationInSec', 3600)
                }
            else:
                return {
                    'success': False,
                    'error': f'Strike API error: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Strike request failed: {str(e)}'
            }
    
    def check_payment_status(self, invoice_id: str) -> Dict[str, Any]:
        """Check Strike invoice status"""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(
                f'{self.api_url}/invoices/{invoice_id}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'backend': 'strike',
                    'status': 'paid' if result.get('state') == 'PAID' else 'pending',
                    'paid_at': result.get('updated'),
                    'amount_received_usd': result.get('amount', {}).get('amount'),
                    'amount_received_sats': int(float(result.get('amount', {}).get('amount', 0)) * 100_000_000 / 35000)
                }
            else:
                return {
                    'success': False,
                    'error': f'Status check failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Status check failed: {str(e)}'
            }
    
    def get_exchange_rates(self) -> Dict[str, Any]:
        """Get current BTC exchange rates (Strike-specific feature)"""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(
                f'{self.api_url}/rates/ticker',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                rates = response.json()
                return {
                    'success': True,
                    'backend': 'strike',
                    'rates': rates
                }
            else:
                return {
                    'success': False,
                    'error': f'Rates request failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Rates request failed: {str(e)}'
            }
```

### Resources
- **Developer Portal**: https://developer.strike.me
- **API Documentation**: https://developer.strike.me/docs
- **Sandbox Environment**: Free for developers
- **Support**: https://help.strike.me

---

## 3. 🔵 OpenNode - Production Grade

**For developers building serious commercial applications**

### Why OpenNode?
- ✅ **Production-grade service** used by real businesses
- ✅ **Comprehensive API** with webhooks, callbacks, and more
- ✅ **Multiple cryptocurrencies** (Bitcoin, Lightning, on-chain)
- ✅ **Developer-friendly** with great documentation
- ✅ **Reasonable pricing** for production use

### Setup Instructions

1. **Create account**: https://dev.opennode.com
2. **Generate API key** from dashboard
3. **Choose environment**:
   ```bash
   # Development
   export OPENNODE_API_KEY="your_dev_api_key"
   export OPENNODE_ENV="dev"
   
   # Production (when ready)
   export OPENNODE_API_KEY="your_live_api_key"
   export OPENNODE_ENV="live"
   ```

### Implementation Example
```python
import requests
from typing import Dict, Any
from datetime import datetime

class OpenNodeLightningService:
    """OpenNode API - Production Lightning payments"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENNODE_API_KEY')
        self.environment = os.getenv('OPENNODE_ENV', 'dev')
        
        if self.environment == 'dev':
            self.api_url = 'https://dev-api.opennode.com/v1'
        else:
            self.api_url = 'https://api.opennode.com/v1'
        
        if not self.api_key:
            raise ValueError("OPENNODE_API_KEY is required. Get it from dev.opennode.com")
    
    def create_invoice(self, amount_sats: int, description: str, **kwargs) -> Dict[str, Any]:
        """Create OpenNode charge (invoice)"""
        try:
            headers = {
                'Authorization': self.api_key,
                'Content-Type': 'application/json'
            }
            
            data = {
                'amount': amount_sats,
                'currency': 'btc',  # Can also be 'usd', 'eur', etc.
                'description': description,
                'customer_email': kwargs.get('customer_email'),
                'callback_url': kwargs.get('webhook_url'),
                'success_url': kwargs.get('success_url'),
                'order_id': kwargs.get('order_id'),
                'ttl': kwargs.get('ttl', 900)  # 15 minutes default
            }
            
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}
            
            response = requests.post(
                f'{self.api_url}/charges',
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()['data']
                return {
                    'success': True,
                    'backend': 'opennode',
                    'payment_request': result['lightning_invoice']['payreq'],
                    'charge_id': result['id'],
                    'amount_sats': amount_sats,
                    'status': result['status'],
                    'expires_at': result['expires_at'],
                    'hosted_checkout_url': result['hosted_checkout_url']  # Optional UI
                }
            else:
                return {
                    'success': False,
                    'error': f'OpenNode API error: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'OpenNode request failed: {str(e)}'
            }
    
    def check_payment_status(self, charge_id: str) -> Dict[str, Any]:
        """Check OpenNode charge status"""
        try:
            headers = {'Authorization': self.api_key}
            
            response = requests.get(
                f'{self.api_url}/charge/{charge_id}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()['data']
                return {
                    'success': True,
                    'backend': 'opennode',
                    'status': result['status'],  # 'unpaid', 'paid', 'expired', etc.
                    'paid_at': result.get('paid_at'),
                    'amount_received_sats': result.get('amount'),
                    'fee_sats': result.get('fee'),
                    'notes': result.get('notes')
                }
            else:
                return {
                    'success': False,
                    'error': f'Status check failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Status check failed: {str(e)}'
            }
    
    def get_exchange_rates(self) -> Dict[str, Any]:
        """Get current exchange rates"""
        try:
            response = requests.get(
                f'{self.api_url}/rates',
                timeout=10
            )
            
            if response.status_code == 200:
                rates = response.json()['data']
                return {
                    'success': True,
                    'backend': 'opennode',
                    'rates': rates
                }
            else:
                return {
                    'success': False,
                    'error': f'Rates request failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Rates request failed: {str(e)}'
            }
    
    def setup_webhook(self, webhook_url: str, events: list = None) -> Dict[str, Any]:
        """Setup webhook for payment notifications"""
        try:
            headers = {
                'Authorization': self.api_key,
                'Content-Type': 'application/json'
            }
            
            data = {
                'url': webhook_url,
                'events': events or ['charge.completed', 'charge.failed']
            }
            
            response = requests.post(
                f'{self.api_url}/webhooks',
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()['data']
                return {
                    'success': True,
                    'backend': 'opennode',
                    'webhook_id': result['id'],
                    'webhook_url': result['url'],
                    'events': result['events']
                }
            else:
                return {
                    'success': False,
                    'error': f'Webhook setup failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Webhook setup failed: {str(e)}'
            }
```

### Resources
- **Developer Portal**: https://dev.opennode.com
- **API Documentation**: https://developers.opennode.com
- **Webhooks Guide**: https://developers.opennode.com/webhooks
- **Status Page**: https://status.opennode.com

---

## 4. ⚡ Voltage Cloud - Your Own Lightning Node

**For advanced developers who want complete control**

### Why Voltage?
- ✅ **Real Lightning node** in the cloud
- ✅ **Full LND API access** - learn Lightning deeply
- ✅ **Managed infrastructure** - no server maintenance
- ✅ **Professional setup** used by businesses
- ✅ **Educational pricing** available

### Setup Instructions

1. **Sign up**: https://voltage.cloud
2. **Create a Lightning node** (choose testnet for learning)
3. **Download connection details**:
   - REST API endpoint
   - Admin macaroon
   - TLS certificate

4. **Set environment variables**:
   ```bash
   export VOLTAGE_NODE_URL="https://your-node.m.voltageapp.io"
   export VOLTAGE_MACAROON="your_admin_macaroon_hex"
   export VOLTAGE_TLS_CERT="path/to/tls.cert"
   ```

### Implementation Example
```python
import requests
import base64
from typing import Dict, Any

class VoltageLightningService:
    """Voltage Cloud - Real Lightning Node API"""
    
    def __init__(self):
        self.node_url = os.getenv('VOLTAGE_NODE_URL')
        self.macaroon = os.getenv('VOLTAGE_MACAROON')
        self.tls_cert = os.getenv('VOLTAGE_TLS_CERT')
        
        if not all([self.node_url, self.macaroon]):
            raise ValueError("Voltage node URL and macaroon are required")
    
    def _get_headers(self):
        return {
            'Grpc-Metadata-macaroon': self.macaroon,
            'Content-Type': 'application/json'
        }
    
    def get_node_info(self) -> Dict[str, Any]:
        """Get Lightning node information"""
        try:
            response = requests.get(
                f'{self.node_url}/v1/getinfo',
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'backend': 'voltage',
                    'node_info': {
                        'alias': result.get('alias'),
                        'identity_pubkey': result.get('identity_pubkey'),
                        'num_active_channels': result.get('num_active_channels'),
                        'num_peers': result.get('num_peers'),
                        'block_height': result.get('block_height'),
                        'synced_to_chain': result.get('synced_to_chain'),
                        'version': result.get('version'),
                        'chains': result.get('chains', [])
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Node info request failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Node info request failed: {str(e)}'
            }
    
    def create_invoice(self, amount_sats: int, description: str, expiry_seconds: int = 900) -> Dict[str, Any]:
        """Create Lightning invoice via your Voltage node"""
        try:
            data = {
                'value': str(amount_sats),
                'memo': description,
                'expiry': str(expiry_seconds)
            }
            
            response = requests.post(
                f'{self.node_url}/v1/invoices',
                json=data,
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'backend': 'voltage',
                    'payment_request': result['payment_request'],
                    'r_hash': result['r_hash'],
                    'payment_addr': result['payment_addr'],
                    'amount_sats': amount_sats,
                    'add_index': result['add_index']
                }
            else:
                return {
                    'success': False,
                    'error': f'Invoice creation failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Invoice creation failed: {str(e)}'
            }
    
    def check_invoice(self, r_hash: str) -> Dict[str, Any]:
        """Check invoice status"""
        try:
            # Convert r_hash to base64url if needed
            r_hash_b64 = base64.urlsafe_b64encode(bytes.fromhex(r_hash)).decode().rstrip('=')
            
            response = requests.get(
                f'{self.node_url}/v1/invoice/{r_hash_b64}',
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'backend': 'voltage',
                    'status': 'paid' if result.get('settled') else 'pending',
                    'amount_paid_sats': int(result.get('amt_paid_sat', 0)),
                    'settle_date': result.get('settle_date'),
                    'payment_request': result.get('payment_request')
                }
            else:
                return {
                    'success': False,
                    'error': f'Invoice lookup failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Invoice lookup failed: {str(e)}'
            }
    
    def get_balance(self) -> Dict[str, Any]:
        """Get Lightning wallet balance"""
        try:
            response = requests.get(
                f'{self.node_url}/v1/balance/channels',
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'backend': 'voltage',
                    'balance': {
                        'total_balance_sats': int(result.get('balance', 0)),
                        'pending_balance_sats': int(result.get('pending_open_balance', 0)),
                        'local_balance': result.get('local_balance', {}),
                        'remote_balance': result.get('remote_balance', {})
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Balance request failed: {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Balance request failed: {str(e)}'
            }
```

### Resources
- **Voltage Cloud**: https://voltage.cloud
- **Documentation**: https://docs.voltage.cloud
- **LND API Reference**: https://lightning.engineering/api-docs
- **Educational Pricing**: Contact support for educational discounts

---

## 🔧 Updated Lightning Factory

Here's how to integrate all these real APIs into your Lightning Digital Marketplace:

```python
# services/lightning/lightning_factory.py

class LightningFactory:
    """Updated factory with real production APIs"""
    
    @staticmethod
    def create_service(backend_type="lnbits"):
        """Create Lightning service with real APIs"""
        
        if backend_type == "lnbits":
            from .lnbits_backend import LNbitsLightningService
            return LNbitsLightningService()
            
        elif backend_type == "strike":
            from .strike_backend import StrikeLightningService
            return StrikeLightningService()
            
        elif backend_type == "opennode":
            from .opennode_backend import OpenNodeLightningService
            return OpenNodeLightningService()
            
        elif backend_type == "voltage":
            from .voltage_backend import VoltageLightningService
            return VoltageLightningService()
            
        elif backend_type == "polar":
            from .polar_backend import PolarService
            return PolarService()  # Local development
            
        else:
            # Fallback to demo/mock services
            print(f"⚠️  {backend_type} backend not found, using demo mode")
            from .breeze_backend import BreezeLightningService
            return BreezeLightningService()
    
    @staticmethod
    def get_production_backends():
        """Get information about production-ready APIs"""
        return {
            'lnbits': {
                'name': 'LNbits',
                'description': 'Free Lightning wallet API - perfect for learning',
                'setup_url': 'https://demo.lnbits.com',
                'difficulty': 'Beginner',
                'cost': 'Free',
                'features': ['Real Lightning', 'No signup for demo', 'Open source']
            },
            'strike': {
                'name': 'Strike',
                'description': 'Lightning payments with fiat integration',
                'setup_url': 'https://developer.strike.me',
                'difficulty': 'Intermediate', 
                'cost': 'Free sandbox',
                'features': ['Fiat bridge', 'Professional API', 'Great docs']
            },
            'opennode': {
                'name': 'OpenNode',
                'description': 'Production-grade Lightning payment processor',
                'setup_url': 'https://dev.opennode.com',
                'difficulty': 'Advanced',
                'cost': 'Low fees',
                'features': ['Production ready', 'Webhooks', 'Multiple currencies']
            },
            'voltage': {
                'name': 'Voltage Cloud',
                'description': 'Your own Lightning node in the cloud',
                'setup_url': 'https://voltage.cloud',
                'difficulty': 'Expert',
                'cost': 'Paid service',
                'features': ['Full node control', 'Real Lightning', 'LND API']
            },
            'polar': {
                'name': 'Polar',
                'description': 'Local Lightning development environment',
                'setup_url': 'https://lightningpolar.com',
                'difficulty': 'Intermediate',
                'cost': 'Free',
                'features': ['Local development', 'Docker based', 'Multiple nodes']
            }
        }
    
    @staticmethod
    def validate_backend_config(backend_type: str) -> Dict[str, Any]:
        """Validate backend configuration"""
        required_env_vars = {
            'lnbits': ['LNBITS_ADMIN_KEY', 'LNBITS_INVOICE_KEY'],
            'strike': ['STRIKE_API_KEY'],
            'opennode': ['OPENNODE_API_KEY'],
            'voltage': ['VOLTAGE_NODE_URL', 'VOLTAGE_MACAROON'],
            'polar': ['POLAR_API_URL']
        }
        
        if backend_type not in required_env_vars:
            return {
                'valid': False,
                'error': f'Unknown backend type: {backend_type}'
            }
        
        missing_vars = []
        for var in required_env_vars[backend_type]:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            return {
                'valid': False,
                'error': f'Missing environment variables: {", ".join(missing_vars)}',
                'missing_vars': missing_vars
            }
        
        return {
            'valid': True,
            'message': f'{backend_type} backend properly configured'
        }
```

---

## 🚀 Quick Start Checklist

### For Hackathons (5 minutes setup):
- [ ] Choose **LNbits** for fastest setup
- [ ] Go to https://demo.lnbits.com
- [ ] Create wallet and copy API keys
- [ ] Set environment variables
- [ ] Test with your application

### For Learning Projects:
- [ ] Start with **LNbits** demo
- [ ] Try **Strike** for fiat integration experience
- [ ] Experiment with **OpenNode** for production features
- [ ] Consider **Voltage** for advanced Lightning learning

### For Production Applications:
- [ ] Evaluate **OpenNode** for commercial use
- [ ] Consider **Voltage** for full control
- [ ] Set up proper error handling and logging
- [ ] Implement webhook notifications
- [ ] Add monitoring and analytics

---

## 🛡️ Security Best Practices

### API Key Management
```bash
# Use environment variables, never hardcode
export LIGHTNING_API_KEY="your_key_here"

# Use .env files for local development
echo "LNBITS_API_KEY=your_key" > .env

# Add .env to .gitignore
echo ".env" >> .gitignore
```

### Error Handling
```python
def create_invoice_safely(service, amount, description):
    """Always wrap API calls in try/catch"""
    try:
        result = service.create_invoice(amount, description)
        if result.get('success'):
            return result
        else:
            logger.error(f"Invoice creation failed: {result.get('error')}")
            return None
    except Exception as e:
        logger.error(f"API call exception: {str(e)}")
        return None
```

### Rate Limiting
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    """Simple rate limiting decorator"""
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 60.0 / calls_per_minute - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator
```

---

## 🎓 Learning Path Recommendations

### Week 1-2: Get Started
- Set up **LNbits** demo instance
- Create your first invoice
- Test payment flow
- Build basic payment UI

### Week 3-4: Add Features  
- Implement payment status checking
- Add QR code generation
- Build order management
- Add customer notifications

### Week 5-6: Go Professional
- Try **Strike** or **OpenNode**
- Add webhook handling
- Implement proper error handling
- Add logging and monitoring

### Week 7+: Advanced Topics
- Set up **Voltage** node
- Learn Lightning Network routing
- Implement multi-backend support
- Build advanced analytics

---

## 📚 Additional Resources

### Lightning Network Learning
- **Lightning Network Specification**: https://github.com/lightning/bolts
- **Lightning Labs Guides**: https://docs.lightning.engineering
- **Lightning Network Paper**: https://lightning.network/lightning-network-paper.pdf

### Development Tools
- **Lightning Decoder**: https://lndecode.com (decode payment requests)
- **Lightning Explorer**: https://1ml.com (explore Lightning Network)
- **Testnet Faucets**: Get testnet Bitcoin for testing

### Community
- **Lightning Developer Slack**: https://lightningcommunity.slack.com
- **Bitcoin Stack Exchange**: https://bitcoin.stackexchange.com
- **Lightning Network Developers**: https://github.com/lightning

---

## ⚡ Ready to Build!

You now have access to **real Lightning APIs** that you can use in your hackathon projects, portfolio applications, and learning experiments. Each API offers different features and learning opportunities:

- **Start with LNbits** for immediate results
- **Try Strike** to learn fiat integration  
- **Use OpenNode** for production features
- **Explore Voltage** for advanced Lightning development

**Happy Lightning Building!** 🚀

---

*This guide is maintained by the Lightning Digital Marketplace project. Contributions and updates are welcome via GitHub issues and pull requests.*