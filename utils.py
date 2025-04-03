# utils.py

import random
import datetime
import uuid
import math
import numpy as np
import logging
import json # &lt;-- Add this import

# Import constants from config - ensures consistency
try:
    import config
except ImportError:
    logging.error("Could not import config.py. Ensure it exists in the same directory.")
    # Define fallbacks or raise error if config is critical for utils
    # For now, we'll assume config defines necessary lists like BASE_INTEREST_CATEGORIES etc.
    # If a function relies heavily on config, add specific error handling or defaults.
    class MockConfig:
        BASE_INTEREST_CATEGORIES = ["Electronics", "Books", "Home", "Clothing", "Grocery"]
        ADJECTIVES1 = ['Premium', 'Basic', 'Advanced']
        ADJECTIVES2 = ['Series', 'Model', 'Edition']
        NOUNS = ['Device', 'Item', 'Accessory']
        BRANDS = ['OmniCorp', 'Acme', 'GenericBrand']
        PRODUCT_MODIFIERS = ['for Home', '']
    config = MockConfig()


# --- Date & Time Functions ---

def generate_random_date(start_date, end_date):
    """Generates a random datetime between start_date and end_date."""
    if not isinstance(start_date, datetime.datetime) or not isinstance(end_date, datetime.datetime):
        logging.error(f"generate_random_date received non-datetime objects: {start_date}, {end_date}")
        # Return a default or raise error
        return datetime.datetime.now()

    if start_date > end_date:
        logging.warning(f"generate_random_date start_date {start_date} is after end_date {end_date}. Swapping.")
        start_date, end_date = end_date, start_date

    time_between_dates = end_date - start_date
    seconds_between_dates = max(0, time_between_dates.total_seconds())

    if seconds_between_dates == 0:
        random_number_of_seconds = 0
    else:
        # Use random.randrange for integer seconds if precision isn't microsecond critical
        # random_number_of_seconds = random.randrange(int(seconds_between_dates) + 1)
        # Or keep uniform for float seconds
        random_number_of_seconds = random.uniform(0, seconds_between_dates)

    random_date = start_date + datetime.timedelta(seconds=random_number_of_seconds)
    return random_date

def format_iso_timestamp(dt):
    """Formats datetime object to ISO string with Z (UTC indicator). Handles None."""
    if dt is None:
        return None
    if not isinstance(dt, datetime.datetime):
        logging.warning(f"format_iso_timestamp received non-datetime object: {dt}. Returning None.")
        return None
    # Ensure timezone is UTC if not already set (or handle timezone conversion)
    # For simplicity, assume generated dates are meant to be UTC for the 'Z'
    # dt_utc = dt.astimezone(datetime.timezone.utc) # More robust handling
    # return dt_utc.isoformat(timespec='seconds').replace('+00:00', 'Z')
    return dt.isoformat(timespec='seconds') + "Z" # Simpler version assuming UTC


# --- ID Generation Functions ---

def generate_product_id():
    """Generates a fake product ID (ASIN-like). B0 + 9 hex digits."""
    return f"B0{random.randint(0, 0xFFFFFFFFF):09X}"

def generate_order_id():
    """Generates a fake order ID (e.g., 111-xxxxxxx-xxxxxxx)."""
    return f"{random.randint(100, 999)}-{random.randint(1000000, 9999999)}-{random.randint(1000000, 9999999)}"

def generate_session_id():
    """Generates a unique session ID."""
    return str(uuid.uuid4())

def generate_customer_id(index):
    """Generates a customer ID based on index."""
    # Example: CUST-YYYYMMDD-Index
    # today_str = datetime.date.today().strftime("%Y%m%d")
    # return f"CUST-{today_str}-{index:0{config.FILENAME_DIGITS}d}"
    # Or simpler:
    return f"cust_{index:0{config.FILENAME_DIGITS}d}" # Matches profile ID format

def generate_review_id():
    """Generates a unique review ID."""
    return f"R{random.randint(10**9, 10**10 - 1)}" # R + 10 digits

def generate_question_id():
    """Generates a unique question ID."""
    return f"Q{random.randint(10**8, 10**9 - 1)}" # Q + 9 digits

def generate_coupon_code():
    """Generates a fake coupon code."""
    part1 = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=4))
    part2 = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=4))
    return f"{part1}-{part2}"


# --- Statistical Sampling Functions ---

def sample_normal(mean, std_dev, min_val=None, max_val=None):
    """Sample from normal distribution with optional clamping"""
    value = np.random.normal(mean, std_dev)
    if min_val is not None:
        value = max(min_val, value)
    if max_val is not None:
        value = min(max_val, value)
    return value

