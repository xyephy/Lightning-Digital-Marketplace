"""
Lightning Digital Marketplace - Subscription Models
Stage 5: Advanced Business Features

Data models for subscription management and recurring payments
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import json

class SubscriptionStatus(Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"

class SubscriptionPlan:
    """Subscription plan model"""
    
    def __init__(self, plan_id: str, name: str, description: str, 
                 price_sats: int, billing_interval: str, features: List[str],
                 trial_days: int = 0):
        self.plan_id = plan_id
        self.name = name
        self.description = description
        self.price_sats = price_sats
        self.billing_interval = billing_interval  # 'monthly', 'yearly', 'weekly'
        self.features = features
        self.trial_days = trial_days
        self.created_at = datetime.now()
        self.is_active = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary"""
        return {
            'plan_id': self.plan_id,
            'name': self.name,
            'description': self.description,
            'price_sats': self.price_sats,
            'billing_interval': self.billing_interval,
            'features': self.features,
            'trial_days': self.trial_days,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubscriptionPlan':
        """Create plan from dictionary"""
        plan = cls(
            plan_id=data['plan_id'],
            name=data['name'],
            description=data['description'],
            price_sats=data['price_sats'],
            billing_interval=data['billing_interval'],
            features=data['features'],
            trial_days=data.get('trial_days', 0)
        )
        plan.created_at = datetime.fromisoformat(data['created_at'])
        plan.is_active = data.get('is_active', True)
        return plan

class Subscription:
    """Customer subscription model"""
    
    def __init__(self, subscription_id: str, customer_id: str, plan_id: str,
                 status: SubscriptionStatus = SubscriptionStatus.PENDING):
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.plan_id = plan_id
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.current_period_start = None
        self.current_period_end = None
        self.trial_end = None
        self.cancelled_at = None
        self.ended_at = None
        self.payment_history: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
    
    def start_subscription(self, plan: SubscriptionPlan):
        """Start the subscription with a plan"""
        self.status = SubscriptionStatus.ACTIVE
        self.current_period_start = datetime.now()
        
        # Set trial period if applicable
        if plan.trial_days > 0:
            self.trial_end = self.current_period_start + timedelta(days=plan.trial_days)
            self.current_period_end = self.trial_end
        else:
            self.current_period_end = self._calculate_next_billing_date(plan.billing_interval)
        
        self.updated_at = datetime.now()
    
    def _calculate_next_billing_date(self, billing_interval: str) -> datetime:
        """Calculate next billing date based on interval"""
        now = datetime.now()
        if billing_interval == 'weekly':
            return now + timedelta(weeks=1)
        elif billing_interval == 'monthly':
            return now + timedelta(days=30)
        elif billing_interval == 'yearly':
            return now + timedelta(days=365)
        else:
            raise ValueError(f"Unsupported billing interval: {billing_interval}")
    
    def add_payment(self, payment_hash: str, amount_sats: int, 
                   invoice_data: Dict[str, Any]):
        """Add payment to subscription history"""
        payment_record = {
            'payment_hash': payment_hash,
            'amount_sats': amount_sats,
            'payment_date': datetime.now().isoformat(),
            'invoice_data': invoice_data,
            'status': 'completed'
        }
        self.payment_history.append(payment_record)
        self.updated_at = datetime.now()
    
    def cancel_subscription(self, reason: str = ""):
        """Cancel the subscription"""
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self.updated_at = datetime.now()
        if reason:
            self.metadata['cancellation_reason'] = reason
    
    def pause_subscription(self):
        """Pause the subscription"""
        self.status = SubscriptionStatus.PAUSED
        self.updated_at = datetime.now()
    
    def resume_subscription(self):
        """Resume a paused subscription"""
        if self.status == SubscriptionStatus.PAUSED:
            self.status = SubscriptionStatus.ACTIVE
            self.updated_at = datetime.now()
    
    def is_in_trial(self) -> bool:
        """Check if subscription is in trial period"""
        if not self.trial_end:
            return False
        return datetime.now() < self.trial_end
    
    def days_until_renewal(self) -> int:
        """Get days until next renewal"""
        if not self.current_period_end:
            return 0
        delta = self.current_period_end - datetime.now()
        return max(0, delta.days)
    
    def total_revenue(self) -> int:
        """Calculate total revenue from this subscription"""
        return sum(payment['amount_sats'] for payment in self.payment_history)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary"""
        return {
            'subscription_id': self.subscription_id,
            'customer_id': self.customer_id,
            'plan_id': self.plan_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'trial_end': self.trial_end.isoformat() if self.trial_end else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'payment_history': self.payment_history,
            'metadata': self.metadata,
            'is_in_trial': self.is_in_trial(),
            'days_until_renewal': self.days_until_renewal(),
            'total_revenue': self.total_revenue()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        """Create subscription from dictionary"""
        subscription = cls(
            subscription_id=data['subscription_id'],
            customer_id=data['customer_id'],
            plan_id=data['plan_id'],
            status=SubscriptionStatus(data['status'])
        )
        
        subscription.created_at = datetime.fromisoformat(data['created_at'])
        subscription.updated_at = datetime.fromisoformat(data['updated_at'])
        
        if data.get('current_period_start'):
            subscription.current_period_start = datetime.fromisoformat(data['current_period_start'])
        if data.get('current_period_end'):
            subscription.current_period_end = datetime.fromisoformat(data['current_period_end'])
        if data.get('trial_end'):
            subscription.trial_end = datetime.fromisoformat(data['trial_end'])
        if data.get('cancelled_at'):
            subscription.cancelled_at = datetime.fromisoformat(data['cancelled_at'])
        if data.get('ended_at'):
            subscription.ended_at = datetime.fromisoformat(data['ended_at'])
        
        subscription.payment_history = data.get('payment_history', [])
        subscription.metadata = data.get('metadata', {})
        
        return subscription

# Sample subscription plans for the marketplace
SAMPLE_PLANS = [
    SubscriptionPlan(
        plan_id="basic",
        name="Basic Plan",
        description="Essential features for individual creators",
        price_sats=50000,  # ~$15 at $30k BTC
        billing_interval="monthly",
        features=[
            "Upload up to 10 digital products",
            "Basic analytics dashboard",
            "Lightning payment processing",
            "Email support"
        ],
        trial_days=7
    ),
    SubscriptionPlan(
        plan_id="pro",
        name="Pro Plan", 
        description="Advanced features for growing businesses",
        price_sats=150000,  # ~$45 at $30k BTC
        billing_interval="monthly",
        features=[
            "Unlimited digital products",
            "Advanced analytics & insights",
            "Priority Lightning routing",
            "Custom branding options",
            "API access",
            "Priority support"
        ],
        trial_days=14
    ),
    SubscriptionPlan(
        plan_id="enterprise",
        name="Enterprise Plan",
        description="Full-featured solution for large organizations",
        price_sats=500000,  # ~$150 at $30k BTC
        billing_interval="monthly",
        features=[
            "Everything in Pro",
            "Multi-user accounts",
            "Advanced API access",
            "Custom integrations",
            "Dedicated account manager",
            "SLA guarantees",
            "White-label options"
        ],
        trial_days=30
    )
]
