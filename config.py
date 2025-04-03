# config.py - Refactored for Behavioral Parameters

import random

# --- Core Simulation Settings ---
NUM_PROFILES_TO_GENERATE = 25000 # Generate 25,000 profiles
SIMULATION_DURATION_YEARS = 5
SIMULATION_DURATION_DAYS = SIMULATION_DURATION_YEARS * 365
OUTPUT_DIR = "."
FILENAME_PREFIX = "amazon_customer_profile_"
FILENAME_DIGITS = 5 # For 00001 to 25000
START_PROFILE_INDEX = 1
# File size limits removed - prioritizing detail

# --- Foundational Demographic/Contextual Constants ---

INCOME_BRACKETS = ["Low (<$30k)", "Lower-Medium ($30k-$50k)", "Medium ($50k-$75k)", "Upper-Medium ($75k-$120k)", "High ($120k-$200k)", "Very High (>$200k)"]
LOCATION_TYPES = ["Dense Urban", "Urban", "Suburban", "Small Town", "Rural", "Remote"]
HOUSEHOLD_COMPOSITIONS = ["Single", "Couple (No Kids)", "Family (Young Kids)", "Family (Teenagers)", "Roommates", "Single Parent", "Multi-generational"]
DEVICE_TYPES = ["Mobile App (iOS)", "Mobile App (Android)", "Desktop Website (Windows)", "Desktop Website (Mac)", "Tablet App (iPad)", "Tablet App (Android)", "Fire TV", "Echo Device", "Kindle Reader", "Smart Watch", "Other Smart Home Device"]
LOGIN_FREQUENCIES = ["Multiple times a day", "Daily", "Few times a week", "Weekly", "Bi-Weekly", "Monthly", "Quarterly", "Rarely (< Quarterly)"] # Used for initial estimate, activity drives events

# --- Life Stages (Influence Interests and Parameter Distributions) ---
# Still useful for setting context and initial interests
LIFE_STAGES = [
    {"name": "Student", "age_range": (18, 24), "income_bracket_indices": [0, 1, 2], "interests": ["Books", "Textbooks", "Electronics", "Software", "Office Products", "Clothing", "Snacks", "Video Games", "Streaming Services"], "param_adjustments": {"deal_seeking_propensity": 0.2, "purchase_latency_factor": -0.1, "brand_affinity_strength": -0.1}},
    {"name": "Young Professional", "age_range": (25, 34), "income_bracket_indices": [2, 3, 4], "interests": ["Electronics", "Clothing", "Home Decor", "Travel", "Fitness", "Career & Business Books", "Restaurants", "Entertainment"], "param_adjustments": {"tech_adoption_propensity": 0.1, "purchase_latency_factor": -0.1}},
    {"name": "Established Professional", "age_range": (35, 54), "income_bracket_indices": [4, 5], "interests": ["Automotive", "Tools & Home Improvement", "Finance Books", "Luxury Goods", "Travel", "Wine & Spirits", "Smart Home"], "param_adjustments": {"brand_affinity_strength": 0.1, "purchase_latency_factor": 0.1}},
    {"name": "Parent (Young Children)", "age_range": (25, 44), "income_bracket_indices": [2, 3, 4], "interests": ["Toys & Games", "Baby Products", "Children's Clothing", "Grocery", "Household Supplies", "Parenting Books", "Streaming Services (Kids)", "Subscribe & Save"], "param_adjustments": {"subscribe_save_propensity": 0.3, "activity_level_boost": 0.1, "purchase_latency_factor": 0.1}},
    {"name": "Parent (Teenagers)", "age_range": (40, 59), "income_bracket_indices": [3, 4, 5], "interests": ["Electronics", "Video Games", "Sports Equipment", "Clothing", "School Supplies", "Grocery", "Automotive", "Entertainment"], "param_adjustments": {"activity_level_boost": 0.05}},
    {"name": "Empty Nester", "age_range": (50, 69), "income_bracket_indices": [3, 4, 5], "interests": ["Travel", "Hobbies & Crafts", "Garden & Outdoor", "Health & Wellness", "Books", "Home Improvement", "Wine & Spirits", "Restaurants"], "param_adjustments": {"purchase_latency_factor": 0.2, "deal_seeking_propensity": -0.1}},
    {"name": "Retiree", "age_range": (65, 90), "income_bracket_indices": [1, 2, 3, 4], "interests": ["Books", "Health & Personal Care", "Grocery", "Comfort", "Hobbies", "Travel", "Garden & Outdoor", "Streaming Services"], "param_adjustments": {"tech_adoption_propensity": -0.2, "deal_seeking_propensity": 0.1, "activity_level_boost": -0.1}},
]

