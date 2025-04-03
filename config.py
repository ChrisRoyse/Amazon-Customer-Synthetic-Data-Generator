# config.py - Enhanced for Realistic Customer Diversity
import random
import numpy as np
from collections import defaultdict

# --- Core Simulation Settings ---
NUM_PROFILES_TO_GENERATE = 20000 # Generate 30,000 profiles
SIMULATION_DURATION_YEARS = 5
SIMULATION_DURATION_DAYS = SIMULATION_DURATION_YEARS * 365
OUTPUT_DIR = "."
FILENAME_PREFIX = "amazon_customer_profile_"
FILENAME_DIGITS = 5
START_PROFILE_INDEX = 1
# Probability of a minor life event occurring per year (approx)
MINOR_EVENT_YEARLY_PROB = 0.6

# --- Behavioral Parameter Ranges/Defaults with Distribution Types ---
BEHAVIORAL_PARAMS_CONFIG = {
    # Core Shopping Behaviors
    "activity_level": {"range": (0.05, 0.95), "type": "float", "distribution": "beta", "params": {"alpha": 1.8, "beta": 1.8}}, # (Adjusted alpha/beta for more spread)
    "purchase_frequency": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 3.0}},
    "cart_size_tendency": {"range": (1, 10), "type": "float", "distribution": "exponential", "params": {"scale": 2.0}},
    "price_sensitivity": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 3.0, "beta": 2.0}},
    "brand_loyalty": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 1.7, "beta": 1.7}}, # More spread
    "deal_seeking_propensity": {"range": (0.05, 0.95), "type": "float", "distribution": "beta", "params": {"alpha": 3.0, "beta": 2.0}},
    "impulse_buying_tendency": {"range": (0.05, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 1.8, "beta": 3.5}}, # Slightly adjusted
    # Decision Making Patterns
    "research_depth": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "review_influence": {"range": (0.2, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 3.0, "beta": 2.0}},
    "social_proof_sensitivity": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.5, "beta": 2.0}},
    "risk_tolerance": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.5}},
    "novelty_seeking": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.5}},

    # Category-Specific Behaviors
    "tech_adoption_propensity": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 1.8, "beta": 2.5}},
    "fashion_consciousness": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 2.0}},
    "health_consciousness": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "eco_consciousness": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}},
    "luxury_orientation": {"range": (0.05, 0.9), "type": "float", "distribution": "exponential", "params": {"scale": 0.2}},
    
    # Platform Usage Patterns
    "mobile_usage": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 3.0, "beta": 2.0}},
    "desktop_usage": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.5}},
    "app_usage": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.5, "beta": 2.0}},
    "voice_shopping": {"range": (0.0, 0.7), "type": "float", "distribution": "exponential", "params": {"scale": 0.1}},
    
    # Service Engagement
    "prime_engagement": {"range": (0.2, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 3.0, "beta": 1.5}},
    "prime_video_engagement": {"range": (0.1, 0.85), "type": "float", "distribution": "beta", "params": {"alpha": 2.5, "beta": 2.0}},
    "subscription_services": {"range": (0.1, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}},
    "digital_content_consumption": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "fresh_grocery_usage": {"range": (0.0, 0.8), "type": "float", "distribution": "exponential", "params": {"scale": 0.2}},
    
    # Shopping Style
    "browse_depth": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "cart_abandonment": {"range": (0.1, 0.7), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 3.0}},
    "wishlist_usage": {"range": (0.1, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}},
    "comparison_shopping": {"range": (0.2, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.5, "beta": 2.0}},
    
    # Time-Related Patterns
    "seasonal_shopping": {"range": (0.2, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "time_of_day_preference": {"range": (0, 23), "type": "int", "distribution": "custom_daily"},
    "weekend_shopping": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    
    # Financial Behaviors
    "payment_method_diversity": {"range": (1, 4), "type": "int", "distribution": "poisson", "params": {"lam": 1.5}},
    "installment_usage": {"range": (0.0, 0.7), "type": "float", "distribution": "exponential", "params": {"scale": 0.15}},
    "credit_usage": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    
    # Social Behaviors
    "review_writing": {"range": (0.05, 0.7), "type": "float", "distribution": "exponential", "params": {"scale": 0.15}},
    "question_asking": {"range": (0.05, 0.6), "type": "float", "distribution": "exponential", "params": {"scale": 0.1}},
    "social_sharing": {"range": (0.05, 0.7), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}},
    
    # Customer Service
    "support_contact_rate": {"range": (0.05, 0.5), "type": "float", "distribution": "exponential", "params": {"scale": 0.1}},
    "issue_resolution_patience": {"range": (0.2, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "feedback_provision": {"range": (0.1, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 2.5}},
    
    # Custom Behavioral Traits
    "practical_purchase_bias": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "aesthetic_preference_bias": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "safety_conscious_bias": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.5, "beta": 2.0}},
    "bulk_buying_propensity": {"range": (0.1, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}},
    "quality_preference_bias": {"range": (0.2, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.5, "beta": 2.0}},
    "brand_ethics_importance": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}},
    "time_saving_focus": {"range": (0.2, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "early_adopter_bias": {"range": (0.1, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}},
    "family_oriented_bias": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "minimalist_bias": {"range": (0.1, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}},
    "nostalgia_bias": {"range": (0.1, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.5}},
    "business_oriented_bias": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.5}},
    "home_improvement_focus": {"range": (0, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}},
    "career_focus": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "alexa_shopping_propensity": {"range": (0.0, 0.4), "type": "float", "distribution": "exponential", "params": {"scale": 0.05}}, # Propensity to use Alexa for shopping actions
    "amazon_music_engagement": {"range": (0.1, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.5}}, # Engagement with Amazon Music
    "audible_engagement": {"range": (0.05, 0.7), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}}, # Engagement with Audible
    "brand_affinity_strength": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}}, # How strongly user prefers known brands
    "cart_abandon_propensity": {"range": (0.1, 0.7), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 3.0}}, # Likelihood to abandon cart (synonym for cart_abandonment?)
    "comparison_shopping_prob": {"range": (0.2, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.5, "beta": 2.0}}, # Likelihood to compare products (synonym for comparison_shopping?)
    "impulse_purchase_prob": {"range": (0.05, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}}, # Likelihood of impulse buys (synonym for impulse_buying_tendency?)
    "kindle_engagement": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}}, # Engagement with Kindle books/store
    "page_view_factor": {"range": (0.5, 2.0), "type": "float", "distribution": "normal", "params": {"mean": 1.0, "std_dev": 0.3}}, # Multiplier for page views per session
    "purchase_latency_factor": {"range": (0.3, 3.0), "type": "float", "distribution": "normal", "params": {"mean": 1.0, "std_dev": 0.5}}, # Multiplier for time spent viewing before action
    "return_propensity": {"range": (0.02, 0.4), "type": "float", "distribution": "exponential", "params": {"scale": 0.08}}, # Likelihood to return items
    "review_read_propensity": {"range": (0.2, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 3.0, "beta": 2.0}}, # How likely user is to read reviews (synonym for review_influence?)
    "review_write_propensity": {"range": (0.05, 0.7), "type": "float", "distribution": "exponential", "params": {"scale": 0.15}}, # How likely user is to write reviews (synonym for review_writing?)
    "session_length_factor": {"range": (0.5, 2.5), "type": "float", "distribution": "normal", "params": {"mean": 1.0, "std_dev": 0.4}}, # Multiplier for session duration
    "subscribe_save_propensity": {"range": (0.0, 0.6), "type": "float", "distribution": "exponential", "params": {"scale": 0.1}}, # Likelihood to use Subscribe & Save
    "wishlist_usage_propensity": {"range": (0.1, 0.8), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}}, # Likelihood to use wishlist (synonym for wishlist_usage?)
    "learning_focused_bias": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "leisure_focused_bias": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    # --- Marketing Behavior Ontology (MBO) Parameters ---
    "reward_sensitivity": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.5, "beta": 2.0}, "description": "Sensitivity to rewards, deals, and loyalty programs."},
    "attention_focus": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}, "description": "Level of focus vs. distractibility during browsing/shopping."},
    "category_exploration_propensity": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.5}, "description": "Tendency to explore new product categories vs. sticking to familiar ones."},
    "habit_formation_speed": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 1.5, "beta": 3.0}, "description": "Speed at which habitual behaviors like reordering form."},

}

