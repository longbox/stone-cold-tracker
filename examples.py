#!/usr/bin/env python
"""
Stone Cold Tracker - Example Usage Script
Demonstrates how to use the complete analysis pipeline.
"""

import json
from agent import create_pipeline
from agent.meal_decomposer import MealDecomposer, COMPOSITE_MEAL_CATALOG


def example_analyze_by_id():
    """Example: Analyze a product by ID."""
    print("=" * 60)
    print("EXAMPLE 1: Analyze Product by ID")
    print("=" * 60)
    
    pipeline = create_pipeline()
    
    try:
        result = pipeline.analyze_product('broccoli_fresh_raw')
        
        print(f"\nProduct: {result['product']['name']}")
        print(f"Health Score: {result['score']['health_score']}/100 {result['score']['emoji']}")
        print(f"Category: {result['score']['category']}")
        print(f"Frequency: {result['score']['frequency']}\n")
        
        print("Tags:", ' '.join(result['tags']['tags']))
        print("\nCaption:")
        print(result['caption']['caption'][:200] + "...\n")
    
    except Exception as e:
        print(f"Error: {e}\n")


def example_find_alternatives():
    """Example: Find alternatives for a product."""
    print("=" * 60)
    print("EXAMPLE 2: Find Alternatives")
    print("=" * 60)
    
    pipeline = create_pipeline()
    
    try:
        result = pipeline.find_alternatives('spinach_fresh_raw')
        
        product = result['original_product']['product']
        score = result['original_product']['score']
        
        print(f"\nOriginal: {product['name']}")
        print(f"Health Score: {score['health_score']}/100 {score['emoji']}")
        print(f"Oxalate: {product['oxalate_mg_per_100g']}mg/100g\n")
        
        print("Better Alternatives:")
        for i, alt in enumerate(result['alternatives'][:3], 1):
            alt_product = alt['product']
            alt_score = alt['score']
            print(f"{i}. {alt_product['name']}")
            print(f"   Score: {alt_score['health_score']}/100 {alt_score['emoji']}")
            print(f"   Oxalate: {alt_product['oxalate_mg_per_100g']}mg/100g\n")
    
    except Exception as e:
        print(f"Error: {e}\n")


def example_generate_series():
    """Example: Generate content series for a category."""
    print("=" * 60)
    print("EXAMPLE 3: Generate Content Series")
    print("=" * 60)
    
    pipeline = create_pipeline()
    
    try:
        results = pipeline.generate_content_series('cruciferous', count=3)
        
        print(f"\nGenerated {len(results)} product analyses:\n")
        
        for i, analysis in enumerate(results, 1):
            if 'product' in analysis:
                product = analysis['product']
                score = analysis['score']
                print(f"{i}. {product['name']}")
                print(f"   Score: {score['health_score']}/100 {score['emoji']}")
                print(f"   Tags: {' '.join(analysis['tags']['tags'][:3])}\n")
    
    except Exception as e:
        print(f"Error: {e}\n")


def example_database_stats():
    """Example: View database statistics."""
    print("=" * 60)
    print("EXAMPLE 4: Database Statistics")
    print("=" * 60)
    
    from agent import DatabaseManager
    
    db = DatabaseManager()
    stats = db.get_statistics()
    
    print(f"\nTotal Products: {stats.get('total_products', 0)}")
    print(f"Categories: {stats.get('categories', 0)}")
    print(f"Average Oxalate: {stats.get('oxalate_avg', 0)}mg/100g")
    print(f"Oxalate Range: {stats.get('oxalate_min', 0)} - {stats.get('oxalate_max', 0)}mg/100g")
    print(f"Average Calcium: {stats.get('calcium_avg', 0)}mg/100g\n")
    
    print("Categories:")
    for category in stats.get('categories_list', []):
        print(f"  - {category}")


def example_kidney_friendly_products():
    """Example: Get kidney-friendly products."""
    print("=" * 60)
    print("EXAMPLE 5: Kidney-Friendly Products")
    print("=" * 60)
    
    from agent import DatabaseManager, HealthScorer
    
    db = DatabaseManager()
    scorer = HealthScorer()
    
    kidney_friendly = db.get_kidney_friendly(threshold=20)
    
    print(f"\nFound {len(kidney_friendly)} kidney-friendly products (<=20mg oxalate):\n")
    
    for product in kidney_friendly[:5]:
        score = scorer.calculate_health_score(product)
        print(f"{product['name']}")
        print(f"  Oxalate: {product['oxalate_mg_per_100g']}mg/100g")
        print(f"  Score: {score['health_score']}/100 {score['emoji']}\n")


