"""
Lightning Digital Marketplace - Main Flask Application
Stage 1: Foundation Setup

A learning-focused Lightning commerce platform built with Flask.
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from services.polar_service import PolarService
from services.payment_service import PaymentService
from models.product import ProductService
from config import config
import os

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Setup CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# Initialize services
polar_service = PolarService()
payment_service = PaymentService()
product_service = ProductService()

# Routes
@app.route('/')
def index():
    """Home page - Stage 1 foundation"""
    return render_template('index.html', stage='Stage 1: Foundation')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'stage': 'Stage 1: Foundation',
        'version': '1.0.0',
        'lightning_backend': app.config['LIGHTNING_BACKEND']
    })

@app.route('/api/node-info')
def get_node_info():
    """Get Lightning node information"""
    node_name = request.args.get('node', 'alice')
    node_info = polar_service.get_node_info(node_name)
    return jsonify(node_info)

@app.route('/api/all-nodes')
def get_all_nodes():
    """Get information about all Lightning nodes"""
    all_nodes = polar_service.get_all_nodes_info()
    return jsonify(all_nodes)

@app.route('/api/connection-status')
def connection_status():
    """Check Polar Lightning connection status"""
    status = polar_service.check_connection_status()
    return jsonify(status)

@app.route('/api/stage-info')
def stage_info():
    """Get current stage information and next steps"""
    return jsonify({
        'current_stage': 'Stage 2: Commerce Core',
        'description': 'Product catalog with Lightning payment integration',
        'completed_features': [
            '✅ Flask application setup and routing',
            '✅ Environment variable management', 
            '✅ Polar Lightning node connection',
            '✅ Basic Lightning API integration',
            '✅ Clean project structure',
            '✅ Product catalog with sample digital products',
            '✅ Shopping cart functionality',
            '✅ Lightning invoice generation', 
            '✅ QR code display for payments',
            '✅ Basic payment verification'
        ],
        'next_stage': 'Stage 3: Real-Time Features',
        'next_features': [
            '🔄 WebSocket integration for real-time updates',
            '🔄 Live payment status notifications',
            '🔄 Real-time order tracking',
            '🔄 Interactive payment flow'
        ],
        'learning_objectives': [
            'E-commerce product management',
            'Lightning Network payment flow',
            'QR code generation and handling',
            'Order lifecycle management',
            'Payment status monitoring'
        ]
    })

# Stage 2: Commerce Core Routes

@app.route('/store')
def store():
    """Product store page"""
    return render_template('store.html', stage='Stage 2: Commerce Core')

@app.route('/checkout/<int:product_id>')
def checkout(product_id):
    """Checkout page for specific product"""
    return render_template('checkout.html', stage='Stage 2: Commerce Core')

@app.route('/api/products')
def get_products():
    """Get all products"""
    try:
        products = product_service.get_all_products()
        return jsonify({
            'success': True,
            'products': [p.to_dict() for p in products],
            'count': len(products)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """Get specific product"""
    try:
        product = product_service.get_product_by_id(product_id)
        if product:
            return jsonify({
                'success': True,
                'product': product.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products/search')
def search_products():
    """Search products"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        
        if query:
            products = product_service.search_products(query)
        elif category:
            products = product_service.get_products_by_category(category)
        else:
            products = product_service.get_all_products()
        
        return jsonify({
            'success': True,
            'products': [p.to_dict() for p in products],
            'count': len(products),
            'query': query,
            'category': category
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/categories')
def get_categories():
    """Get all product categories"""
    try:
        categories = product_service.get_categories()
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    """Create Lightning payment request"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        customer_email = data.get('customer_email')
        
        if not product_id:
            return jsonify({
                'success': False,
                'error': 'Product ID is required'
            }), 400
        
        # Get product details
        product = product_service.get_product_by_id(product_id)
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Create payment request
        payment_result = payment_service.create_payment_request(
            product_id=product.id,
            product_name=product.name,
            price_sats=product.price_sats,
            customer_email=customer_email
        )
        
        return jsonify(payment_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/payment-status/<order_id>')
def check_payment_status(order_id):
    """Check payment status"""
    try:
        result = payment_service.check_payment_status(order_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/deliver-product/<order_id>')
def deliver_product(order_id):
    """Deliver digital product"""
    try:
        result = payment_service.deliver_product(order_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cancel-payment/<order_id>', methods=['POST'])
def cancel_payment(order_id):
    """Cancel payment request"""
    try:
        result = payment_service.cancel_payment(order_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<order_id>/<int:product_id>')
def download_product(order_id, product_id):
    """Download digital product (demo endpoint)"""
    try:
        # Verify order and product
        order_result = payment_service.get_order_details(order_id)
        if not order_result['success']:
            return jsonify({
                'success': False,
                'error': 'Invalid order'
            }), 404
        
        order = order_result['order']
        if order['status'] not in ['paid', 'delivered']:
            return jsonify({
                'success': False,
                'error': 'Order not paid'
            }), 403
        
        # For demo, return success message
        return jsonify({
            'success': True,
            'message': 'In a real implementation, this would serve the digital file',
            'order_id': order_id,
            'product_id': product_id,
            'demo_note': 'This is a demonstration download endpoint'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found', 'stage': 'Stage 1'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error', 'stage': 'Stage 1'}), 500

if __name__ == '__main__':
    print("🚀 Lightning Digital Marketplace - Stage 1: Foundation")
    print("=" * 50)
    print("📍 Starting Flask development server...")
    print(f"⚡ Lightning Backend: {app.config['LIGHTNING_BACKEND']}")
    print(f"🌐 Polar Network: {app.config['POLAR_NETWORK']}")
    print("🔗 Available endpoints:")
    print("   • http://localhost:5000 - Home page")
    print("   • http://localhost:5000/api/health - Health check")
    print("   • http://localhost:5000/api/node-info - Lightning node info")
    print("   • http://localhost:5000/api/connection-status - Polar status")
    print("   • http://localhost:5000/api/stage-info - Current stage info")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )

