"""
Stone Cold Tracker - Tag Generator
Generates creative, varied hashtags based on health scores and product benefits.
"""

import json
import random
from typing import Dict, List, Set
from datetime import datetime


class TagGenerator:
    """Generates creative Instagram hashtags based on scoring and product data."""
    
    def __init__(self, templates_path: str = "models/tag_templates.json"):
        """
        Initialize tag generator with templates.
        
        Args:
            templates_path: Path to tag templates JSON file
        """
        self.templates = self._load_templates(templates_path)
        self.used_combinations = set()
    
    @staticmethod
    def _load_templates(templates_path: str) -> Dict:
        """Load tag templates from JSON file."""
        try:
            with open(templates_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Tag templates not found: {templates_path}")
    
    def generate_tags(
        self,
        health_score: float,
        product: Dict,
        count: int = 7
    ) -> Dict:
        """
        Generate hashtags for a product.
        
        Args:
            health_score: Product health score (0-100)
            product: Product data dictionary
            count: Number of tags to generate (5-10)
        
        Returns:
            Dictionary with tags and diversity score
        """
        count = max(5, min(10, count))  # Constrain to 5-10 tags
        tags = set()
        
        # Determine category
        category = self._get_category_name(health_score)
        
        # Add category-specific tags
        category_tags = self.templates['category_tags'].get(category, [])
        if category_tags:
            tags.add(random.choice(category_tags))
        
        # Add benefit-based tags
        benefit_tags = self._get_benefit_tags(product)
        if benefit_tags:
            tags.add(random.choice(benefit_tags))
        
        # Add seasonal tags
        season = self._get_current_season()
        seasonal_tags = self.templates['seasonal_tags'].get(season, [])
        if seasonal_tags:
            tags.add(random.choice(seasonal_tags))
        
        # Add trending health tags
        trending = self.templates['trending_health_tags'].get('2026_trending', [])
        if trending:
            tags.add(random.choice(trending))
        
        # Fill remaining count with additional category tags
        remaining = count - len(tags)
        if remaining > 0 and category_tags:
            additional = random.sample(
                [t for t in category_tags if t not in tags],
                min(remaining, len(category_tags))
            )
            tags.update(additional)
        
        # Convert to sorted list for consistency
        tags_list = sorted(list(tags))[:count]
        
        # Calculate diversity score
        diversity_score = self._calculate_diversity(tags_list)
        
        return {
            'tags': tags_list,
            'count': len(tags_list),
            'diversity_score': round(diversity_score, 2),
            'category': category
        }
    
    def _get_category_name(self, health_score: float) -> str:
        """Map health score to tag category."""
        if health_score >= 95:
            return 'excellent'
        elif health_score >= 85:
            return 'great'
        elif health_score >= 70:
            return 'good'
        elif health_score >= 50:
            return 'fair'
        elif health_score >= 25:
            return 'poor'
        else:
            return 'terrible'
    
    def _get_benefit_tags(self, product: Dict) -> List[str]:
        """
        Extract benefit-based tags from product nutrients.
        
        Args:
            product: Product data dictionary
        
        Returns:
            List of relevant benefit tags
        """
        benefit_tags = []
        nutrients = product.get('nutrients', {})
        
        # High fiber
        if nutrients.get('fiber_g', 0) > 2.5:
            benefit_tags.extend(self.templates['benefit_tags'].get('high_fiber', []))
        
        # High calcium
        if nutrients.get('calcium_mg', 0) > 50:
            benefit_tags.extend(self.templates['benefit_tags'].get('high_calcium', []))
        
        # High protein
        if nutrients.get('protein_g', 0) > 3:
            benefit_tags.extend(self.templates['benefit_tags'].get('high_protein', []))
        
        # High magnesium
        if nutrients.get('magnesium_mg', 0) > 20:
            benefit_tags.extend(self.templates['benefit_tags'].get('high_magnesium', []))
        
        # High potassium
        if nutrients.get('potassium_mg', 0) > 200:
            benefit_tags.extend(self.templates['benefit_tags'].get('high_potassium', []))
        
        # Antioxidant (if has vitamin C)
        if nutrients.get('vitamin_c_mg', 0) > 10:
            benefit_tags.extend(self.templates['benefit_tags'].get('antioxidant', []))
        
        # Low calorie (approximate)
        if nutrients.get('calories', 0) < 50:  # Most veggies are low cal
            benefit_tags.extend(self.templates['benefit_tags'].get('low_calorie', []))
        
        return benefit_tags
    
    @staticmethod
    def _get_current_season() -> str:
        """Get current season for seasonal tags."""
        month = datetime.now().month
        
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'fall'
        else:
            return 'winter'
    
    @staticmethod
    def _calculate_diversity(tags: List[str]) -> float:
        """
        Calculate diversity score based on tag variety.
        
        Args:
            tags: List of tags
        
        Returns:
            Diversity score 0-1
        """
        if not tags or len(tags) < 2:
            return 0.0
        
        # Diversity = unique prefixes / total tags
        prefixes = set()
        for tag in tags:
            # Extract prefix (first meaningful part before number/qualifier)
            prefix = tag.split('#')[1].rstrip('0123456789') if '#' in tag else tag
            prefixes.add(prefix[:3])  # Use first 3 chars as prefix
        
        return len(prefixes) / len(tags)
    
    def generate_hashtag_string(
        self,
        health_score: float,
        product: Dict,
        count: int = 7
    ) -> str:
        """
        Generate hashtags as a formatted string for Instagram.
        
        Args:
            health_score: Product health score
            product: Product data dictionary
            count: Number of tags to generate
        
        Returns:
            Space-separated hashtag string
        """
        result = self.generate_tags(health_score, product, count)
        return ' '.join(result['tags'])
    
    def get_trending_tags(self, count: int = 5) -> List[str]:
        """
        Get current trending health tags.
        
        Args:
            count: Number of trending tags to return
        
        Returns:
            List of trending tags
        """
        trending = self.templates['trending_health_tags'].get('2026_trending', [])
        return random.sample(trending, min(count, len(trending)))
    
    def get_category_tags(self, score: float, count: int = 3) -> List[str]:
        """
        Get tags for a specific score category.
        
        Args:
            score: Health score (0-100)
            count: Number of tags to return
        
        Returns:
            List of category tags
        """
        category = self._get_category_name(score)
        tags = self.templates['category_tags'].get(category, [])
        return random.sample(tags, min(count, len(tags)))


def generate_tags(health_score: float, product: Dict) -> Dict:
    """
    Convenience function to generate tags.
    
    Args:
        health_score: Product health score
        product: Product data dictionary
    
    Returns:
        Tags result dictionary
    """
    generator = TagGenerator()
    return generator.generate_tags(health_score, product)
