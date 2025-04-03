# simulation.py - Refactored for Behavioral Parameters

import random
import datetime
import time
import logging
from collections import defaultdict

# Import necessary components from other modules
try:
    import config
    import utils
    import event_generator
except ImportError as e:
    logging.error(f"Error importing modules in simulation.py: {e}. Ensure config.py, utils.py, and event_generator.py exist.")
    raise

def check_for_minor_life_event(profile, days_since_last_event):
    """
    Checks if a minor life event occurs and updates profile state, potentially
    adjusting behavioral parameters slightly over the 5-year period.

    Args:
        profile (dict): The customer profile dictionary.
        days_since_last_event (int): Days passed since the last minor event check.

    Returns:
        bool: True if an event occurred, False otherwise.
    """
    state = profile["_internal_state"]
    # Probability increases slightly over time
    daily_prob = (config.MINOR_EVENT_YEARLY_PROB / 365.0) * (1 + days_since_last_event / (365 * 2.5)) # Slower increase

    if random.random() < daily_prob:
        if not config.MINOR_LIFE_EVENT_TYPES: return False

        chosen_event = random.choice(config.MINOR_LIFE_EVENT_TYPES)
        event_timestamp = state["current_timestamp"]
        current_age = state["current_age"]
        profile_id = profile.get("profile_id", "N/A")
        logging.info(f"Profile {profile_id} experienced minor life event: {chosen_event['name']} at age {current_age:.1f}")

        # Apply effects
        effect = chosen_event["effect"]
        behavioral_params = state.get("behavioral_params", {})

        # 1. Adjust Behavioral Parameters
        if "param_adjust" in effect:
            for param, adjustment in effect["param_adjust"].items():
                if param in behavioral_params:
                    current_value = behavioral_params[param]
                    # Apply adjustment (can be additive or multiplicative based on config if needed)
                    new_value = current_value + adjustment # Simple additive adjustment
                    # Clamp the value back to its original range defined in config, if range exists
                    param_config = config.BEHAVIORAL_PARAMS_CONFIG.get(param)
                    if param_config and "range" in param_config:
                        min_val, max_val = param_config["range"]
                        if new_value is not None: # Ensure value is not None before clamping
                            new_value = max(min_val, min(max_val, new_value))
                    behavioral_params[param] = new_value
                    logging.debug(f"  Param '{param}' adjusted to: {new_value:.3f}")
                else:
                    logging.warning(f"  Attempted to adjust non-existent param '{param}' for profile {profile_id}")

        # 2. Shift Interests
        if "interest_shift" in effect:
            new_interests = set()
            # Handle placeholder for hobby dynamically
            if "Related Hobby Supplies" in effect["interest_shift"]:
                # Pick a random hobby category if not already present
                hobby_cats = [i for i in config.BASE_INTEREST_CATEGORIES if any(h in i.lower() for h in ["hobby", "craft", "sport", "outdoor", "music", "collectible", "game"])]
                available_hobbies = [h for h in hobby_cats if h not in state["current_interests"]]
                if available_hobbies:
                    new_interests.add(random.choice(available_hobbies))
                # Add other specified interests
                new_interests.update(i for i in effect["interest_shift"] if i != "Related Hobby Supplies")
            else:
                new_interests.update(effect["interest_shift"])

            if new_interests:
                state["current_interests"].update(new_interests)
                # Optional: Prune oldest interests if list gets too long?
                max_interests = 25 # Example limit
                if len(state["current_interests"]) > max_interests:
                     # Simple pruning: remove random interests beyond the new ones
                     interests_to_prune = list(state["current_interests"] - new_interests)
                     num_to_remove = len(state["current_interests"]) - max_interests
                     if num_to_remove > 0 and len(interests_to_prune) >= num_to_remove:
                          removed = random.sample(interests_to_prune, num_to_remove)
                          state["current_interests"].difference_update(removed)

                logging.debug(f"  Minor interest shift. Added: {new_interests}. New count: {len(state['current_interests'])}")

        # Record the minor event
        profile.setdefault("life_events", []).append({
            "timestamp": utils.format_iso_timestamp(event_timestamp),
            "event_name": chosen_event["name"],
            "age_at_event": round(current_age, 1),
            "details": {"type": "minor"} # Could add params before/after if needed
        })
        return True # Event occurred
    return False # No event


