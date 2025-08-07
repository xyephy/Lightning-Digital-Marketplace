"""
Lightning Digital Marketplace - Main Flask Application
Stage 1: Foundation Setup

A learning-focused Lightning commerce platform built with Flask.
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from services.polar_service import PolarService
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
        'current_stage': 'Stage 1: Foundation',
        'description': 'Basic Flask app connected to Polar Lightning',
        'completed_features': [
            '✅ Flask application setup and routing',
            '✅ Environment variable management', 
            '✅ Polar Lightning node connection',
            '✅ Basic Lightning API integration',
            '✅ Clean project structure'
        ],
        'next_stage': 'Stage 2: Commerce Core',
        'next_features': [
            '🔄 Product catalog with sample digital products',
            '🔄 Shopping cart functionality',
            '🔄 Lightning invoice generation', 
            '🔄 QR code display for payments',
            '🔄 Basic payment verification'
        ],
        'learning_objectives': [
            'Understanding Flask web framework basics',
            'Lightning Network node connectivity',
            'API design and RESTful endpoints',
            'Environment-based configuration',
            'Clean code architecture'
        ]
    })

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

