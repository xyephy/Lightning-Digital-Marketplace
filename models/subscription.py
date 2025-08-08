"""
Lightning Digital Marketplace - Subscription Model
Stage 5: Advanced Business Features
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

class SubscriptionStatus(Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"

class SubscriptionPlan(Enum):
    """Subscription plan types"""
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

@dataclass
class Subscription:
    """Subscription model for recurring Lightning payments"""
    id: str
    customer_email: str
    plan: SubscriptionPlan
    price_sats_per_month: int
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    next_payment_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    last_payment_at: Optional[datetime] = None
    failed_payments: int = 0
    
    @property
    def price_btc_per_month(self) -> float:
        """Convert monthly satoshis to BTC"""
        return self.price_sats_per_month / 100_000_000
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return self.status == SubscriptionStatus.ACTIVE
    
    @property
    def days_until_next_payment(self) -> Optional[int]:
        """Get days until next payment"""
        if self.next_payment_at:
            delta = self.next_payment_at - datetime.now()
            return max(0, delta.days)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary"""
        return {
            'id': self.id,
            'customer_email': self.customer_email,
            'plan': self.plan.value,
            'price_sats_per_month': self.price_sats_per_month,
            'price_btc_per_month': self.price_btc_per_month,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'next_payment_at': self.next_payment_at.isoformat() if self.next_payment_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'last_payment_at': self.last_payment_at.isoformat() if self.last_payment_at else None,
            'failed_payments': self.failed_payments,
            'is_active': self.is_active,
            'days_until_next_payment': self.days_until_next_payment
        }

class SubscriptionService:
    """Service for managing subscriptions"""
    
    PLANS = {
        SubscriptionPlan.BASIC: {
            'name': 'Basic Plan',
            'price_sats': 10000,  # 0.0001 BTC per month
            'features': [
                'Access to basic digital products',
                'Lightning payment support',
                'Email support'
            ]
        },
        SubscriptionPlan.PREMIUM: {
            'name': 'Premium Plan',
            'price_sats': 25000,  # 0.00025 BTC per month
            'features': [
                'Access to all digital products',
                'Priority Lightning transactions',
                'Advanced analytics',
                'Priority support'
            ]
        },
        SubscriptionPlan.ENTERPRISE: {
            'name': 'Enterprise Plan',
            'price_sats': 50000,  # 0.0005 BTC per month
            'features': [
                'All Premium features',
                'Custom Lightning integrations',
                'API access',
                'Dedicated account manager',
                'Advanced reporting'
            ]
        }
    }
    
    def __init__(self):
        self._subscriptions: Dict[str, Subscription] = {}
    
    def create_subscription(self, customer_email: str, plan: SubscriptionPlan) -> Subscription:
        """Create a new subscription"""
        import uuid
        
        subscription_id = str(uuid.uuid4())[:8]
        plan_info = self.PLANS[plan]
        
        subscription = Subscription(
            id=subscription_id,
            customer_email=customer_email,
            plan=plan,
            price_sats_per_month=plan_info['price_sats'],
            status=SubscriptionStatus.PENDING
        )
        
        self._subscriptions[subscription_id] = subscription
        return subscription
    
    def activate_subscription(self, subscription_id: str) -> bool:
        """Activate a subscription after successful payment"""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return False
        
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.started_at = datetime.now()
        subscription.last_payment_at = datetime.now()
        subscription.next_payment_at = datetime.now() + timedelta(days=30)
        
        return True
    
    def process_subscription_payment(self, subscription_id: str, success: bool) -> bool:
        """Process subscription payment"""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return False
        
        if success:
            subscription.last_payment_at = datetime.now()
            subscription.next_payment_at = datetime.now() + timedelta(days=30)
            subscription.failed_payments = 0
            subscription.status = SubscriptionStatus.ACTIVE
        else:
            subscription.failed_payments += 1
            if subscription.failed_payments >= 3:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.now()
        
        return True
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription"""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return False
        
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.now()
        
        return True
    
    def pause_subscription(self, subscription_id: str) -> bool:
        """Pause a subscription"""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            return False
        
        subscription.status = SubscriptionStatus.PAUSED
        
        return True
    
    def resume_subscription(self, subscription_id: str) -> bool:
        """Resume a paused subscription"""
        subscription = self._subscriptions.get(subscription_id)
        if not subscription or subscription.status != SubscriptionStatus.PAUSED:
            return False
        
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.next_payment_at = datetime.now() + timedelta(days=30)
        
        return True
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID"""
        return self._subscriptions.get(subscription_id)
    
    def get_customer_subscriptions(self, customer_email: str) -> List[Subscription]:
        """Get all subscriptions for a customer"""
        return [sub for sub in self._subscriptions.values() if sub.customer_email == customer_email]
    
    def get_subscriptions_by_status(self, status: SubscriptionStatus) -> List[Subscription]:
        """Get subscriptions by status"""
        return [sub for sub in self._subscriptions.values() if sub.status == status]
    
    def get_expiring_subscriptions(self, days_ahead: int = 7) -> List[Subscription]:
        """Get subscriptions expiring within specified days"""
        expiring_date = datetime.now() + timedelta(days=days_ahead)
        return [
            sub for sub in self._subscriptions.values() 
            if (sub.status == SubscriptionStatus.ACTIVE and 
                sub.next_payment_at and 
                sub.next_payment_at <= expiring_date)
        ]
    
    def get_subscription_analytics(self) -> Dict[str, Any]:
        """Get subscription analytics"""
        total_subscriptions = len(self._subscriptions)
        active_subscriptions = len(self.get_subscriptions_by_status(SubscriptionStatus.ACTIVE))
        cancelled_subscriptions = len(self.get_subscriptions_by_status(SubscriptionStatus.CANCELLED))
        
        # Calculate monthly recurring revenue (MRR) in sats
        mrr_sats = sum(
            sub.price_sats_per_month 
            for sub in self._subscriptions.values() 
            if sub.status == SubscriptionStatus.ACTIVE
        )
        
        # Plan distribution
        plan_distribution = {}
        for plan in SubscriptionPlan:
            plan_distribution[plan.value] = len([
                sub for sub in self._subscriptions.values() 
                if sub.plan == plan and sub.status == SubscriptionStatus.ACTIVE
            ])
        
        return {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'cancelled_subscriptions': cancelled_subscriptions,
            'churn_rate': cancelled_subscriptions / total_subscriptions if total_subscriptions > 0 else 0,
            'mrr_sats': mrr_sats,
            'mrr_btc': mrr_sats / 100_000_000,
            'plan_distribution': plan_distribution,
            'expiring_soon': len(self.get_expiring_subscriptions())
        }
    
    @classmethod
    def get_available_plans(cls) -> Dict[str, Dict[str, Any]]:
        """Get available subscription plans"""
        plans = {}
        for plan, info in cls.PLANS.items():
            plans[plan.value] = {
                'name': info['name'],
                'price_sats': info['price_sats'],
                'price_btc': info['price_sats'] / 100_000_000,
                'features': info['features']
            }
        return plans