def determine_next_event_type(profile_state):
    """
    Determines the next event type based on weighted probabilities derived
    from the profile's behavioral parameters and base weights.

    Args:
        profile_state (dict): The '_internal_state' of the profile.

    Returns:
        str: The chosen event type, or None if no events are possible.
    """
    event_weights = defaultdict(float)
    base_weights = config.BASE_EVENT_WEIGHTS
    params = profile_state.get("behavioral_params", {})

    # --- Get key parameters ---
    activity_level = params.get("activity_level", 0.5)
    deal_propensity = params.get("deal_seeking_propensity", 0.5)
    review_read_propensity = params.get("review_read_propensity", 0.5)
    review_write_propensity = params.get("review_write_propensity", 0.1)
    cart_abandon_propensity = params.get("cart_abandon_propensity", 0.3)
    return_propensity = params.get("return_propensity", 0.1)
    wishlist_propensity = params.get("wishlist_usage_propensity", 0.3)
    prime_video_engagement = params.get("prime_video_engagement", 0.5)
    music_engagement = params.get("amazon_music_engagement", 0.5)
    kindle_engagement = params.get("kindle_engagement", 0.5)
    audible_engagement = params.get("audible_engagement", 0.4)
    alexa_shopping_propensity = params.get("alexa_shopping_propensity", 0.1)
    subscribe_save_propensity = params.get("subscribe_save_propensity", 0.2)

    # --- Contextual state ---
    is_prime = profile_state.get("is_prime", False)
    has_echo = any("Echo" in d for d in profile_state.get("devices", []))
    has_kindle_access = any(s in profile_state.get("used_services", set()) for s in ["Kindle Unlimited", "Prime Reading"]) or any(i in profile_state.get("current_interests", set()) for i in ["Kindle Store", "Books (Physical)"])
    has_audible_access = "Audible Membership (Premium Plus/Plus)" in profile_state.get("used_services", set()) or "Audible Books & Originals" in profile_state.get("current_interests", set())
    has_music_access = any(s in profile_state.get("used_services", set()) for s in ["Amazon Music Unlimited", "Prime Music (Bundled)"])
    has_cart = bool(profile_state.get("cart", []))
    has_orders = bool(profile_state.get("orders", []))
    has_shipped_order = any(o.get("status") == "shipped" for o in profile_state.get("orders", []))
    has_delivered_order = any(o.get("status") == "delivered" for o in profile_state.get("orders", []))
    has_subscribesave_service = "Subscribe & Save" in profile_state.get("used_services", set())
    has_wholefoods_service = "Amazon Fresh/Whole Foods Delivery" in profile_state.get("used_services", set())
    has_pharmacy_service = "Amazon Pharmacy" in profile_state.get("used_services", set())
    has_photos_service = "Amazon Photos" in profile_state.get("used_services", set())
    has_aws_service = "AWS Usage (Free/Paid)" in profile_state.get("used_services", set())


    # --- Adjust weights based on parameters and state ---
    for event, base_weight in base_weights.items():
        adjusted_weight = float(base_weight)

        # Modify based on parameters and context
        if event == "purchase":
            # Purchase more likely if cart exists, less likely if high abandon propensity
            adjusted_weight *= (1.5 if has_cart else 0.2) * (1.0 - cart_abandon_propensity * 0.5)
        elif event == "add_to_cart":
             adjusted_weight *= (1.0 - cart_abandon_propensity * 0.3) # Less likely if high abandoner
        elif event == "remove_from_cart":
             adjusted_weight *= (cart_abandon_propensity * 2) if has_cart else 0
        elif event == "return_item":
             adjusted_weight *= (return_propensity * 2) if has_delivered_order else 0 # Higher chance if high return propensity
        elif event == "track_package":
             adjusted_weight = base_weight * 5 if has_shipped_order else 0
        elif event == "write_review" or event == "rate_product":
             adjusted_weight *= (review_write_propensity * 2) if has_delivered_order else 0
        elif event == "view_review":
             adjusted_weight *= (review_read_propensity * 1.5) # Boost based on propensity
        elif event == "watch_prime_video":
             adjusted_weight = base_weight * prime_video_engagement if is_prime else 0
        elif event == "listen_amazon_music":
             adjusted_weight = base_weight * music_engagement if has_music_access else 0
        elif event == "read_kindle_book":
             adjusted_weight = base_weight * kindle_engagement if has_kindle_access else 0
        elif event == "listen_audible":
             adjusted_weight = base_weight * audible_engagement if has_audible_access else 0
        elif event == "alexa_interaction":
             # Base likelihood on having echo, specific shopping intent handled in event_generator
             adjusted_weight = base_weight if has_echo else 0
        elif event == "order_whole_foods":
             adjusted_weight = base_weight if has_wholefoods_service else 0
        elif event == "manage_subscribe_save":
             adjusted_weight = base_weight * subscribe_save_propensity * 1.5 if has_subscribesave_service else 0
        elif event == "use_amazon_pharmacy":
             adjusted_weight = base_weight if has_pharmacy_service else 0
        elif event == "use_amazon_photos":
             adjusted_weight = base_weight if has_photos_service else 0
        elif event == "view_aws_console":
             adjusted_weight = base_weight if has_aws_service else 0
        elif event == "clip_coupon" or event == "view_deal":
             adjusted_weight *= (deal_propensity * 1.8) # Boost significantly for deal seekers
        elif event == "update_wishlist":
             adjusted_weight *= (wishlist_propensity * 1.5)

        # General activity level influence
        adjusted_weight *= (0.5 + activity_level) # Scale weight by activity (range 0.5 to 1.5 multiplier)

        # Store final weight if > 0
        if adjusted_weight > 0.01: # Use a small threshold to avoid near-zero weights
            event_weights[event] = adjusted_weight

    # --- Select Event ---
    possible_events = list(event_weights.keys())
    weights = list(event_weights.values())

    if not possible_events:
        logging.warning(f"No possible events could be determined for profile {profile_state.get('profile_id', 'N/A')}. State: {profile_state}")
        return "browse_category" # Fallback to browse if nothing else fits

    # Normalize weights before choosing? Optional, random.choices handles unnormalized.
    # total_weight = sum(weights)
    # normalized_weights = [w / total_weight for w in weights]
    # chosen_event = random.choices(possible_events, weights=normalized_weights, k=1)[0]

    chosen_event = random.choices(possible_events, weights=weights, k=1)[0]
    return chosen_event