def sample_beta(alpha, beta, min_val=0, max_val=1):
    """Sample from beta distribution, scaled to min/max"""
    value = np.random.beta(alpha, beta)
    return min_val + (max_val - min_val) * value

def sample_exponential(scale, min_val=None, max_val=None):
    """Sample from exponential distribution with optional clamping"""
    value = np.random.exponential(scale)
    if min_val is not None:
        value = max(min_val, value)
    if max_val is not None:
        value = min(max_val, value)
    return value

def sample_pareto(shape, min_val=None, max_val=None):
    """Sample from Pareto distribution with optional clamping"""
    value = np.random.pareto(shape) + 1  # +1 so minimum value is 1
    if min_val is not None:
        value = max(min_val, value)
    if max_val is not None:
        value = min(max_val, value)
    return value

def sample_zipf(exponent, size=1, min_val=None, max_val=None):
    """Sample from Zipf distribution with optional clamping"""
    value = np.random.zipf(exponent, size)[0]
    if min_val is not None:
        value = max(min_val, value)
    if max_val is not None:
        value = min(max_val, value)
    return value

# Weighted random selection from distribution dictionary
def sample_from_distribution(distribution_dict):
    """Sample a key from a distribution dictionary where values are probabilities"""
    items = list(distribution_dict.items())
    keys = [item[0] for item in items]
    probabilities = [item[1] for item in items]
    return random.choices(keys, weights=probabilities, k=1)[0]

# --- Product & Pricing Functions ---

def get_plausible_price(category):
    """Generates a somewhat plausible price based on category."""
    price = 19.99 # Default
    if category is None: category = "Unknown"
    category_lower = category.lower()

    # Define price ranges per category (adjust as needed)
    price_ranges = {
        "luxury": (200, 5000), "high-end": (200, 5000),
        "electronics": (30, 3000), "computers": (100, 4000), "appliances": (50, 2500), "furniture": (100, 3000), "smart home": (20, 500),
        "clothing": (15, 500), "shoes": (20, 600), "jewelry": (25, 5000), "watches": (50, 10000),
        "tools": (10, 800), "automotive": (5, 1000), "sports": (10, 1500), "outdoors": (15, 2000),
        "toys": (5, 300), "baby": (5, 400), "pet supplies": (3, 200),
        "books": (5, 150), "kindle": (1, 30), "audible": (5, 50), "music": (1, 50), "movies": (3, 60), "software": (10, 1000), "video games": (10, 100),
        "grocery": (0.5, 100), "health": (2, 200), "beauty": (3, 300), "pharmacy": (5, 500),
        "office": (1, 300), "crafts": (2, 150), "hobbies": (5, 500),
        "default": (5, 500)
    }

    chosen_range = price_ranges["default"]
    for key, price_range in price_ranges.items():
        if key in category_lower:
            chosen_range = price_range
            break # Take first match

    # Generate price within the range, potentially skewed
    min_p, max_p = chosen_range
    # Skew towards lower end for most items? Use power law or similar?
    # Simple approach: uniform within range
    price = random.uniform(min_p, max_p)

    # Apply common price endings (e.g., .99, .95)
    if random.random() < 0.75:
        price = math.floor(price) + random.choice([0.99, 0.95, 0.49, 0.79, 0.00])
    elif random.random() < 0.1: # Occasional whole numbers
         price = round(price)

    return round(max(0.50, price), 2) # Ensure minimum price

