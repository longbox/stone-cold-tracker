# Stone Cold Tracker: Medical Research & Food Analysis Framework

## Overview

This document outlines a consistent, thorough, and accurate model for tracking medical research and chemical analysis of food products, specifically focused on oxalate content analysis with Instagram caption generation.

---

## 1. Data Architecture

### Three-Layer System Design

```
┌─────────────────────────────────────────────────────────────┐
│           INGREDIENT DATABASE                               │
│  - Product names, ingredients, portions                      │
│  - Oxalate content (mg/100g, per serving)                   │
│  - Nutritional profile (Ca, K, Mg, vitamin content)         │
│  - Source citations (research papers, USDA, studies)        │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│           ANALYSIS ENGINE                                   │
│  - Cumulative oxalate calculation                           │
│  - Bioavailability adjustment (soluble vs insoluble)        │
│  - Nutrient interaction scoring                             │
│  - Risk stratification                                      │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│           RATING & CONTENT SYSTEM                           │
│  - Health score (0-100)                                     │
│  - Creative tags (5-7 per product)                          │
│  - Instagram captions                                       │
│  - Usage recommendations                                    │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Image Input** → Ingredient Recognition → Database Lookup
2. **Database Lookup** → Oxalate & Nutrient Data Retrieval → Citation Linking
3. **Analysis Engine** → Multi-factor Scoring → Health Score Calculation
4. **Rating & Content** → Tag Generation → Caption Creation → Output

---

## 2. Health Score Model (Excellent → Terrible)

### Multi-Factor Scoring System

Rather than relying on a single metric, use a weighted multi-factor approach:

```
HEALTH_SCORE = (70 × Oxalate_Factor) 
             + (15 × Nutrient_Factor) 
             + (10 × Bioavailability_Factor)
             + (5 × Context_Factor)