# --- Behavioral Parameter Ranges/Defaults ---
# These define the *potential range* for individual profiles.
# Each profile gets its own specific value sampled from these ranges (or distributions).
# Values typically 0-1 represent probabilities or normalized tendencies.
# Factors > 1 or < 1 act as multipliers.
BEHAVIORAL_PARAMS_CONFIG = {
    "activity_level": {"range": (0.05, 0.95), "type": "float"}, # Base tendency for interaction frequency
    "review_read_propensity": {"range": (0.05, 0.95), "type": "float"}, # Likelihood to view reviews before purchase
    "review_write_propensity": {"range": (0.01, 0.50), "type": "float"}, # Likelihood to write reviews post-purchase
    "purchase_latency_factor": {"range": (0.3, 4.0), "type": "float"}, # Multiplier for time between interest & purchase (lower=faster)
    "deal_seeking_propensity": {"range": (0.05, 0.95), "type": "float"}, # Tendency to look for/use deals, coupons, sales
    "brand_affinity_strength": {"range": (0.05, 0.90), "type": "float"}, # Likelihood to repurchase same brand vs explore
    "tech_adoption_propensity": {"range": (0.1, 0.9), "type": "float"}, # Tendency to use newer features/devices/services
    "cart_abandon_propensity": {"range": (0.05, 0.70), "type": "float"}, # Likelihood to abandon cart before purchase
    "return_propensity": {"range": (0.02, 0.40), "type": "float"}, # Likelihood to return items post-purchase
    "session_length_factor": {"range": (0.5, 2.5), "type": "float"}, # Multiplier for average session duration
    "page_view_factor": {"range": (0.5, 3.0), "type": "float"}, # Multiplier for average page views/session
    "comparison_shopping_prob": {"range": (0.1, 0.9), "type": "float"}, # Likelihood to use comparison features or view multiple similar items
    "subscribe_save_propensity": {"range": (0.0, 0.8), "type": "float"}, # Likelihood to use Subscribe & Save
    "wishlist_usage_propensity": {"range": (0.05, 0.9), "type": "float"}, # Tendency to use wishlist feature
    "impulse_purchase_prob": {"range": (0.01, 0.30), "type": "float"}, # Base probability of making an unplanned purchase per session/opportunity
    "prime_video_engagement": {"range": (0.1, 0.9), "type": "float"}, # If Prime, how likely to watch video
    "amazon_music_engagement": {"range": (0.1, 0.8), "type": "float"}, # If Prime/Music sub, how likely to listen
    "kindle_engagement": {"range": (0.1, 0.9), "type": "float"}, # If Kindle access/interest, how likely to read
    "audible_engagement": {"range": (0.1, 0.8), "type": "float"}, # If Audible access/interest, how likely to listen
    "alexa_shopping_propensity": {"range": (0.0, 0.3), "type": "float"}, # If has Alexa, likelihood to use it for shopping tasks
}