def simulate_activity(profile):
    """
    Simulates user activity over the defined period using behavioral parameters.

    Args:
        profile (dict): The base customer profile dictionary with '_internal_state'.

    Returns:
        dict: The profile dictionary updated with 'activity_log', 'life_events',
              and final state summaries. Returns None if simulation fails critically.
    """
    if "_internal_state" not in profile or "behavioral_params" not in profile["_internal_state"]:
        logging.error(f"Profile {profile.get('profile_id', 'N/A')} missing '_internal_state' or 'behavioral_params'. Cannot simulate.")
        return None

    state = profile["_internal_state"]
    sim_start_date = state["current_timestamp"]
    end_date = sim_start_date + datetime.timedelta(days=config.SIMULATION_DURATION_DAYS)
    start_sim_time = time.time()
    event_count = 0
    profile_id = profile.get("profile_id", "N/A")

    logging.info(f"Simulating profile {profile_id} from {sim_start_date} to {end_date}")

    while state["current_timestamp"] < end_date:
        # 1. Calculate Time Delta to Next Event (using activity_level param)
        time_delta_hours = utils.calculate_event_time_delta(
            state["behavioral_params"]["activity_level"],
            state["seasonal_boost"]
        )

        # 2. Advance Time
        next_event_timestamp = state["current_timestamp"] + datetime.timedelta(hours=time_delta_hours)

        # 3. Handle Session Timeouts
        if (next_event_timestamp - state["last_event_timestamp"]).total_seconds() > 30 * 60:
            state["current_session_id"] = utils.generate_session_id()
            state["session_start_time"] = next_event_timestamp
            state["events_in_session"] = 0
            # logging.debug(f"New session {state['current_session_id']} started for profile {profile_id}") # Can be verbose

        # 4. Check for Day Change & Daily/Periodic Updates
        if next_event_timestamp.date() > state["current_timestamp"].date():
            days_passed = (next_event_timestamp.date() - state["current_timestamp"].date()).days
            state["time_since_last_minor_event"] = state.get("time_since_last_minor_event", 0) + days_passed
            state["current_age"] += days_passed / 365.0
            state["seasonal_boost"] = utils.get_seasonal_boost_from_config(next_event_timestamp)
            # Check for minor life events that might perturb parameters
            if check_for_minor_life_event(profile, state["time_since_last_minor_event"]):
                state["time_since_last_minor_event"] = 0

        # --- Update timestamp AFTER daily checks ---
        state["current_timestamp"] = next_event_timestamp
        if state["current_timestamp"] > end_date: break

        # 5. Determine Next Event Type (using refactored function)
        chosen_event_type = determine_next_event_type(state)
        if chosen_event_type is None:
            # logging.warning(f"Could not determine next event for profile {profile_id} at {state['current_timestamp']}. Skipping step.")
            state["last_event_timestamp"] = state["current_timestamp"]
            continue

        # 6. Generate Event Details & Update State
        details = event_generator.generate_event_details(
            chosen_event_type,
            profile,
            state["current_timestamp"]
        )

        # 7. Record Event
        if details:
            event = {
                "timestamp": utils.format_iso_timestamp(state["current_timestamp"]),
                "event_type": chosen_event_type,
                "details": details
            }
            profile["activity_log"].append(event)
            event_count += 1
            state["events_in_session"] += 1
            state["last_event_timestamp"] = state["current_timestamp"]

            # Log progress periodically (less frequently for longer sims)
            if event_count % 1000 == 0: # Log every 1000 events
                 elapsed = time.time() - start_sim_time
                 time_elapsed_sim = state["current_timestamp"] - sim_start_date
                 total_sim_duration = end_date - sim_start_date
                 percent_done = (time_elapsed_sim / total_sim_duration) * 100 if total_sim_duration.total_seconds() > 0 else 0
                 logging.debug(f"  Profile {profile_id}: {event_count} events. Sim Time: {state['current_timestamp'].date()}. Progress: {percent_done:.1f}%. Elapsed Real: {elapsed:.1f}s")
        else:
             # logging.debug(f"Could not generate details for event '{chosen_event_type}' for profile {profile_id}. Skipping.")
             state["last_event_timestamp"] = state["current_timestamp"]

    # --- Simulation End ---
    end_sim_time = time.time()
    logging.info(f"Finished simulating profile {profile_id}. Generated {event_count} events in {end_sim_time - start_sim_time:.2f} seconds.")

    # 8. Finalize Profile
    profile["activity_log"].sort(key=lambda x: x["timestamp"])

    # Update final demographic/status fields based on end state
    profile["demographics"]["age_at_simulation_end"] = round(state["current_age"], 1)
    profile["amazon_status"]["is_prime_member_final"] = state["is_prime"]
    profile["amazon_status"]["used_services_final"] = sorted(list(state["used_services"]))
    profile["interests_final"] = sorted(list(state["current_interests"]))

    # Remove internal state before saving
    try:
        del profile["_internal_state"]
    except KeyError:
        logging.warning(f"'_internal_state' key not found during finalization for profile {profile_id}.")

    return profile