# --- Shopping Patterns & Timing ---
SHOPPING_PATTERNS = {
    "weekday_distribution": {
        "Monday": 0.12,
        "Tuesday": 0.13,
        "Wednesday": 0.15,
        "Thursday": 0.16,
        "Friday": 0.18,
        "Saturday": 0.15,
        "Sunday": 0.11
    },
    "hourly_distribution": {
        "early_morning": {"hours": range(5, 9), "weight": 0.1},
        "morning": {"hours": range(9, 12), "weight": 0.2},
        "afternoon": {"hours": range(12, 17), "weight": 0.25},
        "evening": {"hours": range(17, 22), "weight": 0.35},
        "late_night": {"hours": [22, 23, 0, 1, 2, 3, 4], "weight": 0.1} # Combined hours for late night
    },
    "seasonal_peaks": {
        "holiday_season": {"months": [11, 12], "boost": 1.5},
        "prime_day": {"months": [7], "days": list(range(10, 17)), "boost": 1.8},
        "black_friday": {"months": [11], "days": list(range(20, 30)), "boost": 2.0},
        "back_to_school": {"months": [8], "boost": 1.3},
        "spring_cleaning": {"months": [3, 4], "boost": 1.2},
        "summer_shopping": {"months": [6, 7], "boost": 1.1},
        "post_holiday": {"months": [1], "days": list(range(1, 15)), "boost": 1.2},
        "tax_refund": {"months": [2, 3], "boost": 1.15}
    }
}
# --- Base Event Weights --- 
# Relative likelihood of different event types occurring, before parameter adjustments
BASE_EVENT_WEIGHTS = {
    # Core Shopping
    "browse_category": 25.0,
    "search": 20.0,
    "view_product": 30.0,
    "add_to_cart": 8.0,
    "remove_from_cart": 2.0,
    "purchase": 5.0,
    "update_wishlist": 3.0,
    "view_review": 10.0,
    "write_review": 0.5,
    "rate_product": 0.8, # Slightly more likely than writing full review
    "return_item": 0.7,
    "track_package": 1.5, # Only relevant after purchase
    # Deals & Coupons
    "view_deal": 4.0,
    "clip_coupon": 2.5,
    # Service Usage
    "watch_prime_video": 6.0,
    "listen_amazon_music": 3.0,
    "read_kindle_book": 2.0,
    "listen_audible": 1.0,
    "alexa_interaction": 4.0,
    "order_whole_foods": 0.5,
    "manage_subscribe_save": 0.6,
    "use_amazon_pharmacy": 0.2,
    "use_amazon_photos": 0.4,
    "view_aws_console": 0.1, # Niche
    # Customer Service (Placeholder - add if needed)
    # "contact_support": 0.3,
    # "view_help_page": 1.0
}

# --- Payment Methods ---
PAYMENT_METHODS = [
    {"type": "Amazon Store Card", "credit_required": True, "rewards": True, "frequency": 0.15},
    {"type": "Amazon Prime Rewards Visa", "credit_required": True, "rewards": True, "frequency": 0.20},
    {"type": "Credit Card", "credit_required": True, "rewards": True, "frequency": 0.35},
    {"type": "Debit Card", "credit_required": False, "rewards": False, "frequency": 0.25},
    {"type": "Bank Account", "credit_required": False, "rewards": False, "frequency": 0.10},
    {"type": "Gift Card", "credit_required": False, "rewards": False, "frequency": 0.15},
    {"type": "Buy Now Pay Later", "credit_required": True, "rewards": False, "frequency": 0.08},
    {"type": "Amazon Pay", "credit_required": False, "rewards": False, "frequency": 0.05},
    {"type": "PayPal", "credit_required": False, "rewards": False, "frequency": 0.07}
]
# --- Brands --- 
# (Add more realistic brands as needed)
BRANDS = [
    "OmniCorp", "Acme", "GenericBrand", "Innovate Inc.", "HomeSphere", 
    "Nature's Best", "Urban Threads", "Summit Gear", "Coastal Co.", 
    "Heritage Brand", "Nova Fashion", "TechCore", "Apex Devices", 
    "Quantum Systems", "ElectroGadget", "KitchenWiz", "ComfortLiving", 
    "DesignHaus", "UrbanFurnish", "FarmFresh", "Pantry Staples", 
    "Gourmet Select", "Healthy Harvest", "ToyWorld", "PlayFun", 
    "KidzKraft", "GameMasters", "BrainyBuilders"
]

# --- Product Naming Components ---
ADJECTIVES1 = ['Premium', 'Basic', 'Advanced', 'Deluxe', 'Standard', 'Pro', 'Lite', 'Ultra', 'Eco']
ADJECTIVES2 = ['Series', 'Model', 'Edition', 'Version', 'Generation', 'Plus', 'Max', 'Mini']
NOUNS = ['Device', 'Item', 'Accessory', 'Gadget', 'Tool', 'Appliance', 'Kit', 'System', 'Unit']
PRODUCT_MODIFIERS = ['for Home', 'for Office', 'Portable', 'Wireless', 'Heavy Duty', 'Compact', 'Smart', '']
# --- Geography & Demographic Distribution ---
# Population distribution based on US Census
US_REGION_DISTRIBUTION = {
    "Northeast": 0.17,  # ME, NH, VT, MA, RI, CT, NY, NJ, PA
    "Midwest": 0.21,    # OH, MI, IN, WI, IL, MN, IA, MO, ND, SD, NE, KS
    "South": 0.38,      # DE, MD, DC, VA, WV, KY, NC, SC, TN, GA, FL, AL, MS, AR, LA, OK, TX
    "West": 0.24        # MT, ID, WY, CO, NM, AZ, UT, NV, WA, OR, CA, AK, HI
}

