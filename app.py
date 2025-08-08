"""
Lightning Digital Marketplace - Main Flask Application
Stage 1: Foundation Setup

A learning-focused Lightning commerce platform built with Flask.
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from services.polar_service import PolarService
from services.payment_service import PaymentService
from services.websocket_service import WebSocketService, NotificationManager
from services.lightning.lightning_factory import LightningFactory
from services.analytics.analytics_service import AnalyticsService
from models.product import ProductService
from models.subscription import SubscriptionService
from config import config
import os

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Setup CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ORIGINS'])

# Initialize services
polar_service = PolarService()
lightning_service = LightningFactory.create_service()
payment_service = PaymentService()
product_service = ProductService()
subscription_service = SubscriptionService()
websocket_service = WebSocketService(socketio)
notification_manager = NotificationManager(websocket_service)
analytics_service = AnalyticsService(payment_service.order_service, subscription_service, product_service)

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
        'current_stage': 'Stage 5: Advanced Business Features',
        'description': 'Complete business platform with analytics and subscriptions',
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
            '✅ Basic payment verification',
            '✅ WebSocket integration for real-time updates',
            '✅ Live payment status notifications',
            '✅ Real-time order tracking',
            '✅ Interactive payment flow',
            '✅ Multiple Lightning backend support (Polar/Phoenix/Breeze/LND/CLN)',
            '✅ Environment-based configuration',
            '✅ Production deployment setup',
            '✅ Real Lightning network transactions',
            '✅ Sales analytics dashboard',
            '✅ Subscription payment models',
            '✅ Customer management system',
            '✅ Business intelligence metrics'
        ],
        'next_stage': 'Complete!',
        'next_features': [
            '🎉 Ready for production deployment',
            '🎉 Full-featured Lightning commerce platform',
            '🎉 Scalable business model',
            '🎉 Advanced analytics and insights'
        ],
        'learning_objectives': [
            'Business analytics and metrics',
            'Subscription model implementation',
            'Customer lifecycle management',
            'Revenue optimization strategies',
            'Advanced Lightning commerce patterns'
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
        
        # Start real-time monitoring if payment was created successfully
        if payment_result.get('success') and payment_result.get('order_id'):
            order_id = payment_result['order_id']
            
            # Notify about payment creation
            notification_manager.payment_created(order_id, payment_result)
            
            # Start background monitoring
            websocket_service.start_payment_monitoring(order_id, payment_service)
        
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
        
        # Stop real-time monitoring
        websocket_service.stop_payment_monitoring(order_id)
        
        # Notify about cancellation
        if result.get('success'):
            websocket_service.broadcast_payment_update(order_id, {
                'type': 'payment_cancelled',
                'status': 'cancelled',
                'message': 'Payment was cancelled by user'
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Stage 4: Production Ready Routes

@app.route('/api/lightning/backends')
def get_lightning_backends():
    """Get available Lightning backends"""
    try:
        backends = LightningFactory.get_available_backends()
        current_backend = app.config.get('LIGHTNING_BACKEND', 'polar')
        
        return jsonify({
            'success': True,
            'current_backend': current_backend,
            'available_backends': backends
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lightning/validate/<backend_type>')
def validate_lightning_backend(backend_type):
    """Validate Lightning backend configuration"""
    try:
        validation = LightningFactory.validate_backend_config(backend_type)
        return jsonify({
            'success': True,
            'validation': validation
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lightning/test/<backend_type>')
def test_lightning_backend(backend_type):
    """Test Lightning backend connection"""
    try:
        test_result = LightningFactory.test_backend_connection(backend_type)
        return jsonify({
            'success': True,
            'test_result': test_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lightning/node-info')
def get_lightning_node_info():
    """Get current Lightning backend node info"""
    try:
        node_info = lightning_service.get_node_info()
        return jsonify(node_info)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lightning/balance')
def get_lightning_balance():
    """Get Lightning wallet balance"""
    try:
        balance = lightning_service.get_balance()
        return jsonify(balance)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Stage 3: Real-Time Features Routes

@app.route('/api/websocket/stats')
def websocket_stats():
    """Get WebSocket connection statistics"""
    try:
        stats = websocket_service.get_room_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/notify/test', methods=['POST'])
def test_notification():
    """Test endpoint for sending notifications"""
    try:
        data = request.get_json()
        message = data.get('message', 'Test notification')
        notification_type = data.get('type', 'info')
        
        websocket_service.send_general_notification(message, notification_type)
        
        return jsonify({
            'success': True,
            'message': 'Notification sent successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Stage 5: Advanced Business Features Routes

@app.route('/dashboard')
def dashboard():
    """Analytics dashboard page"""
    return render_template('dashboard/analytics.html', stage='Stage 5: Advanced Business Features')

@app.route('/subscriptions')
def subscriptions_page():
    """Subscriptions management page"""
    return render_template('dashboard/subscriptions.html', stage='Stage 5: Advanced Business Features')

@app.route('/api/analytics/dashboard')
def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    try:
        dashboard_data = analytics_service.get_comprehensive_dashboard()
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/sales')
def get_sales_analytics():
    """Get sales analytics"""
    try:
        days = int(request.args.get('days', 30))
        sales_data = analytics_service.get_sales_analytics(days)
        return jsonify({
            'success': True,
            'analytics': sales_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/export')
def export_analytics():
    """Export analytics data"""
    try:
        format_type = request.args.get('format', 'json')
        exported_data = analytics_service.export_analytics(format_type)
        
        if format_type == 'csv':
            from flask import Response
            return Response(
                exported_data,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=analytics.csv'}
            )
        else:
            return jsonify({
                'success': True,
                'data': exported_data
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/subscriptions/plans')
def get_subscription_plans():
    """Get available subscription plans"""
    try:
        plans = SubscriptionService.get_available_plans()
        return jsonify({
            'success': True,
            'plans': plans
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/subscriptions', methods=['POST'])
def create_subscription():
    """Create a new subscription"""
    try:
        data = request.get_json()
        customer_email = data.get('customer_email')
        plan_name = data.get('plan')
        
        if not customer_email or not plan_name:
            return jsonify({
                'success': False,
                'error': 'Customer email and plan are required'
            }), 400
        
        from models.subscription import SubscriptionPlan
        plan = SubscriptionPlan(plan_name)
        
        subscription = subscription_service.create_subscription(customer_email, plan)
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/subscriptions/<subscription_id>')
def get_subscription(subscription_id):
    """Get subscription details"""
    try:
        subscription = subscription_service.get_subscription(subscription_id)
        if subscription:
            return jsonify({
                'success': True,
                'subscription': subscription.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Subscription not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/subscriptions/analytics')
def get_subscription_analytics():
    """Get subscription analytics"""
    try:
        analytics = subscription_service.get_subscription_analytics()
        return jsonify({
            'success': True,
            'analytics': analytics
        })
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
    print("🚀 Lightning Digital Marketplace - Stage 5: Advanced Business Features")
    print("🎉 COMPLETE LIGHTNING COMMERCE PLATFORM!")
    print("=" * 80)
    print("📍 Starting production-ready Lightning commerce server...")
    print(f"⚡ Lightning Backend: {app.config.get('LIGHTNING_BACKEND', 'polar')}")
    print(f"🌐 Network: {app.config.get('LIGHTNING_NETWORK', 'regtest')}")
    print("🔗 Main application:")
    print("   • http://localhost:5000 - Home page")
    print("   • http://localhost:5000/store - Digital marketplace")
    print("   • http://localhost:5000/dashboard - Business analytics")
    print("   • http://localhost:5000/subscriptions - Subscription management")
    print("🎯 Complete features:")
    print("   • Full Lightning e-commerce platform")
    print("   • Real-time payments and notifications")
    print("   • Multiple Lightning backend support")
    print("   • Advanced business analytics")
    print("   • Subscription payment models")
    print("   • Production deployment ready")
    print("🎊 Developers now have a COMPLETE Lightning application!")
    print("=" * 80)
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )

