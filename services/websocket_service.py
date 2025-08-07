"""
Lightning Digital Marketplace - WebSocket Service
Stage 3: Real-Time Features

This service handles real-time communication for payment updates and notifications.
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
from typing import Dict, Any, Optional
import threading
import time

class WebSocketService:
    """Service for managing WebSocket connections and real-time updates"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.active_sessions = {}  # Track active payment sessions
        self.room_users = {}  # Track users in rooms
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            print(f"Client connected: {id}")
            emit('connection_status', {
                'status': 'connected',
                'message': 'Connected to Lightning Marketplace',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            print(f"Client disconnected")
            # Clean up any rooms this client was in
            self._cleanup_client_sessions()
        
        @self.socketio.on('join_payment_room')
        def handle_join_payment_room(data):
            """Join a payment monitoring room"""
            order_id = data.get('order_id')
            if order_id:
                join_room(f"payment_{order_id}")
                self.room_users[f"payment_{order_id}"] = self.room_users.get(f"payment_{order_id}", 0) + 1
                
                emit('room_joined', {
                    'room': f"payment_{order_id}",
                    'order_id': order_id,
                    'message': 'Monitoring payment status...',
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"Client joined payment room: {order_id}")
        
        @self.socketio.on('leave_payment_room')
        def handle_leave_payment_room(data):
            """Leave a payment monitoring room"""
            order_id = data.get('order_id')
            if order_id:
                leave_room(f"payment_{order_id}")
                if f"payment_{order_id}" in self.room_users:
                    self.room_users[f"payment_{order_id}"] = max(0, self.room_users[f"payment_{order_id}"] - 1)
                
                emit('room_left', {
                    'room': f"payment_{order_id}",
                    'order_id': order_id,
                    'message': 'Stopped monitoring payment',
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"Client left payment room: {order_id}")
        
        @self.socketio.on('ping')
        def handle_ping():
            """Handle ping for connection testing"""
            emit('pong', {
                'timestamp': datetime.now().isoformat(),
                'status': 'alive'
            })
    
    def _cleanup_client_sessions(self):
        """Clean up sessions when client disconnects"""
        # In a real implementation, you'd track which rooms this specific client was in
        pass
    
    def broadcast_payment_update(self, order_id: str, update_data: Dict[str, Any]):
        """Broadcast payment status update to all clients monitoring this order"""
        room = f"payment_{order_id}"
        
        # Add timestamp to update
        update_data['timestamp'] = datetime.now().isoformat()
        update_data['order_id'] = order_id
        
        # Emit to all clients in the payment room
        self.socketio.emit('payment_update', update_data, room=room)
        
        print(f"Broadcasted payment update for order {order_id}: {update_data.get('status', 'unknown')}")
    
    def notify_payment_confirmation(self, order_id: str, payment_data: Dict[str, Any]):
        """Send payment confirmation notification"""
        notification = {
            'type': 'payment_confirmed',
            'order_id': order_id,
            'message': 'Payment confirmed! Preparing your download...',
            'payment_hash': payment_data.get('payment_hash'),
            'amount_sats': payment_data.get('amount_sats'),
            'timestamp': datetime.now().isoformat()
        }
        
        self.broadcast_payment_update(order_id, notification)
    
    def notify_payment_expired(self, order_id: str):
        """Send payment expiration notification"""
        notification = {
            'type': 'payment_expired',
            'order_id': order_id,
            'message': 'Payment window has expired',
            'status': 'expired',
            'timestamp': datetime.now().isoformat()
        }
        
        self.broadcast_payment_update(order_id, notification)
    
    def notify_payment_pending(self, order_id: str, time_remaining: int):
        """Send payment pending notification with countdown"""
        notification = {
            'type': 'payment_pending',
            'order_id': order_id,
            'message': f'Waiting for payment... {time_remaining}s remaining',
            'status': 'pending',
            'time_remaining': time_remaining,
            'timestamp': datetime.now().isoformat()
        }
        
        self.broadcast_payment_update(order_id, notification)
    
    def notify_product_delivery(self, order_id: str, delivery_data: Dict[str, Any]):
        """Send product delivery notification"""
        notification = {
            'type': 'product_delivered',
            'order_id': order_id,
            'message': f"Product '{delivery_data.get('product_name')}' is ready for download!",
            'status': 'delivered',
            'download_link': delivery_data.get('download_link'),
            'product_name': delivery_data.get('product_name'),
            'timestamp': datetime.now().isoformat()
        }
        
        self.broadcast_payment_update(order_id, notification)
    
    def send_general_notification(self, message: str, notification_type: str = 'info'):
        """Send general notification to all connected clients"""
        notification = {
            'type': 'general_notification',
            'notification_type': notification_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('general_notification', notification, broadcast=True)
        print(f"Sent general notification: {message}")
    
    def get_room_stats(self) -> Dict[str, Any]:
        """Get statistics about active rooms and connections"""
        return {
            'active_rooms': len(self.room_users),
            'room_details': self.room_users,
            'total_connections': sum(self.room_users.values()),
            'timestamp': datetime.now().isoformat()
        }
    
    def start_payment_monitoring(self, order_id: str, payment_service):
        """Start monitoring a payment in a background thread"""
        def monitor_payment():
            """Background task to monitor payment status"""
            monitoring_duration = 900  # 15 minutes
            check_interval = 5  # Check every 5 seconds
            elapsed_time = 0
            
            while elapsed_time < monitoring_duration:
                try:
                    # Check payment status
                    result = payment_service.check_payment_status(order_id)
                    
                    if result.get('success'):
                        status = result.get('status')
                        
                        if status == 'paid':
                            self.notify_payment_confirmation(order_id, result)
                            # Attempt delivery
                            delivery_result = payment_service.deliver_product(order_id)
                            if delivery_result.get('success'):
                                self.notify_product_delivery(order_id, delivery_result)
                            break
                        
                        elif status == 'expired':
                            self.notify_payment_expired(order_id)
                            break
                        
                        elif status == 'payment_pending':
                            time_remaining = result.get('time_remaining', 0)
                            if time_remaining > 0:
                                self.notify_payment_pending(order_id, time_remaining)
                            else:
                                self.notify_payment_expired(order_id)
                                break
                    
                    time.sleep(check_interval)
                    elapsed_time += check_interval
                    
                except Exception as e:
                    print(f"Error monitoring payment {order_id}: {e}")
                    time.sleep(check_interval)
                    elapsed_time += check_interval
            
            # Clean up monitoring session
            if order_id in self.active_sessions:
                del self.active_sessions[order_id]
        
        # Start monitoring thread if not already active
        if order_id not in self.active_sessions:
            self.active_sessions[order_id] = True
            thread = threading.Thread(target=monitor_payment)
            thread.daemon = True
            thread.start()
            print(f"Started payment monitoring for order: {order_id}")
    
    def stop_payment_monitoring(self, order_id: str):
        """Stop monitoring a specific payment"""
        if order_id in self.active_sessions:
            del self.active_sessions[order_id]
            print(f"Stopped payment monitoring for order: {order_id}")
    
    def broadcast_lightning_network_status(self, status_data: Dict[str, Any]):
        """Broadcast Lightning Network connection status to all clients"""
        notification = {
            'type': 'lightning_status',
            'status': status_data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('lightning_status_update', notification, broadcast=True)
        print(f"Broadcasted Lightning status: {status_data.get('polar_running', 'unknown')}")

class NotificationManager:
    """Manager for different types of notifications"""
    
    def __init__(self, websocket_service: WebSocketService):
        self.ws_service = websocket_service
    
    def payment_created(self, order_id: str, payment_data: Dict[str, Any]):
        """Notification when payment is created"""
        self.ws_service.broadcast_payment_update(order_id, {
            'type': 'payment_created',
            'status': 'payment_pending',
            'message': 'Payment request created. Please scan QR code to pay.',
            'amount_sats': payment_data.get('amount_sats'),
            'expires_at': payment_data.get('expires_at')
        })
    
    def invoice_scanned(self, order_id: str):
        """Notification when QR code is scanned (simulated)"""
        self.ws_service.broadcast_payment_update(order_id, {
            'type': 'invoice_scanned',
            'status': 'payment_pending',
            'message': 'Invoice scanned! Waiting for payment confirmation...'
        })
    
    def payment_routing(self, order_id: str, hop_count: int):
        """Notification about payment routing through Lightning Network"""
        self.ws_service.broadcast_payment_update(order_id, {
            'type': 'payment_routing',
            'status': 'payment_pending',
            'message': f'Payment routing through Lightning Network... (hop {hop_count})',
            'hop_count': hop_count
        })
    
    def system_maintenance(self, message: str):
        """System maintenance notification"""
        self.ws_service.send_general_notification(
            message=message,
            notification_type='warning'
        )
    
    def new_product_added(self, product_name: str):
        """Notification when new product is added"""
        self.ws_service.send_general_notification(
            message=f"New product available: {product_name}",
            notification_type='info'
        )
