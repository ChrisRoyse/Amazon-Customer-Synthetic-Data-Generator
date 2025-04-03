# personas.py - Refactored for Behavioral Parameters

import random
import datetime
import logging

# Import necessary components from other modules
try:
    import config
    import utils
except ImportError as e:
    logging.error(f"Error importing modules in personas.py: {e}. Ensure config.py and utils.py exist.")
    raise

def _sample_parameter(param_config, life_stage_adjustments=None, param_name=None):
    """Samples a value for a behavioral parameter based on its config and life stage adjustments."""
    value = None
    param_type = param_config.get("type", "float") # Default to float
    base_range = param_config.get("range")

    if base_range:
        min_val, max_val = base_range
        if param_type == "float":
            value = random.uniform(min_val, max_val)
        elif param_type == "int":
            value = random.randint(min_val, max_val)
        else: # Default to float if type unknown
             value = random.uniform(min_val, max_val)

        # Apply life stage adjustments if provided
        if life_stage_adjustments and param_name in life_stage_adjustments:
            adjustment = life_stage_adjustments[param_name]
            value += adjustment
            # Clamp value back into the original range after adjustment
            value = max(min_val, min(max_val, value))

    else:
        logging.warning(f"Parameter config for '{param_name}' missing 'range'. Cannot sample.")
        # Potentially return a default value if defined, or None
        value = param_config.get("default") # Add default option to config if needed

    return value