Final Score: 0-100 (normalized percentage)
```

### Component Definitions

#### Oxalate_Factor (Weight: 70%)
Normalized 0-1 scale based on oxalate content per 100g:

- **≤20 mg/100g** = 1.0 (No significant oxalate)
- **20-50 mg/100g** = 0.7 (Low oxalate)
- **50-100 mg/100g** = 0.4 (Moderate oxalate)
- **100-200 mg/100g** = 0.2 (High oxalate)
- **>200 mg/100g** = 0.0 (Extreme oxalate)

Linear interpolation between ranges for precise scoring.

#### Nutrient_Factor (Weight: 15%)
Positive health indicators (0-1):

- Vitamin C, K, folate presence: +0.15 each
- Fiber content >3g/100g: +0.20
- Protein content >5g/100g: +0.15
- Mineral diversity (Ca, Mg, K, Fe, Zn): +0.10
- Antioxidant properties: +0.10
- Cap at 1.0

#### Bioavailability_Factor (Weight: 10%)
How well nutrients are absorbed and oxalate is managed (0-1):

- Calcium content >50mg/100g: +0.30 (binds oxalate)
- Magnesium presence: +0.20 (supports kidney function)
- Low phytate content: +0.20 (improves absorption)
- Soluble oxalate ratio (lower is better): +0.15
- Preparation method reduces soluble oxalates: +0.15
- Cap at 1.0

#### Context_Factor (Weight: 5%)
User & temporal relevance (0-1):

- Seasonal availability: +0.20
- Trending health topics: +0.15
- User preferences/dietary restrictions: +0.30
- Budget/accessibility score: +0.20
- Cap at 1.0

### Score Interpretation Matrix

| Score Range | Category | Emoji | Key Message | Usage Guideline |
|---|---|---|---|---|
| 95-100 | Excellent | ⭐ | Oxalate-free champion | Daily staple |
| 85-94 | Great | 🌟 | Low oxalate winner | Regular consumption |
| 70-84 | Good | ✓ | Moderate oxalate, nutrient-rich | 3-4x per week |
| 50-69 | Fair | ⚠️ | Balance needed | 1-2x per week |
| 25-49 | Poor | ⛔ | High oxalate | 1-2x per month |
| 0-24 | Terrible | 🚫 | Extreme oxalate | Severe limitation |

---

## 3. Critical Research Data Points to Track

### Bioavailability Profiles

- **Soluble Oxalate**: Absorbed in gut, reaches kidneys (problematic for kidney-sensitive individuals)
- **Insoluble Oxalate**: Passes through system, lower absorption risk
- **Binding Factors**: Calcium, magnesium, and protein reduce oxalate absorption

### Nutrient Synergies

- **Calcium (>50mg/100g)**: Binds oxalate in gut, prevents absorption
- **Magnesium**: Supports kidney function, dietary antagonist to oxalate
- **Vitamin K**: Bone health, kidney support
- **Fiber**: Digestive health, nutrient transport
- **Vitamin C**: Antioxidant, but increases oxalate production (track)

### Preparation Method Impact

Track how preparation affects oxalate content:

| Method | Soluble Oxalate Reduction | Notes |
|---|---|---|
| Boiling | 30-60% | Leaches water-soluble compounds |
| Steaming | 10-25% | Less loss than boiling |
| Roasting | 5-15% | Minimal reduction |
| Raw | 0% | Baseline measurement |
| Fermentation | 15-40% | Depends on duration |

### Individual Risk Factors

- **Kidney Function**: Flag products for CKD, stone formers
- **Absorption Capacity**: Age, gut microbiome, medications
- **Cumulative Intake**: Track daily/weekly totals
- **Medication Interactions**: Certain drugs affect oxalate metabolism

### Source Citations

Maintain complete audit trail:

```json
{
  "product_id": "spinach_fresh",
  "oxalate_mg_per_100g": 656,
  "sources": [
    {
      "source": "USDA FoodData Central",
      "database_id": "FDC_ID_12345",
      "measurement_method": "HPLC",
      "confidence": "high",
      "last_verified": "2024-01-15"
    },
    {
      "source": "PubMed Study",
      "pubmed_id": "PMID_1234567",
      "authors": ["Smith, J.", "Doe, J."],
      "year": 2022,
      "confidence": "high",
      "notes": "Peer-reviewed analysis of 50 spinach varieties"
    }
  ]
}
```

---

## 4. Rating Categories & Descriptions

### ⭐ Excellent (95-100)

**Profile**: Oxalate-free or negligible, nutrient powerhouse

**Sample Products**: Broccoli, Brussels sprouts, cauliflower, garlic, onions, herbs (basil, parsley)

**Message**: "Oxalate-free champion"

**Use Case**: Daily staple, unlimited consumption

**Example Caption**: "This green warrior has ZERO oxalate concerns! Load up your plate guilt-free. Perfect for kidney-conscious eating. 💚 #OxalateFree #KidneyFriendly"

---

### 🌟 Great (85-94)

**Profile**: Low oxalate with solid nutritional value

**Sample Products**: Cabbage, zucchini, asparagus, green beans, cucumber, bell peppers

**Message**: "Low oxalate winner"

**Use Case**: Regular consumption, 5-6x per week

**Example Caption**: "Great news! This veggie has minimal oxalate AND packs minerals. Your kidney will thank you. 🥒 #LowOxalate #BudgetFriendly"

---

### ✓ Good (70-84)

**Profile**: Moderate oxalate but rich in nutrients; prepare wisely

**Sample Products**: Carrots, green peas, artichokes, beets, mushrooms

**Message**: "Moderate oxalate, nutrient-rich"

**Use Case**: 3-4x per week, portion-controlled

**Example Caption**: "This veggie packs nutrition but needs moderation. Pro tip: pair with calcium-rich foods to reduce oxalate absorption! 🥕 #ModerateOxalate #BalancedBite"

---

### ⚠️ Fair (50-69)

**Profile**: Higher oxalate; balance needed through preparation or pairing

**Sample Products**: Sweet potato, kale, chard, rhubarb (low amounts)

**Message**: "Balance needed, enjoy in moderation"

**Use Case**: 1-2x per week, strategic pairing with calcium

**Example Caption**: "Love this veggie? Enjoy it 1-2x weekly and pair with cheese or yogurt to minimize oxalate! Smart eating. 🥗 #EnjoyInModeration #CombinedWisely"

---

### ⛔ Poor (25-49)

**Profile**: High oxalate; limit intake significantly

**Sample Products**: Spinach (cooked), beet greens, certain nuts (almonds, peanuts)

**Message**: "High oxalate, limit portions"

**Use Case**: 1-2x per month, maximum 1 serving

**Example Caption**: "This favorite is HIGH in oxalate! If you have kidney concerns, save this for special occasions. Quality over quantity. 🌱 #HighOxalate #RareIndulgence"

---

### 🚫 Terrible (0-24)

**Profile**: Extreme oxalate content; severe limitation recommended

**Sample Products**: Raw spinach (mega-high), sorrel, rhubarb (cooked), certain teas (black tea)

**Message**: "Extreme oxalate, not recommended"

**Use Case**: Avoid or extreme limitation; consult healthcare provider

**Example Caption**: "⚠️ WARNING: This is EXTREMELY high in oxalate. If kidney health is a concern, consult your doctor before consuming. #AvoidIfPossible #KidneyStress #ConsultDoctor"

---

## 5. Creative Tag Generation Strategy

### Tag Template System

Tags are generated dynamically based on:
1. Health Score (category)
2. Primary nutritional benefit
3. Preparation method
4. Seasonal timing
5. Current health trends
6. User preferences

### Scoring Category Tags

#### For Excellent (95-100)
```
#OxalateFree
#KidneyFriendly
#HealthyDaily
#ZeroOxalate
#SafeForKidney
#NutrientDense
#SuperFood
#GuiltFree
#CleanEating
#VitaminBoost
```

#### For Great (85-94)
```
#LowOxalate
#BudgetFriendly
#QuickMeal
#FamilyApproved
#MineralRich
#VitaminBoost
#NutritionWin
#WeekdayStaple
#HealthyChoice
#TastyAndSafe
```

#### For Good (70-84)
```
#ModerateOxalate
#BalancedBite
#PortionControl
#TravelFriendly
#ConvenientChoice
#ComfortFood
#ModerateIntake
#SmartEating
#NutrientPower
#FlexibleChoice
```

#### For Fair (50-69)
```
#EnjoyInModeration
#OccasionalTreat
#MealPairing
#CombinedWisely
#SpecialOccasion
#LimitedServing
#PairWithCa
#StrategicChoice
#BalancedApproach
#WeeklyTreat
```

#### For Poor (25-49)
```
#HighOxalate
#RareIndulgence
#NotForEveryDay
#SipsNotGulps
#CasualOnly
#SmallPortion
#ResearchNeeded
#LimitIntake
#ThinkTwice
#OccasionalOnly
```

#### For Terrible (0-24)
```
#AvoidIfPossible
#HighRisk
#KidneyStress
#LimitSeverely
#NotRecommended
#ConsultDoctor
#ProceedCautiously
#HealthAlert
#UseCaution
#SpeakWithDoctor
```

### Benefit-Based Tags

```
HIGH_FIBER: #FiberRich #DigestiveHealth #GutFriendly
HIGH_CALCIUM: #CalciumBoosted #BoneStrength #DairyFree
HIGH_PROTEIN: #ProteinPacked #MuscleSupport #PlantBased
ANTIOXIDANT: #AntioxidantPower #AntiInflammatory #CellProtection
LOW_CALORIE: #LowCalorie #WeightManagement #SlimmeDown
ORGANIC: #Organic #NoChemicals #FarmFresh #Sustainable
VEGAN: #VeganFriendly #PlantBased #CrueltyFree
GLUTEN_FREE: #GlutenFree #CeliacFriendly #GlutenSafe
```

### Seasonal Tags

```
SPRING: #SpringFresh #SeasonalEats #FarmToTable
SUMMER: #SummerVibes #LightAndFresh #BBQReady
FALL: #FallFavs #CozyFood #HarvestTime
WINTER: #WinterWarmer #ComfortFood #CozyMeals
```

### Tag Selection Algorithm

```python
selected_tags = []