# States by region for more specific location information
US_STATES_BY_REGION = {
    "Northeast": ["ME", "NH", "VT", "MA", "RI", "CT", "NY", "NJ", "PA"],
    "Midwest": ["OH", "MI", "IN", "WI", "IL", "MN", "IA", "MO", "ND", "SD", "NE", "KS"],
    "South": ["DE", "MD", "DC", "VA", "WV", "KY", "NC", "SC", "TN", "GA", "FL", "AL", "MS", "AR", "LA", "OK", "TX"],
    "West": ["MT", "ID", "WY", "CO", "NM", "AZ", "UT", "NV", "WA", "OR", "CA", "AK", "HI"]
}

# Population density data informing the urban/rural distribution
URBAN_RURAL_DISTRIBUTION = {
    "Dense Urban": 0.25,    # Major city centers
    "Urban": 0.30,          # Cities and large towns
    "Suburban": 0.25,       # Suburbs of cities
    "Small Town": 0.10,     # Small towns
    "Rural": 0.08,          # Rural areas
    "Remote": 0.02          # Very remote areas
}

# Income distribution (approximate US distribution)
INCOME_DISTRIBUTION = {
    "Low (<$30k)": 0.25,
    "Lower-Medium ($30k-$50k)": 0.20,
    "Medium ($50k-$75k)": 0.18,
    "Upper-Medium ($75k-$120k)": 0.20,
    "High ($120k-$200k)": 0.12,
    "Very High (>$200k)": 0.05
}

INCOME_BRACKETS = list(INCOME_DISTRIBUTION.keys())
LOCATION_TYPES = list(URBAN_RURAL_DISTRIBUTION.keys())

# Age distribution (approximate US distribution)
AGE_DISTRIBUTION = {
    (18, 24): 0.12,
    (25, 34): 0.18,
    (35, 44): 0.16,
    (45, 54): 0.15,
    (55, 64): 0.17,
    (65, 74): 0.14,
    (75, 90): 0.08
}

# Household composition distribution
HOUSEHOLD_COMPOSITIONS = [
    "Single", "Couple (No Kids)", "Family (Young Kids)", 
    "Family (Teenagers)", "Roommates", "Single Parent", 
    "Multi-generational", "Empty Nester", "Extended Family"
]

HOUSEHOLD_COMPOSITION_DISTRIBUTION = {
    "Single": 0.28,
    "Couple (No Kids)": 0.25,
    "Family (Young Kids)": 0.14,
    "Family (Teenagers)": 0.12,
    "Roommates": 0.06,
    "Single Parent": 0.09,
    "Multi-generational": 0.04,
    "Empty Nester": 0.01,
    "Extended Family": 0.01
}

# Educational levels
EDUCATION_LEVELS = {
    "Some High School": 0.10,
    "High School Diploma": 0.28,
    "Some College": 0.16,
    "Associate's Degree": 0.10,
    "Bachelor's Degree": 0.22,
    "Master's Degree": 0.10,
    "Doctoral/Professional Degree": 0.04
}

# Employment status
EMPLOYMENT_STATUS = {
    "Full-time": 0.48,
    "Part-time": 0.12,
    "Self-employed": 0.07,
    "Student": 0.08,
    "Retired": 0.16,
    "Unemployed": 0.05,
    "Homemaker": 0.04
}

# --- Device Types & Technical Context ---
DEVICE_TYPES = [
    {"name": "Desktop (Windows)", "platform": "web", "conversion_rate": 0.045},
    {"name": "Desktop (Mac)", "platform": "web", "conversion_rate": 0.048},
    {"name": "Desktop (Linux)", "platform": "web", "conversion_rate": 0.039},
    {"name": "Laptop (Windows)", "platform": "web", "conversion_rate": 0.043},
    {"name": "Laptop (Mac)", "platform": "web", "conversion_rate": 0.046},
    {"name": "Laptop (Chrome OS)", "platform": "web", "conversion_rate": 0.041},
    {"name": "Mobile (iOS - iPhone)", "platform": "app", "conversion_rate": 0.038},
    {"name": "Mobile (iOS - iPhone SE)", "platform": "app", "conversion_rate": 0.036},
    {"name": "Mobile (iOS - iPhone Pro)", "platform": "app", "conversion_rate": 0.040},
    {"name": "Mobile (Android - Samsung)", "platform": "app", "conversion_rate": 0.037},
    {"name": "Mobile (Android - Google)", "platform": "app", "conversion_rate": 0.039},
    {"name": "Mobile (Android - OnePlus)", "platform": "app", "conversion_rate": 0.035},
    {"name": "Mobile (Android - Budget)", "platform": "app", "conversion_rate": 0.030},
    {"name": "Mobile (Web - iOS)", "platform": "web", "conversion_rate": 0.031},
    {"name": "Mobile (Web - Android)", "platform": "web", "conversion_rate": 0.029},
    {"name": "Tablet (iPad)", "platform": "app", "conversion_rate": 0.042},
    {"name": "Tablet (iPad Mini)", "platform": "app", "conversion_rate": 0.040},
    {"name": "Tablet (iPad Pro)", "platform": "app", "conversion_rate": 0.044},
    {"name": "Tablet (Android)", "platform": "app", "conversion_rate": 0.038},
    {"name": "Tablet (Kindle Fire)", "platform": "app", "conversion_rate": 0.041},
    {"name": "Tablet (Web - iOS)", "platform": "web", "conversion_rate": 0.034},
    {"name": "Tablet (Web - Android)", "platform": "web", "conversion_rate": 0.032},
    {"name": "Smart TV (Samsung)", "platform": "app", "conversion_rate": 0.026},
    {"name": "Smart TV (LG)", "platform": "app", "conversion_rate": 0.025},
    {"name": "Smart TV (Roku)", "platform": "app", "conversion_rate": 0.027},
    {"name": "Smart TV (Fire TV)", "platform": "app", "conversion_rate": 0.029},
    {"name": "Smart TV (Apple TV)", "platform": "app", "conversion_rate": 0.027},
    {"name": "Echo Device (Standard)", "platform": "voice", "conversion_rate": 0.030},
    {"name": "Echo Device (Dot)", "platform": "voice", "conversion_rate": 0.028},
    {"name": "Echo Device (Show)", "platform": "voice", "conversion_rate": 0.032},
    {"name": "Gaming Console (PlayStation)", "platform": "app", "conversion_rate": 0.023},
    {"name": "Gaming Console (Xbox)", "platform": "app", "conversion_rate": 0.022},
    {"name": "Gaming Console (Nintendo)", "platform": "app", "conversion_rate": 0.021},
    {"name": "Smartwatch (Apple)", "platform": "app", "conversion_rate": 0.018},
    {"name": "Smartwatch (Samsung)", "platform": "app", "conversion_rate": 0.017},
    {"name": "Smartwatch (Garmin)", "platform": "app", "conversion_rate": 0.016}
]

