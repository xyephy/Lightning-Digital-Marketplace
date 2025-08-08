"""
Lightning Digital Marketplace - Order Model
Stage 2: Commerce Core
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class Order:
    """Order model for tracking purchases"""
    id: str
    product_id: int
    product_name: str
    price_sats: int
    customer_email: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    lightning_invoice: Optional[str] = None
    payment_hash: Optional[str] = None
    payment_preimage: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    @property
    def price_btc(self) -> float:
        """Convert satoshis to BTC"""
        return self.price_sats / 100_000_000
    
    @property
    def is_expired(self) -> bool:
        """Check if order has expired"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False
    
    @property
    def time_remaining(self) -> Optional[int]:
        """Get seconds remaining until expiration"""
        if self.expires_at:
            remaining = self.expires_at - datetime.now()
            return max(0, int(remaining.total_seconds()))
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'price_sats': self.price_sats,
            'price_btc': self.price_btc,
            'customer_email': self.customer_email,
            'status': self.status.value,
            'lightning_invoice': self.lightning_invoice,
            'payment_hash': self.payment_hash,
            'payment_preimage': self.payment_preimage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired,
            'time_remaining': self.time_remaining
        }

class OrderService:
    """Service for managing orders"""
    
    def __init__(self):
        self._orders: Dict[str, Order] = {}
    
    def create_order(self, product_id: int, product_name: str, price_sats: int, 
                    customer_email: Optional[str] = None) -> Order:
        """Create a new order"""
        import uuid
        
        order_id = str(uuid.uuid4())[:8]  # Short order ID
        
        order = Order(
            id=order_id,
            product_id=product_id,
            product_name=product_name,
            price_sats=price_sats,
            customer_email=customer_email,
            status=OrderStatus.PENDING
        )
        
        self._orders[order_id] = order
        return order
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self._orders.get(order_id)
    
    def update_order_payment(self, order_id: str, lightning_invoice: str, 
                           payment_hash: str, expires_at: datetime) -> bool:
        """Update order with payment information"""
        order = self._orders.get(order_id)
        if not order:
            return False
        
        order.lightning_invoice = lightning_invoice
        order.payment_hash = payment_hash
        order.expires_at = expires_at
        order.status = OrderStatus.PAYMENT_PENDING
        
        return True
    
    def mark_order_paid(self, order_id: str, payment_preimage: str) -> bool:
        """Mark order as paid"""
        order = self._orders.get(order_id)
        if not order:
            return False
        
        order.payment_preimage = payment_preimage
        order.paid_at = datetime.now()
        order.status = OrderStatus.PAID
        
        return True
    
    def mark_order_delivered(self, order_id: str) -> bool:
        """Mark order as delivered"""
        order = self._orders.get(order_id)
        if not order or order.status != OrderStatus.PAID:
            return False
        
        order.delivered_at = datetime.now()
        order.status = OrderStatus.DELIVERED
        
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        order = self._orders.get(order_id)
        if not order:
            return False
        
        order.status = OrderStatus.CANCELLED
        return True
    
    def expire_order(self, order_id: str) -> bool:
        """Mark order as expired"""
        order = self._orders.get(order_id)
        if not order:
            return False
        
        order.status = OrderStatus.EXPIRED
        return True
    
    def get_orders_by_status(self, status: OrderStatus) -> list:
        """Get all orders with specific status"""
        return [order for order in self._orders.values() if order.status == status]
    
    def cleanup_expired_orders(self) -> int:
        """Clean up expired orders and return count"""
        expired_count = 0
        
        for order in self._orders.values():
            if (order.status == OrderStatus.PAYMENT_PENDING and 
                order.is_expired):
                order.status = OrderStatus.EXPIRED
                expired_count += 1
        
        return expired_count