# Add 1-2 score category tags
selected_tags += pick_random(category_tags, 2)

# Add 2 benefit tags if applicable
if has_high_fiber:
    selected_tags += [pick_random(HIGH_FIBER_TAGS, 1)]
if has_high_calcium:
    selected_tags += [pick_random(HIGH_CALCIUM_TAGS, 1)]

# Add 1 seasonal tag
selected_tags += [pick_seasonal_tag()]

# Add 1 trending tag
selected_tags += [pick_trending_health_tag()]

# Ensure 5-7 total tags, remove duplicates
final_tags = list(set(selected_tags))[:7]
```

---

## 6. Repository Structure

### Recommended File Organization

```
stone-cold-tracker/
│
├── ANALYSIS_FRAMEWORK.md          # This file
├── README.md
├── requirements.txt
│
├── data/
│   ├── oxalate_database.json       # Primary oxalate reference data
│   ├── nutrient_database.json      # Nutritional profiles
│   ├── bioavailability_factors.json # Preparation method impacts
│   ├── research_citations.json     # Source tracking & citations
│   └── prepare_methods.json        # Cooking technique data
│
├── models/
│   ├── product_schema.json         # JSON schema validation
│   ├── score_thresholds.json       # Configurable rating cutoffs
│   ├── tag_templates.json          # Tag generation templates
│   └── caption_templates.json      # Caption generation templates
│
├── agent/
│   ├── __init__.py
│   ├── analysis_engine.py          # Health score calculation
│   ├── image_processor.py          # Ingredient recognition from images
│   ├── health_scorer.py            # Rating calculation & interpretation
│   ├── tag_generator.py            # Creative tag creation
│   ├── caption_generator.py        # Instagram caption generation
│   ├── database_manager.py         # Database queries & updates
│   └── memory/
│       ├── CHORES.md               # Task tracking
│       └── research_log.md         # Findings & updates
│
├── tests/
│   ├── __init__.py
│   ├── test_scoring.py             # Health score calculation tests
│   ├── test_tags.py                # Tag generation tests
│   ├── test_captions.py            # Caption generation tests
│   ├── test_database.py            # Database accuracy tests
│   └── test_accuracy.py            # Overall accuracy metrics
│
└── docs/
    ├── API.md                      # API documentation
    ├── DATA_SOURCES.md             # Citation & source documentation
    ├── CALIBRATION.md              # Scoring tuning documentation
    └── MEDICAL_DISCLAIMERS.md      # Legal & safety disclaimers
