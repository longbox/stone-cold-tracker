"""
Stone Cold Tracker - Unit Tests
Comprehensive test suite for health scoring, tagging, and caption generation.
"""

import pytest
import json
from pathlib import Path

from agent.health_scorer import HealthScorer
from agent.tag_generator import TagGenerator
from agent.caption_generator import CaptionGenerator
from agent.database_manager import DatabaseManager


class TestHealthScorer:
    """Test suite for health scoring engine."""
    
    @pytest.fixture
    def scorer(self):
        """Create a health scorer instance."""
        return HealthScorer()
    
    @pytest.fixture
    def sample_product(self):
        """Sample product for testing."""
        return {
            'id': 'test_product',
            'name': 'Test Product',
            'oxalate_mg_per_100g': 50,
            'oxalate_type': 'mixed',
            'bioavailability': 0.4,
            'confidence_score': 0.9,
            'nutrients': {
                'calcium_mg': 60,
                'magnesium_mg': 25,
                'potassium_mg': 300,
                'vitamin_c_mg': 15,
                'fiber_g': 2.5
            }
        }
    
    def test_oxalate_factor_calculation(self, scorer):
        """Test oxalate factor calculation."""
        # Test no oxalate
        assert scorer._calculate_oxalate_factor(15) == 1.0
        
        # Test low oxalate
        assert scorer._calculate_oxalate_factor(30) == 0.7
        
        # Test moderate oxalate
        assert scorer._calculate_oxalate_factor(75) == 0.4
        
        # Test high oxalate
        assert scorer._calculate_oxalate_factor(150) == 0.2
        
        # Test extreme oxalate
        assert scorer._calculate_oxalate_factor(300) == 0.0
    
    def test_nutrient_factor_calculation(self, scorer):
        """Test nutrient factor calculation."""
        nutrients = {
            'calcium_mg': 60,
            'fiber_g': 3.5,
            'vitamin_c_mg': 50
        }
        factor = scorer._calculate_nutrient_factor(nutrients)
        assert 0 <= factor <= 1.0
        assert factor > 0  # Should have positive score
    
    def test_bioavailability_factor_calculation(self, scorer):
        """Test bioavailability factor calculation."""
        product = {
            'nutrients': {'calcium_mg': 100, 'magnesium_mg': 20},
            'oxalate_type': 'insoluble',
            'bioavailability': 0.2
        }
        factor = scorer._calculate_bioavailability_factor(product)
        assert 0 <= factor <= 1.0
    
    def test_health_score_calculation(self, scorer, sample_product):
        """Test complete health score calculation."""
        result = scorer.calculate_health_score(sample_product)
        
        assert 'health_score' in result
        assert 0 <= result['health_score'] <= 100
        assert 'category' in result
        assert result['category'] in ['Excellent', 'Great', 'Good', 'Fair', 'Poor', 'Terrible']
        assert 'factors' in result
        assert 'flags' in result
        assert 'recommendations' in result
    
    def test_rating_categories(self, scorer):
        """Test rating category mapping."""
        assert scorer._get_rating_category(98)['category'] == 'Excellent'
        assert scorer._get_rating_category(90)['category'] == 'Great'
        assert scorer._get_rating_category(75)['category'] == 'Good'
        assert scorer._get_rating_category(60)['category'] == 'Fair'
        assert scorer._get_rating_category(35)['category'] == 'Poor'
        assert scorer._get_rating_category(10)['category'] == 'Terrible'
    
    def test_flag_generation(self, scorer, sample_product):
        """Test risk flag generation."""
        # High oxalate product
        high_oxalate_product = sample_product.copy()
        high_oxalate_product['oxalate_mg_per_100g'] = 150
        
        flags = scorer._generate_flags(high_oxalate_product, 50)
        assert len(flags) > 0
        assert any('HIGH_OXALATE' in flag for flag in flags)