# --- Interests & Categories ---
BASE_INTEREST_CATEGORIES = [
    # Core Retail
    "Electronics", "Computers & Accessories", "Software", "Video Games", "Smart Home",
    "Clothing", "Shoes", "Jewelry", "Watches", "Handbags & Accessories", "Luggage",
    "Home & Kitchen", "Furniture", "Home Decor", "Bed & Bath", "Appliances",
    "Tools & Home Improvement", "Garden & Outdoor", "Patio & Lawn",
    "Grocery & Gourmet Food", "Whole Foods Market", "Health & Personal Care", "Beauty & Grooming", "Luxury Beauty",
    "Toys & Games", "Baby Products",
    "Sports & Outdoors", "Fitness & Exercise", "Camping & Hiking",
    "Automotive", "Motorcycle & Powersports", "Industrial & Scientific",
    "Pet Supplies", "Office Products", "School Supplies",
    "Arts, Crafts & Sewing", "Hobbies",
    "Gift Cards", "Collectibles & Fine Art",
    "Musical Instruments", "Camera & Photo",
    # Media & Content
    "Movies & TV (Buy/Rent)", "Prime Video", "Digital Music (Buy)", "Amazon Music", "Books (Physical)", "Kindle Store", "Audible Books & Originals", "Magazine Subscriptions",
    # Amazon Specific Programs/Services
    "Amazon Prime", "Subscribe & Save", "Amazon Fresh", "Amazon Pharmacy", "Alexa Skills",
    "Amazon Business", "AWS", "Amazon Handmade", "Amazon Launchpad",
    "Amazon Warehouse Deals", "Amazon Outlet", "Amazon Photos", "Amazon Drive",
    # Abstract/Behavioral
    "Deals & Bargains", "Sustainable Products", "Used & Renewed", "Travel", "Business & Investing", "Career Development", "Self-Help", "Cookbooks", "Parenting",
]

# --- Amazon Services (Used to determine potential actions) ---
AMAZON_SERVICES = [
    "Prime Membership", "Prime Video", "Amazon Music Unlimited", "Prime Music (Bundled)", "Kindle Unlimited", "Prime Reading",
    "Audible Membership (Premium Plus/Plus)", "Amazon Photos", "Amazon Drive (Deprecated but legacy)", "Subscribe & Save",
    "Amazon Fresh/Whole Foods Delivery", "Amazon Pharmacy", "Alexa Skills Usage",
    "Amazon Business Account", "AWS Usage (Free/Paid)", "Amazon Handmade Seller/Buyer", "Amazon Launchpad Buyer",
    "Amazon Warehouse Deals Shopper", "Amazon Outlet Shopper", "Amazon Luna", "Amazon Kids+"
]

# --- Minor Life Events (Can slightly perturb parameters/interests over 5 years) ---
MINOR_LIFE_EVENT_TYPES = [
    {"name": "Job Change (Minor)", "effect": {"param_adjust": {"activity_level": 0.05, "purchase_latency_factor": -0.05}, "interest_shift": ["Career Development", "Office Products"]}},
    {"name": "Relocation (Minor)", "effect": {"param_adjust": {"activity_level": 0.1}, "interest_shift": ["Home Decor", "Furniture", "Tools & Home Improvement"]}},
    {"name": "New Hobby Acquired", "effect": {"param_adjust": {"activity_level": 0.05}, "interest_shift": ["Related Hobby Supplies"]}}, # Placeholder, specific hobby added dynamically
    {"name": "Income Change (Minor)", "effect": {"param_adjust": {"deal_seeking_propensity": random.uniform(-0.1, 0.1), "purchase_latency_factor": random.uniform(-0.1, 0.1)}}},
    {"name": "Change in Household Size (Minor)", "effect": {"param_adjust": {"activity_level": 0.05}, "interest_shift": ["Grocery", "Household Supplies"]}},
    {"name": "Increased Tech Exposure", "effect": {"param_adjust": {"tech_adoption_propensity": 0.1}}},
    {"name": "Decreased Tech Exposure", "effect": {"param_adjust": {"tech_adoption_propensity": -0.1}}},
]
MINOR_EVENT_YEARLY_PROB = 0.4 # Chance per year of a minor event occurring