# Device ownership distribution (percentages who own each type)
DEVICE_OWNERSHIP_DISTRIBUTION = {
    "Smartphone": 0.85,
    "Laptop/Desktop": 0.76,
    "Tablet": 0.53,
    "Smart TV": 0.49,
    "Smart Speaker": 0.32,
    "Smartwatch": 0.21,
    "Gaming Console": 0.39,
    "E-reader": 0.26,
    "Smart Home Device": 0.17
}

# Technical savviness categories
TECH_SAVVINESS_LEVELS = [
    {"level": "Novice", "description": "Basic usage only, limited engagement with technology, tends to stick with familiar interfaces", "params": {"tech_adoption_propensity": 0.2, "mobile_usage": 0.3, "app_usage": 0.2}},
    {"level": "Basic", "description": "Comfortable with technology but not enthusiastic, follows mainstream adoption", "params": {"tech_adoption_propensity": 0.4, "mobile_usage": 0.5, "app_usage": 0.4}},
    {"level": "Intermediate", "description": "Regularly uses technology, adopts new services, has multiple devices", "params": {"tech_adoption_propensity": 0.6, "mobile_usage": 0.7, "app_usage": 0.6}},
    {"level": "Advanced", "description": "Tech-enthusiast, early adopter, uses multiple devices and platforms", "params": {"tech_adoption_propensity": 0.8, "mobile_usage": 0.8, "app_usage": 0.8}},
    {"level": "Expert", "description": "Cutting-edge user, maximizes feature usage, multiple devices across ecosystems", "params": {"tech_adoption_propensity": 0.9, "mobile_usage": 0.9, "app_usage": 0.9}}
]

# Platform usage patterns
PLATFORM_USAGE_DISTRIBUTION = {
    "Primarily Mobile": 0.38,
    "Primarily Desktop": 0.30,
    "Multi-platform": 0.25,
    "Mobile + Voice": 0.04,
    "Desktop + Mobile + Voice": 0.03
}

# Login frequency categories
LOGIN_FREQUENCIES = ["Multiple times a day", "Daily", "Few times a week", "Weekly", "Bi-Weekly", "Monthly", "Quarterly", "Rarely (< Quarterly)"]