class TestTagGenerator:
    """Test suite for tag generator."""
    
    @pytest.fixture
    def tag_generator(self):
        """Create a tag generator instance."""
        return TagGenerator()
    
    @pytest.fixture
    def sample_product(self):
        """Sample product for testing."""
        return {
            'id': 'test_product',
            'name': 'Test Vegetable',
            'category': 'vegetables',
            'oxalate_mg_per_100g': 25,
            'nutrients': {
                'fiber_g': 3.0,
                'calcium_mg': 60,
                'vitamin_c_mg': 20,
                'potassium_mg': 250
            }
        }
    
    def test_tag_generation(self, tag_generator, sample_product):
        """Test tag generation for a product."""
        result = tag_generator.generate_tags(85, sample_product, 7)
        
        assert 'tags' in result
        assert 'count' in result
        assert 'diversity_score' in result
        assert 5 <= result['count'] <= 10
        assert 0 <= result['diversity_score'] <= 1
    
    def test_category_name_mapping(self, tag_generator):
        """Test health score to category mapping."""
        assert tag_generator._get_category_name(98) == 'excellent'
        assert tag_generator._get_category_name(90) == 'great'
        assert tag_generator._get_category_name(75) == 'good'
        assert tag_generator._get_category_name(60) == 'fair'
        assert tag_generator._get_category_name(35) == 'poor'
        assert tag_generator._get_category_name(10) == 'terrible'
    
    def test_benefit_tags_extraction(self, tag_generator, sample_product):
        """Test benefit tag extraction from nutrients."""
        benefit_tags = tag_generator._get_benefit_tags(sample_product)
        
        assert len(benefit_tags) > 0
        # Should include high fiber and calcium tags
        assert any('Fiber' in tag or 'fiber' in tag for tag in benefit_tags)
    
    def test_hashtag_string_generation(self, tag_generator, sample_product):
        """Test hashtag string generation."""
        hashtags = tag_generator.generate_hashtag_string(85, sample_product)
        
        assert isinstance(hashtags, str)
        assert hashtags.startswith('#')
        assert hashtags.count('#') >= 5


class TestCaptionGenerator:
    """Test suite for caption generator."""
    
    @pytest.fixture
    def caption_generator(self):
        """Create a caption generator instance."""
        return CaptionGenerator()
    
    @pytest.fixture
    def sample_product(self):
        """Sample product for testing."""
        return {
            'id': 'test_product',
            'name': 'Broccoli',
            'oxalate_mg_per_100g': 18,
            'nutrients': {
                'calcium_mg': 89,
                'fiber_g': 2.4,
                'vitamin_c_mg': 89
            }
        }
    
    def test_caption_generation(self, caption_generator, sample_product):
        """Test caption generation."""
        tags = ['#LowOxalate', '#KidneyFriendly', '#Healthy']
        result = caption_generator.generate_caption(
            sample_product,
            85,
            tags
        )
        
        assert 'caption' in result
        assert 'character_count' in result
        assert 'within_instagram_limit' in result
        assert result['within_instagram_limit'] is True
        assert len(result['caption']) > 0
    
    def test_caption_validation(self, caption_generator):
        """Test caption validation."""
        caption = "This is a great food! #Healthy #LowOxalate\n\nDISCLAIMER: This is for info purposes only."
        
        validation = caption_generator.validate_caption(caption)
        
        assert 'valid' in validation
        assert 'character_count' in validation
        assert 'hashtag_count' in validation
        assert 'issues' in validation
        assert 'warnings' in validation
    
    def test_short_caption_generation(self, caption_generator):
        """Test short caption generation for stories."""
        short_caption = caption_generator.generate_short_caption(85, "Broccoli")
        
        assert isinstance(short_caption, str)
        assert len(short_caption) > 0
    
    def test_disclaimer_inclusion(self, caption_generator, sample_product):
        """Test that disclaimer is included when requested."""
        tags = ['#Test']
        
        # With disclaimer
        result_with = caption_generator.generate_caption(
            sample_product,
            85,
            tags,
            include_disclaimer=True
        )
        assert 'DISCLAIMER' in result_with['caption']
        
        # Without disclaimer
        result_without = caption_generator.generate_caption(
            sample_product,
            85,
            tags,
            include_disclaimer=False
        )
        assert 'DISCLAIMER' not in result_without['caption']


class TestDatabaseManager:
    """Test suite for database manager."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a database manager instance."""
        return DatabaseManager()
    
    def test_database_loading(self, db_manager):
        """Test database loads correctly."""
        assert len(db_manager.products) > 0
        assert len(db_manager.products_by_id) > 0
    
    def test_product_retrieval(self, db_manager):
        """Test product retrieval by ID."""
        # Use first product in database
        if db_manager.products:
            product_id = db_manager.products[0]['id']
            product = db_manager.get_product(product_id)
            
            assert product is not None
            assert product['id'] == product_id
    
    def test_product_search(self, db_manager):
        """Test product search functionality."""
        results = db_manager.search_products('broccoli')
        
        assert isinstance(results, list)
        if results:
            assert any('broccoli' in p['name'].lower() for p in results)
    
    def test_category_filtering(self, db_manager):
        """Test filtering by category."""
        categories = db_manager.get_categories()
        
        assert len(categories) > 0
        
        if categories:
            category = categories[0]
            products = db_manager.get_by_category(category)
            assert len(products) > 0
    
    def test_oxalate_filtering(self, db_manager):
        """Test filtering by oxalate content."""
        low_oxalate = db_manager.filter_by_oxalate_level(0, 20)
        
        assert isinstance(low_oxalate, list)
        assert all(p['oxalate_mg_per_100g'] <= 20 for p in low_oxalate)
    
    def test_statistics(self, db_manager):
        """Test database statistics."""
        stats = db_manager.get_statistics()
        
        assert 'total_products' in stats
        assert 'categories' in stats
        assert stats['total_products'] > 0