```

---

## 7. Implementation Roadmap

### Phase 1: Data Foundation (Weeks 1-2)

**Objectives**: Build authoritative databases

- [ ] Populate `oxalate_database.json` with 100+ verified foods
  - Source: USDA FoodData Central
  - Peer-reviewed studies
  - Kidney health organizations (NKUDIC)
- [ ] Create `nutrient_database.json` with mineral/vitamin profiles
- [ ] Build `bioavailability_factors.json` with preparation method impacts
- [ ] Document all sources in `research_citations.json`

**Data Sources**:
- **USDA FoodData Central**: https://fdc.nal.usda.gov/
- **PubMed Central**: https://www.ncbi.nlm.nih.gov/pmc/
- **National Kidney Foundation**: https://www.kidney.org/
- **ResearchGate**: https://www.researchgate.net/

### Phase 2: Scoring Engine (Weeks 3-4)

**Objectives**: Implement health scoring logic

- [ ] Develop `analysis_engine.py` with multi-factor formula
- [ ] Create `health_scorer.py` with interpretation rules
- [ ] Build test suite for scoring accuracy
- [ ] Implement configurable thresholds in `score_thresholds.json`
- [ ] Validate against 50+ known products

**Deliverables**:
- Scoring algorithm with weighted components
- Test coverage >90%
- Calibration documentation

### Phase 3: Image & Recognition (Weeks 5-6)

**Objectives**: Connect visual input to analysis

- [ ] Develop `image_processor.py` for ingredient recognition
- [ ] Integrate with OpenAI vision API (already in requirements.txt)
- [ ] Build fallback mechanisms for unrecognized items
- [ ] Create database lookup pipeline

**Testing**: 100+ sample food images

### Phase 4: Content Generation (Weeks 7-8)

**Objectives**: Create engaging Instagram content

- [ ] Build `tag_generator.py` with template system
- [ ] Develop `caption_generator.py` with variability
- [ ] Create caption templates for all score categories
- [ ] Implement hashtag diversity algorithms

**Testing**: Generate 50+ unique captions per product

### Phase 5: Integration & Refinement (Weeks 9-10)

**Objectives**: Bring all components together

- [ ] Full pipeline integration
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Error handling & edge cases
- [ ] Memory system for learning

### Phase 6: Deployment & Monitoring (Weeks 11+)

**Objectives**: Production readiness

- [ ] Deploy to production environment
- [ ] Monitor accuracy metrics
- [ ] Collect user feedback
- [ ] Iterate on tag variety (from CHORES.md)
- [ ] Build seasonal content calendar

---

## 8. Data Schema Examples

### oxalate_database.json Structure

```json
{
  "products": [
    {
      "id": "spinach_fresh_raw",
      "name": "Spinach, Fresh (Raw)",
      "category": "leafy_greens",
      "oxalate_mg_per_100g": 656,
      "oxalate_mg_per_cup": 656,
      "serving_size_grams": 30,
      "oxalate_per_serving": 197,
      "oxalate_type": "soluble",
      "bioavailability": 0.8,
      "nutrients": {
        "calcium_mg": 99,
        "magnesium_mg": 79,
        "potassium_mg": 558,
        "vitamin_k_mcg": 483
      },
      "sources": ["USDA_FDC_ID_123456", "PMID_9876543"],
      "last_updated": "2024-01-15",
      "confidence_score": 0.95,
      "notes": "High oxalate when raw; cooking reduces soluble content by 45%"
    },
    {
      "id": "broccoli_fresh",
      "name": "Broccoli, Fresh (Raw)",
      "category": "cruciferous",
      "oxalate_mg_per_100g": 18,
      "oxalate_mg_per_cup": 36,
      "serving_size_grams": 89,
      "oxalate_per_serving": 16,
      "oxalate_type": "insoluble",
      "bioavailability": 0.2,
      "nutrients": {
        "calcium_mg": 89,
        "magnesium_mg": 19,
        "potassium_mg": 316,
        "vitamin_k_mcg": 102,
        "vitamin_c_mg": 89
      },
      "sources": ["USDA_FDC_ID_654321", "PMID_1234567"],
      "last_updated": "2024-01-10",
      "confidence_score": 0.98,
      "notes": "Low oxalate, high in calcium which binds remaining oxalate"
    }
  ]
}
```

### score_thresholds.json

```json
{
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
    { "min_score": 95, "max_score": 100, "category": "Excellent", "emoji": "⭐" },
    { "min_score": 85, "max_score": 94, "category": "Great", "emoji": "🌟" },
    { "min_score": 70, "max_score": 84, "category": "Good", "emoji": "✓" },
    { "min_score": 50, "max_score": 69, "category": "Fair", "emoji": "⚠️" },
    { "min_score": 25, "max_score": 49, "category": "Poor", "emoji": "⛔" },
    { "min_score": 0, "max_score": 24, "category": "Terrible", "emoji": "🚫" }
  ]
}
```

### tag_templates.json

```json
{
  "category_tags": {
    "excellent": ["#OxalateFree", "#KidneyFriendly", "#HealthyDaily", "#ZeroOxalate", "#SafeForKidney", "#NutrientDense", "#SuperFood"],
    "great": ["#LowOxalate", "#BudgetFriendly", "#QuickMeal", "#FamilyApproved", "#MineralRich", "#VitaminBoost", "#NutritionWin"],
    "good": ["#ModerateOxalate", "#BalancedBite", "#PortionControl", "#TravelFriendly", "#ConvenientChoice", "#ComfortFood"],
    "fair": ["#EnjoyInModeration", "#OccasionalTreat", "#MealPairing", "#CombinedWisely", "#SpecialOccasion", "#LimitedServing"],
    "poor": ["#HighOxalate", "#RareIndulgence", "#NotForEveryDay", "#SipsNotGulps", "#CasualOnly", "#SmallPortion"],
    "terrible": ["#AvoidIfPossible", "#HighRisk", "#KidneyStress", "#LimitSeverely", "#NotRecommended", "#ConsultDoctor"]
  },
  "benefit_tags": {
    "high_fiber": ["#FiberRich", "#DigestiveHealth", "#GutFriendly", "#CleanEating"],
    "high_calcium": ["#CalciumBoosted", "#BoneStrength", "#DairyFree", "#StrongBones"],
    "high_protein": ["#ProteinPacked", "#MuscleSupport", "#PlantBased", "#FitnessFood"],
    "antioxidant": ["#AntioxidantPower", "#AntiInflammatory", "#CellProtection", "#HealthBoost"],
    "low_calorie": ["#LowCalorie", "#WeightManagement", "#SlimmeDown", "#HealthySnack"],
    "organic": ["#Organic", "#NoChemicals", "#FarmFresh", "#Sustainable"],
    "vegan": ["#VeganFriendly", "#PlantBased", "#CrueltyFree", "#VeganLife"],
    "gluten_free": ["#GlutenFree", "#CeliacFriendly", "#GlutenSafe", "#SafeToEat"]
  },
  "seasonal_tags": {
    "spring": ["#SpringFresh", "#SeasonalEats", "#FarmToTable", "#GardenFresh"],
    "summer": ["#SummerVibes", "#LightAndFresh", "#BBQReady", "#SeasonalChoice"],
    "fall": ["#FallFavs", "#CozyFood", "#HarvestTime", "#AutumnEats"],
    "winter": ["#WinterWarmer", "#ComfortFood", "#CozyMeals", "#WarmAndFilling"]
  }
}
```

### caption_templates.json

```json
{
  "excellent": [
    "This green warrior has ZERO oxalate concerns! Load up your plate guilt-free. Perfect for kidney-conscious eating. 💚",
    "Oxalate-free zone! This powerhouse is safe for daily consumption. Your kidneys will thank you. 🌱",
    "The ultimate kidney-friendly choice! Eat this daily without worry. Maximum nutrition, zero oxalate stress. ✨"
  ],
  "great": [
    "Great news! This veggie has minimal oxalate AND packs minerals. Your kidney will thank you. 🥒",
    "Low oxalate + high nutrition = a winning combo! Perfect for regular consumption. 🎯",
    "Budget-friendly AND kidney-friendly! This is a weekday staple you can feel good about. 💚"
  ],
  "good": [
    "This veggie packs nutrition but needs moderation. Pro tip: pair with calcium-rich foods to reduce oxalate absorption! 🥕",
    "Good nutrition here! Enjoy 3-4x per week for balanced health. Smart portions = smart eating. 📊",
    "Nutrient powerhouse with moderate oxalate. The key: smart pairing with dairy or calcium sources. 🧀"
  ],
  "fair": [
    "Love this veggie? Enjoy it 1-2x weekly and pair with cheese or yogurt to minimize oxalate! Smart eating. 🥗",
    "Balance is everything! This one deserves special occasion status. Pair wisely, enjoy modestly. ⚖️",
    "This is better enjoyed as an occasional treat. Combine with calcium-rich foods for best results. 🍽️"
  ],
  "poor": [
    "This favorite is HIGH in oxalate! If you have kidney concerns, save this for special occasions. Quality over quantity. 🌱",
    "High oxalate alert! Limit to 1-2x per month maximum. When you do enjoy it, keep portions tiny. ⚠️",
    "This is a rare indulgence, not a daily choice. If kidney health matters to you, consume sparingly. 🎯"
  ],
  "terrible": [
    "⚠️ WARNING: This is EXTREMELY high in oxalate. If kidney health is a concern, consult your doctor before consuming.",
    "🚫 EXTREME OXALATE: This product requires serious caution. Not recommended for kidney-conscious eating. Speak with your healthcare provider.",
    "HIGH RISK: This item should be avoided entirely if you have kidney concerns. Always check with your doctor first. 👨‍⚕️"
  ]
}
```

---

## 9. Medical Disclaimers & Legal Compliance

### Required Disclaimer Template

Include in every analysis output:

```
⚠️ MEDICAL DISCLAIMER