# --- Life Stages & Demographic Contexts ---
# More diverse life stages with realistic parameters and interests
LIFE_STAGES = [
    # Young Adults (18-24)
    {"name": "College Student", "age_range": (18, 24), "income_bracket_indices": [0, 1], "employment_status": ["Student", "Part-time"], 
     "interests": ["Textbooks", "Electronics", "Dorm Essentials", "Study Supplies", "Instant Food", "Entertainment", "Budget Fashion", "Fitness Equipment", "Streaming Services"],
     "param_adjustments": {"deal_seeking_propensity": 0.3, "tech_adoption_propensity": 0.2, "price_sensitivity": 0.4}, "weight": 8},
    
    {"name": "Trade School Student", "age_range": (18, 24), "income_bracket_indices": [0, 1, 2], "employment_status": ["Student", "Part-time", "Full-time"],
     "interests": ["Tools", "Work Wear", "Safety Equipment", "Technical Manuals", "Professional Equipment", "Industry Supplies"],
     "param_adjustments": {"deal_seeking_propensity": 0.2, "practical_purchase_bias": 0.3, "brand_loyalty": 0.2}, "weight": 3},
    
    {"name": "Early Career Professional", "age_range": (22, 28), "income_bracket_indices": [1, 2, 3], "employment_status": ["Full-time"], 
     "interests": ["Business Attire", "Professional Development Books", "Office Supplies", "Meal Prep", "Commuting Gear", "Home Basics", "Budget Furniture"],
     "param_adjustments": {"brand_loyalty": 0.1, "comparison_shopping": 0.3, "career_focus": 0.4}, "weight": 12},
    
    {"name": "Service Industry Worker", "age_range": (18, 30), "income_bracket_indices": [0, 1], "employment_status": ["Full-time", "Part-time"], 
     "interests": ["Comfortable Shoes", "Work Clothes", "Energy Drinks", "Quick Meals", "Budget Entertainment", "Mobile Gaming"],
     "param_adjustments": {"deal_seeking_propensity": 0.4, "price_sensitivity": 0.5, "time_saving_focus": 0.3}, "weight": 7},
    
    {"name": "Young Adult Living at Home", "age_range": (18, 25), "income_bracket_indices": [0, 1, 2], "employment_status": ["Student", "Part-time", "Full-time", "Unemployed"], 
     "interests": ["Video Games", "Entertainment", "Electronics", "Personal Care", "Hobby Supplies", "Fashion"],
     "param_adjustments": {"price_sensitivity": 0.2, "impulse_buying_tendency": 0.4, "tech_adoption_propensity": 0.3}, "weight": 6},
    
    {"name": "Military (Early Career)", "age_range": (18, 24), "income_bracket_indices": [1, 2], "employment_status": ["Full-time"], 
     "interests": ["Fitness Equipment", "Tactical Gear", "Portable Electronics", "Outdoor Equipment", "Casual Clothing"],
     "param_adjustments": {"practical_purchase_bias": 0.4, "brand_loyalty": 0.3, "activity_level": 0.2}, "weight": 2},
    
    # Young to Mid Adults (25-34)
    {"name": "Tech Professional", "age_range": (25, 34), "income_bracket_indices": [2, 3, 4, 5], "employment_status": ["Full-time", "Self-employed"], 
     "interests": ["Latest Gadgets", "Smart Home", "Gaming", "Tech Books", "Ergonomic Office", "Software Subscriptions"],
     "param_adjustments": {"tech_adoption_propensity": 0.4, "early_adopter_bias": 0.3, "brand_loyalty": 0.2}, "weight": 10},
    
    {"name": "Creative Professional", "age_range": (25, 34), "income_bracket_indices": [1, 2, 3, 4], "employment_status": ["Full-time", "Part-time", "Self-employed"], 
     "interests": ["Art Supplies", "Photography", "Design Books", "Creative Software", "Studio Equipment", "Premium Coffee"],
     "param_adjustments": {"aesthetic_preference_bias": 0.3, "brand_loyalty": 0.2, "research_depth": 0.2}, "weight": 6},
    
    {"name": "Healthcare Worker", "age_range": (25, 34), "income_bracket_indices": [2, 3, 4, 5], "employment_status": ["Full-time", "Part-time"], 
     "interests": ["Scrubs", "Comfortable Shoes", "Medical References", "Wellness Products", "Quick Meals", "Sleep Aids", "Stress Management"],
     "param_adjustments": {"health_consciousness": 0.3, "time_saving_focus": 0.4, "practical_purchase_bias": 0.3}, "weight": 9},
    
    {"name": "Young Parent", "age_range": (25, 34), "income_bracket_indices": [1, 2, 3, 4], "employment_status": ["Full-time", "Part-time", "Self-employed", "Homemaker"], 
     "interests": ["Baby Essentials", "Child Safety", "Parenting Books", "Family Entertainment", "Time-Saving Devices", "Children's Clothing"],
     "param_adjustments": {"safety_conscious_bias": 0.4, "bulk_buying_propensity": 0.3, "subscription_services": 0.3}, "weight": 11},
    
    {"name": "Urban Professional", "age_range": (27, 38), "income_bracket_indices": [2, 3, 4, 5], "employment_status": ["Full-time", "Self-employed"], 
     "interests": ["Fashion", "Fine Dining", "Travel Gear", "Luxury Accessories", "Smart Home", "Premium Electronics", "Entertainment"],
     "param_adjustments": {"luxury_orientation": 0.3, "tech_adoption_propensity": 0.3, "brand_loyalty": 0.3}, "weight": 8},
    
    {"name": "First-Time Homeowner", "age_range": (26, 35), "income_bracket_indices": [2, 3, 4], "employment_status": ["Full-time", "Self-employed"], 
     "interests": ["Home Improvement", "Tools", "Furniture", "Home Décor", "Appliances", "Gardening", "DIY Books"],
     "param_adjustments": {"home_improvement_focus": 0.4, "research_depth": 0.3, "comparison_shopping": 0.4}, "weight": 7},
    
    # Mid Adults (35-44)
    {"name": "Established Professional", "age_range": (35, 44), "income_bracket_indices": [3, 4, 5], "employment_status": ["Full-time", "Self-employed"], 
     "interests": ["Business Books", "Premium Electronics", "Home Office", "Luxury Items", "Wellness", "Fine Dining", "Smart Home"],
     "param_adjustments": {"brand_loyalty": 0.3, "quality_preference_bias": 0.4, "luxury_orientation": 0.3}, "weight": 14},
    
    {"name": "Mid-Career Parent", "age_range": (35, 44), "income_bracket_indices": [2, 3, 4], "employment_status": ["Full-time", "Part-time", "Self-employed", "Homemaker"], 
     "interests": ["Family Activities", "Educational Toys", "Home Organization", "Bulk Groceries", "Family Entertainment", "Children's Sports Equipment"],
     "param_adjustments": {"bulk_buying_propensity": 0.3, "family_oriented_bias": 0.4, "subscription_services": 0.3}, "weight": 15},
    
    {"name": "Small Business Owner", "age_range": (35, 44), "income_bracket_indices": [2, 3, 4, 5], "employment_status": ["Self-employed"], 
     "interests": ["Business Supplies", "Office Equipment", "Professional Services", "Industry Publications", "Business Software"],
     "param_adjustments": {"business_oriented_bias": 0.4, "practical_purchase_bias": 0.3, "research_depth": 0.3}, "weight": 5},
    
    # Mid to Late Adults (45-54)
    {"name": "Senior Professional", "age_range": (45, 54), "income_bracket_indices": [3, 4, 5], "employment_status": ["Full-time", "Self-employed"], 
     "interests": ["Premium Products", "Investment Books", "Luxury Travel", "High-End Electronics", "Home Improvement", "Wine & Spirits"],
     "param_adjustments": {"quality_preference_bias": 0.4, "brand_loyalty": 0.3, "luxury_orientation": 0.4}, "weight": 13},
    
    {"name": "Parent of Teenagers", "age_range": (40, 54), "income_bracket_indices": [2, 3, 4], "employment_status": ["Full-time", "Part-time", "Self-employed", "Homemaker"], 
     "interests": ["Teen Electronics", "College Prep", "Family Entertainment", "Household Organization", "Teen Fashion", "Sports Equipment"],
     "param_adjustments": {"family_oriented_bias": 0.3, "bulk_buying_propensity": 0.2, "research_depth": 0.3}, "weight": 12},
    
    {"name": "Career Changer", "age_range": (40, 54), "income_bracket_indices": [1, 2, 3, 4], "employment_status": ["Full-time", "Part-time", "Self-employed", "Student"], 
     "interests": ["Educational Materials", "Career Books", "Professional Development", "Home Office", "Stress Management", "Productivity Tools"],
     "param_adjustments": {"learning_focused_bias": 0.3, "career_focus": 0.4, "research_depth": 0.3}, "weight": 4},
    
    # Late Adults (55+)
    {"name": "Active Retiree", "age_range": (55, 75), "income_bracket_indices": [2, 3, 4], "employment_status": ["Retired", "Part-time"], 
     "interests": ["Travel", "Hobbies", "Health Products", "Garden", "Entertainment", "Books", "Outdoor Activities"],
     "param_adjustments": {"leisure_focused_bias": 0.4, "health_consciousness": 0.3, "quality_preference_bias": 0.3}, "weight": 10},
    
    {"name": "Grandparent", "age_range": (55, 80), "income_bracket_indices": [1, 2, 3, 4], "employment_status": ["Retired", "Part-time", "Full-time"], 
     "interests": ["Gifts for Grandkids", "Crafts", "Family Games", "Comfort Items", "Traditional Products", "Photography", "Holiday Decorations"],
     "param_adjustments": {"family_oriented_bias": 0.4, "nostalgia_bias": 0.3, "seasonal_shopping": 0.4}, "weight": 9},
    
    {"name": "Tech-Savvy Senior", "age_range": (60, 80), "income_bracket_indices": [2, 3, 4], "employment_status": ["Retired", "Part-time", "Self-employed"], 
     "interests": ["Electronics", "Smart Home", "Digital Content", "Online Learning", "Tech Gadgets", "Photography", "Health Tech"],
     "param_adjustments": {"tech_adoption_propensity": 0.3, "learning_focused_bias": 0.3, "research_depth": 0.4}, "weight": 5},
    
    # Special Categories (Across Age Ranges)
    {"name": "Luxury Shopper", "age_range": (30, 65), "income_bracket_indices": [4, 5], "employment_status": ["Full-time", "Self-employed"], 
     "interests": ["Designer Fashion", "Luxury Electronics", "Fine Jewelry", "Premium Home Goods", "Gourmet Food & Wine", "High-End Beauty"],
     "param_adjustments": {"luxury_orientation": 0.8, "brand_loyalty": 0.4, "quality_preference_bias": 0.5, "price_sensitivity": -0.3}, "weight": 3},
    
    {"name": "Minimalist", "age_range": (25, 55), "income_bracket_indices": [1, 2, 3, 4, 5], "employment_status": ["Full-time", "Part-time", "Self-employed"], 
     "interests": ["Sustainable Products", "Multi-purpose Items", "Quality Basics", "Digital Content", "Experiential Purchases", "Organization Solutions"],
     "param_adjustments": {"minimalist_bias": 0.5, "quality_preference_bias": 0.4, "eco_consciousness": 0.3}, "weight": 4},
    
    {"name": "Eco-Conscious Consumer", "age_range": (18, 70), "income_bracket_indices": [1, 2, 3, 4, 5], "employment_status": ["Full-time", "Part-time", "Self-employed", "Student", "Retired"], 
     "interests": ["Sustainable Products", "Eco-Friendly Packaging", "Organic Food", "Energy Efficient Devices", "Environmental Books", "Second-Hand Items"],
     "param_adjustments": {"eco_consciousness": 0.6, "research_depth": 0.4, "brand_ethics_importance": 0.5}, "weight": 6},
    
    {"name": "Deal Hunter", "age_range": (25, 65), "income_bracket_indices": [0, 1, 2, 3, 4], "employment_status": ["Full-time", "Part-time", "Self-employed", "Student", "Homemaker", "Retired"], 
     "interests": ["Clearance Items", "Couponing", "Warehouse Deals", "Refurbished Electronics", "Outlet Shopping", "Discount Brands", "Sale Events"],
     "param_adjustments": {"deal_seeking_propensity": 0.7, "price_sensitivity": 0.6, "comparison_shopping": 0.5}, "weight": 7}
]

