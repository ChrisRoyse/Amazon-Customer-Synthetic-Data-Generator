# generate_profiles_v2.py

import os
import json
import datetime
import time
import logging
import math

# Import shared configuration and utility functions
try:
    import config
    import utils
except ImportError as e:
    logging.error(f"Failed to import config or utils: {e}. Ensure config.py and utils.py are present.")
    exit(1) # Exit if core config/utils are missing

# Import core generation logic modules
try:
    import personas
    import simulation
except ImportError as e:
    logging.error(f"Failed to import personas or simulation: {e}. Ensure personas.py and simulation.py are present.")
    exit(1) # Exit if generation logic is missing


# --- Logging Setup ---
# Configure logging level (e.g., INFO for general progress, DEBUG for detailed steps)
log_level = logging.INFO # Or change to logging.DEBUG for more verbosity
logging.basicConfig(level=log_level,
                    format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# --- Main Execution ---

def main():
    """Main function to generate customer profiles."""
    output_dir = config.OUTPUT_DIR
    num_profiles = config.NUM_PROFILES_TO_GENERATE
    start_index = config.START_PROFILE_INDEX
    filename_prefix = config.FILENAME_PREFIX
    filename_digits = config.FILENAME_DIGITS
    sim_duration_days = config.SIMULATION_DURATION_DAYS # Use pre-calculated days from config

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir) and output_dir != ".":
        try:
            os.makedirs(output_dir)
            logging.info(f"Created output directory: {output_dir}")
        except OSError as e:
            logging.error(f"Failed to create output directory '{output_dir}': {e}")
            return # Stop execution if directory cannot be created

    logging.info(f"--- Starting Synthetic Amazon Customer Profile Generation ---")
    logging.info(f"Number of profiles to generate: {num_profiles}")
    logging.info(f"Profile indices: {start_index} to {start_index + num_profiles - 1}")
    logging.info(f"Simulation duration: {config.SIMULATION_DURATION_YEARS} years ({sim_duration_days} days)")
 # Use years in log
    logging.info(f"Output directory: {os.path.abspath(output_dir)}")
    logging.info(f"File size/line limits: Disabled (prioritizing detail)") # Updated log message

    total_start_time = time.time()
    profiles_generated = 0
    profiles_failed = 0

    # Determine the simulation start date (relative to "now" when the script runs)
    # All profiles will share the same simulation time window for consistency
    simulation_start_date_for_all = datetime.datetime.now() - datetime.timedelta(days=config.SIMULATION_DURATION_DAYS) # Use config value directly
    logging.info(f"Simulation time window: {simulation_start_date_for_all.date()} to {datetime.datetime.now().date()}")

    # --- Generation Loop ---
    for i in range(start_index, start_index + num_profiles):
        profile_index = i
        profile_start_time = time.time()
        logging.info(f"--- Generating profile {profile_index:0{filename_digits}d}/{start_index + num_profiles - 1} ---")

        base_profile = None
        simulated_profile = None
        final_profile_data = None

        try:
            # 1. Create Base Profile
            logging.debug(f"[{profile_index}] Calling create_base_profile...")
            base_profile = personas.create_base_profile(profile_index, simulation_start_date_for_all)
            if not base_profile:
                raise ValueError("Failed to create base profile structure.")
            logging.debug(f"[{profile_index}] Base profile created.")

            # 2. Simulate Activity
            logging.debug(f"[{profile_index}] Calling simulate_activity...")
            simulated_profile = simulation.simulate_activity(base_profile) # Pass the profile with internal state
            if not simulated_profile:
                raise ValueError("Simulation failed to produce a final profile.")
            logging.debug(f"[{profile_index}] Simulation complete. Events: {len(simulated_profile.get('activity_log', []))}")

            # 3. Finalize Profile Data (No truncation needed anymore)
            final_profile_data = simulated_profile # Use the potentially truncated profile

            # 4. Construct File Path
            file_name = f"{filename_prefix}{profile_index:0{filename_digits}d}.json"
            file_path = os.path.join(output_dir, file_name)

            # 5. Write Profile to JSON File
            logging.debug(f"[{profile_index}] Writing profile to {file_path}...")
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use indent for readability, ensure_ascii=False for broader character support
                json.dump(final_profile_data, f, indent=2, ensure_ascii=False, default=str) # default=str handles datetime objects

            profile_end_time = time.time()
            logging.info(f"Successfully generated and saved profile {profile_index:0{filename_digits}d} (took {profile_end_time - profile_start_time:.2f}s)")
            profiles_generated += 1

        except Exception as e:
            profile_end_time = time.time()
            logging.error(f"Error processing profile {profile_index:0{filename_digits}d} (took {profile_end_time - profile_start_time:.2f}s): {e}", exc_info=True) # exc_info=True logs traceback
            profiles_failed += 1
            # Optional: Decide whether to stop or continue on error
            # continue # Default: Continue to next profile
            # break # Uncomment to stop on the first error

        # --- Progress Logging ---
        profiles_processed = profiles_generated + profiles_failed
        if profiles_processed % 50 == 0 or i == start_index + num_profiles - 1: # Log every 50 profiles or at the end
             elapsed_total = time.time() - total_start_time
             avg_time = elapsed_total / profiles_processed if profiles_processed > 0 else 0
             est_remaining_profiles = num_profiles - profiles_processed
             est_remaining_time = est_remaining_profiles * avg_time if avg_time > 0 else 0
             logging.info(f"Progress: {profiles_processed}/{num_profiles} profiles processed.")
             logging.info(f"Success: {profiles_generated}, Failed: {profiles_failed}.")
             logging.info(f"Avg time/profile: {avg_time:.2f}s. Est. time remaining: {est_remaining_time:.0f}s ({est_remaining_time/60.0:.1f} min)")


    # --- Final Summary ---
    total_end_time = time.time()
    logging.info(f"\n--- Generation Complete ---")
    logging.info(f"Total execution time: {total_end_time - total_start_time:.2f} seconds")
    logging.info(f"Successfully generated: {profiles_generated} profiles")
    logging.info(f"Failed to generate: {profiles_failed} profiles")
    logging.info(f"Profiles saved in '{os.path.abspath(output_dir)}'.")
    if profiles_failed > 0:
        logging.warning("There were errors during generation. Please check the log above for details on failed profiles.")

if __name__ == "__main__":
    main()