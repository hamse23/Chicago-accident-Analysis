import csv
from collections import defaultdict
from rapidfuzz import process, fuzz

# Load data from CSV
def load_csv(file_path):
    with open(file_path, 'r') as file:
        return [row for row in csv.DictReader(file)]

# Save data to CSV
def save_csv(file_path, data, fieldnames):
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Standardize city names
def standardize_city(city_name):
    return city_name.strip().lower() if city_name else None

# Function to find the best match using RapidFuzz
def semantic_correct_city(city_name, reference_list, threshold=80):
    if not city_name:
        return None
    match = process.extractOne(city_name, reference_list, scorer=fuzz.ratio)
    if match and match[1] >= threshold:
        return match[0]
    return city_name

# Map corrected cities to their states
def map_city_to_state(row, city_to_state_mapping):
    city = row.get("corrected_city", "").strip().lower()
    return city_to_state_mapping.get(city, "XX")

# Clean and format city and state
def clean_and_format(data, reference_list):
    for row in data:
        city = row.get("CITY")
        row["CITY"] = standardize_city(city)
        row["corrected_city"] = semantic_correct_city(row["CITY"], reference_list)
        row["corrected_city"] = row["corrected_city"].strip().title() if row["corrected_city"] else ""
        row["STATE"] = row.get("STATE", "").strip().upper()
    return data

# Correct state based on city-to-state mapping
def correct_state(data, city_to_state_mapping):
    for row in data:
        if row.get("corrected_city") and row.get("corrected_city") != "Unknown":
            row["corrected_state"] = map_city_to_state(row, city_to_state_mapping)
        else:
            row["corrected_state"] = "XX"
    return data

# Fill missing DAMAGE based on DAMAGE_CATEGORY
def fill_missing_damage(data):
    damage_category_to_damage = {
        "OVER $1,500": 3000,
        "$501 - $1,500": 1000,
        "$500 OR LESS": 250
    }
    for row in data:
        if not row.get("DAMAGE") and row.get("DAMAGE_CATEGORY") in damage_category_to_damage:
            row["DAMAGE"] = damage_category_to_damage[row["DAMAGE_CATEGORY"]]
    return data

# Fill missing SEX values
def fill_missing_sex(data):
    for row in data:
        if not row.get("SEX"):
            row["SEX"] = "X"
    return data

# Fill default values in other columns
def fill_defaults(data):
    default_values = {
        "SAFETY_EQUIPMENT": "USAGE UNKNOWN",
        "AIRBAG_DEPLOYED": "DEPLOYMENT UNKNOWN",
        "EJECTION": "UNKNOWN",
        "INJURY_CLASSIFICATION": "UNKNOWN",
        "DRIVER_ACTION": "UNKNOWN",
        "DRIVER_VISION": "UNKNOWN",
        "PHYSICAL_CONDITION": "UNKNOWN",
        "BAC_RESULT": "UNKNOWN"
    }
    for row in data:
        for key, default in default_values.items():
            if not row.get(key):
                row[key] = default
    return data

# Assign AGE_GROUP and fill missing AGE_GROUP and AGE
def assign_age_group(data):
    age_bins = [0, 12, 19, 35, 60, 120]
    age_labels = ['Child', 'Teen', 'Young Adult', 'Adult', 'Senior']

    def get_age_group(age):
        for i, upper in enumerate(age_bins[1:], start=1):
            if age < upper:
                return age_labels[i - 1]
        return age_labels[-1]

    age_groups = defaultdict(list)
    for row in data:
        age = row.get("AGE")
        if age:
            age = float(age)
            row["AGE_GROUP"] = get_age_group(age)
            age_groups[row["AGE_GROUP"]].append(age)

    for row in data:
        if not row.get("AGE_GROUP"):
            row["AGE_GROUP"] = max(age_groups, key=lambda g: len(age_groups[g]))
        if not row.get("AGE"):
            group = row["AGE_GROUP"]
            row["AGE"] = sum(age_groups[group]) / len(age_groups[group]) if age_groups[group] else None
    return data

# Process VEHICLE_ID column
def process_vehicle_id(data):
    for row in data:
        vehicle_id = row.get("VEHICLE_ID")
        if not vehicle_id or vehicle_id.strip() in ("", "-1"):
            row["VEHICLE_ID"] = -1
        else:
            row["VEHICLE_ID"] = vehicle_id.strip()
    return data

# Main function
def rename_and_clean_columns(data):
    """
    Rename `corrected_city` to `CITY` and `corrected_state` to `STATE`,
    and remove the old `CITY` and `STATE` columns.

    Args:
        data (list): List of dictionaries representing the dataset.

    Returns:
        list: Updated dataset with renamed and cleaned columns.
    """
    for row in data:
        # Rename corrected_city to CITY
        if "corrected_city" in row:
            row["CITY"] = row.pop("corrected_city")
        
        # Rename corrected_state to STATE
        if "corrected_state" in row:
            row["STATE"] = row.pop("corrected_state")
        
        # Remove old CITY and STATE columns if they exist
        row.pop("CITY", None)
        row.pop("STATE", None)
    
    return data

# Example usage
def process_data_with_rename(people_file, reference_file, output_file):
    # Load data
    people_data = load_csv(people_file)
    reference_data = load_csv(reference_file)

    # Create city reference list and city-to-state mapping
    reference_list = [row["city"].strip().lower() for row in reference_data]
    city_to_state_mapping = {row["city"].strip().lower(): row["state_id"] for row in reference_data}

    # Clean, format, and correct city and state
    people_data = clean_and_format(people_data, reference_list)
    people_data = correct_state(people_data, city_to_state_mapping)

    # Fill missing values and clean data
    people_data = fill_missing_damage(people_data)
    people_data = fill_missing_sex(people_data)
    people_data = fill_defaults(people_data)
    people_data = assign_age_group(people_data)
    people_data = process_vehicle_id(people_data)

    # Rename columns and clean up
    people_data = rename_and_clean_columns(people_data)

    # Save processed data
    fieldnames = people_data[0].keys()
    save_csv(output_file, people_data, fieldnames)

# Run processing
process_data_with_rename('people.csv', 'uscities.csv', 'processed_people.csv')