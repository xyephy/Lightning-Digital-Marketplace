"""
Lightning Digital Marketplace - Product Model
Stage 2: Commerce Core
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json

@dataclass
class Product:
    """Product model for digital marketplace"""
    id: int
    name: str
    description: str
    price_sats: int
    category: str
    image_url: str
    digital_content: Optional[str] = None
    is_active: bool = True
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @property
    def price_btc(self) -> float:
        """Convert satoshis to BTC"""
        return self.price_sats / 100_000_000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price_sats': self.price_sats,
            'price_btc': self.price_btc,
            'category': self.category,
            'image_url': self.image_url,
            'digital_content': self.digital_content,
            'is_active': self.is_active,
            'tags': self.tags
        }

class ProductService:
    """Service for managing products"""
    
    def __init__(self, data_file: str = 'data/products.json'):
        self.data_file = data_file
        self._products = self._load_products()
    
    def _load_products(self) -> List[Product]:
        """Load products from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Filter out price_btc since it's a computed property
                clean_data = []
                for item in data:
                    clean_item = {k: v for k, v in item.items() if k != 'price_btc'}
                    clean_data.append(clean_item)
                return [Product(**item) for item in clean_data]
        except FileNotFoundError:
            return self._create_sample_products()
    
    def _create_sample_products(self) -> List[Product]:
        """Create sample products for demo"""
        sample_products = [
            Product(
                id=1,
                name="Lightning Network Whitepaper",
                description="The original Lightning Network whitepaper by Joseph Poon and Thaddeus Dryja. Essential reading for understanding the Lightning Network.",
                price_sats=1000,
                category="educational",
                image_url="https://via.placeholder.com/300x200?text=Lightning+Whitepaper",
                digital_content="lightning_whitepaper.pdf",
                tags=["bitcoin", "lightning", "whitepaper", "educational"]
            ),
            Product(
                id=2,
                name="Bitcoin Developer Toolkit",
                description="Complete toolkit for Bitcoin development including sample code, libraries, and documentation.",
                price_sats=5000,
                category="development",
                image_url="https://via.placeholder.com/300x200?text=Dev+Toolkit",
                digital_content="bitcoin_dev_toolkit.zip",
                tags=["bitcoin", "development", "tools", "code"]
            ),
            Product(
                id=3,
                name="Lightning Node Setup Guide",
                description="Step-by-step guide to setting up your own Lightning Network node with best practices and security tips.",
                price_sats=2500,
                category="tutorial",
                image_url="https://via.placeholder.com/300x200?text=Node+Setup",
                digital_content="lightning_node_guide.pdf",
                tags=["lightning", "node", "tutorial", "setup"]
            ),
            Product(
                id=4,
                name="Bitcoin Trading Bot Script",
                description="Python script for automated Bitcoin trading with Lightning Network integration for fast settlements.",
                price_sats=10000,
                category="automation",
                image_url="https://via.placeholder.com/300x200?text=Trading+Bot",
                digital_content="trading_bot.py",
                tags=["bitcoin", "trading", "automation", "python"]
            ),
            Product(
                id=5,
                name="Lightning Payment Widget",
                description="Ready-to-use JavaScript widget for accepting Lightning payments on your website.",
                price_sats=7500,
                category="development",
                image_url="https://via.placeholder.com/300x200?text=Payment+Widget",
                digital_content="lightning_widget.js",
                tags=["lightning", "payments", "javascript", "widget"]
            ),
            Product(
                id=6,
                name="Cryptocurrency Market Analysis",
                description="Comprehensive market analysis report covering Bitcoin, Lightning Network adoption, and future trends.",
                price_sats=3000,
                category="analysis",
                image_url="https://via.placeholder.com/300x200?text=Market+Analysis",
                digital_content="market_analysis.pdf",
                tags=["bitcoin", "market", "analysis", "trends"]
            )
        ]
        
        # Save sample products to file
        self._save_products(sample_products)
        return sample_products
    
    def _save_products(self, products: List[Product]):
        """Save products to JSON file"""
        import os
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        with open(self.data_file, 'w') as f:
            json.dump([p.to_dict() for p in products], f, indent=2)
    
    def get_all_products(self) -> List[Product]:
        """Get all active products"""
        return [p for p in self._products if p.is_active]
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        for product in self._products:
            if product.id == product_id and product.is_active:
                return product
        return None
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Get products by category"""
        return [p for p in self._products if p.category == category and p.is_active]
    
    def search_products(self, query: str) -> List[Product]:
        """Search products by name, description, or tags"""
        query = query.lower()
        results = []
        
        for product in self._products:
            if not product.is_active:
                continue
                
            if (query in product.name.lower() or 
                query in product.description.lower() or
                any(query in tag.lower() for tag in product.tags)):
                results.append(product)
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        categories = set()
        for product in self._products:
            if product.is_active:
                categories.add(product.category)
        return sorted(list(categories))