Stone Cold Tracker analyzes food products based on oxalate content 
and nutritional data but does NOT provide medical advice. This 
analysis is for informational purposes only.

Individuals with kidney disease, kidney stones, or other medical 
conditions should consult their healthcare provider or registered 
dietitian before making significant dietary changes.

All oxalate values are estimates based on research. Individual 
responses vary based on genetics, gut health, medications, and 
absorption capacity.

This tool is not a substitute for professional medical guidance.
```

### Privacy & Data Usage

- No personal health information stored
- No medical history tracking
- User disclaims self-diagnosis
- Link to kidney health organizations for professional guidance

---

## 10. Metrics & Validation

### Accuracy Measurements

```
Scoring Accuracy: Compare agent scores against 
  - Peer-reviewed study data
  - USDA reference values
  - Clinical dietitian assessments
  → Target: >95% alignment

Database Coverage: 
  - Initial target: 100+ verified products
  - Expansion target: 500+ products
  - Coverage metric: Accuracy per category

Caption Engagement:
  - Track Instagram engagement metrics
  - A/B test caption variations
  - Refine based on audience response

Tag Performance:
  - Analyze hashtag reach
  - Monitor trending vs. evergreen tags
  - Optimize seasonal tag timing
```

### Quality Checklist

- [ ] All oxalate values have peer-reviewed sources
- [ ] Multiple data sources available for validation
- [ ] Confidence scores >0.85 for all rated products
- [ ] Medical disclaimers visible on all outputs
- [ ] Captions tested for accuracy with 50+ products
- [ ] Tags generated with at least 50% variety
- [ ] Image recognition tested on 100+ sample images

---

## 11. Success Metrics

### Short-term (3 months)
- [ ] Database populated with 150+ verified foods
- [ ] Scoring engine operational with >90% test coverage
- [ ] Image recognition working on 80%+ of common foods
- [ ] 50+ unique caption variations generated
- [ ] Tag diversity averaging 7+ unique tags per product

### Medium-term (6 months)
- [ ] Database expanded to 300+ foods
- [ ] Scoring accuracy validated against clinical data
- [ ] Image recognition >85% accurate
- [ ] Instagram engagement metrics tracked
- [ ] User feedback integration implemented

### Long-term (12 months)
- [ ] 500+ food products in database
- [ ] Personalized user profiles (preferences, restrictions)
- [ ] Seasonal content calendar automated
- [ ] Trending health topics integration
- [ ] Registered dietitian review & partnership

---

## 12. Next Steps

### Immediate Actions

1. **Data Population** (Priority: HIGH)
   - Start with 50 most common foods
   - Gather oxalate data from USDA FoodData Central
   - Add peer-reviewed source citations

2. **Schema Validation** (Priority: HIGH)
   - Create and test JSON schemas
   - Validate data integrity
   - Build confidence scoring system

3. **Scoring Logic** (Priority: HIGH)
   - Implement multi-factor formula
   - Calibrate weights based on domain expertise
   - Test against 30+ known products

4. **Documentation** (Priority: MEDIUM)
   - Create data source guide
   - Document all assumptions
   - Build medical disclaimer library

5. **Testing Framework** (Priority: MEDIUM)
   - Unit tests for scoring
   - Integration tests for pipeline
   - Accuracy benchmarks

### Long-term Development

Refer to `agent/memory/CHORES.md` for ongoing task tracking.

---

## References & Resources

### Data Sources
- **USDA FoodData Central**: https://fdc.nal.usda.gov/
- **PubMed Central**: https://www.ncbi.nlm.nih.gov/pmc/
- **National Kidney Foundation**: https://www.kidney.org/
- **American Dietary Association**: https://www.eatright.org/

### Peer-Reviewed Research
- Search for: "oxalate bioavailability", "kidney stone prevention", "food mineral content"
- Focus on: Clinical nutrition journals, food science research

### Industry Standards
- USDA Nutrient Database
- FDA Food Allergen Labeling
- Clinical Dietetics Guidelines

---

**Document Version**: 1.0  
**Last Updated**: June 2026  
**Maintainer**: Stone Cold Tracker Development Team  
**Status**: Active Development