# --- Expanded Interest Categories ---
BASE_INTEREST_CATEGORIES = [
    # Technology & Electronics
    "Smartphones & Accessories", "Laptops & Computing", "Gaming & VR", "Smart Home Devices", "Wearable Tech",
    "Audio Equipment", "Photography & Video", "Home Theater", "Computer Components", "Network & WiFi",
    "Tech Protection & Security", "Charging & Power", "Streaming Devices", "Digital Storage", "Tech Repair Tools",
    
    # Home & Living
    "Furniture & Decor", "Kitchen & Dining", "Bed & Bath", "Storage & Organization", "Cleaning Supplies",
    "Home Improvement", "Garden & Outdoor", "Smart Home Integration", "Home Security", "Seasonal Decor",
    "Pet Supplies", "Laundry & Garment Care", "Home Safety", "Air Quality & Climate", "Pest Control",
    
    # Health & Wellness
    "Fitness Equipment", "Vitamins & Supplements", "Personal Care", "Mental Wellness", "Sleep & Recovery",
    "Medical Supplies", "Natural Remedies", "Fitness Tracking", "Massage & Relaxation", "Air Purification",
    "Water Filtration", "Oral Care", "Vision Care", "First Aid", "Mobility Assistance",
    
    # Fashion & Accessories
    "Casual Wear", "Professional Attire", "Athletic Wear", "Shoes & Footwear", "Accessories & Jewelry",
    "Designer Brands", "Sustainable Fashion", "Seasonal Clothing", "Special Occasion", "Fashion Tech",
    "Handbags & Wallets", "Watches", "Eyewear", "Children's Clothing", "Maternity Wear",
    
    # Food & Beverage
    "Grocery Staples", "Specialty Foods", "Beverages & Drinks", "Snacks & Treats", "Organic & Natural",
    "International Foods", "Meal Prep", "Diet Specific", "Coffee & Tea", "Wine & Spirits",
    "Baking Supplies", "Condiments & Sauces", "Meat & Seafood", "Dairy & Eggs", "Produce",
    
    # Entertainment & Media
    "Streaming Services", "Gaming", "Books (Physical)", "eBooks", "Audiobooks", 
    "Music (Digital)", "Movies & TV (Digital)", "Board Games", "Outdoor Recreation", "Arts & Crafts", 
    "Musical Instruments", "Collectibles", "Toys & Games", "Hobby Supplies", "Subscription Boxes",
    
    # Work & Professional
    "Office Supplies", "Business Equipment", "Professional Development", "Work From Home", "Business Services",
    "Industry Tools", "Safety Equipment", "Professional References", "Networking Tools", "Business Software",
    "Education & Teaching", "Legal Services", "Financial Services", "HR & Recruiting", "Marketing Materials",
    
    # Special Interests & Hobbies
    "Photography", "Art Supplies", "Crafting", "DIY Tools", "Gardening",
    "Cooking & Baking", "Sports Equipment", "Travel Gear", "Collecting", "Music Making",
    "Outdoor Adventure", "Camping & Hiking", "Fishing & Hunting", "Winter Sports", "Water Sports",
    
    # Family & Kids
    "Baby Essentials", "Kids Clothing", "Educational Toys", "Family Games", "Child Safety",
    "School Supplies", "Kids Tech", "Family Activities", "Parenting Tools", "Kids Room",
    "Baby Feeding", "Diapering", "Children's Books", "Kids Furniture", "Pregnancy & Maternity",
    
    # Automotive & Industrial
    "Car Accessories", "Motorcycle Gear", "Vehicle Maintenance", "Tools & Equipment", "Car Electronics",
    "RV & Camping", "Automotive Safety", "Industrial Supplies", "Janitorial & Sanitation", "Material Handling",
    
    # Specialty Categories
    "Sustainable Products", "Luxury Items", "Handmade Goods", "Vintage & Antique", "Limited Editions",
    "Local Products", "Seasonal Items", "Personalized Items", "Subscription Boxes", "Gift Sets",
    "Cultural Products", "Religious Items", "Charity & Causes", "Celebrity Brands", "Trending Products"
]

# --- Amazon Services ---
AMAZON_SERVICES = [
    "Prime Membership", "Prime Video", "Amazon Music Unlimited", "Prime Music (Bundled)", "Kindle Unlimited", 
    "Prime Reading", "Audible Plus", "Audible Premium Plus", "Amazon Photos", "Amazon Drive", 
    "Subscribe & Save", "Amazon Fresh", "Whole Foods Delivery", "Amazon Pharmacy", "Amazon Care", 
    "Amazon Protect", "Amazon Explore", "Amazon Home Services", "Amazon Key", "Amazon Business", 
    "AWS Personal", "Amazon Handmade", "Amazon Launchpad", "Amazon Warehouse", "Amazon Outlet", 
    "Amazon Luna", "Amazon Kids+", "Amazon Renewed", "Amazon Custom", "Alexa Skills",
    "Amazon Prime Wardrobe", "Amazon Prime Try Before You Buy", "Amazon Family", "Amazon Dash", 
    "Lightning Deals Access", "Prime Day Access", "Prime Early Access", "Prime Exclusive Deals"
]
# --- Search Types ---
SEARCH_TYPES = ["Product Search", "Information Search", "Media Search", "How-to Search"]

# --- Return Reasons ---
RETURN_REASONS = [
    "Defective/Does not work properly", "Wrong item was sent", "Changed mind", 
    "Found better price elsewhere", "Item doesn't fit", "Not as described on website",
    "Accidental order", "Arrived too late", "Damaged during shipping", "No longer needed"
]

