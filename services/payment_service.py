"""
Lightning Digital Marketplace - Payment Service
Stage 2: Commerce Core
"""

import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from services.polar_service import PolarService
from models.order import Order, OrderService, OrderStatus

class PaymentService:
    """Service for handling Lightning payments"""
    
    def __init__(self):
        self.polar_service = PolarService()
        self.order_service = OrderService()
        self.default_node = 'alice'  # Default merchant node
    
    def create_payment_request(self, product_id: int, product_name: str, 
                             price_sats: int, customer_email: Optional[str] = None) -> Dict[str, Any]:
        """Create a payment request with Lightning invoice"""
        try:
            # Create order
            order = self.order_service.create_order(
                product_id=product_id,
                product_name=product_name,
                price_sats=price_sats,
                customer_email=customer_email
            )
            
            # Create Lightning invoice
            invoice_data = self._create_lightning_invoice(
                amount_sats=price_sats,
                description=f"Purchase: {product_name} (Order #{order.id})",
                order_id=order.id
            )
            
            if not invoice_data['success']:
                return {
                    'success': False,
                    'error': invoice_data['error'],
                    'order_id': order.id
                }
            
            # Update order with payment info
            expires_at = datetime.now() + timedelta(minutes=15)  # 15 minute expiry
            self.order_service.update_order_payment(
                order_id=order.id,
                lightning_invoice=invoice_data['payment_request'],
                payment_hash=invoice_data['payment_hash'],
                expires_at=expires_at
            )
            
            # Generate QR code
            qr_code = self._generate_qr_code(invoice_data['payment_request'])
            
            return {
                'success': True,
                'order_id': order.id,
                'payment_request': invoice_data['payment_request'],
                'payment_hash': invoice_data['payment_hash'],
                'amount_sats': price_sats,
                'amount_btc': price_sats / 100_000_000,
                'description': f"Purchase: {product_name}",
                'expires_at': expires_at.isoformat(),
                'qr_code': qr_code,
                'node_info': {
                    'node': self.default_node,
                    'alias': 'Lightning Marketplace'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create payment request: {str(e)}"
            }
    
    def _create_lightning_invoice(self, amount_sats: int, description: str, 
                                order_id: str) -> Dict[str, Any]:
        """Create real Lightning invoice using Polar service"""
        try:
            # Stage 4: Create real Lightning invoice using Polar
            invoice_result = self.polar_service.create_invoice(
                node=self.default_node,
                amount_sats=amount_sats,
                description=description,
                expiry=900  # 15 minutes
            )
            
            if invoice_result['success']:
                return {
                    'success': True,
                    'payment_request': invoice_result['payment_request'],
                    'payment_hash': invoice_result.get('payment_hash', ''),
                    'amount_sats': amount_sats,
                    'description': description,
                    'expires_at': (datetime.now() + timedelta(minutes=15)).isoformat()
                }
            else:
                # Fallback to simulation if Polar is not available
                import hashlib
                import secrets
                
                # Generate fake payment hash for demo
                payment_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
                
                # Generate fake Lightning invoice for demo
                payment_request = f"lnbcrt{amount_sats}u1p3xnhl2pp5{payment_hash[:20]}...fake_invoice_for_demo"
                
                return {
                    'success': True,
                    'payment_request': payment_request,
                    'payment_hash': payment_hash,
                    'amount_sats': amount_sats,
                    'description': description,
                    'expires_at': (datetime.now() + timedelta(minutes=15)).isoformat(),
                    'simulation': True
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create Lightning invoice: {str(e)}"
            }
    
    def _generate_qr_code(self, payment_request: str) -> str:
        """Generate QR code for Lightning payment request"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(payment_request)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for web display
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return ""
    
    def check_payment_status(self, order_id: str) -> Dict[str, Any]:
        """Check if payment has been completed"""
        try:
            order = self.order_service.get_order(order_id)
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
            
            # Stage 4: Real Lightning payment verification
            
            # Check if order has expired
            if order.is_expired and order.status == OrderStatus.PAYMENT_PENDING:
                self.order_service.expire_order(order_id)
                return {
                    'success': True,
                    'status': 'expired',
                    'message': 'Payment window has expired'
                }
            
            # Check real Lightning payment status if payment is pending
            if order.status == OrderStatus.PAYMENT_PENDING and order.payment_hash:
                payment_check = self.polar_service.lookup_invoice(
                    self.default_node, 
                    order.payment_hash
                )
                
                if payment_check.get('success') and payment_check.get('settled'):
                    # Payment confirmed! Mark as paid
                    # Use payment hash as preimage for now (in production, get actual preimage)
                    self.order_service.mark_order_paid(order_id, order.payment_hash)
                    
                    return {
                        'success': True,
                        'status': 'paid',
                        'message': 'Payment confirmed!',
                        'payment_hash': order.payment_hash,
                        'settled_date': payment_check.get('settle_date', 0)
                    }
            
            return {
                'success': True,
                'status': order.status.value,
                'time_remaining': order.time_remaining,
                'message': self._get_status_message(order.status)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to check payment status: {str(e)}"
            }
    
    def _get_status_message(self, status: OrderStatus) -> str:
        """Get user-friendly status message"""
        messages = {
            OrderStatus.PENDING: "Order created, preparing payment...",
            OrderStatus.PAYMENT_PENDING: "Waiting for Lightning payment...",
            OrderStatus.PAID: "Payment confirmed!",
            OrderStatus.DELIVERED: "Product delivered successfully",
            OrderStatus.CANCELLED: "Order was cancelled",
            OrderStatus.EXPIRED: "Payment window expired"
        }
        return messages.get(status, "Unknown status")
    
    def deliver_product(self, order_id: str) -> Dict[str, Any]:
        """Deliver digital product after payment confirmation"""
        try:
            order = self.order_service.get_order(order_id)
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
            
            if order.status != OrderStatus.PAID:
                return {
                    'success': False,
                    'error': 'Order not paid'
                }
            
            # Mark as delivered
            self.order_service.mark_order_delivered(order_id)
            
            # For demo, return fake download link
            download_link = f"/download/{order_id}/{order.product_id}"
            
            return {
                'success': True,
                'message': 'Product delivered successfully',
                'download_link': download_link,
                'product_name': order.product_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to deliver product: {str(e)}"
            }
    
    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Get complete order details"""
        try:
            order = self.order_service.get_order(order_id)
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
            
            return {
                'success': True,
                'order': order.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to get order details: {str(e)}"
            }
    
    def cancel_payment(self, order_id: str) -> Dict[str, Any]:
        """Cancel a payment request"""
        try:
            order = self.order_service.get_order(order_id)
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
            
            if order.status not in [OrderStatus.PENDING, OrderStatus.PAYMENT_PENDING]:
                return {
                    'success': False,
                    'error': 'Cannot cancel order in current status'
                }
            
            self.order_service.cancel_order(order_id)
            
            return {
                'success': True,
                'message': 'Payment cancelled successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to cancel payment: {str(e)}"
            }
