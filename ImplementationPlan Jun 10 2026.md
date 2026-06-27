Implementation Plan - Image Nutrition Extraction and Interactive Meal Scoring
This plan proposes expanding Stone Cold Tracker to support nutrition info extraction from images and interactive composite meal scoring (e.g., salad component proportions).

User Review Required
NOTE

We will represent the interactive prompting flow using a structured console-based selection step in our examples and expose clear API methods so that front-end clients can easily build user interfaces (e.g., sliders or checkboxes) around it.

Proposed Changes
Core Business Logic
[MODIFY] 
image_processor.py
Expand ImageProcessor to add:

analyze_nutrition_and_ingredients(image_source): A specialized method that detects if an image is a product nutrition label/ingredients list, and extracts ingredient names along with nutritional metrics (calcium, magnesium, potassium, fiber, protein, vitamin C, calories).
Update prompt formats to handle extracting detailed nutrition facts from labels.
[NEW] 
meal_decomposer.py
Create a new module to handle composite meals:

Define a dictionary of common composite foods (e.g., salad, smoothie, sandwich, soup) with their common ingredients.
decompose_meal(meal_query: str) -> Dict: Detects meal type and returns common components and instructions for proportions.
calculate_composite_score(components: Dict[str, float], database_manager, health_scorer) -> Dict:
Takes a dictionary mapping product IDs to percentages (totaling 100%).
Fetches individual component nutrients.
Computes a weighted average of nutrients and oxalate content to create a composite virtual product.
Calls HealthScorer on this composite product to yield a composite score.
[MODIFY] 
analysis_pipeline.py
Integrate the meal decomposer and nutrition extraction:

Add analyze_composite_meal(components: Dict[str, float]) -> Dict orchestrating the composite scoring, tag, and caption generation.
Add analyze_label_image(image_source: str) -> Dict returning parsed nutrition details and matching products.
Verification Plan
Automated Tests
Add test cases in tests/test_scoring.py (or a new test file) verifying:

Extraction parsing logic.
Composite meal score calculation (e.g., verifying that a 50/50 mix of spinach and broccoli has a score between the two individual scores).
Manual Verification
Update examples.py to demonstrate:
Interactive terminal-based salad composition input.
Score calculation of the custom salad.