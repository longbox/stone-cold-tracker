"""
Stone Cold Tracker - Main Analysis Pipeline
Orchestrates the complete analysis workflow: image → scoring → tags → caption.
"""

import json
from typing import Dict, Optional
from pathlib import Path

from agent.database_manager import DatabaseManager
from agent.health_scorer import HealthScorer
from agent.tag_generator import TagGenerator
from agent.caption_generator import CaptionGenerator
from agent.image_processor import ImageProcessor


class AnalysisPipeline:
    """
    Main orchestrator for the complete Stone Cold Tracker analysis pipeline.
    """
    
    def __init__(self):
        """Initialize all pipeline components."""
        self.db_manager = DatabaseManager()
        self.health_scorer = HealthScorer()
        self.tag_generator = TagGenerator()
        self.caption_generator = CaptionGenerator()
        self.image_processor = ImageProcessor()
    
    def analyze_product(
        self,
        product_id: str,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze a product by ID.
        
        Args:
            product_id: Product identifier
            user_context: Optional user context for personalization
        
        Returns:
            Complete analysis result
        """
        # Get product from database
        product = self.db_manager.get_product(product_id)
        
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        # Calculate health score
        score_result = self.health_scorer.calculate_health_score(product, user_context)
        health_score = score_result['health_score']
        
        # Generate tags
        tags_result = self.tag_generator.generate_tags(health_score, product)
        
        # Generate caption
        caption_result = self.caption_generator.generate_caption(
            product,
            health_score,
            tags_result['tags']
        )
        
        return {
            'product': product,
            'score': score_result,
            'tags': tags_result,
            'caption': caption_result,
            'pipeline_status': 'success'
        }
    
    def analyze_from_image(
        self,
        image_source: str,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze a food image through the complete pipeline.
        
        Args:
            image_source: Image file path or URL
            user_context: Optional user context
        
        Returns:
            Complete analysis result
        """
        # Step 1: Analyze image and extract ingredients
        image_result = self.image_processor.process_image_full_pipeline(
            image_source,
            self.db_manager,
            self.health_scorer
        )
        
        if not image_result.get('success'):
            return {
                'success': False,
                'error': image_result.get('error'),
                'pipeline_status': 'image_analysis_failed'
            }
        
        # Step 2: Map ingredients to products
        ingredients = [ing.get('name') for ing in 
                      image_result['image_analysis'].get('ingredients', [])]
        ingredient_mapping = self.image_processor.identify_from_ingredients(
            ingredients,
            self.db_manager
        )
        
        # Step 3: Score matched products and generate content
        analyses = []
        for matched in ingredient_mapping.get('matched_products', []):
            product_id = matched['product_id']
            product = self.db_manager.get_product(product_id)
            
            if product:
                analysis = self.analyze_product(product_id, user_context)
                analyses.append(analysis)
        
        return {
            'success': True,
            'dish_name': image_result.get('dish_name'),
            'image_analysis': image_result['image_analysis'],
            'ingredient_mapping': ingredient_mapping,
            'product_analyses': analyses,
            'pipeline_status': 'success'
        }
    
    def batch_analyze(
        self,
        product_ids: list,
        user_context: Optional[Dict] = None
    ) -> list:
        """
        Analyze multiple products at once.
        
        Args:
            product_ids: List of product IDs to analyze
            user_context: Optional user context
        
        Returns:
            List of analysis results
        """
        results = []
        
        for product_id in product_ids:
            try:
                result = self.analyze_product(product_id, user_context)
                results.append(result)
            except Exception as e:
                results.append({
                    'product_id': product_id,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def find_alternatives(
        self,
        product_id: str,
        lower_oxalate_only: bool = True
    ) -> Dict:
        """
        Find alternative products for a given product.
        
        Args:
            product_id: Product to find alternatives for
            lower_oxalate_only: Only show lower-oxalate alternatives
        
        Returns:
            Dictionary with product and alternatives with scoring
        """
        product = self.db_manager.get_product(product_id)
        
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        # Get alternatives
        alts = self.db_manager.get_product_with_alternatives(product_id)
        
        # Score the main product
        main_score = self.health_scorer.calculate_health_score(product)
        
        # Score alternatives
        alternatives_with_scores = []
        for alt in alts.get('alternatives', []):
            alt_score = self.health_scorer.calculate_health_score(alt)
            alternatives_with_scores.append({
                'product': alt,
                'score': alt_score
            })
        
        # Sort by health score (best first)
        alternatives_with_scores.sort(key=lambda x: x['score']['health_score'], reverse=True)
        
        return {
            'original_product': {
                'product': product,
                'score': main_score
            },
            'alternatives': alternatives_with_scores
        }
    
    def generate_content_series(
        self,
        category: str,
        count: int = 5
    ) -> list:
        """
        Generate content series for products in a category.
        
        Args:
            category: Product category
            count: Number of products to analyze
        
        Returns:
            List of analyses ready for posting
        """
        products = self.db_manager.get_by_category(category)
        
        if not products:
            raise ValueError(f"No products found in category: {category}")
        
        # Take subset
        products = products[:count]
        product_ids = [p['id'] for p in products]
        
        return self.batch_analyze(product_ids)
    
    def export_analysis(
        self,
        analysis: Dict,
        output_path: str,
        format: str = 'json'
    ) -> bool:
        """
        Export analysis result to file.
        
        Args:
            analysis: Analysis dictionary to export
            output_path: Path to write file
            format: Output format ('json' or 'markdown')
        
        Returns:
            True if successful
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'json':
                with open(output_file, 'w') as f:
                    json.dump(analysis, f, indent=2)
            
            elif format == 'markdown':
                md_content = self._analysis_to_markdown(analysis)
                with open(output_file, 'w') as f:
                    f.write(md_content)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return True
        
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    @staticmethod
    def _analysis_to_markdown(analysis: Dict) -> str:
        """Convert analysis to markdown format."""
        md = f"# Product Analysis\n\n"
        
        product = analysis.get('product', {})
        score = analysis.get('score', {})
        
        md += f"## {product.get('name', 'Unknown')}\n\n"
        md += f"**Health Score:** {score.get('health_score', 'N/A')}/100 {score.get('emoji', '')}\n\n"
        md += f"**Category:** {score.get('category', 'Unknown')}\n"
        md += f"**Frequency:** {score.get('frequency', 'N/A')}\n\n"
        
        md += "### Oxalate Content\n"
        md += f"- **Per 100g:** {product.get('oxalate_mg_per_100g', 'N/A')}mg\n"
        md += f"- **Type:** {product.get('oxalate_type', 'Unknown')}\n\n"
        
        md += "### Nutritional Highlights\n"
        nutrients = product.get('nutrients', {})
        for nutrient, value in nutrients.items():
            md += f"- {nutrient.replace('_', ' ').title()}: {value}\n"
        
        md += "\n### Recommendations\n"
        for rec in score.get('recommendations', []):
            md += f"- {rec}\n"
        
        caption = analysis.get('caption', {})
        md += f"\n### Instagram Caption\n\n{caption.get('caption', '')}\n"
        
        return md


def create_pipeline() -> AnalysisPipeline:
    """Create and return an AnalysisPipeline instance."""
    return AnalysisPipeline()
