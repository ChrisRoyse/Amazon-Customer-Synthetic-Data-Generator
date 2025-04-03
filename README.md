
# Amazon Customer Synthetic Data Generator

A sophisticated synthetic data generation system that creates realistic Amazon customer profiles with behavioral simulation over time. This project produces detailed customer profiles with activity logs spanning multiple years, driven by parameterized behavioral models rather than fixed archetypes.

## 🚀 Features

- Generate thousands of diverse, realistic Amazon customer profiles
- Parameterized behavioral simulation across a 5-year period
- Detailed activity logs with timestamps and contextual information
- Realistic product interactions, purchases, and service usage patterns
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

```bash
# Clone the repository
git clone https://github.com/yourusername/AmazonCustomers.git
cd AmazonCustomers

# No external dependencies required beyond Python 3.6+
# All modules use standard library components
```

## 🔍 Usage

```bash
# Generate the default number of profiles (25,000)
python generate_profiles.py

# Output is saved to JSON files in the current directory by default
# Each profile is saved as amazon_customer_profile_XXXXX.json
```

## ⚙️ Configuration

The `config.py` file contains all configurable parameters for the simulation:

### Core Settings
```python
NUM_PROFILES_TO_GENERATE = 25000  # Number of profiles to generate
SIMULATION_DURATION_YEARS = 5     # Duration of the simulation period 
OUTPUT_DIR = "."                  # Output directory for JSON files
FILENAME_PREFIX = "amazon_customer_profile_"  # Prefix for output files
```

### Behavioral Parameters
The system uses continuous behavioral parameters rather than discrete archetypes, allowing for more realistic variation:

```python
BEHAVIORAL_PARAMS_CONFIG = {
    "activity_level": {"range": (0.05, 0.95), "type": "float"},
    "review_read_propensity": {"range": (0.05, 0.95), "type": "float"},
    "deal_seeking_propensity": {"range": (0.05, 0.95), "type": "float"},
    "tech_adoption_propensity": {"range": (0.1, 0.9), "type": "float"},
    # ... and many more parameters
}
```

### Life Stage Influences
Life stages provide initial context and parameter influences:

```python
LIFE_STAGES = [
    {"name": "Student", "age_range": (18, 24), "income_bracket_indices": [0, 1, 2], 
     "interests": ["Books", "Textbooks", "Electronics"...], 
     "param_adjustments": {"deal_seeking_propensity": 0.2, ...}},
    # ... other life stages
]
```

## 🏗️ Project Structure

- **`config.py`**: Core configuration and constants
- **`generate_profiles.py`**: Main script for generating profiles
- **`personas.py`**: Creates base customer profiles with behavioral parameters
- **`simulation.py`**: Simulates customer activity over time
- **`event_generator.py`**: Generates specific event details for the activity log
- **`utils.py`**: Utility functions for ID generation, naming, dates, etc.

## 📊 Data Model

### Customer Profile Structure

```json
{
  "profile_id": "cust_00001",
  "demographics": {
    "age_at_simulation_end": 32,
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
    "used_services_final": ["Prime Membership", "Prime Video", "Subscribe & Save", "Amazon Photos"]
  },
  "device_usage": {
    "primary_device": "Mobile App (iOS)",
    "all_devices": ["Desktop Website (Windows)", "Mobile App (iOS)", "Echo Device"],
    "login_frequency_initial_estimate": "Daily"
  },
  "interests_initial": ["Electronics", "Home Decor", "Travel"],
  "interests_final": ["Electronics", "Home Decor", "Travel", "Smart Home", "Wine & Spirits"],
  "activity_log": [
    {
      "timestamp": "2020-01-02T19:12:23Z",
      "event_type": "search",
      "details": {
        "search_term": "bluetooth headphones",
        "search_type": "Product Search",
        "device": "Mobile App (iOS)",
        "session_id": "a1b2c3d4-e5f6-4a5b-9c0d-1e2f3a4b5c6d"
      }
    },
    // Many more events...
  ],
  "life_events": [
    {
      "timestamp": "2022-06-15T08:34:12Z",
      "event_name": "Relocation (Minor)",
      "age_at_event": 28.5,
      "details": {"type": "minor"}
    }
  ]
}
```

## 🔄 Simulation Approach

### Behavioral Parameters

Rather than using fixed customer "types," this system assigns continuous behavioral parameters to each profile:

- `activity_level`: Overall frequency of Amazon interactions
- `deal_seeking_propensity`: Tendency to use deals, coupons, sales
- `brand_affinity_strength`: Likelihood to repurchase same brand vs explore
- `tech_adoption_propensity`: Tendency to use newer features/devices/services
- And many more parameters driving realistic behavior patterns

### Event Generation

1. Each profile starts with behavioral parameters, demographics, and initial state
2. The simulation advances time, calculating intervals between events based on activity level
3. Event types are probabilistically selected based on profile parameters, state, and context
4. Detailed event information is generated appropriate to the event type
5. The profile's state is updated after each event
6. Minor life events can occur, slightly altering parameters and interests over time
7. Seasonal effects influence activity levels throughout the year

## 📄 Output Format

Each profile is saved as a separate JSON file. The standard output contains:

- Basic demographic information
- Amazon account status (Prime, services used)
- Device usage patterns
- Initial and final interests
- A detailed activity log of events
- Minor life events that occurred

## 📝 Examples

A typical workflow to analyze the generated data:

```python
import json
import os
import glob

# Load generated profiles
profile_files = glob.glob("amazon_customer_profile_*.json")
profiles = []

for file_path in profile_files[:100]:  # First 100 profiles
    with open(file_path, 'r') as f:
        profiles.append(json.load(f))

# Example: Count Prime members
prime_count = sum(1 for p in profiles if p["amazon_status"]["is_prime_member_final"])
print(f"Prime members: {prime_count}/{len(profiles)} ({prime_count/len(profiles)*100:.1f}%)")

# Example: Most common interests
all_interests = []
for p in profiles:
    all_interests.extend(p["interests_final"])
    
from collections import Counter
common_interests = Counter(all_interests).most_common(10)
print("Top 10 interests:")
for interest, count in common_interests:
    print(f"- {interest}: {count}")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🔮 Future Enhancements

- Add support for B2B customer simulation
- Implement more detailed product category interactions
- Create visualization tools for the generated profiles
- Add support for exporting to different formats (CSV, Parquet)
- Create a web interface for profile generation and configuration
