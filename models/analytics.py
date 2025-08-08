"""
Lightning Digital Marketplace - Analytics Models
Stage 5: Advanced Business Features

Data models for analytics tracking and business intelligence
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import json

class MetricType(Enum):
    """Types of analytics metrics"""
    SALES = "sales"
    REVENUE = "revenue"
    CUSTOMER = "customer"
    LIGHTNING = "lightning"
    SUBSCRIPTION = "subscription"
    CONVERSION = "conversion"

class Period(Enum):
    """Time periods for analytics"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class AnalyticsEvent:
    """Individual analytics event"""
    event_id: str
    event_type: str
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    order_id: Optional[str] = None
    subscription_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'metric_type': self.metric_type.value,
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'metadata': self.metadata,
            'customer_id': self.customer_id,
            'product_id': self.product_id,
            'order_id': self.order_id,
            'subscription_id': self.subscription_id
        }

@dataclass
class MetricSnapshot:
    """Snapshot of a metric at a specific time"""
    metric_name: str
    metric_type: MetricType
    period: Period
    timestamp: datetime
    value: float
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def trend(self) -> str:
        """Get trend direction"""
        if self.previous_value is None or self.previous_value == 0:
            return "neutral"
        
        if self.value > self.previous_value:
            return "up"
        elif self.value < self.previous_value:
            return "down"
        else:
            return "neutral"
    
    def calculate_change_percent(self) -> float:
        """Calculate percentage change from previous value"""
        if self.previous_value is None or self.previous_value == 0:
            return 0.0
        
        self.change_percent = ((self.value - self.previous_value) / self.previous_value) * 100
        return self.change_percent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary"""
        return {
            'metric_name': self.metric_name,
            'metric_type': self.metric_type.value,
            'period': self.period.value,
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'previous_value': self.previous_value,
            'change_percent': self.change_percent,
            'trend': self.trend,
            'metadata': self.metadata
        }

@dataclass
class KPI:
    """Key Performance Indicator"""
    name: str
    description: str
    current_value: float
    target_value: Optional[float] = None
    unit: str = ""
    format_type: str = "number"  # number, currency, percentage
    last_updated: datetime = field(default_factory=datetime.now)
    trend_data: List[float] = field(default_factory=list)
    
    @property
    def target_progress(self) -> Optional[float]:
        """Progress towards target as percentage"""
        if self.target_value is None or self.target_value == 0:
            return None
        return (self.current_value / self.target_value) * 100
    
    @property
    def performance_status(self) -> str:
        """Performance status based on target"""
        if self.target_value is None:
            return "no_target"
        
        progress = self.target_progress
        if progress >= 100:
            return "excellent"
        elif progress >= 80:
            return "good"
        elif progress >= 60:
            return "average"
        else:
            return "poor"
    
    def add_trend_point(self, value: float, max_points: int = 30):
        """Add a data point to trend history"""
        self.trend_data.append(value)
        if len(self.trend_data) > max_points:
            self.trend_data.pop(0)
        self.current_value = value
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert KPI to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'current_value': self.current_value,
            'target_value': self.target_value,
            'unit': self.unit,
            'format_type': self.format_type,
            'last_updated': self.last_updated.isoformat(),
            'trend_data': self.trend_data,
            'target_progress': self.target_progress,
            'performance_status': self.performance_status
        }

class AnalyticsTracker:
    """Service for tracking and storing analytics events"""
    
    def __init__(self):
        self._events: List[AnalyticsEvent] = []
        self._snapshots: Dict[str, List[MetricSnapshot]] = {}
        self._kpis: Dict[str, KPI] = {}
        self._initialize_default_kpis()
    
    def _initialize_default_kpis(self):
        """Initialize default KPIs for the marketplace"""
        self._kpis = {
            'total_revenue': KPI(
                name='Total Revenue',
                description='Total revenue in satoshis',
                current_value=0,
                target_value=1000000,  # 1M sats
                unit='sats',
                format_type='currency'
            ),
            'monthly_orders': KPI(
                name='Monthly Orders',
                description='Number of orders per month',
                current_value=0,
                target_value=100,
                unit='orders',
                format_type='number'
            ),
            'conversion_rate': KPI(
                name='Conversion Rate',
                description='Percentage of visitors who make a purchase',
                current_value=0,
                target_value=5.0,
                unit='%',
                format_type='percentage'
            ),
            'customer_acquisition_cost': KPI(
                name='Customer Acquisition Cost',
                description='Cost to acquire a new customer in sats',
                current_value=0,
                target_value=10000,  # 10k sats
                unit='sats',
                format_type='currency'
            ),
            'lightning_success_rate': KPI(
                name='Lightning Success Rate',
                description='Percentage of successful Lightning transactions',
                current_value=0,
                target_value=99.0,
                unit='%',
                format_type='percentage'
            ),
            'active_subscriptions': KPI(
                name='Active Subscriptions',
                description='Number of active recurring subscriptions',
                current_value=0,
                target_value=50,
                unit='subscriptions',
                format_type='number'
            )
        }
    
    def track_event(self, event: AnalyticsEvent):
        """Track a new analytics event"""
        self._events.append(event)
        
        # Update related KPIs
        self._update_kpis_from_event(event)
    
    def _update_kpis_from_event(self, event: AnalyticsEvent):
        """Update KPIs based on incoming event"""
        if event.event_type == 'order_completed':
            # Update revenue KPI
            if 'total_revenue' in self._kpis:
                current_total = self._kpis['total_revenue'].current_value + event.value
                self._kpis['total_revenue'].add_trend_point(current_total)
        
        elif event.event_type == 'subscription_activated':
            # Update active subscriptions KPI
            if 'active_subscriptions' in self._kpis:
                current_count = self._kpis['active_subscriptions'].current_value + 1
                self._kpis['active_subscriptions'].add_trend_point(current_count)
    
    def create_snapshot(self, metric_name: str, metric_type: MetricType, 
                       period: Period, value: float, 
                       previous_value: Optional[float] = None) -> MetricSnapshot:
        """Create a metric snapshot"""
        snapshot = MetricSnapshot(
            metric_name=metric_name,
            metric_type=metric_type,
            period=period,
            timestamp=datetime.now(),
            value=value,
            previous_value=previous_value
        )
        
        snapshot.calculate_change_percent()
        
        # Store snapshot
        key = f"{metric_name}_{period.value}"
        if key not in self._snapshots:
            self._snapshots[key] = []
        
        self._snapshots[key].append(snapshot)
        
        # Keep only last 100 snapshots per metric
        if len(self._snapshots[key]) > 100:
            self._snapshots[key].pop(0)
        
        return snapshot
    
    def get_events(self, metric_type: Optional[MetricType] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None) -> List[AnalyticsEvent]:
        """Get filtered analytics events"""
        events = self._events
        
        if metric_type:
            events = [e for e in events if e.metric_type == metric_type]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        return events
    
    def get_snapshots(self, metric_name: str, period: Period,
                     limit: int = 30) -> List[MetricSnapshot]:
        """Get metric snapshots"""
        key = f"{metric_name}_{period.value}"
        snapshots = self._snapshots.get(key, [])
        return snapshots[-limit:] if limit > 0 else snapshots
    
    def get_kpi(self, name: str) -> Optional[KPI]:
        """Get a specific KPI"""
        return self._kpis.get(name)
    
    def get_all_kpis(self) -> Dict[str, KPI]:
        """Get all KPIs"""
        return self._kpis.copy()
    
    def update_kpi_target(self, name: str, target_value: float):
        """Update KPI target value"""
        if name in self._kpis:
            self._kpis[name].target_value = target_value
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        return {
            'kpis': {name: kpi.to_dict() for name, kpi in self._kpis.items()},
            'total_events': len(self._events),
            'recent_events': [e.to_dict() for e in self._events[-10:]],
            'metric_counts': {
                metric_type.value: len([e for e in self._events if e.metric_type == metric_type])
                for metric_type in MetricType
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def export_data(self, format_type: str = 'json') -> str:
        """Export analytics data"""
        data = {
            'events': [e.to_dict() for e in self._events],
            'kpis': {name: kpi.to_dict() for name, kpi in self._kpis.items()},
            'snapshots': {
                key: [s.to_dict() for s in snapshots]
                for key, snapshots in self._snapshots.items()
            },
            'exported_at': datetime.now().isoformat()
        }
        
        if format_type == 'json':
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

# Sample analytics events for demonstration
SAMPLE_EVENTS = [
    AnalyticsEvent(
        event_id="evt_001",
        event_type="order_completed",
        metric_type=MetricType.SALES,
        value=50000,  # 50k sats
        metadata={"product_name": "Premium Lightning Course", "customer_type": "new"}
    ),
    AnalyticsEvent(
        event_id="evt_002",
        event_type="subscription_activated",
        metric_type=MetricType.SUBSCRIPTION,
        value=25000,  # 25k sats monthly
        metadata={"plan": "premium", "trial_period": True}
    ),
    AnalyticsEvent(
        event_id="evt_003",
        event_type="lightning_payment_success",
        metric_type=MetricType.LIGHTNING,
        value=1.0,  # Success rate metric
        metadata={"tx_size_sats": 50000, "confirmation_time": 0.5}
    )
]