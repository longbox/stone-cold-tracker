"""
Stone Cold Tracker - Database Manager
Handles loading, querying, and managing oxalate and nutrient databases.
"""

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class DatabaseManager:
    """Manages loading and querying product and research databases."""
    
    def __init__(self, oxalate_db_path: str = "data/oxalate_database.json"):
        """
        Initialize database manager.
        
        Args:
            oxalate_db_path: Path to oxalate database JSON file
        """
        self.oxalate_db_path = oxalate_db_path
        self.products_by_id = {}
        self.products_by_category = {}
        self._load_databases()
    
    def _load_databases(self):
        """Load all databases into memory."""
        try:
            with open(self.oxalate_db_path, 'r') as f:
                data = json.load(f)
                self.products = data.get('products', [])
                
                # Build indexes
                for product in self.products:
                    self.products_by_id[product['id']] = product
                    
                    category = product.get('category')
                    if category not in self.products_by_category:
                        self.products_by_category[category] = []
                    self.products_by_category[category].append(product)
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Database not found: {self.oxalate_db_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in database: {self.oxalate_db_path}")
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """
        Get product by ID.
        
        Args:
            product_id: Product identifier
        
        Returns:
            Product dictionary or None if not found
        """
        return self.products_by_id.get(product_id)
    
    def search_products(self, query: str) -> List[Dict]:
        """
        Search products by name.
        
        Args:
            query: Search query string (case-insensitive)
        
        Returns:
            List of matching products
        """
        query_lower = query.lower()
        return [p for p in self.products 
                if query_lower in p.get('name', '').lower()]
    
    def get_by_category(self, category: str) -> List[Dict]:
        """
        Get all products in a category.
        
        Args:
            category: Product category
        
        Returns:
            List of products in category
        """
        return self.products_by_category.get(category, [])
    
    def get_categories(self) -> List[str]:
        """Get list of all product categories."""
        return sorted(list(self.products_by_category.keys()))
    
    def filter_by_oxalate_level(
        self,
        min_oxalate: float = 0,
        max_oxalate: float = 10000
    ) -> List[Dict]:
        """
        Filter products by oxalate content range.
        
        Args:
            min_oxalate: Minimum oxalate content (mg/100g)
            max_oxalate: Maximum oxalate content (mg/100g)
        
        Returns:
            List of products within range
        """
        return [p for p in self.products
                if min_oxalate <= p.get('oxalate_mg_per_100g', 0) <= max_oxalate]
    
    def get_kidney_friendly(self, threshold: float = 50) -> List[Dict]:
        """
        Get kidney-friendly products (low oxalate).
        
        Args:
            threshold: Oxalate threshold (mg/100g)
        
        Returns:
            List of low-oxalate products
        """
        return self.filter_by_oxalate_level(0, threshold)
    
    def get_high_calcium(self, threshold: float = 50) -> List[Dict]:
        """
        Get products high in calcium.
        
        Args:
            threshold: Minimum calcium (mg/100g)
        
        Returns:
            List of high-calcium products
        """
        return [p for p in self.products
                if p.get('nutrients', {}).get('calcium_mg', 0) >= threshold]
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        if not self.products:
            return {}
        
        oxalate_values = [p.get('oxalate_mg_per_100g', 0) for p in self.products]
        calcium_values = [p.get('nutrients', {}).get('calcium_mg', 0) for p in self.products]
        
        return {
            'total_products': len(self.products),
            'categories': len(self.products_by_category),
            'oxalate_avg': round(sum(oxalate_values) / len(oxalate_values), 2),
            'oxalate_min': round(min(oxalate_values), 2),
            'oxalate_max': round(max(oxalate_values), 2),
            'calcium_avg': round(sum(calcium_values) / len(calcium_values), 2),
            'categories_list': self.get_categories()
        }
    
    def add_product(self, product: Dict) -> bool:
        """
        Add a new product to the database.
        
        Args:
            product: Product dictionary to add
        
        Returns:
            True if successful, False if product already exists
        """
        product_id = product.get('id')
        
        if product_id in self.products_by_id:
            return False
        
        self.products.append(product)
        self.products_by_id[product_id] = product
        
        category = product.get('category')
        if category not in self.products_by_category:
            self.products_by_category[category] = []
        self.products_by_category[category].append(product)
        
        return True
    
    def export_to_json(self, output_path: str):
        """
        Export database to JSON file.
        
        Args:
            output_path: Path to write database
        """
        data = {
            'products': self.products,
            'metadata': {
                'total_products': len(self.products),
                'categories': len(self.products_by_category)
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_product_with_alternatives(self, product_id: str) -> Dict:
        """
        Get a product with lower-oxalate alternatives in same category.
        
        Args:
            product_id: Product to find alternatives for
        
        Returns:
            Dictionary with product and alternatives
        """
        product = self.get_product(product_id)
        if not product:
            return {}
        
        category = product.get('category')
        alternatives = [p for p in self.get_by_category(category)
                       if p['oxalate_mg_per_100g'] < product['oxalate_mg_per_100g']]
        
        # Sort by oxalate content (lowest first)
        alternatives.sort(key=lambda x: x['oxalate_mg_per_100g'])
        
        return {
            'product': product,
            'alternatives': alternatives[:5]  # Return top 5 alternatives
        }