# --- Alexa Intents ---
ALEXA_INTENTS = [
    "Play Music", "Set Timer", "Check Weather", "Ask Question", "Control Smart Home", 
    "Order Product", "Shopping List Add/Remove", "Check Order Status", "Get News", 
    "Set Reminder", "Tell Joke", "Get Traffic Update"
]

# --- Expanded Minor Life Events ---
MINOR_LIFE_EVENT_TYPES = [
    # Career & Work Life
    {"name": "Job Promotion", "effect": {"param_adjust": {"activity_level": 0.1, "luxury_orientation": 0.1}, "interest_shift": ["Professional Attire", "Office Upgrades", "Success Books"]}},
    {"name": "Career Change", "effect": {"param_adjust": {"learning_focused_bias": 0.2}, "interest_shift": ["Educational Materials", "Professional Development", "Industry Specific Items"]}},
    {"name": "Started Side Business", "effect": {"param_adjust": {"business_oriented_bias": 0.2}, "interest_shift": ["Business Supplies", "Marketing Materials", "Home Office"]}},
    {"name": "Work From Home Transition", "effect": {"param_adjust": {"home_improvement_focus": 0.3}, "interest_shift": ["Home Office", "Ergonomic Furniture", "Video Conference Gear"]}},
    {"name": "Career Certification", "effect": {"param_adjust": {"career_focus": 0.2}, "interest_shift": ["Professional References", "Educational Materials", "Professional Development"]}},
    {"name": "Job Loss", "effect": {"param_adjust": {"price_sensitivity": 0.3, "deal_seeking_propensity": 0.3}, "interest_shift": ["Career Books", "Budget Items", "Professional Development"]}},
    {"name": "Retirement", "effect": {"param_adjust": {"leisure_focused_bias": 0.3}, "interest_shift": ["Hobbies", "Travel Gear", "Health Products"]}},
    
    # Home & Living Situation
    {"name": "New Pet", "effect": {"param_adjust": {"activity_level": 0.1}, "interest_shift": ["Pet Supplies", "Pet Care", "Home Protection"]}},
    {"name": "Home Renovation", "effect": {"param_adjust": {"home_improvement_focus": 0.3}, "interest_shift": ["Tools", "Home Decor", "Furniture"]}},
    {"name": "Downsizing", "effect": {"param_adjust": {"minimalist_bias": 0.2}, "interest_shift": ["Storage Solutions", "Organization", "Space Saving"]}},
    {"name": "Garden/Yard Project", "effect": {"param_adjust": {"outdoor_focus": 0.2}, "interest_shift": ["Garden Tools", "Plants", "Outdoor Decor"]}},
    {"name": "Move to New Home", "effect": {"param_adjust": {"home_improvement_focus": 0.3}, "interest_shift": ["Home Essentials", "Furniture", "Moving Supplies"]}},
    {"name": "Roommate Change", "effect": {"param_adjust": {"activity_level": 0.1}, "interest_shift": ["Home Organization", "Kitchen Supplies", "Household Essentials"]}},
    {"name": "Home Appliance Upgrade", "effect": {"param_adjust": {"home_improvement_focus": 0.2}, "interest_shift": ["Appliances", "Smart Home", "Kitchen Gadgets"]}},
    
    # Health & Lifestyle
    {"name": "New Fitness Goal", "effect": {"param_adjust": {"health_consciousness": 0.2}, "interest_shift": ["Fitness Equipment", "Workout Clothes", "Supplements"]}},
    {"name": "Dietary Change", "effect": {"param_adjust": {"health_consciousness": 0.2}, "interest_shift": ["Specialty Foods", "Kitchen Gadgets", "Cookbooks"]}},
    {"name": "New Health Focus", "effect": {"param_adjust": {"health_consciousness": 0.2}, "interest_shift": ["Health Products", "Vitamins", "Wellness Books"]}},
    {"name": "Sleep Improvement Focus", "effect": {"param_adjust": {"health_consciousness": 0.2}, "interest_shift": ["Bedding", "Sleep Aids", "Relaxation"]}},
    {"name": "Minor Health Issue", "effect": {"param_adjust": {"health_consciousness": 0.3}, "interest_shift": ["Medical Supplies", "Health Products", "Comfort Items"]}},
    {"name": "Wellness Retreat/Program", "effect": {"param_adjust": {"health_consciousness": 0.2}, "interest_shift": ["Wellness Books", "Fitness Equipment", "Health Foods"]}},
    {"name": "New Doctor/Healthcare Provider", "effect": {"param_adjust": {"health_consciousness": 0.1}, "interest_shift": ["Medical Supplies", "Health Products", "Personal Care"]}},
    
    # Hobbies & Interests
    {"name": "Started Gaming", "effect": {"param_adjust": {"tech_adoption_propensity": 0.2}, "interest_shift": ["Video Games", "Gaming Gear", "Gaming Furniture"]}},
    {"name": "Photography Interest", "effect": {"param_adjust": {"aesthetic_preference_bias": 0.2}, "interest_shift": ["Cameras", "Photography Gear", "Editing Software"]}},
    {"name": "Music Learning", "effect": {"param_adjust": {"creative_focus": 0.2}, "interest_shift": ["Musical Instruments", "Music Books", "Audio Equipment"]}},
    {"name": "Art/Craft Interest", "effect": {"param_adjust": {"creative_focus": 0.2}, "interest_shift": ["Art Supplies", "Craft Tools", "Creative Books"]}},
    {"name": "Cooking Interest", "effect": {"param_adjust": {"culinary_focus": 0.2}, "interest_shift": ["Kitchen Gadgets", "Cookware", "Specialty Ingredients"]}},
    {"name": "Started Collecting", "effect": {"param_adjust": {"research_depth": 0.2}, "interest_shift": ["Collectibles", "Storage/Display", "Reference Materials"]}},
    {"name": "Outdoor Hobby Adoption", "effect": {"param_adjust": {"activity_level": 0.2}, "interest_shift": ["Outdoor Gear", "Specialty Clothing", "Adventure Equipment"]}},
    
    # Technology Adoption
    {"name": "Smart Home Addition", "effect": {"param_adjust": {"tech_adoption_propensity": 0.2}, "interest_shift": ["Smart Devices", "Home Automation", "Tech Accessories"]}},
    {"name": "New Device Ecosystem", "effect": {"param_adjust": {"tech_adoption_propensity": 0.3}, "interest_shift": ["Electronics", "Tech Accessories", "Digital Services"]}},
    {"name": "Digital Security Focus", "effect": {"param_adjust": {"tech_adoption_propensity": 0.2}, "interest_shift": ["Security Devices", "Privacy Tools", "Tech Protection"]}},
    {"name": "Subscription Service Adoption", "effect": {"param_adjust": {"subscription_services": 0.3}, "interest_shift": ["Digital Content", "Streaming Services", "Subscription Boxes"]}},
    {"name": "Social Media Platform Adoption", "effect": {"param_adjust": {"social_sharing": 0.2}, "interest_shift": ["Mobile Accessories", "Photography Gear", "Tech Gadgets"]}},
    {"name": "Remote Work Tech Upgrade", "effect": {"param_adjust": {"tech_adoption_propensity": 0.2}, "interest_shift": ["Home Office", "Computer Accessories", "Video Conferencing"]}},
    
    # Social & Family
    {"name": "New Social Circle", "effect": {"param_adjust": {"social_influence": 0.2}, "interest_shift": ["Social Activities", "Group Games", "Entertainment"]}},
    {"name": "Family Member Visit", "effect": {"param_adjust": {"family_oriented_bias": 0.2}, "interest_shift": ["Guest Supplies", "Entertainment", "Home Comfort"]}},
    {"name": "Holiday Hosting", "effect": {"param_adjust": {"entertaining_focus": 0.2}, "interest_shift": ["Party Supplies", "Kitchen Gear", "Home Decor"]}},
    {"name": "New Relationship", "effect": {"param_adjust": {"activity_level": 0.2}, "interest_shift": ["Date Night Items", "Gifts", "Home Updates"]}},
    {"name": "Relationship Status Change", "effect": {"param_adjust": {"activity_level": 0.1, "home_improvement_focus": 0.2}, "interest_shift": ["Home Decor", "Self-Care", "Personal Development"]}},
    {"name": "Friend's Life Event", "effect": {"param_adjust": {"social_sharing": 0.1}, "interest_shift": ["Gift Items", "Celebration Supplies", "Event-Specific Goods"]}},
    {"name": "New Cultural Interest", "effect": {"param_adjust": {"novelty_seeking": 0.2}, "interest_shift": ["Cultural Books", "Specialty Foods", "International Products"]}},
    
    # Financial Changes
    {"name": "Minor Income Increase", "effect": {"param_adjust": {"price_sensitivity": -0.1, "luxury_orientation": 0.1}, "interest_shift": ["Quality Upgrades", "Premium Versions", "Home Improvements"]}},
    {"name": "Budget Constraints", "effect": {"param_adjust": {"price_sensitivity": 0.3, "deal_seeking_propensity": 0.3}, "interest_shift": ["Budget Items", "Essential Goods", "DIY Supplies"]}},
    {"name": "Financial Planning Focus", "effect": {"param_adjust": {"research_depth": 0.2}, "interest_shift": ["Finance Books", "Planning Tools", "Organization Solutions"]}},
    {"name": "Investment Interest", "effect": {"param_adjust": {"research_depth": 0.2, "risk_tolerance": 0.1}, "interest_shift": ["Finance Books", "Business News", "Premium Digital Content"]}},
    {"name": "Large Purchase Planning", "effect": {"param_adjust": {"research_depth": 0.3, "comparison_shopping": 0.3}, "interest_shift": ["Research Materials", "Product Comparisons", "Review Subscriptions"]}},
    
    # Seasonal & Environmental
    {"name": "Seasonal Wardrobe Update", "effect": {"param_adjust": {"seasonal_shopping": 0.3}, "interest_shift": ["Seasonal Clothing", "Weather Appropriate Gear", "Fashion Accessories"]}},
    {"name": "Holiday Preparation", "effect": {"param_adjust": {"seasonal_shopping": 0.4}, "interest_shift": ["Holiday Decor", "Gift Items", "Entertaining Supplies"]}},
    {"name": "Climate/Weather Adaptation", "effect": {"param_adjust": {"seasonal_shopping": 0.3}, "interest_shift": ["Weather Protection", "Home Climate Control", "Emergency Supplies"]}},
    {"name": "Eco-Friendly Lifestyle Shift", "effect": {"param_adjust": {"eco_consciousness": 0.3}, "interest_shift": ["Sustainable Products", "Eco-Friendly Alternatives", "Reusable Items"]}},
    {"name": "Local Environmental Event", "effect": {"param_adjust": {"activity_level": 0.1}, "interest_shift": ["Emergency Supplies", "Home Safety", "Protective Equipment"]}}
]