def generate_product_name(category):
    """Generates a more descriptive fake product name using config constants."""
    if category is None: category = "Unknown"
    cat_lower = category.lower()

    # Select components from config lists
    adj1 = random.choice(config.ADJECTIVES1)
    adj2 = random.choice(config.ADJECTIVES2)
    noun = random.choice(config.NOUNS)
    brand = random.choice(config.BRANDS)
    modifier = random.choice(config.PRODUCT_MODIFIERS)
    num = random.choice([f"{random.randint(100, 999)}", f"{random.randint(1, 9)}000", f"X{random.randint(1, 25)}", ''])

    # --- Category-Specific Naming ---
    if "clothing" in cat_lower or "shoes" in cat_lower or "apparel" in cat_lower:
        noun = random.choice(['Shirt', 'T-Shirt', 'Sweater', 'Hoodie', 'Jacket', 'Coat', 'Pants', 'Jeans', 'Shorts', 'Dress', 'Skirt', 'Sneakers', 'Boots', 'Sandals', 'Hat', 'Scarf', 'Gloves', 'Socks'])
        adj1 = random.choice(['Cotton', 'Wool', 'Silk', 'Leather', 'Denim', 'Casual', 'Formal', 'Vintage', 'Modern', 'Slim Fit', 'Relaxed Fit', 'Performance'])
        brand = random.choice(['Urban Threads', 'Summit Gear', 'Coastal Co.', 'Heritage Brand', 'Nova Fashion', brand]) # Add clothing specific brands
    elif "book" in cat_lower or "kindle" in cat_lower or "audible" in cat_lower:
        genre_adj = random.choice(['Lost', 'Secret', 'Forgotten', 'Hidden', 'Last', 'Eternal', 'Silent', 'Burning', 'Crystal', 'Shadow', 'Gilded', 'Crimson'])
        genre_noun = random.choice(['City', 'Garden', 'Key', 'Chronicle', 'Journey', 'Legacy', 'Witness', 'Page', 'Throne', 'River', 'Truth', 'Empire', 'Code', 'Cipher'])
        author_first = random.choice(['Jane', 'John', 'Alex', 'Sam', 'Jordan', 'Casey', 'Morgan', 'Taylor', 'Jamie', 'Riley', 'Chris', 'Pat'])
        author_last = random.choice(['Doe', 'Smith', 'Reed', 'Morgan', 'Bell', 'Hayes', 'Black', 'White', 'Green', 'Gray', 'Miller', 'Davis'])
        return f"'{random.choice(['The', 'A', 'An'])} {genre_adj} {genre_noun}' by {author_first} {author_last}"
    elif "electronics" in cat_lower or "computer" in cat_lower or "smart home" in cat_lower:
        noun = random.choice(['Laptop', 'Smartphone', 'Tablet', 'Monitor', 'Keyboard', 'Mouse', 'Headphones', 'Speaker', 'Router', 'Camera', 'Webcam', 'Printer', 'Scanner', 'Projector', 'Smart Plug', 'Smart Bulb', 'Security Camera', 'Thermostat'])
        adj1 = random.choice(['Wireless', 'Bluetooth', 'Gaming', '4K', 'HD', 'Curved', 'Mechanical', 'Noise-Cancelling', 'Portable', 'High-Performance', 'NextGen'])
        brand = random.choice(['TechCore', 'Innovate Inc.', 'Apex Devices', 'Quantum Systems', 'ElectroGadget', brand])
    elif "home" in cat_lower or "kitchen" in cat_lower or "furniture" in cat_lower:
        noun = random.choice(['Blender', 'Mixer', 'Toaster', 'Kettle', 'Coffee Maker', 'Microwave', 'Air Fryer', 'Lamp', 'Chair', 'Table', 'Sofa', 'Bookshelf', 'Desk', 'Bed Frame', 'Mattress', 'Nightstand', 'Dresser', 'Shelf', 'Organizer', 'Cookware Set', 'Bakeware Set', 'Cutlery Set', 'Dinnerware Set', 'Vacuum Cleaner', 'Air Purifier'])
        adj1 = random.choice(['Stainless Steel', 'Non-stick', 'Cast Iron', 'Wooden', 'Modern', 'Minimalist', 'Industrial', 'Farmhouse', 'Mid-Century', 'Adjustable', 'Ergonomic'])
        brand = random.choice(['HomeSphere', 'KitchenWiz', 'ComfortLiving', 'DesignHaus', 'UrbanFurnish', brand])
    elif "grocery" in cat_lower:
         noun = random.choice(['Coffee Beans', 'Tea Bags', 'Pasta', 'Rice', 'Cereal', 'Granola Bar', 'Snack Mix', 'Chocolate Bar', 'Olive Oil', 'Vinegar', 'Spice Blend', 'Canned Soup', 'Frozen Vegetables', 'Yogurt', 'Milk', 'Cheese', 'Bread'])
         adj1 = random.choice(['Organic', 'Gluten-Free', 'Non-GMO', 'Fair Trade', 'Artisanal', 'Gourmet', 'Family Size', 'Single Origin'])
         brand = random.choice(['Nature\'s Best', 'FarmFresh', 'Pantry Staples', 'Gourmet Select', 'Healthy Harvest', brand])
    elif "toys" in cat_lower or "games" in cat_lower:
        noun = random.choice(['Action Figure', 'Doll', 'Building Blocks', 'Board Game', 'Card Game', 'Puzzle', 'Plush Toy', 'RC Car', 'Drone', 'Video Game', 'Educational Toy'])
        adj1 = random.choice(['Interactive', 'Collectible', 'Remote Control', 'STEM', 'Creative', 'Strategy', 'Cooperative', 'Award-Winning'])
        brand = random.choice(['ToyWorld', 'PlayFun', 'KidzKraft', 'GameMasters', 'BrainyBuilders', brand])

    # Construct the name
    name_parts = [brand, adj1, category, noun, adj2, num, modifier]
    # Filter out empty parts and join
    full_name = " ".join(part for part in name_parts if part).replace("  ", " ").strip()

    # Prevent overly long names
    return (full_name[:150] + '...') if len(full_name) > 150 else full_name