def example_composite_meal_interactive():
    """
    Example: Interactive composite meal scoring.
    Simulates a user saying 'I ate a salad' and selecting ingredient proportions.
    """
    print("=" * 60)
    print("EXAMPLE 6: Interactive Composite Meal Scoring")
    print("=" * 60)
    
    pipeline = create_pipeline()
    decomposer = MealDecomposer()
    
    # User describes their meal
    user_input = "I ate a salad for lunch"
    print(f"\nUser: \"{user_input}\"")
    
    # Decompose meal to get common ingredients
    decomp = decomposer.decompose_meal(user_input)
    
    if not decomp["matched"]:
        print(f"\nNo exact match. Available meal types: {[o['name'] for o in decomp['options']]}")
        return
    
    print(f"\nIdentified meal type: {decomp['name']}")
    print(f"Description: {decomp['description']}")
    
    # Show ingredient options with default proportions
    ingredients = decomp["common_ingredients"]
    print("\nCommon ingredients for this meal (with suggested proportions):")
    print("-" * 60)
    for i, ing in enumerate(ingredients, 1):
        pct = ing['default_pct']
        bar = "█" * int(pct / 5)
        print(f"  {i}. {ing['name']:<35} {bar:<20} {pct:.0f}%")
    print("-" * 60)
    
    # Simulate user customizing their salad proportions
    # (In a real UI this would be sliders/checkboxes)
    print("\nCustomized proportions (simulating user input):")
    custom_components = {
        "broccoli_fresh_raw": 40,    # user upped broccoli
        "carrot_fresh_raw": 30,      # kept carrots
        "bell_pepper_raw": 20,       # kept peppers
        "kale_fresh_raw": 10,        # reduced kale
        # spinach removed entirely
    }
    
    for prod_id, pct in custom_components.items():
        from agent import DatabaseManager
        db = DatabaseManager()
        product = db.get_product(prod_id)
        if product:
            bar = "█" * int(pct / 5)
            print(f"  {product['name']:<35} {bar:<20} {pct:.0f}%")
    
    # Score the composite meal
    print("\nCalculating composite health score...")
    try:
        result = pipeline.analyze_composite_meal(custom_components)
        
        score = result['score']
        product = result['product']
        
        print(f"\n{'=' * 60}")
        print(f"  COMPOSITE MEAL ANALYSIS")
        print(f"{'=' * 60}")
        print(f"  Composite Oxalate: {product['oxalate_mg_per_100g']} mg/100g")
        print(f"  Health Score:      {score['health_score']}/100 {score['emoji']}")
        print(f"  Verdict:           {score['category']} - {score['frequency']}")
        print(f"\n  Breakdown:")
        for comp in result['components_breakdown']:
            print(f"    {comp['name']:<35} {comp['percentage']:.1f}%  ({comp['oxalate_mg_per_100g']} mg/100g oxalate)")
        
        if score.get('recommendations'):
            print(f"\n  Recommendation: {score['recommendations'][0]}")
        
        print(f"\n  Tags: {' '.join(result['tags']['tags'])}\n")
    
    except Exception as e:
        print(f"Error: {e}\n")


def example_label_image_analysis():
    """
    Example: Analyze a nutrition label image.
    Uses a mocked response to demonstrate workflow without an API key.
    """
    print("=" * 60)
    print("EXAMPLE 7: Nutrition Label / Ingredient Image Analysis")
    print("=" * 60)
    
    pipeline = create_pipeline()
    
    print("\nSimulating analysis of a product label image...")
    print("(In production: pass a real image path or URL to pipeline.analyze_label_image())\n")
    
    # Simulate a returned result (as it would look with API key configured)
    from unittest.mock import MagicMock
    mock_response = {
        "success": True,
        "product_name": "Organic Kale & Spinach Blend",
        "ingredients": ["kale", "spinach"],
        "nutrients": {
            "calories": 35,
            "protein_g": 2.5,
            "fiber_g": 2.0,
            "calcium_mg": 117,
            "magnesium_mg": 57,
            "potassium_mg": 525,
            "vitamin_c_mg": 31,
            "oxalate_mg_per_100g": 361
        },
        "overall_confidence": "high",
        "notes": "Extracted from front-of-pack nutrition panel."
    }
    pipeline.image_processor.analyze_nutrition_and_ingredients = MagicMock(return_value=mock_response)
    
    try:
        result = pipeline.analyze_label_image("path/to/kale_spinach_label.jpg")
        
        if result.get("success"):
            score = result['score']
            product = result['product']
            
            print(f"  Product: {result['product_name']}")
            print(f"  Oxalate: {product['oxalate_mg_per_100g']} mg/100g")
            print(f"  Calcium: {product['nutrients'].get('calcium_mg', 'N/A')} mg")
            print(f"  Fiber:   {product['nutrients'].get('fiber_g', 'N/A')} g")
            print(f"\n  Health Score: {score['health_score']}/100 {score['emoji']}")
            print(f"  Verdict:      {score['category']} - {score['frequency']}")
            print(f"  Tags: {' '.join(result['tags']['tags'][:5])}\n")
        else:
            print(f"Analysis failed: {result.get('error')}\n")
    
    except Exception as e:
        print(f"Error: {e}\n")


def main():
    """Run all examples."""
    print("\n")
    print("=" * 60)
    print(" STONE COLD TRACKER - EXAMPLE USAGE ".center(60))
    print("=" * 60)
    
    example_analyze_by_id()
    example_database_stats()
    example_kidney_friendly_products()
    example_find_alternatives()
    example_generate_series()
    example_composite_meal_interactive()
    example_label_image_analysis()
    
    print("=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
