#!/usr/bin/env python
"""
Stone Cold Tracker - Example Usage Script
Demonstrates how to use the complete analysis pipeline.
"""

import json
from agent import create_pipeline


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
    
    print(f"\nFound {len(kidney_friendly)} kidney-friendly products (≤20mg oxalate):\n")
    
    for product in kidney_friendly[:5]:
        score = scorer.calculate_health_score(product)
        print(f"{product['name']}")
        print(f"  Oxalate: {product['oxalate_mg_per_100g']}mg/100g")
        print(f"  Score: {score['health_score']}/100 {score['emoji']}\n")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " STONE COLD TRACKER - EXAMPLE USAGE ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    example_analyze_by_id()
    example_database_stats()
    example_kidney_friendly_products()
    example_find_alternatives()
    example_generate_series()
    
    print("=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