def create_base_profile(profile_index, simulation_start_date):
    """
    Creates the base structure of a customer profile, sampling behavioral
    parameters instead of assigning fixed archetypes.

    Args:
        profile_index (int): The index number for the profile being generated.
        simulation_start_date (datetime.datetime): The starting date for the simulation period.

    Returns:
        dict: A dictionary representing the base customer profile, including
              an '_internal_state' with sampled behavioral parameters. Returns None on critical error.
    """
    profile_id = utils.generate_customer_id(profile_index)
    logging.debug(f"Creating base profile {profile_id}")

    try:
        # 1. Select Life Stage (influences interests & parameter adjustments)
        if not config.LIFE_STAGES:
             logging.error("LIFE_STAGES list in config is empty. Cannot create profile.")
             return None
        life_stage_data = random.choice(config.LIFE_STAGES)
        life_stage_adjustments = life_stage_data.get("param_adjustments", {})

        # 2. Sample Behavioral Parameters
        behavioral_params = {}
        for param_name, param_config in config.BEHAVIORAL_PARAMS_CONFIG.items():
            behavioral_params[param_name] = _sample_parameter(param_config, life_stage_adjustments, param_name)
            if behavioral_params[param_name] is None:
                 logging.error(f"Failed to sample required parameter '{param_name}' for profile {profile_id}. Aborting profile creation.")
                 return None # Abort if a critical parameter can't be sampled

        # Apply life stage activity boost directly if defined
        activity_level_boost = life_stage_adjustments.get("activity_level_boost", 0.0)
        behavioral_params["activity_level"] = max(0.01, min(1.0, behavioral_params["activity_level"] * (1 + activity_level_boost)))


        # 3. Determine Demographics (influenced by Life Stage)
        min_age, max_age = life_stage_data["age_range"]
        if min_age > max_age: min_age, max_age = 25, 35 # Fallback
        age_at_sim_end = random.randint(min_age, max_age)
        birth_year = simulation_start_date.year - age_at_sim_end

        # Calculate Account Creation Date (same logic as before)
        account_creation_min_age = 18
        min_creation_year = max(birth_year + account_creation_min_age, 1998)
        max_creation_year = simulation_start_date.year - 1
        account_creation_date = None
        if min_creation_year > max_creation_year:
            earliest_creation_dt = datetime.datetime(birth_year + account_creation_min_age, 1, 1) # Approx 18th birthday start of year
            latest_creation_dt = simulation_start_date - datetime.timedelta(days=1)
            if earliest_creation_dt <= latest_creation_dt:
                 account_creation_date = utils.generate_random_date(earliest_creation_dt, latest_creation_dt)
            else:
                 account_creation_date = latest_creation_dt # Fallback
        else:
            account_creation_year = random.randint(min_creation_year, max_creation_year)
            year_start = datetime.datetime(account_creation_year, 1, 1)
            year_end = datetime.datetime(account_creation_year, 12, 31)
            account_creation_date = utils.generate_random_date(year_start, year_end)
        account_creation_date = min(account_creation_date, simulation_start_date - datetime.timedelta(days=1))

        # Select income bracket based on indices defined in life stage
        income_indices = life_stage_data.get("income_bracket_indices", list(range(len(config.INCOME_BRACKETS))))
        chosen_index = random.choice(income_indices)
        income_bracket = config.INCOME_BRACKETS[chosen_index]

        household_composition = random.choice(config.HOUSEHOLD_COMPOSITIONS) # Could also be influenced by life stage if needed
        location_type = random.choice(config.LOCATION_TYPES)

        # 4. Determine Initial Interests (Primarily from Life Stage + some randomness)
        interests = set(life_stage_data.get("interests", []))
        # Add a few random interests for variety
        num_extra_interests = random.randint(1, 5)
        available_interests = [i for i in config.BASE_INTEREST_CATEGORIES if i not in interests]
        if available_interests:
            interests.update(random.sample(available_interests, min(num_extra_interests, len(available_interests))))

        # 5. Determine Amazon Status (Prime, Services) - Influenced by parameters
        # Prime probability can be influenced by parameters like deal seeking, activity level?
        base_prime_prob = 0.6
        # Adjust based on parameters (example adjustments)
        prime_prob_adjust = (behavioral_params["deal_seeking_propensity"] - 0.5) * 0.1 # Higher deal seeker -> slightly more likely prime
        prime_prob_adjust += (behavioral_params["activity_level"] - 0.5) * 0.2 # Higher activity -> more likely prime
        prime_prob_adjust += (behavioral_params["tech_adoption_propensity"] - 0.5) * 0.1 # Higher tech -> slightly more likely

        final_prime_prob = max(0.01, min(0.99, base_prime_prob + prime_prob_adjust))
        is_prime = random.random() < final_prime_prob

        prime_start_date = None
        if is_prime:
            prime_possible_start = max(account_creation_date, datetime.datetime(2005, 2, 1))
            prime_possible_end = simulation_start_date - datetime.timedelta(days=1)
            if prime_possible_start < prime_possible_end:
                prime_start_date = utils.generate_random_date(prime_possible_start, prime_possible_end)
            else:
                prime_start_date = utils.generate_random_date(account_creation_date, simulation_start_date - datetime.timedelta(days=1))

        # Determine usage of other services based on Prime AND behavioral parameters
        used_services = set()
        if is_prime: used_services.add("Prime Membership")

        tech_propensity = behavioral_params["tech_adoption_propensity"]
        activity = behavioral_params["activity_level"]

        # Media Services
        if is_prime and random.random() < behavioral_params["prime_video_engagement"]: used_services.add("Prime Video")
        if (is_prime or random.random() < 0.1) and random.random() < behavioral_params["amazon_music_engagement"]: # Small chance even if not prime
             used_services.add("Prime Music (Bundled)") # Assume bundled first
             if random.random() < 0.3 * tech_propensity: used_services.add("Amazon Music Unlimited") # Upgrade chance based on tech

        kindle_interest = any(i in interests for i in ["Books (Physical)", "Kindle Store"])
        if kindle_interest and random.random() < behavioral_params["kindle_engagement"]:
             if is_prime: used_services.add("Prime Reading")
             if random.random() < 0.4: used_services.add("Kindle Unlimited")

        audible_interest = "Audible Books & Originals" in interests or (kindle_interest and random.random() < 0.3)
        if audible_interest and random.random() < behavioral_params["audible_engagement"]:
             used_services.add("Audible Membership (Premium Plus/Plus)")

        # Other Services
        if random.random() < tech_propensity * 0.8: used_services.add("Alexa Skills Usage") # Higher tech -> more likely Alexa
        if random.random() < behavioral_params["subscribe_save_propensity"]: used_services.add("Subscribe & Save")
        if "Grocery & Gourmet Food" in interests and location_type in ["Dense Urban", "Urban", "Suburban"] and random.random() < 0.4 * activity: used_services.add("Amazon Fresh/Whole Foods Delivery")
        if "Health & Personal Care" in interests and random.random() < 0.2 * activity: used_services.add("Amazon Pharmacy")
        if random.random() < tech_propensity * 0.1: used_services.add("AWS Usage (Free/Paid)") # Low base chance, higher for techy
        if "Amazon Handmade" in interests and random.random() < 0.3: used_services.add("Amazon Handmade Buyer")
        if "Amazon Launchpad" in interests and random.random() < tech_propensity * 0.2: used_services.add("Amazon Launchpad Buyer")
        if random.random() < behavioral_params["deal_seeking_propensity"] * 0.5: used_services.add("Amazon Warehouse Deals Shopper")
        if random.random() < behavioral_params["deal_seeking_propensity"] * 0.4: used_services.add("Amazon Outlet Shopper")
        if random.random() < tech_propensity * 0.6: used_services.add("Amazon Photos")


        # 6. Device Usage (Influenced by tech_adoption_propensity)
        tech_propensity = behavioral_params["tech_adoption_propensity"]
        # Higher tech propensity -> more devices, more likely newer types
        num_devices_mean = 1.5 + tech_propensity * 3 # Mean devices from 1.8 to 4.5
        num_devices = max(1, int(random.gauss(num_devices_mean, 1.0))) # Gaussian distribution around mean

        # Weight devices based on tech propensity (simple example)
        device_weights = []
        for device in config.DEVICE_TYPES:
            weight = 1.0
            if any(t in device for t in ["Mobile App", "Tablet App"]): weight *= (0.5 + tech_propensity)
            if any(t in device for t in ["Echo", "Fire TV", "Smart Watch", "Smart Home"]): weight *= (0.2 + tech_propensity * 1.5)
            if "Desktop" in device: weight *= (1.5 - tech_propensity) # Less likely primary for high tech?
            device_weights.append((device, max(0.1, weight))) # Ensure min weight

        final_devices = []  # Change from set to list
        attempts = 0
        while len(final_devices) < num_devices and attempts < num_devices * 3:
            chosen_device = utils.select_weighted_item(device_weights)
            if chosen_device and chosen_device not in final_devices:  # Check for uniqueness manually
                final_devices.append(chosen_device)  # Append to list instead of adding to set
            attempts += 1
        if not final_devices: # Ensure at least one device
             final_devices.append(random.choice(config.DEVICE_TYPES))  # Append to list

        primary_device = random.choice(final_devices)

        # 7. Determine Initial Login Frequency (Estimate based on activity level)
        activity_level = behavioral_params["activity_level"]
        if activity_level > 0.8: login_freq = "Multiple times a day"
        elif activity_level > 0.6: login_freq = random.choice(["Multiple times a day", "Daily"])
        elif activity_level > 0.4: login_freq = random.choice(["Daily", "Few times a week"])
        elif activity_level > 0.2: login_freq = random.choice(["Few times a week", "Weekly", "Bi-Weekly"])
        elif activity_level > 0.05: login_freq = random.choice(["Weekly", "Bi-Weekly", "Monthly", "Quarterly"])
        else: login_freq = random.choice(["Monthly", "Quarterly", "Rarely (< Quarterly)"])


        # 8. Construct Profile Dictionary (NO Archetype Names)
        profile = {
            "profile_id": profile_id,
            "generation_timestamp": utils.format_iso_timestamp(datetime.datetime.now()),
            "simulation_period_start": utils.format_iso_timestamp(simulation_start_date),
            "simulation_period_end": utils.format_iso_timestamp(simulation_start_date + datetime.timedelta(days=config.SIMULATION_DURATION_DAYS)),
            # --- Demographics & Context (Observable/Inferrable) ---
            "demographics": {
                "age_at_simulation_end": age_at_sim_end, # Will be updated
                "birth_year": birth_year, # For reference
                "location_type": location_type, # Inferrable from IP/Shipping
                "household_composition_initial": household_composition, # Potentially inferrable (shipping names, baby registry etc) - Keep for context
                "estimated_income_bracket_initial": income_bracket, # Potentially inferrable (purchase types, location) - Keep for context
                "life_stage_initial_context": life_stage_data["name"], # Keep for context, not direct output if sensitive
            },
            "amazon_status": {
                "account_creation_date": utils.format_iso_timestamp(account_creation_date),
                "is_prime_member_initial": is_prime,
                "prime_membership_start_date": utils.format_iso_timestamp(prime_start_date),
                "used_services_initial": sorted(list(used_services)), # Observable through usage
            },
            "device_usage": {
                "primary_device": primary_device, # Inferrable from usage patterns
                "all_devices": sorted(final_devices, key=lambda d: d['name']), # Sort by device name
                "login_frequency_initial_estimate": login_freq, # Estimate, actual usage is in log
            },
            "interests_initial": sorted(list(interests)), # Inferrable from browsing/purchases
            # --- Core Behavioral Data ---
            "activity_log": [],
            "life_events": [], # Minor events over 5 years

            # --- Internal Simulation State (NOT SAVED in final JSON) ---
            "_internal_state": {
                "current_timestamp": simulation_start_date,
                "current_age": age_at_sim_end - config.SIMULATION_DURATION_YEARS,
                "current_life_stage": life_stage_data, # Used for potential minor adjustments
                "current_household_composition": household_composition,
                "current_income_bracket": income_bracket,
                "current_interests": interests,
                "is_prime": is_prime,
                "prime_start_date": prime_start_date,
                "used_services": used_services,
                "behavioral_params": behavioral_params, # Store the sampled parameters here
                "login_frequency": login_freq, # Store initial estimate
                "devices": final_devices, # Removed redundant list() conversion
                "primary_device": primary_device,
                # Dynamic state
                "cart": [],
                "orders": [],
                "wishlist": set(),
                "viewed_products": [],
                "search_history": [],
                "last_event_timestamp": simulation_start_date,
                "current_session_id": utils.generate_session_id(),
                "session_start_time": simulation_start_date,
                "events_in_session": 0,
                "time_since_last_minor_event": random.randint(0, 180), # Start with random offset
                "seasonal_boost": utils.get_seasonal_boost(simulation_start_date),
                "active_promotions": {},
                "customer_service_interactions": 0,
                "brand_purchase_counts": {}, # Track brand purchases for affinity simulation
            }
        }
        logging.debug(f"Base profile {profile_id} created successfully with behavioral parameters.")
        return profile

    except Exception as e:
        logging.error(f"Failed to create base profile {profile_id}: {e}", exc_info=True)
        return None


if __name__ == '__main__':
    # Example usage/test
    logging.basicConfig(level=logging.DEBUG)
    print("--- Testing Refactored Persona Generation ---")
    start_date = datetime.datetime(2024, 1, 1)
    test_profile = create_base_profile(1, start_date)
    if test_profile:
        import json
        print("\n--- Generated Profile (Excluding Internal State) ---")
        output_profile = {k: v for k, v in test_profile.items() if k != '_internal_state'}
        print(json.dumps(output_profile, indent=2, default=str))
        print("\n--- Sampled Behavioral Parameters (Internal State) ---")
        print(json.dumps(test_profile['_internal_state']['behavioral_params'], indent=2))
    else:
        print("Failed to generate test profile.")
    print("\n--- Persona Test Complete ---")