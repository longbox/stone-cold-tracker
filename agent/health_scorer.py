"""
Stone Cold Tracker - Health Scorer
Evaluates products based on oxalate content and nutritional modifiers.
"""

import json
from typing import Dict, Any, Optional, List


class HealthScorer:
    """Evaluates product health scores based on oxalate and nutrient profile."""
    
    def __init__(self, thresholds_path: str = "models/score_thresholds.json"):
        """
        Initialize health scorer with thresholds configuration.
        
        Args:
            thresholds_path: Path to score thresholds JSON file
        """
        self.thresholds_path = thresholds_path
        self._load_thresholds()
    
    def _load_thresholds(self):
        """Load scoring thresholds from configuration file with defaults fallback."""
        try:
            with open(self.thresholds_path, 'r') as f:
                self.thresholds = json.load(f)
        except Exception:
            # Fallback to default thresholds if file doesn't exist or is invalid
            self.thresholds = {
                "scoring_formula": {
                    "oxalate_factor_weight": 0.70,
                    "nutrient_factor_weight": 0.15,
                    "bioavailability_factor_weight": 0.10,
                    "context_factor_weight": 0.05
                },
                "oxalate_factor_ranges": [
                    { "max_mg_per_100g": 20, "score": 1.0, "level": "none" },
                    { "max_mg_per_100g": 50, "score": 0.7, "level": "low" },
                    { "max_mg_per_100g": 100, "score": 0.4, "level": "moderate" },
                    { "max_mg_per_100g": 200, "score": 0.2, "level": "high" },
                    { "max_mg_per_100g": 10000, "score": 0.0, "level": "extreme" }
                ],
                "rating_categories": [
                    { "min_score": 95, "max_score": 100, "category": "Excellent", "emoji": "⭐", "frequency": "Daily staple" },
                    { "min_score": 85, "max_score": 94, "category": "Great", "emoji": "🌟", "frequency": "Regular consumption" },
                    { "min_score": 70, "max_score": 84, "category": "Good", "emoji": "✓", "frequency": "3-4x per week" },
                    { "min_score": 50, "max_score": 69, "category": "Fair", "emoji": "⚠️", "frequency": "1-2x per week" },
                    { "min_score": 25, "max_score": 49, "category": "Poor", "emoji": "⛔", "frequency": "1-2x per month" },
                    { "min_score": 0, "max_score": 24, "category": "Terrible", "emoji": "🚫", "frequency": "Severe limitation" }
                ]
            }

    def _calculate_oxalate_factor(self, oxalate_mg: float) -> float:
        """
        Calculate oxalate factor on a 0-1 scale based on thresholds.
        
        Args:
            oxalate_mg: Oxalate content in mg/100g
            
        Returns:
            Oxalate factor between 0.0 and 1.0
        """
        ranges = self.thresholds.get("oxalate_factor_ranges", [])
        for r in ranges:
            if oxalate_mg <= r["max_mg_per_100g"]:
                return float(r["score"])
        return 0.0

    def _calculate_nutrient_factor(self, nutrients: Dict[str, Any]) -> float:
        """
        Calculate nutrient factor on a 0-1 scale based on positive indicators.
        
        Args:
            nutrients: Dictionary of nutrient quantities
            
        Returns:
            Nutrient factor between 0.0 and 1.0
        """
        factor = 0.0
        
        # Vitamin C, K, folate presence: +0.15 each
        vit_c = nutrients.get('vitamin_c_mg', 0) or nutrients.get('vitamin_c_mcg', 0) or nutrients.get('vitamin_c', 0)
        if vit_c > 0:
            factor += 0.15
            
        vit_k = nutrients.get('vitamin_k_mcg', 0) or nutrients.get('vitamin_k_mg', 0) or nutrients.get('vitamin_k', 0)
        if vit_k > 0:
            factor += 0.15
            
        folate = nutrients.get('folate_mcg', 0) or nutrients.get('folate_mg', 0) or nutrients.get('folate', 0)
        if folate > 0:
            factor += 0.15
            
        # Fiber content > 3g/100g: +0.20
        fiber = nutrients.get('fiber_g', 0) or nutrients.get('fiber', 0)
        if fiber > 3.0:
            factor += 0.20
            
        # Protein content > 5g/100g: +0.15
        protein = nutrients.get('protein_g', 0) or nutrients.get('protein', 0)
        if protein > 5.0:
            factor += 0.15
            
        # Mineral diversity (Ca, Mg, K, Fe, Zn): +0.10 if at least 2 are present
        minerals_present = 0
        for mineral in ['calcium_mg', 'magnesium_mg', 'potassium_mg', 'iron_mg', 'zinc_mg']:
            if nutrients.get(mineral, 0) > 0:
                minerals_present += 1
        if minerals_present >= 2:
            factor += 0.10
            
        # Antioxidant properties: +0.10
        if nutrients.get('antioxidants', False) or vit_c > 20:
            factor += 0.10
            
        return min(1.0, factor)

    def _calculate_bioavailability_factor(self, product: Dict[str, Any]) -> float:
        """
        Calculate bioavailability factor on a 0-1 scale.
        
        Args:
            product: Product data dictionary
            
        Returns:
            Bioavailability factor between 0.0 and 1.0
        """
        factor = 0.0
        nutrients = product.get('nutrients', {})
        
        # Calcium content >50mg/100g: +0.30 (binds oxalate)
        calcium = nutrients.get('calcium_mg', 0)
        if calcium > 50:
            factor += 0.30
            
        # Magnesium presence: +0.20 (supports kidney function)
        magnesium = nutrients.get('magnesium_mg', 0)
        if magnesium > 0:
            factor += 0.20
            
        # Low phytate content: +0.20
        if product.get('phytate_content', 'low') == 'low':
            factor += 0.20
            
        # Soluble oxalate ratio (lower is better): insoluble oxalate type gets +0.15
        oxalate_type = product.get('oxalate_type', '')
        if oxalate_type == 'insoluble':
            factor += 0.15
        elif oxalate_type == 'mixed':
            factor += 0.07
            
        # Preparation method reduces soluble oxalates: +0.15
        prep = product.get('preparation', 'raw')
        if prep in ['boiled', 'steamed', 'cooked', 'fermented']:
            factor += 0.15
            
        return min(1.0, factor)

    def _calculate_context_factor(self, product: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate context factor on a 0-1 scale.
        
        Args:
            product: Product data dictionary
            user_context: Optional user preferences
            
        Returns:
            Context factor between 0.0 and 1.0
        """
        factor = 0.0
        
        # Seasonal availability: +0.20
        if product.get('in_season', True):
            factor += 0.20
            
        # Trending health topics: +0.15
        if product.get('trending', False):
            factor += 0.15
            
        # User preferences/dietary restrictions: +0.30
        if user_context:
            pref_categories = user_context.get('preferred_categories', [])
            if product.get('category') in pref_categories:
                factor += 0.30
                
        # Budget/accessibility score: +0.20
        if product.get('accessible', True):
            factor += 0.20
            
        return min(1.0, factor)

    def _get_rating_category(self, score: float) -> Dict[str, Any]:
        """
        Map health score to rating category info.
        
        Args:
            score: Health score (0-100)
            
        Returns:
            Dictionary with category name, emoji, message, and frequency
        """
        categories = self.thresholds.get("rating_categories", [])
        for c in categories:
            if c["min_score"] <= score <= c["max_score"]:
                return {
                    "category": c["category"],
                    "emoji": c["emoji"],
                    "frequency": c.get("frequency", "Daily staple")
                }
        return {
            "category": "Terrible",
            "emoji": "🚫",
            "frequency": "Severe limitation"
        }

    def _generate_flags(self, product: Dict[str, Any], score: float) -> List[str]:
        """
        Generate risk flags based on product profile and score.
        
        Args:
            product: Product data dictionary
            score: Health score
            
        Returns:
            List of warning flags
        """
        flags = []
        oxalate = product.get('oxalate_mg_per_100g', 0)
        nutrients = product.get('nutrients', {})
        
        if oxalate > 200:
            flags.append('EXTREME_OXALATE')
        elif oxalate >= 100:
            flags.append('HIGH_OXALATE')
            
        calcium = nutrients.get('calcium_mg', 0)
        if calcium < 50 and oxalate > 50:
            flags.append('LOW_CALCIUM_WARNING')
            
        vit_c = nutrients.get('vitamin_c_mg', 0)
        if vit_c > 500:
            flags.append('HIGH_VITAMIN_C_WARNING')
            
        return flags

    def calculate_health_score(self, product: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None, *args, **kwargs) -> Dict[str, Any]:
        """
        Calculates a kidney-health score based on oxalate content and nutrient profile.
        
        Args:
            product: Product data dictionary
            user_context: Optional user context
            
        Returns:
            Dictionary of scoring results
        """
        oxalate_mg = product.get('oxalate_mg_per_100g', 0)
        nutrients = product.get('nutrients', {})
        calcium_mg = nutrients.get('calcium_mg', 0)
        vit_c_mg = nutrients.get('vitamin_c_mg', 0)
        
        # Calculate component factors
        oxalate_factor = self._calculate_oxalate_factor(oxalate_mg)
        nutrient_factor = self._calculate_nutrient_factor(nutrients)
        bioavailability_factor = self._calculate_bioavailability_factor(product)
        context_factor = self._calculate_context_factor(product, user_context)
        
        # Compute weighted score (0-100)
        formula = self.thresholds.get("scoring_formula", {})
        w_oxalate = formula.get("oxalate_factor_weight", 0.70)
        w_nutrient = formula.get("nutrient_factor_weight", 0.15)
        w_bioavail = formula.get("bioavailability_factor_weight", 0.10)
        w_context = formula.get("context_factor_weight", 0.05)
        
        raw_score = (100 * w_oxalate * oxalate_factor) + \
                    (100 * w_nutrient * nutrient_factor) + \
                    (100 * w_bioavail * bioavailability_factor) + \
                    (100 * w_context * context_factor)
                    
        final_score = max(0, min(100, int(round(raw_score))))
        
        # Get rating category info
        rating_info = self._get_rating_category(final_score)
        
        # Generate risk flags
        flags = self._generate_flags(product, final_score)
        
        # Generate recommendations
        recommendations = []
        if final_score >= 95:
            recommendations.append("Excellent choice for regular consumption. Negligible oxalate risk.")
        elif final_score >= 85:
            recommendations.append("Great low-oxalate choice for regular consumption.")
        elif final_score >= 70:
            recommendations.append("Consume in moderation. Be mindful of portion sizes.")
        elif final_score >= 50:
            recommendations.append("Balance needed. Enjoy in moderation.")
        elif final_score >= 25:
            recommendations.append("High oxalate content. Avoid or limit portion sizes.")
        else:
            recommendations.append("Extreme oxalate content. Avoid if prone to calcium oxalate stones.")
            
        if calcium_mg > 100:
            if oxalate_mg > 20:
                recommendations.append("The high calcium content helps bind some of the oxalates.")
        elif calcium_mg < 50 and oxalate_mg > 50:
            recommendations.append("Pro-tip: Pair this with a high-calcium food (like dairy) to reduce oxalate absorption.")
            
        if vit_c_mg > 500:
            recommendations.append("Caution: Extremely high Vitamin C can convert to oxalate in the body.")
            
        # Category tags for backward compatibility and tags system
        category_tags = ["low_oxalate", "kidney_safe"] if final_score >= 70 else ["high_oxalate", "stone_diet_caution"]
        
        return {
            "health_score": final_score,
            "emoji": rating_info["emoji"],
            "category": rating_info["category"],
            "category_tags": category_tags,
            "frequency": rating_info["frequency"],
            "recommendations": recommendations,
            "factors": {
                "oxalate_factor": oxalate_factor,
                "nutrient_factor": nutrient_factor,
                "bioavailability_factor": bioavailability_factor,
                "context_factor": context_factor
            },
            "flags": flags
        }