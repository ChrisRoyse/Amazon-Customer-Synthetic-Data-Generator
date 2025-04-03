# Amazon Customer Synthetic Data Generator

A sophisticated synthetic data generation system that creates realistic Amazon customer profiles with nuanced behavioral simulation over time. This project produces detailed customer profiles with activity logs spanning multiple years, driven by parameterized behavioral models, including new parameter concepts, leading to more robust and realistic data.

## 🚀 Features

- Generate UNLIMITED  diverse, realistic Amazon customer profiles
- Parameterized behavioral simulation across a 5-year period using statistical distributions
- **Improved Profile Diversity:** Utilizes weighted random selection for life stages and adjusted parameter distributions for greater realism.
- Detailed activity logs with timestamps and contextual information
- Realistic product interactions, purchases, and service usage patterns
- **New Event Type:** Includes `reorder_item` events driven by habit formation parameters.
- Minor life events that affect customer behavior over time
- Seasonal and promotional effects on shopping behavior
- Prime membership and Amazon service adoption simulation
- Device usage patterns and cross-platform behavior

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Data Model](#data-model)
- [Simulation Approach](#simulation-approach)
- [Output Format](#output-format)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

Requires Python 3.6+ and NumPy.

```bash
# Clone the repository
git clone https://github.com/yourusername/AmazonCustomers.git
cd AmazonCustomers

# Install dependencies (NumPy)
pip install numpy

# Alternatively, if you use a requirements file:
# pip install -r requirements.txt 
# (Note: requirements.txt not currently included in this project)
```

## 🔍 Usage

```bash
# Generate the default number of profiles (currently 20,000)
python generate_profiles.py

# Output is saved to JSON files in the current directory by default
# Each profile is saved as amazon_customer_profile_XXXXX.json
```

## ⚙️ Configuration

The `config.py` file contains all configurable parameters for the simulation, including core settings, behavioral parameter distributions, and life stage definitions.

### Core Settings
```python
NUM_PROFILES_TO_GENERATE = 20000  # Number of profiles to generate (Default: 20000)
SIMULATION_DURATION_YEARS = 5     # Duration of the simulation period 
OUTPUT_DIR = "."                  # Output directory for JSON files
FILENAME_PREFIX = "amazon_customer_profile_"  # Prefix for output files
FILENAME_DIGITS = 5               # Number of digits for the profile index in the filename
START_PROFILE_INDEX = 1           # Starting index for profile generation
```

### Behavioral Parameters
The system uses continuous behavioral parameters sampled from various statistical distributions (beta, exponential, normal, etc.) rather than discrete archetypes, allowing for more realistic variation. See `config.py` for the full list and distribution details.

**New MBO-Inspired Parameters:** Recent additions include parameters like `reward_sensitivity`, `attention_focus`, `category_exploration_propensity`, and `habit_formation_speed` to model more complex consumer decision-making processes.

```python
BEHAVIORAL_PARAMS_CONFIG = {
    # Core Shopping Behaviors
    "activity_level": {"range": (0.05, 0.95), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 2.0}},
    "purchase_frequency": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 2.0, "beta": 3.0}},
    "price_sensitivity": {"range": (0.1, 0.9), "type": "float", "distribution": "beta", "params": {"alpha": 3.0, "beta": 2.0}},
    # ... and many more parameters defined with ranges, types, and distributions, including MBO-inspired ones
}
```

### Life Stage Influences
Life stages provide initial context (demographics, interests) and apply adjustments to the sampled behavioral parameters. See `config.py` for the full list of life stages, their associated interests, and parameter adjustments.

**Weighted Selection:** Life stages are now selected using weights defined in `config.py` (e.g., `{"name": "...", "weight": 10, ...}`) to better reflect real-world demographic distributions.

```python
LIFE_STAGES = [
    {"name": "College Student", "age_range": (18, 24), "income_bracket_indices": [0, 1], 
     "interests": ["Textbooks", "Electronics", "Dorm Essentials", ...], 
     "param_adjustments": {"deal_seeking_propensity": 0.3, "tech_adoption_propensity": 0.2, ...},
     "weight": 8}, # Example weight
    # ... many other detailed life stages with weights
]
```

## 🏗️ Project Structure

- **`config.py`**: Core configuration, constants, distributions, life stages, interests, MBO parameters, etc.
- **`generate_profiles.py`**: Main script for generating profiles. Orchestrates the process.
- **`personas.py`**: Creates base customer profiles, samples behavioral parameters (including MBO) based on config and weighted life stage selection.
- **`simulation.py`**: Simulates customer activity over the defined time period based on parameters and state.
- **`event_generator.py`**: Generates specific event details (e.g., search query, product viewed, purchase details, reorder) for the activity log, influenced by parameters (including MBO).
- **`utils.py`**: Utility functions for ID generation, naming, dates, pricing, weighted choices, etc.

## 📊 Data Model

### Customer Profile Structure

```json
{
  "profile_id": "cust_00001",
  "generation_timestamp": "...",
  "simulation_period_start": "...",
  "simulation_period_end": "...",
  "demographics": {
    "age_at_simulation_end": 32.0,
    "birth_year": 1992,
    "location_type": "Urban",
    "household_composition_initial": "Couple (No Kids)",
    "estimated_income_bracket_initial": "Medium ($50k-$75k)",
    "life_stage_initial_context": "Young Professional"
  },
  "amazon_status": {
    "account_creation_date": "2015-06-12T14:23:45Z",
    "is_prime_member_initial": true,
    "prime_membership_start_date": "2018-03-22T09:14:32Z",
    "used_services_initial": ["Prime Membership", "Prime Video", "Subscribe & Save"],
    "is_prime_member_final": true,
    "used_services_final": ["Prime Membership", "Prime Video", "Subscribe & Save", "Amazon Photos"]
  },
  "device_usage": {
    "primary_device": {"name": "Mobile (iOS - iPhone)", "platform": "app", "conversion_rate": 0.038},
    "all_devices": [
        {"name": "Desktop (Windows)", "platform": "web", "conversion_rate": 0.045}, 
        {"name": "Mobile (iOS - iPhone)", "platform": "app", "conversion_rate": 0.038}, 
        {"name": "Echo Device (Standard)", "platform": "voice", "conversion_rate": 0.030}
    ],
    "login_frequency_initial_estimate": "Daily"
  },
  "interests_initial": ["Electronics", "Home Decor", "Travel"],
  "interests_final": ["Electronics", "Home Decor", "Travel", "Smart Home", "Wine & Spirits"],
  "behavioral_parameters": {
      "activity_level": 0.65,
      "purchase_frequency": 0.4,
      "price_sensitivity": 0.7,
      "reward_sensitivity": 0.8, 
      "attention_focus": 0.5,
      "category_exploration_propensity": 0.3,
      "habit_formation_speed": 0.6,
      "...": "..." 
  },
  "activity_log": [
    {
      "timestamp": "2020-01-02T19:12:23Z",
      "event_type": "search",
      "details": {
        "session_id": "a1b2c3d4-e5f6-4a5b-9c0d-1e2f3a4b5c6d",
        "device_used": {"name": "Mobile (iOS - iPhone)", "platform": "app", "conversion_rate": 0.038},
        "search_type": "Product Search",
        "search_query": "Electronics cheap",
        "results_count": 1234,
        "filters_used": ["prime", "rating_4_star_up"]
      }
    },
    {
      "timestamp": "2021-03-15T10:05:00Z",
      "event_type": "reorder_item",
      "details": {
         "session_id": "...",
         "device_used": {"name": "Desktop (Windows)", "platform": "web", "conversion_rate": 0.045},
         "product_id": "B07XYZABCD",
         "product_name": "Favorite Coffee Pods - 100 Count",
         "category": "Grocery",
         "price": 35.99,
         "quantity": 1 
      }
    }
    // Many more events...
  ],
  "life_events": [
    {
      "timestamp": "2022-06-15T08:34:12Z",
      "event_name": "New Pet",
      "age_at_event": 28.5,
      "details": {"type": "minor"}
    }
  ]
}
```

## 🔄 Simulation Approach

### Behavioral Parameters & Personas
1.  A life stage is chosen based on weighted probabilities defined in `config.py`.
2.  Behavioral parameters (activity level, price sensitivity, **MBO-inspired parameters like `reward_sensitivity`, `habit_formation_speed`**, etc.) are sampled for the profile using statistical distributions (beta, exponential, etc.) defined in `config.py`.
3.  Adjustments are applied to these parameters based on the chosen life stage.
4.  Initial demographics, interests, device usage, and Amazon service status are determined based on the life stage and sampled parameters.
5.  This forms the base profile and its internal state for simulation.

### Event Generation
1.  The simulation advances time step by step over the configured duration (e.g., 5 years).
2.  The time until the next event is calculated using an exponential distribution based on the profile's current `activity_level` and seasonal factors.
3.  The type of the next event (e.g., `search`, `view_product`, `purchase`, `watch_prime_video`, **`reorder_item`**) is chosen probabilistically. These probabilities are weighted based on the profile's behavioral parameters (including MBO-inspired ones like `attention_focus` or `category_exploration_propensity`) and current state (e.g., a profile with high `deal_seeking_propensity` is more likely to `clip_coupon`; `purchase` is more likely if the cart has items; `reorder_item` is influenced by `habit_formation_speed`).
4.  Detailed information for the chosen event is generated by `event_generator.py`, again influenced by parameters (e.g., search query terms influenced by interests and deal seeking; number of reviews read influenced by `review_read_propensity`; reorder likelihood influenced by `habit_formation_speed`).
5.  The profile's internal state (cart contents, viewed products, interests, etc.) is updated based on the event.
6.  Minor life events (e.g., `New Pet`, `Job Promotion`, `New Fitness Goal`) can occur periodically, slightly altering behavioral parameters and interests over the simulation duration.
7.  Seasonal effects (holidays, Prime Day) influence activity levels throughout the year.

## 📄 Output Format

Each profile is saved as a separate JSON file. The standard output contains:

- Basic demographic information (age, location type, etc.)
- Amazon account status (Prime status, services used - initial and final)
- Device usage patterns
- Initial and final interests
- Sampled behavioral parameters (including MBO-inspired ones)
- A detailed activity log of events over the simulation period
- A list of minor life events that occurred during the simulation

## 📝 Examples

A typical workflow to analyze the generated data:

```python
import json
import os
import glob
from collections import Counter
import numpy as np # Added for potential analysis

# Load generated profiles
profile_files = glob.glob("amazon_customer_profile_*.json")
profiles = []
print(f"Found {len(profile_files)} profile files.")

# Load a sample (e.g., first 100)
for file_path in profile_files[:100]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            profiles.append(json.load(f))
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {file_path}")
    except Exception as e:
        print(f"Error loading {file_path}: {e}")

if not profiles:
    print("No profiles loaded. Exiting analysis.")
else:
    print(f"Loaded {len(profiles)} profiles for analysis.")

    # Example: Count final Prime members
    prime_count = sum(1 for p in profiles if p.get("amazon_status", {}).get("is_prime_member_final", False))
    print(f"\nFinal Prime members: {prime_count}/{len(profiles)} ({prime_count/len(profiles)*100:.1f}%)")

    # Example: Most common final interests
    all_interests = []
    for p in profiles:
        all_interests.extend(p.get("interests_final", []))
        
    common_interests = Counter(all_interests).most_common(10)
    print("\nTop 10 final interests:")
    for interest, count in common_interests:
        print(f"- {interest}: {count}")

    # Example: Average number of events per profile
    total_events = sum(len(p.get("activity_log", [])) for p in profiles)
    avg_events = total_events / len(profiles) if profiles else 0
    print(f"\nAverage events per profile (in sample): {avg_events:.1f}")

    # Example: Distribution of primary devices
    primary_devices = [p.get("device_usage", {}).get("primary_device", {}).get("name", "Unknown") for p in profiles]
    device_counts = Counter(primary_devices).most_common(5)
    print("\nTop 5 Primary Devices:")
    for device, count in device_counts:
        print(f"- {device}: {count}")
        
    # Example: Analyze a behavioral parameter (e.g., habit_formation_speed)
    habit_speeds = [p.get("behavioral_parameters", {}).get("habit_formation_speed") for p in profiles if p.get("behavioral_parameters", {}).get("habit_formation_speed") is not None]
    if habit_speeds:
        avg_habit_speed = np.mean(habit_speeds)
        print(f"\nAverage Habit Formation Speed (in sample): {avg_habit_speed:.2f}")
    else:
        print("\nHabit Formation Speed data not found in sample profiles.")

```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details (if one exists).

---

## 🔮 Future Enhancements

- Add support for B2B customer simulation
- Implement more detailed product category interactions and attributes
- Create visualization tools for the generated profiles
- Add support for exporting to different formats (CSV, Parquet)
- Create a web interface for profile generation and configuration
- Refine life event impacts and add major life events
- Enhance product recommendation simulation within events