# --- Major Life Events (Less Frequent but Higher Impact) ---
MAJOR_LIFE_EVENT_TYPES = [
    {"name": "Marriage/Partnership", "frequency": 0.02, "effect": {"param_adjust": {"family_oriented_bias": 0.4, "home_improvement_focus": 0.3}, "interest_shift": ["Home Essentials", "Furniture", "Registry Items", "Couple Activities"]}},
    {"name": "Divorce/Separation", "frequency": 0.01, "effect": {"param_adjust": {"activity_level": 0.2, "price_sensitivity": 0.2}, "interest_shift": ["Home Essentials", "Self-Help", "Organization", "New Hobbies"]}},
    {"name": "New Child", "frequency": 0.02, "effect": {"param_adjust": {"family_oriented_bias": 0.5, "safety_conscious_bias": 0.4}, "interest_shift": ["Baby Essentials", "Child Safety", "Parenting Books", "Family Activities"]}},
    {"name": "Child Leaving Home", "frequency": 0.01, "effect": {"param_adjust": {"leisure_focused_bias": 0.3, "home_improvement_focus": 0.2}, "interest_shift": ["Travel", "Hobbies", "Home Updates", "Personal Development"]}},
    {"name": "Major Relocation", "frequency": 0.03, "effect": {"param_adjust": {"activity_level": 0.3, "home_improvement_focus": 0.4}, "interest_shift": ["Moving Supplies", "Furniture", "Home Essentials", "Local Resources"]}},
    {"name": "Major Career Shift", "frequency": 0.02, "effect": {"param_adjust": {"career_focus": 0.4, "learning_focused_bias": 0.3}, "interest_shift": ["Professional Development", "Career Books", "Industry Tools", "Work Attire"]}},
    {"name": "Significant Health Event", "frequency": 0.01, "effect": {"param_adjust": {"health_consciousness": 0.5, "research_depth": 0.3}, "interest_shift": ["Medical Supplies", "Health Books", "Wellness Products", "Adaptive Equipment"]}},
    {"name": "Home Purchase", "frequency": 0.02, "effect": {"param_adjust": {"home_improvement_focus": 0.5, "research_depth": 0.3}, "interest_shift": ["Home Essentials", "Tools", "Furniture", "Home Improvement"]}},
    {"name": "Retirement", "frequency": 0.01, "effect": {"param_adjust": {"leisure_focused_bias": 0.4, "health_consciousness": 0.3}, "interest_shift": ["Travel", "Hobbies", "Health Products", "Home Comfort"]}},
    {"name": "Major Financial Change", "frequency": 0.01, "effect": {"param_adjust": {"price_sensitivity": 0.4, "research_depth": 0.3}, "interest_shift": ["Financial Planning", "Budget Solutions", "Investment Resources"]}}
]