# --- Persona & Profile Helpers ---

def select_weighted_item(items_with_weights):
    """Selects an item from a list of (item, weight) tuples."""
    total_weight = sum(w for _, w in items_with_weights)
    if total_weight <= 0:
        # Fallback: return a random item if weights are zero or invalid
        return random.choice([item for item, _ in items_with_weights]) if items_with_weights else None

    r = random.uniform(0, total_weight)
    upto = 0
    for item, weight in items_with_weights:
        if upto + weight >= r:
            return item
        upto += weight
    # Should not reach here if total_weight > 0, but as a fallback:
    return items_with_weights[-1][0] if items_with_weights else None

def get_seasonal_boost_from_config(current_date):
    """Applies a boost to activity/spending around holidays/seasons."""
    if not isinstance(current_date, datetime.datetime):
        return 1.0 # Default if date is invalid

    month = current_date.month
    day = current_date.day
    boost = 1.0

    max_boost = 1.0 # Track the maximum boost found for the date

    seasonal_peaks = config.SHOPPING_PATTERNS.get('seasonal_peaks', {})

    for peak_name, peak_data in seasonal_peaks.items():
        peak_months = peak_data.get("months")
        peak_days = peak_data.get("days") # Optional list of specific days
        peak_boost = peak_data.get("boost", 1.0)
 # Corrected key from "boo5.\n"

        if peak_months and month in peak_months:
            # Check if specific days are defined and if the current day matches
            if peak_days is None or day in peak_days:
                max_boost = max(max_boost, peak_boost) # Apply the highest boost if multiple peaks match

    return max_boost

# --- Simulation Helpers ---

def calculate_event_time_delta(activity_level, seasonal_boost=1.0):
    """Calculates time delta in hours until the next event."""
    # Base mean hours for avg activity (0.5) -> event every 3 days (72 hours)
    mean_hours_base = 72
    activity_factor = max(0.05, activity_level) # Avoid division by zero, ensure minimum activity effect
    mean_hours_between_events = (mean_hours_base / activity_factor) / max(0.1, seasonal_boost) # Avoid boost being zero

    # Add random jitter (e.g., +/- 20%)
    mean_hours_between_events *= random.uniform(0.8, 1.2)
    mean_hours_between_events = max(0.01, mean_hours_between_events) # Min time delta (approx 30 secs)

    # Use exponential distribution for realistic event timing
    time_delta_hours = random.expovariate(1.0 / mean_hours_between_events)
    return time_delta_hours

# --- Output & File Helpers ---
# (No file helpers currently needed)

if __name__ == '__main__':
    # Example usage/tests
    logging.basicConfig(level=logging.DEBUG)
    print("--- Testing Utils ---")
    start = datetime.datetime(2024, 1, 1)
    end = datetime.datetime(2024, 1, 31)
    print(f"Random Date: {generate_random_date(start, end)}")
    print(f"Formatted Timestamp: {format_iso_timestamp(datetime.datetime.now())}")
    print(f"Product ID: {generate_product_id()}")
    print(f"Order ID: {generate_order_id()}")
    print(f"Session ID: {generate_session_id()}")
    print(f"Customer ID (123): {generate_customer_id(123)}")
    print(f"Review ID: {generate_review_id()}")
    print(f"Question ID: {generate_question_id()}")
    print(f"Coupon Code: {generate_coupon_code()}")
    print(f"Plausible Price (Electronics): {get_plausible_price('Electronics')}")
    print(f"Plausible Price (Grocery): {get_plausible_price('Grocery')}")
    print(f"Plausible Price (Luxury Watch): {get_plausible_price('Luxury Watch')}")
    print(f"Product Name (Clothing): {generate_product_name('Clothing')}")
    print(f"Product Name (Books): {generate_product_name('Books')}")
    print(f"Product Name (Smart Home): {generate_product_name('Smart Home')}")
    print(f"Seasonal Boost (Dec 15): {get_seasonal_boost_from_config(datetime.datetime(2024, 12, 15))}")
    print(f"Seasonal Boost (Jul 12): {get_seasonal_boost_from_config(datetime.datetime(2024, 7, 12))}") # Prime Day?
    print(f"Seasonal Boost (Mar 5): {get_seasonal_boost_from_config(datetime.datetime(2024, 3, 5))}")
    print("--- Utils Test Complete ---") # Added newline implicitly by ending file here