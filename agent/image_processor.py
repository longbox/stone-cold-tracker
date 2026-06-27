"""
Stone Cold Tracker - Image Processor
Handles image recognition and ingredient/nutrition identification using OpenAI Vision API.
"""

import json
import base64
from typing import Dict, List, Optional, Any
from pathlib import Path
import os


class ImageProcessor:
    """
    Processes food images and product labels using OpenAI Vision API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize image processor with OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        # We allow running without an API key to support offline fallback modes in tests
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("OpenAI package required: pip install openai>=1.0.0")
        else:
            self.client = None
    
    def _prepare_image_url_or_base64(self, image_source: str) -> str:
        """
        Prepare image for API call (returns a URL or data URL string).
        
        Args:
            image_source: Image file path or URL
        
        Returns:
            URL or base64 data URL string for OpenAI Vision API
        """
        if image_source.startswith(('http://', 'https://')):
            return image_source
        
        image_path = Path(image_source)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_source}")
        
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')
        
        suffix = image_path.suffix.lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(suffix, 'image/jpeg')
        
        return f"data:{media_type};base64,{image_data}"
    
    def analyze_image(self, image_source: str) -> Dict:
        """
        Analyze a food image and identify ingredients.
        
        Args:
            image_source: Image file path or URL
        
        Returns:
            Dictionary with identified ingredients and confidence scores
        """
        if not self.api_key or not self.client:
            return {
                'success': False,
                'error': 'OpenAI API key not configured',
                'ingredients': [],
                'confidence': 'low'
            }
            
        try:
            image_url = self._prepare_image_url_or_base64(image_source)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
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
            
            return self._parse_vision_response(response)
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'ingredients': [],
                'confidence': 'low'
            }
            
    def analyze_nutrition_and_ingredients(self, image_source: str) -> Dict:
        """
        Analyze a product label/packaging image to extract ingredients list and nutrition facts.
        
        Args:
            image_source: Image file path or URL
            
        Returns:
            Dictionary with extracted product name, ingredients, and nutrients
        """
        if not self.api_key or not self.client:
            return {
                'success': False,
                'error': 'OpenAI API key not configured',
                'ingredients': [],
                'nutrients': {}
            }
            
        try:
            image_url = self._prepare_image_url_or_base64(image_source)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            },
                            {
                                "type": "text",
                                "text": self._get_nutrition_analysis_prompt()
                            }
                        ]
                    }
                ],
                max_tokens=1024
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Find and parse JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                data = json.loads(response_text[start_idx:end_idx])
                return {
                    'success': True,
                    'product_name': data.get('product_name', 'Unknown Product'),
                    'ingredients': data.get('ingredients', []),
                    'nutrients': {k: v for k, v in data.get('nutrients', {}).items() if v is not None},
                    'confidence': data.get('overall_confidence', 'medium'),
                    'notes': data.get('notes', '')
                }
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'ingredients': [],
                'nutrients': {}
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
    def _get_nutrition_analysis_prompt() -> str:
        """Get the prompt for extracting product label nutrition facts."""
        return """Analyze this image of a product label, food packaging, ingredients list, or nutrition facts table.
Extract the following details if present:
1. The product name or description.
2. List of ingredients (simple names).
3. Detailed nutritional facts (per serving or per 100g):
   - Calories
   - Protein (in grams)
   - Fiber (in grams)
   - Calcium (in mg)
   - Magnesium (in mg)
   - Potassium (in mg)
   - Vitamin C (in mg)
   - Oxalate (in mg, if explicitly mentioned)
   
Format your response as JSON with the following structure:
{
    "product_name": "name of the product or packaging",
    "ingredients": ["ingredient 1", "ingredient 2", ...],
    "nutrients": {
        "calories": value (number or null),
        "protein_g": value (number or null),
        "fiber_g": value (number or null),
        "calcium_mg": value (number or null),
        "magnesium_mg": value (number or null),
        "potassium_mg": value (number or null),
        "vitamin_c_mg": value (number or null),
        "oxalate_mg_per_100g": value (number or null)
    },
    "overall_confidence": "high/medium/low",
    "notes": "any additional observations"
}"""
    
    @staticmethod
    def _parse_vision_response(response) -> Dict:
        """Parse OpenAI Vision API response."""
        try:
            # Extract text from response
            response_text = response.choices[0].message.content
            
            # Find JSON in response
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
