"""
Stone Cold Tracker - Image Processor
Handles image recognition and ingredient identification using OpenAI Vision API.
"""

import json
import base64
from typing import Dict, List, Optional
from pathlib import Path
import os


class ImageProcessor:
    """
    Processes food images and identifies ingredients using OpenAI Vision API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize image processor with OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided or set in environment")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package required: pip install openai>=1.0.0")
    
    def analyze_image(self, image_source: str) -> Dict:
        """
        Analyze a food image and identify ingredients.
        
        Args:
            image_source: Image file path or URL
        
        Returns:
            Dictionary with identified ingredients and confidence scores
        """
        try:
            # Prepare image
            image_data = self._prepare_image(image_source)
            
            # Call OpenAI Vision API
            response = self.client.messages.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "image": image_data
                            },
                            {
                                "type": "text",
                                "text": self._get_analysis_prompt()
                            }
                        ]
                    }
                ],
                max_tokens=1024
            )
            
            # Parse response
            return self._parse_vision_response(response)
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'ingredients': [],
                'confidence': 0
            }
    
    def _prepare_image(self, image_source: str) -> Dict:
        """
        Prepare image for API call (supports file path or URL).
        
        Args:
            image_source: Image file path or URL
        
        Returns:
            Image data dictionary for API
        """
        # Check if it's a URL
        if image_source.startswith(('http://', 'https://')):
            return {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": image_source
                }
            }
        
        # Handle local file
        image_path = Path(image_source)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_source}")
        
        # Encode image to base64
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')
        
        # Determine media type
        suffix = image_path.suffix.lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(suffix, 'image/jpeg')
        
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data
            }
        }
    
    @staticmethod
    def _get_analysis_prompt() -> str:
        """Get the prompt for analyzing food images."""
        return """Analyze this food image and identify the main ingredients visible. 
For each ingredient identified, provide:
1. Ingredient name
2. Estimated portion size or quantity visible
3. Confidence level (high/medium/low)
4. Any preparation method visible (raw, cooked, roasted, etc.)

Format your response as JSON with the following structure:
{
    "dish_name": "name of the dish or food item",
    "main_ingredients": [
        {
            "name": "ingredient name",
            "quantity": "estimated amount",
            "preparation": "raw/cooked/etc",
            "confidence": "high/medium/low"
        }
    ],
    "overall_confidence": "high/medium/low",
    "notes": "any additional observations"
}"""
    
    @staticmethod
    def _parse_vision_response(response) -> Dict:
        """Parse OpenAI Vision API response."""
        try:
            # Extract text from response
            response_text = response.choices[0].message.content
            
            # Try to parse JSON from response
            import json
            
            # Find JSON in response (it might have other text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                
                return {
                    'success': True,
                    'dish_name': data.get('dish_name', 'Unknown'),
                    'ingredients': data.get('main_ingredients', []),
                    'confidence': data.get('overall_confidence', 'medium'),
                    'notes': data.get('notes', '')
                }
        
        except (json.JSONDecodeError, AttributeError, IndexError):
            pass
        
        return {
            'success': False,
            'error': 'Failed to parse response',
            'ingredients': [],
            'confidence': 'low'
        }
    
    def identify_from_ingredients(
        self,
        ingredients: List[str],
        database_manager=None
    ) -> Dict:
        """
        Map ingredients to products in database.
        
        Args:
            ingredients: List of ingredient strings
            database_manager: DatabaseManager instance for lookup
        
        Returns:
            Dictionary with mapped products and oxalate content
        """
        if not database_manager:
            return {'success': False, 'error': 'Database manager required'}
        
        results = {
            'ingredients': ingredients,
            'matched_products': [],
            'unmatched': [],
            'total_oxalate_estimate': 0,
            'risk_level': 'unknown'
        }
        
        for ingredient in ingredients:
            # Search for ingredient in database
            matches = database_manager.search_products(ingredient)
            
            if matches:
                best_match = matches[0]
                results['matched_products'].append({
                    'ingredient': ingredient,
                    'matched_product': best_match['name'],
                    'product_id': best_match['id'],
                    'oxalate_mg_per_100g': best_match['oxalate_mg_per_100g']
                })
                results['total_oxalate_estimate'] += best_match['oxalate_mg_per_100g']
            else:
                results['unmatched'].append(ingredient)
        
        # Determine risk level
        avg_oxalate = (results['total_oxalate_estimate'] / 
                      len(results['matched_products']) 
                      if results['matched_products'] else 0)
        
        if avg_oxalate > 200:
            results['risk_level'] = 'extreme'
        elif avg_oxalate > 100:
            results['risk_level'] = 'high'
        elif avg_oxalate > 50:
            results['risk_level'] = 'moderate'
        elif avg_oxalate > 20:
            results['risk_level'] = 'low'
        else:
            results['risk_level'] = 'minimal'
        
        results['average_oxalate'] = round(avg_oxalate, 2)
        
        return results
    
    def process_image_full_pipeline(
        self,
        image_source: str,
        database_manager=None,
        health_scorer=None
    ) -> Dict:
        """
        Complete pipeline: analyze image → identify ingredients → score product.
        
        Args:
            image_source: Image file path or URL
            database_manager: DatabaseManager instance
            health_scorer: HealthScorer instance
        
        Returns:
            Complete analysis with scoring
        """
        # Step 1: Analyze image
        image_analysis = self.analyze_image(image_source)
        
        if not image_analysis.get('success'):
            return {
                'success': False,
                'error': image_analysis.get('error', 'Image analysis failed'),
                'image_analysis': image_analysis
            }
        
        # Step 2: Map to database products
        ingredients = [ing.get('name') for ing in image_analysis.get('ingredients', [])]
        ingredient_mapping = self.identify_from_ingredients(
            ingredients,
            database_manager
        )
        
        result = {
            'success': True,
            'dish_name': image_analysis.get('dish_name'),
            'image_analysis': image_analysis,
            'ingredient_mapping': ingredient_mapping,
            'scores': []
        }
        
        # Step 3: Score each matched product if scorer provided
        if health_scorer:
            for matched in ingredient_mapping.get('matched_products', []):
                product_id = matched['product_id']
                if database_manager:
                    product = database_manager.get_product(product_id)
                    if product:
                        score = health_scorer.calculate_health_score(product)
                        result['scores'].append(score)
        
        return result


def analyze_food_image(image_source: str) -> Dict:
    """
    Convenience function to analyze a food image.
    
    Args:
        image_source: Image file path or URL
    
    Returns:
        Analysis result dictionary
    """
    processor = ImageProcessor()
    return processor.analyze_image(image_source)
