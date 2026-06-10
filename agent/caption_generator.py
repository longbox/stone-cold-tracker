"""
Stone Cold Tracker - Caption Generator
Generates engaging Instagram captions using OpenAI or templates based on product analysis.
"""

import os
import json
import random
from typing import Dict, List, Any


class CaptionGenerator:
    """Generates and validates Instagram captions and stories."""
    
    def __init__(self, templates_path: str = "models/caption_templates.json"):
        """
        Initialize caption generator with templates.
        
        Args:
            templates_path: Path to caption templates JSON file
        """
        self.templates_path = templates_path
        self._load_templates()
        
        # We initialize the OpenAI client for dynamic generation
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def _load_templates(self):
        """Load caption templates from JSON file."""
        try:
            with open(self.templates_path, 'r') as f:
                self.templates = json.load(f)
        except Exception:
            self.templates = {}

    def generate_caption(
        self,
        product: Dict[str, Any],
        score_data: Any,
        tags: List[str] = None,
        include_disclaimer: bool = True
    ) -> Dict[str, Any]:
        """
        Generates an Instagram caption summarizing the oxalate profile.
        
        Args:
            product: Product data dictionary
            score_data: Health score (int/float) or scoring result dictionary
            tags: List of hashtags to append
            include_disclaimer: Whether to include the medical disclaimer
            
        Returns:
            Dictionary with caption, character_count, and within_instagram_limit
        """
        product_name = product.get('name', 'this food')
        oxalate_mg = product.get('oxalate_mg_per_100g', 'Unknown')
        
        if isinstance(score_data, dict):
            health_score = score_data.get('health_score', 'N/A')
            category = score_data.get('category', 'Unknown')
            emoji = score_data.get('emoji', '')
            recs = score_data.get('recommendations', [])
            pro_tip = recs[0] if recs else "Always consult with your nephrologist or dietitian."
        else:
            health_score = score_data
            # Derive rating info using HealthScorer
            from agent.health_scorer import HealthScorer
            scorer = HealthScorer()
            score_dict = scorer.calculate_health_score(product)
            category = score_dict.get('category', 'Unknown')
            emoji = score_dict.get('emoji', '')
            recs = score_dict.get('recommendations', [])
            pro_tip = recs[0] if recs else "Always consult with your nephrologist or dietitian."
            
        category_key = category.lower()
        tag_string = " ".join([f"#{t.replace('#', '')}" for t in (tags or [])])
        
        caption_body = ""
        
        # If OpenAI is configured, generate a dynamic caption
        if self.client:
            prompt = f"""
            You are a kidney health expert running the 'Stone Cold Tracker' Instagram account.
            Write a highly engaging, informative, and concise Instagram caption for {product_name}.
            
            Include these exact data points:
            - Oxalate content: {oxalate_mg}mg per 100g
            - Stone Cold Health Score: {health_score}/100 {emoji}
            - Verdict: {category}
            - Pro Tip: {pro_tip}
            
            Keep the tone educational but accessible. Do not use medical jargon without explaining it. 
            Do NOT include hashtags in your generated text (they will be appended automatically).
            """
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a specialized social media manager for a dietary health app."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                caption_body = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"LLM Caption generation failed, using fallback: {e}")
                
        if not caption_body:
            # Fallback to local template
            templates_list = self.templates.get('caption_templates', {}).get(category_key, [])
            if templates_list:
                caption_body = random.choice(templates_list)
            else:
                caption_body = (
                    f"Let's look at {product_name}! {emoji}\n\n"
                    f"📊 Oxalate Content: {oxalate_mg}mg per 100g\n"
                    f"🎯 Health Score: {health_score}/100 ({category})\n\n"
                    f"💡 Pro-Tip: {pro_tip}"
                )
                
        # Format closing / details if relevant
        if tag_string:
            final_caption = f"{caption_body}\n\n{tag_string}"
        else:
            final_caption = caption_body
            
        if include_disclaimer:
            disclaimer_text = (
                "\n\n⚠️ DISCLAIMER: This analysis is for informational purposes only and does "
                "not constitute medical advice. Individuals with kidney disease, kidney stones, or "
                "other medical conditions should consult their healthcare provider."
            )
            final_caption += disclaimer_text
            
        validation = self.validate_caption(final_caption)
        
        return {
            "caption": final_caption,
            "character_count": len(final_caption),
            "within_instagram_limit": validation["valid"]
        }

    def validate_caption(self, caption: str) -> Dict[str, Any]:
        """
        Validate Instagram caption guidelines.
        
        Args:
            caption: Caption string to validate
            
        Returns:
            Dictionary with validation results
        """
        character_count = len(caption)
        
        # Count hashtags (any word starting with #)
        hashtag_count = sum(1 for word in caption.split() if word.startswith('#'))
        
        issues = []
        warnings = []
        
        if character_count > 2200:
            issues.append("Caption exceeds 2200 characters limit.")
        if hashtag_count > 30:
            issues.append("Caption has more than 30 hashtags.")
            
        if "DISCLAIMER" not in caption:
            warnings.append("Caption is missing a medical disclaimer.")
            
        return {
            "valid": len(issues) == 0,
            "character_count": character_count,
            "hashtag_count": hashtag_count,
            "issues": issues,
            "warnings": warnings
        }

    def generate_short_caption(self, score: float, product_name: str) -> str:
        """
        Generate a short caption suitable for stories.
        
        Args:
            score: Health score (0-100)
            product_name: Name of the product
            
        Returns:
            Short caption string
        """
        # Map score to category info
        if score >= 95:
            category, emoji = "Excellent", "⭐"
        elif score >= 85:
            category, emoji = "Great", "🌟"
        elif score >= 70:
            category, emoji = "Good", "✓"
        elif score >= 50:
            category, emoji = "Fair", "⚠️"
        elif score >= 25:
            category, emoji = "Poor", "⛔"
        else:
            category, emoji = "Terrible", "🚫"
            
        options = [
            f"{product_name}: {score}/100 {emoji} ({category})!",
            f"Checking out {product_name}! Verdict: {category} ({score}/100) {emoji}",
            f"{product_name} scores {score}/100 on kidney health scale! {emoji}"
        ]
        return random.choice(options)