class TestIntegration:
    """Integration tests for complete pipeline."""
    
    def test_complete_analysis_flow(self):
        """Test complete analysis workflow."""
        scorer = HealthScorer()
        tag_gen = TagGenerator()
        caption_gen = CaptionGenerator()
        db = DatabaseManager()
        
        # Get a product
        if not db.products:
            pytest.skip("No products in database")
        
        product = db.products[0]
        
        # Score it
        score = scorer.calculate_health_score(product)
        assert score['health_score'] > 0
        
        # Generate tags
        tags = tag_gen.generate_tags(score['health_score'], product)
        assert tags['count'] > 0
        
        # Generate caption
        caption = caption_gen.generate_caption(
            product,
            score['health_score'],
            tags['tags']
        )
        assert len(caption['caption']) > 0
    
    def test_alternatives_workflow(self):
        """Test finding alternatives workflow."""
        db = DatabaseManager()
        
        if not db.products:
            pytest.skip("No products in database")
        
        product = db.products[0]
        product_id = product['id']
        
        # Get alternatives
        alts = db.get_product_with_alternatives(product_id)
        
        assert 'product' in alts
        assert 'alternatives' in alts


# Fixtures for common test data
@pytest.fixture(scope="session")
def test_config():
    """Load test configuration."""
    config_path = Path("models/score_thresholds.json")
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return None


from unittest.mock import MagicMock

class TestMealDecomposer:
    """Test suite for Meal Decomposer."""
    
    def test_meal_decomposition(self):
        from agent.meal_decomposer import MealDecomposer
        decomposer = MealDecomposer()
        result = decomposer.decompose_meal("I had a mixed salad for lunch")
        assert result["matched"] is True
        assert result["meal_type"] == "salad"
        assert len(result["common_ingredients"]) > 0
        
    def test_unknown_meal_decomposition(self):
        from agent.meal_decomposer import MealDecomposer
        decomposer = MealDecomposer()
        result = decomposer.decompose_meal("I ate lasagna")
        assert result["matched"] is False
        assert len(result["options"]) > 0

    def test_calculate_composite_score(self):
        from agent.meal_decomposer import MealDecomposer
        from agent.database_manager import DatabaseManager
        from agent.health_scorer import HealthScorer
        
        decomposer = MealDecomposer()
        db = DatabaseManager()
        scorer = HealthScorer()
        
        # 50% spinach (656 mg) and 50% broccoli (18 mg) -> average ~ 337 mg
        components = {
            "spinach_fresh_raw": 50,
            "broccoli_fresh_raw": 50
        }
        
        result = decomposer.calculate_composite_score(components, db, scorer)
        
        assert "score" in result
        assert "product" in result
        assert "components_breakdown" in result
        
        virtual_product = result["product"]
        assert virtual_product["oxalate_mg_per_100g"] == round((656 + 18) / 2, 2)
        assert virtual_product["nutrients"]["calcium_mg"] == round((99 + 89) / 2, 2)
        assert result["score"]["health_score"] > 0
        assert result["score"]["health_score"] < 90  # Spinach drags it down


class TestLabelAnalysisIntegration:
    """Test suite for nutrition label image pipeline."""
    
    def test_analyze_label_image(self, monkeypatch):
        from agent.analysis_pipeline import AnalysisPipeline
        pipeline = AnalysisPipeline()
        
        # Mock analyze_nutrition_and_ingredients to avoid calling OpenAI API
        mock_response = {
            "success": True,
            "product_name": "Mega Greens Powder",
            "ingredients": ["spinach", "broccoli"],
            "nutrients": {
                "calories": 45,
                "protein_g": 3.0,
                "fiber_g": 4.5,
                "calcium_mg": 120,
                "magnesium_mg": 80,
                "potassium_mg": 400,
                "vitamin_c_mg": 60,
                "oxalate_mg_per_100g": 150
            },
            "overall_confidence": "high",
            "notes": "Rich in minerals"
        }
        
        monkeypatch.setattr(
            pipeline.image_processor, 
            "analyze_nutrition_and_ingredients", 
            MagicMock(return_value=mock_response)
        )
        
        result = pipeline.analyze_label_image("path/to/fake_label.jpg")
        
        assert result["success"] is True
        assert result["product_name"] == "Mega Greens Powder"
        assert result["product"]["oxalate_mg_per_100g"] == 150
        assert result["score"]["health_score"] > 0
        assert len(result["tags"]["tags"]) > 0
        assert "DISCLAIMER" in result["caption"]["caption"]

