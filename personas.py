# personas.py - Refactored for Behavioral Parameters
import random
import datetime
import logging
import numpy as np # Added for poisson distribution

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
    dist_type = param_config.get("distribution")
    dist_params = param_config.get("params", {})
    base_range = param_config.get("range") # Still needed for clamping and some distributions
    min_val, max_val = base_range if base_range else (None, None)

    try:
        if dist_type == "beta":
            value = utils.sample_beta(dist_params['alpha'], dist_params['beta'], min_val, max_val)
        elif dist_type == "normal":
            value = utils.sample_normal(dist_params['mean'], dist_params['std_dev'], min_val, max_val)
        elif dist_type == "exponential":
            value = utils.sample_exponential(dist_params['scale'], min_val, max_val)
        elif dist_type == "pareto":
            value = utils.sample_pareto(dist_params['shape'], min_val, max_val)
        elif dist_type == "zipf":
            value = utils.sample_zipf(dist_params['exponent'], min_val=min_val, max_val=max_val)
        elif dist_type == "poisson": # Poisson needs integer range
            lam = dist_params.get('lam', 1.0)
            value = np.random.poisson(lam)
            if min_val is not None: value = max(int(min_val), value)
            if max_val is not None: value = min(int(max_val), value)
        elif dist_type == "custom_daily": # Special case for time_of_day_preference
            # Logic to sample based on SHOPPING_PATTERNS['hourly_distribution']
            hourly_dist = config.SHOPPING_PATTERNS.get('hourly_distribution', {})
            if not hourly_dist:
                 logging.warning(f"Hourly distribution not found in config for 'custom_daily' sampling of '{param_name}'. Falling back.")
                 value = random.randint(0, 23) # Fallback to random hour
            else:
                periods = list(hourly_dist.keys())
                weights = [p['weight'] for p in hourly_dist.values()]
                if not periods or not weights or len(periods) != len(weights) or sum(weights) <= 0:
                     logging.warning(f"Invalid hourly distribution weights/periods for 'custom_daily' sampling of '{param_name}'. Falling back.")
                     value = random.randint(0, 23) # Fallback
                else:
                    chosen_period = random.choices(periods, weights=weights, k=1)[0]
                    value = random.choice(hourly_dist[chosen_period]['hours'])
        elif base_range: # Fallback to uniform if distribution unknown but range exists
            logging.warning(f"Unknown distribution '{dist_type}' for '{param_name}'. Falling back to uniform sampling.")
            if param_type == "int": value = random.randint(min_val, max_val)
            else: value = random.uniform(min_val, max_val) # Default to float
        else:
            logging.error(f"Cannot sample parameter '{param_name}': Missing 'range' and unsupported/missing distribution '{dist_type}'.")
            return param_config.get("default") # Return default if specified, else None

        # Apply life stage adjustments AFTER initial sampling
        if life_stage_adjustments and param_name in life_stage_adjustments:
            adjustment = life_stage_adjustments[param_name]
            value += adjustment
            # Clamp value back into the original range after adjustment
            if min_val is not None and max_val is not None:
                value = max(min_val, min(max_val, value))

        # Ensure correct type (especially after adjustments)
        if param_type == "int":
            # Check if value is None before rounding
            if value is not None:
                 value = int(round(value))
            else:
                 # Handle case where value is None after adjustment/clamping?
                 # Maybe return default or log error? For now, keep as None.
                 logging.warning(f"Value became None for int parameter '{param_name}' after adjustments. Check logic.")


    except KeyError as e:
        logging.error(f"Missing required parameter '{e}' in config for distribution '{dist_type}' of parameter '{param_name}'.")
        return param_config.get("default")
    except Exception as e:
        logging.error(f"Error sampling parameter '{param_name}' with distribution '{dist_type}': {e}", exc_info=True)
        return param_config.get("default")

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
        # Use weighted choice based on 'weight' key added to LIFE_STAGES in config
        life_stages = config.LIFE_STAGES
        weights = [ls.get('weight', 1) for ls in life_stages] # Default weight 1 if missing
        if sum(weights) <= 0: # Avoid error if all weights are zero
             logging.warning("Sum of LIFE_STAGES weights is zero. Falling back to equal weighting.")
             life_stage_data = random.choice(life_stages)
        else:
             life_stage_data = random.choices(life_stages, weights=weights, k=1)[0]
        life_stage_adjustments = life_stage_data.get("param_adjustments", {})

        # 2. Sample Behavioral Parameters
        behavioral_params = {}
        for param_name, param_config in config.BEHAVIORAL_PARAMS_CONFIG.items():
            behavioral_params[param_name] = _sample_parameter(param_config, life_stage_adjustments, param_name)
            if behavioral_params[param_name] is None:
                 # Check if a default is defined in config before erroring out
                 default_val = param_config.get("default")
                 if default_val is not None:
                      logging.warning(f"Failed to sample parameter '{param_name}', using default value: {default_val}")
                      behavioral_params[param_name] = default_val
                 else:
                      logging.error(f"Failed to sample required parameter '{param_name}' for profile {profile_id} and no default provided. Aborting profile creation.")
                      return None # Abort if a critical parameter can't be sampled and has no default

        # --- MBO Parameter Integration: Modulate existing parameters ---
        # Modulate research_depth by attention_focus
        if 'research_depth' in behavioral_params and 'attention_focus' in behavioral_params:
            attention_focus = behavioral_params.get('attention_focus', 0.5)
            original_research_depth = behavioral_params['research_depth']
            # Attention focus scales depth: low attention reduces depth, high attention increases it slightly
            modulated_depth = original_research_depth * (0.6 + attention_focus * 0.8) # Scale factor from 0.68 to 1.32
            # Clamp to original parameter range defined in config
            research_config = config.BEHAVIORAL_PARAMS_CONFIG.get('research_depth', {})
            min_rd, max_rd = research_config.get('range', (0.1, 0.9))
            behavioral_params['research_depth'] = max(min_rd, min(max_rd, modulated_depth))


        # 3. Determine Demographics (influenced by Life Stage)
        min_age, max_age = life_stage_data["age_range"]
        if min_age > max_age: min_age, max_age = 25, 35 # Fallback
        age_at_sim_end = random.randint(min_age, max_age)
        birth_year = simulation_start_date.year - age_at_sim_end

        # Calculate Account Creation Date (same logic as before)
        account_creation_min_age = 18
        min_creation_year = max(birth_year + account_creation_min_age, 1998) # Amazon founded 1994, shopping 1995ish
        max_creation_year = simulation_start_date.year - 1 # Can't create account in the future relative to sim start
        account_creation_date = None

        # Ensure min_creation_year is not after max_creation_year
        if min_creation_year > max_creation_year:
             # If 18th birthday is after sim start year, account must be created between 18th birthday and sim start
             earliest_creation_dt = datetime.datetime(birth_year + account_creation_min_age, 1, 1)
             latest_creation_dt = simulation_start_date - datetime.timedelta(days=1)
             if earliest_creation_dt <= latest_creation_dt:
                  account_creation_date = utils.generate_random_date(earliest_creation_dt, latest_creation_dt)
             else:
                  # This case implies the person turned 18 *after* the simulation started, which shouldn't happen based on age sampling.
                  # However, as a fallback, set creation to the day before sim start.
                  logging.warning(f"Profile {profile_id}: Calculated earliest creation date {earliest_creation_dt} is after latest {latest_creation_dt}. Setting creation to sim start - 1 day.")
                  account_creation_date = latest_creation_dt
        else:
             account_creation_year = random.randint(min_creation_year, max_creation_year)
             # Ensure creation date is not after simulation start date
             year_start = datetime.datetime(account_creation_year, 1, 1)
             # Cap year_end at simulation start date if account created in the same year simulation starts
             year_end = min(datetime.datetime(account_creation_year, 12, 31), simulation_start_date - datetime.timedelta(days=1))
             if year_start <= year_end:
                  account_creation_date = utils.generate_random_date(year_start, year_end)
             else:
                  # Fallback if something is wrong with date logic
                  account_creation_date = simulation_start_date - datetime.timedelta(days=1)

        # Final check to ensure creation date is before simulation start
        account_creation_date = min(account_creation_date, simulation_start_date - datetime.timedelta(days=1))


        # Select income bracket based on indices defined in life stage
        income_indices = life_stage_data.get("income_bracket_indices", list(range(len(config.INCOME_BRACKETS))))
        chosen_index = random.choice(income_indices)
        income_bracket = config.INCOME_BRACKETS[chosen_index]

        household_composition = random.choice(config.HOUSEHOLD_COMPOSITIONS) # Could also be influenced by life stage if needed
        location_type = random.choice(config.LOCATION_TYPES)

        # 4. Determine Initial Interests (Primarily from Life Stage + some randomness)
        interests = set(life_stage_data.get("interests", []))
        # Add a few random interests for variety, influenced by category_exploration_propensity
        exploration_propensity = behavioral_params.get('category_exploration_propensity', 0.5)
        # Scale propensity (0.1-0.9) to roughly 1-8 extra interests
        num_extra_interests = 1 + int(round(exploration_propensity * 8))
        available_interests = [i for i in config.BASE_INTEREST_CATEGORIES if i not in interests]
        if available_interests:
            interests.update(random.sample(available_interests, min(num_extra_interests, len(available_interests))))

        # 5. Determine Amazon Status (Prime, Services) - Influenced by parameters
        base_prime_prob = 0.6 # Base probability of having Prime
        prime_prob_adjust = 0.0
        # Adjust based on parameters (example adjustments)
        if "deal_seeking_propensity" in behavioral_params:
             prime_prob_adjust += (behavioral_params.get("deal_seeking_propensity", 0.5) - 0.5) * 0.1
        if "activity_level" in behavioral_params:
             prime_prob_adjust += (behavioral_params.get("activity_level", 0.5) - 0.5) * 0.2
        if "tech_adoption_propensity" in behavioral_params:
             prime_prob_adjust += (behavioral_params.get("tech_adoption_propensity", 0.5) - 0.5) * 0.1
        # --- MBO Parameter Integration: Influence Prime adoption by reward_sensitivity ---
        if "reward_sensitivity" in behavioral_params:
             prime_prob_adjust += (behavioral_params.get("reward_sensitivity", 0.5) - 0.5) * 0.15 # Higher sensitivity increases Prime likelihood

        final_prime_prob = max(0.01, min(0.99, base_prime_prob + prime_prob_adjust))
        is_prime = random.random() < final_prime_prob

        prime_start_date = None
        if is_prime:
            # Prime launched Feb 2005
            prime_possible_start = max(account_creation_date, datetime.datetime(2005, 2, 1))
            prime_possible_end = simulation_start_date - datetime.timedelta(days=1)
            if prime_possible_start < prime_possible_end:
                prime_start_date = utils.generate_random_date(prime_possible_start, prime_possible_end)
            else: # If account created after Prime launch but before sim start, Prime could start anytime between creation and sim start
                prime_start_date = utils.generate_random_date(account_creation_date, simulation_start_date - datetime.timedelta(days=1))

        # Determine usage of other services based on Prime AND behavioral parameters
        used_services = set()
        if is_prime: used_services.add("Prime Membership")

        tech_propensity = behavioral_params.get("tech_adoption_propensity", 0.5) # Use .get with default
        activity = behavioral_params.get("activity_level", 0.5) # Use .get with default

        # Media Services - Use .get with defaults for safety
        if is_prime and random.random() < behavioral_params.get("prime_video_engagement", 0.5): used_services.add("Prime Video")
        if (is_prime or random.random() < 0.1) and random.random() < behavioral_params.get("amazon_music_engagement", 0.3): # Small chance even if not prime
             used_services.add("Prime Music (Bundled)") # Assume bundled first
             if random.random() < 0.3 * tech_propensity: used_services.add("Amazon Music Unlimited") # Upgrade chance based on tech

        kindle_interest = any(i in interests for i in ["Books (Physical)", "Kindle Store", "eBooks"])
        if kindle_interest and random.random() < behavioral_params.get("kindle_engagement", 0.4):
             if is_prime: used_services.add("Prime Reading")
             if random.random() < 0.4: used_services.add("Kindle Unlimited")

        audible_interest = "Audible Books & Originals" in interests or (kindle_interest and random.random() < 0.3)
        if audible_interest and random.random() < behavioral_params.get("audible_engagement", 0.2) * (0.8 + behavioral_params.get("reward_sensitivity", 0.5) * 0.4): # Reward sensitivity slightly boosts
             # Simplified - just add a generic membership type
             used_services.add("Audible Membership (Premium Plus/Plus)")

        # Other Services - Use .get with defaults
        if random.random() < tech_propensity * 0.8: used_services.add("Alexa Skills Usage") # Higher tech -> more likely Alexa
        # --- MBO Parameter Integration: Influence Subscribe & Save by reward_sensitivity ---
        subscribe_save_base_prob = behavioral_params.get("subscribe_save_propensity", 0.1)
        subscribe_save_reward_boost = behavioral_params.get("reward_sensitivity", 0.5) * 0.1 # Sensitivity adds small boost
        final_subscribe_save_prob = max(0, min(1, subscribe_save_base_prob + subscribe_save_reward_boost))
        if random.random() < final_subscribe_save_prob: used_services.add("Subscribe & Save")
        if "Grocery & Gourmet Food" in interests and location_type in ["Dense Urban", "Urban", "Suburban"] and random.random() < 0.4 * activity: used_services.add("Amazon Fresh/Whole Foods Delivery")
        if "Health & Personal Care" in interests and random.random() < 0.2 * activity: used_services.add("Amazon Pharmacy")
        if random.random() < tech_propensity * 0.1: used_services.add("AWS Usage (Free/Paid)") # Low base chance, higher for techy
        if "Amazon Handmade" in interests and random.random() < 0.3: used_services.add("Amazon Handmade Buyer")
        if "Amazon Launchpad" in interests and random.random() < tech_propensity * 0.2: used_services.add("Amazon Launchpad Buyer")
        if random.random() < behavioral_params.get("deal_seeking_propensity", 0.5) * 0.5: used_services.add("Amazon Warehouse Deals Shopper")
        if random.random() < behavioral_params.get("deal_seeking_propensity", 0.5) * 0.4: used_services.add("Amazon Outlet Shopper")
        if random.random() < tech_propensity * 0.6: used_services.add("Amazon Photos")


        # 6. Device Usage (Influenced by tech_adoption_propensity)
        tech_propensity = behavioral_params.get("tech_adoption_propensity", 0.5)
        # Higher tech propensity -> more devices, more likely newer types
        num_devices_mean = 1.5 + tech_propensity * 3 # Mean devices from 1.8 to 4.5
        num_devices = max(1, int(random.gauss(num_devices_mean, 1.0))) # Gaussian distribution around mean

        # Weight devices based on tech propensity (simple example)
        device_weights = []
        for device_info in config.DEVICE_TYPES: # Iterate through device info dicts
            device_name = device_info.get("name", "Unknown Device")
            weight = 1.0
            # Adjust weight based on device type and tech propensity
            if any(t in device_name for t in ["Mobile", "Tablet", "App"]): weight *= (0.5 + tech_propensity)
            if any(t in device_name for t in ["Echo", "Fire TV", "Smart Watch", "Smart Home"]): weight *= (0.2 + tech_propensity * 1.5)
            if "Desktop" in device_name: weight *= (1.5 - tech_propensity) # Less likely primary for high tech?
            device_weights.append((device_info, max(0.1, weight))) # Store the whole dict with weight

        final_devices = []  # List to store chosen device dicts
        attempts = 0
        chosen_device_names = set() # Keep track of names to ensure uniqueness
        while len(final_devices) < num_devices and attempts < num_devices * 3:
            chosen_device_info = utils.select_weighted_item(device_weights)
            if chosen_device_info:
                 chosen_name = chosen_device_info.get("name")
                 if chosen_name and chosen_name not in chosen_device_names:
                      final_devices.append(chosen_device_info)
                      chosen_device_names.add(chosen_name)
            attempts += 1
        if not final_devices: # Ensure at least one device
             final_devices.append(random.choice(config.DEVICE_TYPES))

        primary_device_info = random.choice(final_devices)
        primary_device = primary_device_info.get("name", "Unknown Device")


        # 7. Determine Initial Login Frequency (Estimate based on activity level)
        activity_level = behavioral_params.get("activity_level", 0.5)
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
                "all_devices": sorted([d.get("name", "Unknown") for d in final_devices]), # Store only names
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
                "devices": final_devices, # Store full device info internally
                "primary_device": primary_device_info, # Store full primary device info internally
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
                "seasonal_boost": utils.get_seasonal_boost_from_config(simulation_start_date),
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
        # Convert device list in output_profile for JSON serialization if needed
        if 'device_usage' in output_profile and 'all_devices' in output_profile['device_usage']:
             # Already storing names, should be fine
             pass
        print(json.dumps(output_profile, indent=2, default=str))
        print("\n--- Sampled Behavioral Parameters (Internal State) ---")
        print(json.dumps(test_profile['_internal_state']['behavioral_params'], indent=2))
    else:
        print("Failed to generate test profile.")
    print("\n--- Persona Test Complete ---")