# --- Event Details Constants ---
EVENT_TYPES = [
    # Core Shopping
    "search", "view_product", "add_to_cart", "remove_from_cart", "purchase", "return_item",
    "browse_category", "view_recommendations", "update_wishlist", "use_coupon", "apply_gift_card",
    "view_order_history", "track_package",
    # Reviews & Q&A
    "write_review", "view_review", "rate_product", "ask_question", "answer_question", "report_review", "vote_review_helpfulness",
    # Prime & Media
    "watch_prime_video", "listen_amazon_music", "read_kindle_book", "listen_audible", "browse_prime_video", "browse_amazon_music", "add_video_watchlist", "add_music_playlist",
    # Services & Devices
    "alexa_interaction", "order_whole_foods", "manage_subscribe_save", "use_amazon_photos", "view_aws_console", "use_amazon_pharmacy", "manage_devices",
    # Account Management
    "update_profile", "change_address", "change_payment", "contact_customer_service", "view_account_settings", "change_password", "view_security_settings",
    # Other Interactions
    "share_product", "view_deal", "clip_coupon", "view_seller_profile", "follow_brand", "view_live_stream", "use_ar_view",
]

# Lists for generating event details
ALEXA_INTENTS = ["Ask Weather", "Set Timer", "Play Music", "Control Smart Home", "Ask Question", "Shopping List Add/Remove", "Get News", "Traffic Update", "Set Reminder", "Tell Joke", "Order Product", "Check Order Status", "Play Audiobook", "Call Contact", "Define Word", "Translate Phrase", "Check Calendar", "Get Sports Score", "Find Recipe"]
RETURN_REASONS = ["Wrong item/size/color", "Damaged/Defective", "Changed mind", "Better price available", "Doesn't fit/work", "Not as described", "Accidental order", "Arrived too late", "Unauthorized purchase", "Found elsewhere", "Quality not adequate", "No longer needed"]
VIDEO_CONTENT_TYPES = ["Movie", "TV Show Episode", "Documentary", "Sports Event", "Reality TV", "Kids Show", "Prime Original Series", "Prime Original Movie", "Rented Movie", "Purchased TV Show"]
MUSIC_CONTENT_TYPES = ["Song", "Album", "Playlist (Curated)", "Playlist (User)", "Station", "Podcast", "Purchased Track/Album"]
BOOK_SOURCES = ["Kindle Unlimited", "Prime Reading", "Purchased", "Library Loan (Overdrive)", "Sample", "Audible Purchase", "Audible Plus Catalog"]
CUSTOMER_SERVICE_CHANNELS = ["Chat", "Phone", "Email", "Message Us (App/Web)", "Help Pages"]
CUSTOMER_SERVICE_REASONS = ["Order Issue (Wrong Item, Damaged)", "Return/Refund Inquiry", "Account Problem (Login, Security)", "Payment Issue", "Technical Support (Device, App)", "Product Question", "Delivery Problem (Late, Missing)", "Feedback/Complaint", "Prime Inquiry", "Subscription Issue", "Fraud Concern", "A-to-Z Guarantee Claim"]
SEARCH_TYPES = ["Product Search", "Prime Video Search", "Amazon Music Search", "Kindle Store Search", "Audible Search", "Whole Foods Search", "General Help Search"]
VIDEO_GENRES = ["Action", "Adventure", "Comedy", "Drama", "Sci-Fi", "Fantasy", "Horror", "Thriller", "Mystery", "Documentary", "Kids & Family", "Animation", "Romance", "Musical", "Stand-Up Comedy", "Reality TV", "Sports"]
MUSIC_GENRES = ["Pop", "Rock", "Hip-Hop/Rap", "R&B/Soul", "Electronic/Dance", "Classical", "Jazz", "Country", "Folk/Acoustic", "Blues", "Reggae", "Latin", "World Music", "Soundtracks", "Kids Music", "Indie/Alternative", "Metal", "Christian/Gospel"]
BOOK_GENRES = ["Fiction", "Non-Fiction", "Mystery/Thriller", "Sci-Fi/Fantasy", "Romance", "Historical Fiction", "Biography/Memoir", "Self-Help", "Business/Finance", "History", "Science", "Cooking/Food", "Travel", "Comics/Graphic Novels", "Children's Books", "Young Adult", "Reference", "Religion & Spirituality"]