if __name__ == '__main__':
    # Example usage/test requires refactored personas module
    logging.basicConfig(level=logging.INFO) # Use INFO for test run
    print("--- Testing Refactored Simulation ---")
    try:
        import personas # Import refactored personas here
        start_date = datetime.datetime(2024, 1, 1)
        # Generate a base profile using the refactored personas module
        base_profile = personas.create_base_profile(1, start_date)

        if base_profile:
            print(f"Base profile created for {base_profile['profile_id']}. Starting simulation...")
            # Run the simulation using the refactored logic
            simulated_profile = simulate_activity(base_profile)

            if simulated_profile:
                import json
                print(f"\nSimulation complete. Events generated: {len(simulated_profile['activity_log'])}")
                # Print a small sample of the final profile
                sample_output = {k: v for k, v in simulated_profile.items() if k != 'activity_log'}
                sample_output['activity_log_sample_size'] = len(simulated_profile['activity_log'])
                print(json.dumps(sample_output, indent=2, default=str))
            else:
                print("Simulation failed.")
        else:
            print("Failed to create base profile for simulation test.")

    except ImportError:
        print("Could not import personas module for testing simulation.")
    except Exception as e:
        print(f"An error occurred during simulation test: {e}", exc_info=True)

    print("\n--- Simulation Test Complete ---")