"""
Stone Cold Tracker - Meal Decomposer
Decomposes composite meals (like salads) into individual database products
and calculates composite kidney-health scores based on ingredient proportions.
"""

from typing import Dict, List, Any, Optional


COMPOSITE_MEAL_CATALOG = {
    "salad": {
        "name": "Mixed Salad",
        "common_ingredients": [
            {"id": "spinach_fresh_raw", "name": "Spinach, Fresh (Raw)", "default_pct": 30.0},
            {"id": "kale_fresh_raw", "name": "Kale, Fresh (Raw)", "default_pct": 20.0},
            {"id": "carrot_fresh_raw", "name": "Carrot, Fresh (Raw)", "default_pct": 20.0},
            {"id": "bell_pepper_raw", "name": "Bell Pepper, Red (Raw)", "default_pct": 20.0},
            {"id": "broccoli_fresh_raw", "name": "Broccoli, Fresh (Raw)", "default_pct": 10.0}
        ],
        "description": "A fresh leafy greens salad with various mixed vegetables."
    },
    "smoothie": {
        "name": "Green Smoothie",
        "common_ingredients": [
            {"id": "spinach_fresh_raw", "name": "Spinach, Fresh (Raw)", "default_pct": 40.0},
            {"id": "carrot_fresh_raw", "name": "Carrot, Fresh (Raw)", "default_pct": 30.0},
            {"id": "beet_raw", "name": "Beet, Raw", "default_pct": 30.0}
        ],
        "description": "A blended vegetable and green smoothie."
    },
    "stir_fry": {
        "name": "Vegetable Stir-Fry",
        "common_ingredients": [
            {"id": "broccoli_fresh_raw", "name": "Broccoli, Fresh (Raw)", "default_pct": 40.0},
            {"id": "carrot_fresh_raw", "name": "Carrot, Fresh (Raw)", "default_pct": 30.0},
            {"id": "green_beans_raw", "name": "Green Beans, Raw", "default_pct": 20.0},
            {"id": "garlic_fresh", "name": "Garlic, Fresh (Clove)", "default_pct": 10.0}
        ],
        "description": "Sautéed vegetables in a light seasoning."
    },
    "soup": {
        "name": "Mixed Vegetable Soup",
        "common_ingredients": [
            {"id": "carrot_fresh_raw", "name": "Carrot, Fresh (Raw)", "default_pct": 30.0},
            {"id": "sweet_potato_raw", "name": "Sweet Potato, Raw", "default_pct": 35.0},
            {"id": "green_beans_raw", "name": "Green Beans, Raw", "default_pct": 25.0},
            {"id": "garlic_fresh", "name": "Garlic, Fresh (Clove)", "default_pct": 10.0}
        ],
        "description": "A warm mixed vegetable soup."
    }
}


class MealDecomposer:
    """Decomposes composite meals and calculates weighted health scores."""
    
    def __init__(self, catalog: Dict[str, Any] = COMPOSITE_MEAL_CATALOG):
        """Initialize meal decomposer with a composite meal catalog."""
        self.catalog = catalog
        
    def decompose_meal(self, meal_query: str) -> Dict[str, Any]:
        """
        Identify if a meal query matches a known composite meal type.
        
        Args:
            meal_query: The name of the meal (e.g. "I ate a green salad")
            
        Returns:
            Dictionary with matching composite meal details or fallback option
        """
        query_lower = meal_query.lower()
        
        for key, meal_data in self.catalog.items():
            if key in query_lower:
                return {
                    "matched": True,
                    "meal_type": key,
                    "name": meal_data["name"],
                    "description": meal_data["description"],
                    "common_ingredients": meal_data["common_ingredients"]
                }
                
        # Fallback if no matching meal is found
        # Return all options to let user choose
        return {
            "matched": False,
            "meal_type": "unknown",
            "message": f"Could not identify '{meal_query}'. Choose a common composite type to begin:",
            "options": [
                {"type": k, "name": v["name"], "description": v["description"]}
                for k, v in self.catalog.items()
            ]
        }
        
    def calculate_composite_score(
        self,
        components: Dict[str, float],
        database_manager,
        health_scorer
    ) -> Dict[str, Any]:
        """
        Calculate the weighted kidney health score of a composite food.
        
        Args:
            components: Map of database product IDs to percentages (e.g. {"spinach_fresh_raw": 50, "broccoli_fresh_raw": 50})
            database_manager: DatabaseManager to fetch product nutrient profiles
            health_scorer: HealthScorer to score the virtual composite product
            
        Returns:
            Dictionary containing the score, risk flags, and composite virtual product profile
        """
        if not components:
            raise ValueError("Meal must contain at least one ingredient component.")
            
        total_pct = sum(components.values())
        if total_pct <= 0:
            raise ValueError("Sum of component percentages must be greater than zero.")
            
        # Normalize weights to sum to 1.0
        normalized_weights = {p_id: pct / total_pct for p_id, pct in components.items()}
        
        composite_oxalate = 0.0
        composite_bioavailability = 0.0
        composite_nutrients = {}
        
        soluble_weight = 0.0
        mixed_weight = 0.0
        
        matched_products = []
        
        for p_id, weight in normalized_weights.items():
            product = database_manager.get_product(p_id)
            if not product:
                # If a custom ingredient is passed that is not in the db, skip or default
                continue
                
            matched_products.append(product)
            
            # Weighted oxalate
            composite_oxalate += weight * product.get("oxalate_mg_per_100g", 0)
            
            # Weighted bioavailability
            composite_bioavailability += weight * product.get("bioavailability", 0)
            
            # Soluble type tracking
            ox_type = product.get("oxalate_type", "")
            if ox_type == "soluble":
                soluble_weight += weight
            elif ox_type == "mixed":
                mixed_weight += weight
                
            # Weighted nutrients
            product_nutrients = product.get("nutrients", {})
            for nut_key, val in product_nutrients.items():
                composite_nutrients[nut_key] = composite_nutrients.get(nut_key, 0.0) + (weight * val)
                
        if not matched_products:
            raise ValueError("None of the specified ingredients were found in the database.")
            
        # Determine composite oxalate type
        if soluble_weight >= 0.50:
            composite_ox_type = "soluble"
        elif soluble_weight > 0 or mixed_weight > 0:
            composite_ox_type = "mixed"
        else:
            composite_ox_type = "insoluble"
            
        # Build composite virtual product
        composite_product = {
            "id": "composite_meal_virtual",
            "name": "Custom Composite Meal",
            "category": "mixed",
            "oxalate_mg_per_100g": round(composite_oxalate, 2),
            "oxalate_type": composite_ox_type,
            "bioavailability": round(composite_bioavailability, 2),
            "nutrients": {k: round(v, 2) for k, v in composite_nutrients.items()}
        }
        
        # Calculate composite health score
        score_result = health_scorer.calculate_health_score(composite_product)
        
        return {
            "score": score_result,
            "product": composite_product,
            "components_breakdown": [
                {
                    "product_id": p["id"],
                    "name": p["name"],
                    "percentage": round(normalized_weights[p["id"]] * 100, 1),
                    "oxalate_mg_per_100g": p["oxalate_mg_per_100g"]
                }
                for p in matched_products
            ]
        }
