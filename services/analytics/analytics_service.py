"""
Lightning Digital Marketplace - Analytics Service
Stage 5: Advanced Business Features
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import json

class AnalyticsService:
    """Service for business analytics and reporting"""
    
    def __init__(self, order_service, subscription_service, product_service):
        self.order_service = order_service
        self.subscription_service = subscription_service
        self.product_service = product_service
        self._metrics_cache = {}
        self._cache_expiry = {}
    
    def get_sales_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get sales analytics for specified period"""
        cache_key = f"sales_{days}"
        if self._is_cache_valid(cache_key):
            return self._metrics_cache[cache_key]
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all orders in date range
        all_orders = list(self.order_service._orders.values())
        period_orders = [
            order for order in all_orders
            if order.created_at >= start_date and order.created_at <= end_date
        ]
        
        # Calculate metrics
        total_orders = len(period_orders)
        completed_orders = [o for o in period_orders if o.status.value == 'delivered']
        total_revenue_sats = sum(o.price_sats for o in completed_orders)
        
        # Daily breakdown
        daily_sales = defaultdict(lambda: {'orders': 0, 'revenue_sats': 0})
        for order in completed_orders:
            date_key = order.created_at.strftime('%Y-%m-%d')
            daily_sales[date_key]['orders'] += 1
            daily_sales[date_key]['revenue_sats'] += order.price_sats
        
        # Product performance
        product_sales = defaultdict(lambda: {'count': 0, 'revenue_sats': 0})
        for order in completed_orders:
            product_sales[order.product_name]['count'] += 1
            product_sales[order.product_name]['revenue_sats'] += order.price_sats
        
        analytics = {
            'period_days': days,
            'total_orders': total_orders,
            'completed_orders': len(completed_orders),
            'conversion_rate': len(completed_orders) / total_orders if total_orders > 0 else 0,
            'total_revenue_sats': total_revenue_sats,
            'total_revenue_btc': total_revenue_sats / 100_000_000,
            'average_order_value_sats': total_revenue_sats / len(completed_orders) if completed_orders else 0,
            'daily_sales': dict(daily_sales),
            'top_products': sorted(
                product_sales.items(), 
                key=lambda x: x[1]['revenue_sats'], 
                reverse=True
            )[:5]
        }
        
        self._cache_result(cache_key, analytics)
        return analytics
    
    def get_customer_analytics(self) -> Dict[str, Any]:
        """Get customer analytics"""
        cache_key = "customers"
        if self._is_cache_valid(cache_key):
            return self._metrics_cache[cache_key]
        
        # Get unique customers from orders
        all_orders = list(self.order_service._orders.values())
        customers_with_orders = set(
            order.customer_email 
            for order in all_orders 
            if order.customer_email
        )
        
        # Get unique customers from subscriptions
        customers_with_subscriptions = set(
            sub.customer_email 
            for sub in self.subscription_service._subscriptions.values()
        )
        
        total_customers = len(customers_with_orders | customers_with_subscriptions)
        
        # Customer lifetime value calculation
        customer_values = defaultdict(int)
        for order in all_orders:
            if order.customer_email and order.status.value == 'delivered':
                customer_values[order.customer_email] += order.price_sats
        
        avg_customer_value = sum(customer_values.values()) / len(customer_values) if customer_values else 0
        
        analytics = {
            'total_customers': total_customers,
            'customers_with_orders': len(customers_with_orders),
            'customers_with_subscriptions': len(customers_with_subscriptions),
            'average_customer_lifetime_value_sats': avg_customer_value,
            'average_customer_lifetime_value_btc': avg_customer_value / 100_000_000,
            'top_customers': sorted(
                customer_values.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        }
        
        self._cache_result(cache_key, analytics)
        return analytics
    
    def get_revenue_analytics(self) -> Dict[str, Any]:
        """Get comprehensive revenue analytics"""
        cache_key = "revenue"
        if self._is_cache_valid(cache_key):
            return self._metrics_cache[cache_key]
        
        # One-time sales revenue
        sales_analytics = self.get_sales_analytics(30)
        one_time_revenue = sales_analytics['total_revenue_sats']
        
        # Subscription revenue (MRR)
        subscription_analytics = self.subscription_service.get_subscription_analytics()
        monthly_recurring_revenue = subscription_analytics['mrr_sats']
        
        # Annual recurring revenue (ARR)
        annual_recurring_revenue = monthly_recurring_revenue * 12
        
        analytics = {
            'one_time_revenue_sats': one_time_revenue,
            'one_time_revenue_btc': one_time_revenue / 100_000_000,
            'monthly_recurring_revenue_sats': monthly_recurring_revenue,
            'monthly_recurring_revenue_btc': monthly_recurring_revenue / 100_000_000,
            'annual_recurring_revenue_sats': annual_recurring_revenue,
            'annual_recurring_revenue_btc': annual_recurring_revenue / 100_000_000,
            'total_monthly_revenue_sats': one_time_revenue + monthly_recurring_revenue,
            'total_monthly_revenue_btc': (one_time_revenue + monthly_recurring_revenue) / 100_000_000,
            'revenue_mix': {
                'one_time_percentage': one_time_revenue / (one_time_revenue + monthly_recurring_revenue) * 100 if (one_time_revenue + monthly_recurring_revenue) > 0 else 0,
                'subscription_percentage': monthly_recurring_revenue / (one_time_revenue + monthly_recurring_revenue) * 100 if (one_time_revenue + monthly_recurring_revenue) > 0 else 0
            }
        }
        
        self._cache_result(cache_key, analytics)
        return analytics
    
    def get_lightning_analytics(self) -> Dict[str, Any]:
        """Get Lightning Network specific analytics"""
        cache_key = "lightning"
        if self._is_cache_valid(cache_key):
            return self._metrics_cache[cache_key]
        
        # Get all completed orders
        all_orders = list(self.order_service._orders.values())
        completed_orders = [o for o in all_orders if o.status.value == 'delivered']
        
        # Calculate Lightning metrics
        total_lightning_transactions = len(completed_orders)
        total_lightning_volume_sats = sum(o.price_sats for o in completed_orders)
        
        # Average transaction size
        avg_transaction_sats = total_lightning_volume_sats / total_lightning_transactions if total_lightning_transactions > 0 else 0
        
        # Transaction size distribution
        size_ranges = {
            'micro': 0,    # < 1000 sats
            'small': 0,    # 1000-10000 sats
            'medium': 0,   # 10000-100000 sats
            'large': 0     # > 100000 sats
        }
        
        for order in completed_orders:
            if order.price_sats < 1000:
                size_ranges['micro'] += 1
            elif order.price_sats < 10000:
                size_ranges['small'] += 1
            elif order.price_sats < 100000:
                size_ranges['medium'] += 1
            else:
                size_ranges['large'] += 1
        
        analytics = {
            'total_lightning_transactions': total_lightning_transactions,
            'total_lightning_volume_sats': total_lightning_volume_sats,
            'total_lightning_volume_btc': total_lightning_volume_sats / 100_000_000,
            'average_transaction_sats': avg_transaction_sats,
            'average_transaction_btc': avg_transaction_sats / 100_000_000,
            'transaction_size_distribution': size_ranges,
            'lightning_network_fees_saved': total_lightning_transactions * 1000,  # Estimated savings vs on-chain
            'instant_settlements': total_lightning_transactions  # All Lightning transactions are instant
        }
        
        self._cache_result(cache_key, analytics)
        return analytics
    
    def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard data"""
        return {
            'sales': self.get_sales_analytics(30),
            'customers': self.get_customer_analytics(),
            'revenue': self.get_revenue_analytics(),
            'lightning': self.get_lightning_analytics(),
            'subscriptions': self.subscription_service.get_subscription_analytics(),
            'generated_at': datetime.now().isoformat()
        }
    
    def _is_cache_valid(self, cache_key: str, ttl_minutes: int = 5) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self._cache_expiry:
            return False
        
        expiry_time = self._cache_expiry[cache_key]
        return datetime.now() < expiry_time
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any], ttl_minutes: int = 5):
        """Cache analytics result"""
        self._metrics_cache[cache_key] = result
        self._cache_expiry[cache_key] = datetime.now() + timedelta(minutes=ttl_minutes)
    
    def clear_cache(self):
        """Clear analytics cache"""
        self._metrics_cache.clear()
        self._cache_expiry.clear()
    
    def export_analytics(self, format: str = 'json') -> str:
        """Export analytics data"""
        dashboard_data = self.get_comprehensive_dashboard()
        
        if format == 'json':
            return json.dumps(dashboard_data, indent=2, default=str)
        elif format == 'csv':
            # Simplified CSV export for sales data
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write sales data
            writer.writerow(['Date', 'Orders', 'Revenue (sats)', 'Revenue (BTC)'])
            for date, data in dashboard_data['sales']['daily_sales'].items():
                writer.writerow([
                    date,
                    data['orders'],
                    data['revenue_sats'],
                    data['revenue_sats'] / 100_000_000
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")