# --- Base Event Weights (Adjusted dynamically in simulation) ---
# Represents the relative likelihood of an event type occurring *if conditions allow*.
# The simulation logic will use these as a starting point and modify based on profile state/params.
BASE_EVENT_WEIGHTS = {
    # Core Shopping
    "search": 25, "view_product": 30, "add_to_cart": 12, "purchase": 6,
    "browse_category": 18, "view_recommendations": 10, "update_wishlist": 5,
    "return_item": 1.5, "track_package": 3, "view_order_history": 4,
    # Reviews & Q&A
    "write_review": 1, "view_review": 7, "rate_product": 0.5, "ask_question": 0.3, "answer_question": 0.2, "vote_review_helpfulness": 1,
    # Prime & Media
    "watch_prime_video": 15, "listen_amazon_music": 12, "read_kindle_book": 10, "listen_audible": 8,
    "browse_prime_video": 5, "browse_amazon_music": 4, "add_video_watchlist": 2, "add_music_playlist": 2,
    # Services & Devices
    "alexa_interaction": 9, "order_whole_foods": 4, "manage_subscribe_save": 3, "use_amazon_photos": 1, "view_aws_console": 0.1, "use_amazon_pharmacy": 0.5, "manage_devices": 0.5,
    # Account Management
    "update_profile": 0.2, "change_address": 0.1, "change_payment": 0.3, "contact_customer_service": 0.7, "view_account_settings": 1.5, "change_password": 0.05,
    # Other Interactions
    "share_product": 0.5, "view_deal": 6, "clip_coupon": 4, "view_seller_profile": 1, "follow_brand": 0.5, "view_live_stream": 0.2, "use_ar_view": 0.1,
    "report_review": 0.1, "view_security_settings": 0.2,
}

# --- Product Generation Constants ---
ADJECTIVES1 = ['Premium', 'Basic', 'Advanced', 'Generic', 'Eco-Friendly', 'Smart', 'Heavy-Duty', 'Compact', 'Wireless', 'Organic', 'Handmade', 'Refurbished', 'Professional', 'Portable', 'Essential', 'Deluxe', 'Ultra', 'Standard', 'Lightweight', 'Waterproof', 'Hypoallergenic', 'High-Performance']
ADJECTIVES2 = ['Series', 'Model', 'Edition', 'Collection', 'Mark', 'Pro', 'Lite', 'Plus', 'Ultra', 'Max', 'Mini', 'Classic', 'Sport', 'Limited', 'Signature', 'Value', 'Performance', '']
NOUNS = ['Device', 'Item', 'Accessory', 'Kit', 'Solution', 'System', 'Tool', 'Gadget', 'Apparel', 'Component', 'Unit', 'Set', 'Bundle', 'Charger', 'Case', 'Adapter', 'Cable', 'Mount', 'Holder', 'Organizer', 'Refill', 'Supply']
BRANDS = ['OmniCorp', 'Acme', 'Globex', 'Cyberdyne', 'Stark Industries', 'Wayne Enterprises', 'Initech', 'Bluth Company', 'Pied Piper', 'Hooli', 'GenericBrand', 'NicheMaker', 'Aperture', 'Sirius Cybernetics', 'Tyrell Corp', 'Weyland-Yutani', 'BlueSun', 'MomCorp', 'VirtuCon', 'Soylent', 'Massive Dynamic']
PRODUCT_MODIFIERS = ['for Kids', 'for Home', 'for Office', 'for Travel', 'Gift Set', 'Value Pack', 'New Version', '2.0', 'NextGen', 'XL', 'Compact', 'Travel Size', '']