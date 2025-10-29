import csv
from datetime import datetime

# Read final merged data from CSV
def read_csv(filepath):
    with open(filepath, mode='r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

# Write data to CSV
def write_csv(filepath, data, fieldnames):
    with open(filepath, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Load final merged data
final_merged = read_csv('final_merged.csv')  # Replace with your final merged file path

# Create Dim_date
dim_date = []
date_keys = {}
for row in final_merged:
    crash_date = row['CRASH_DATE']
    if crash_date not in date_keys:
        date_obj = datetime.strptime(crash_date, "%m/%d/%Y %I:%M:%S %p")
        surrogate_key = len(date_keys) + 1
        date_keys[crash_date] = surrogate_key
        dim_date.append({
            "DateKey": surrogate_key,
            "CRASH_DATE": crash_date,
            "CRASH_HOUR": date_obj.hour,
            "CRASH_DAY_OF_WEEK": date_obj.strftime('%A'),
            "CRASH_MONTH": date_obj.strftime('%B'),
            "Year": date_obj.year
        })

# Create Dim_location
dim_location = []
location_keys = {}
for row in final_merged:
    loc_key = (row.get('STREET_NO', ''), row.get('STREET_DIRECTION', ''), row.get('STREET_NAME', ''), row.get('BEAT_OF_OCCURRENCE', ''), row['LATITUDE'], row['LONGITUDE'])
    if loc_key not in location_keys:
        surrogate_key = len(location_keys) + 1
        location_keys[loc_key] = surrogate_key
        dim_location.append({
            "LocationID": surrogate_key,
            "STREET_NO": row.get('STREET_NO', ''),
            "STREET_DIRECTION": row.get('STREET_DIRECTION', ''),
            "STREET_NAME": row.get('STREET_NAME', ''),
            "BEAT_OF_OCCURRENCE": row.get('BEAT_OF_OCCURRENCE', ''),
            "LATITUDE": row['LATITUDE'],
            "LONGITUDE": row['LONGITUDE']
        })

# Create Dim_weather
dim_weather = []
weather_keys = {}
for row in final_merged:
    weather_key = (row['WEATHER_CONDITION'], row['LIGHTING_CONDITION'], row.get('ROADWAY_SURFACE_COND', ''))
    if weather_key not in weather_keys:
        surrogate_key = len(weather_keys) + 1
        weather_keys[weather_key] = surrogate_key
        dim_weather.append({
            "WeatherID": surrogate_key,
            "WEATHER_CONDITION": row['WEATHER_CONDITION'],
            "LIGHTING_CONDITION": row['LIGHTING_CONDITION'],
            "ROADWAY_SURFACE_COND": row.get('ROADWAY_SURFACE_COND', '')
        })

# Create Dim_cause
dim_cause = []
cause_keys = {}
for row in final_merged:
    cause_key = (row.get('PRIM_CONTRIBUTORY_CAUSE', ''), row.get('SEC_CONTRIBUTORY_CAUSE', ''))
    if cause_key not in cause_keys:
        surrogate_key = len(cause_keys) + 1
        cause_keys[cause_key] = surrogate_key
        dim_cause.append({
            "CauseID": surrogate_key,
            "PRIM_CONTRIBUTORY_CAUSE": row.get('PRIM_CONTRIBUTORY_CAUSE', ''),
            "SEC_CONTRIBUTORY_CAUSE": row.get('SEC_CONTRIBUTORY_CAUSE', '')
        })

# Create Dim_people
dim_people = []
people_keys = {}
for row in final_merged:
    person_key = row['PERSON_ID']
    if person_key not in people_keys:
        surrogate_key = len(people_keys) + 1
        people_keys[person_key] = surrogate_key
        dim_people.append({
            "PersonID": surrogate_key,
            "RD_NO": row['RD_NO'],
            "PERSON_TYPE": row['PERSON_TYPE'],
            "SEX": row['SEX'],
            "AGE": row['AGE']
        })

# Create Dim_vehicle
dim_vehicle = []
vehicle_keys = {}
for row in final_merged:
    vehicle_key = row['VEHICLE_ID']
    if vehicle_key not in vehicle_keys:
        surrogate_key = len(vehicle_keys) + 1
        vehicle_keys[vehicle_key] = surrogate_key
        dim_vehicle.append({
            "VehicleID": surrogate_key,
            "MAKE": row['MAKE'],
            "MODEL": row['MODEL'],
            "LIC_PLATE_STATE": row['LIC_PLATE_STATE'],
            "VEHICLE_YEAR": row['VEHICLE_YEAR'],
            "VEHICLE_DEFECT": row['VEHICLE_DEFECT'],
            "VEHICLE_TYPE": row['VEHICLE_TYPE'],
            "VEHICLE_USE": row['VEHICLE_USE']
        })

# Create Dim_crash
dim_crash = []
crash_keys = {}
for row in final_merged:
    rd_no = row['RD_NO']
    if rd_no not in crash_keys:
        surrogate_key = len(crash_keys) + 1
        crash_keys[rd_no] = surrogate_key
        dim_crash.append({
            "CrashKey": surrogate_key,
            "RD_NO": rd_no,
            "POSTED_SPEED_LIMIT": row['POSTED_SPEED_LIMIT'],
            "TRAFFIC_CONTROL_DEVICE": row['TRAFFIC_CONTROL_DEVICE'],
            "DEVICE_CONDITION": row['DEVICE_CONDITION'],
            "TRAFFICWAY_TYPE": row['TRAFFICWAY_TYPE'],
            "ALIGNMENT": row['ALIGNMENT'],
            "SAFETY_EQUIPMENT": row['SAFETY_EQUIPMENT'],
            "AIRBAG_DEPLOYED": row['AIRBAG_DEPLOYED'],
            "TRAVEL_DIRECTION": row['TRAVEL_DIRECTION'],
            "MANEUVER": row['MANEUVER'],
            "OCCUPANT_CNT": row['OCCUPANT_CNT'],
            "FIRST_CONTACT_POINT": row['FIRST_CONTACT_POINT']
        })

# Create Fact_damage
fact_damage = []
for row in final_merged:
    fact_damage.append({
        "RD_NO": row['RD_NO'],
        "PersonID": people_keys[row['PERSON_ID']],
        "VehicleID": vehicle_keys[row['VEHICLE_ID']],
        "DAMAGE_CATEGORY": row['DAMAGE_CATEGORY'],
        "DAMAGE": row['DAMAGE'],
        "DateKey": date_keys[row['CRASH_DATE']],
        "WeatherID": weather_keys[(row['WEATHER_CONDITION'], row['LIGHTING_CONDITION'], row.get('ROADWAY_SURFACE_COND', ''))],
        "LocationID": location_keys[(row.get('STREET_NO', ''), row.get('STREET_DIRECTION', ''), row.get('STREET_NAME', ''), row.get('BEAT_OF_OCCURRENCE', ''), row['LATITUDE'], row['LONGITUDE'])],
        "CauseID": cause_keys[(row.get('PRIM_CONTRIBUTORY_CAUSE', ''), row.get('SEC_CONTRIBUTORY_CAUSE', ''))]
    })

# Save the dimension and fact tables
write_csv('Dim_date.csv', dim_date, fieldnames=["DateKey", "CRASH_DATE", "CRASH_HOUR", "CRASH_DAY_OF_WEEK", "CRASH_MONTH", "Year"])
write_csv('Dim_location.csv', dim_location, fieldnames=["LocationID", "STREET_NO", "STREET_DIRECTION", "STREET_NAME", "BEAT_OF_OCCURRENCE", "LATITUDE", "LONGITUDE"])
write_csv('Dim_weather.csv', dim_weather, fieldnames=["WeatherID", "WEATHER_CONDITION", "LIGHTING_CONDITION", "ROADWAY_SURFACE_COND"])
write_csv('Dim_cause.csv', dim_cause, fieldnames=["CauseID", "PRIM_CONTRIBUTORY_CAUSE", "SEC_CONTRIBUTORY_CAUSE"])
write_csv('Dim_people.csv', dim_people, fieldnames=["PersonID", "RD_NO", "PERSON_TYPE", "SEX", "AGE"])
write_csv('Dim_vehicle.csv', dim_vehicle, fieldnames=["VehicleID", "MAKE", "MODEL", "LIC_PLATE_STATE", "VEHICLE_YEAR", "VEHICLE_DEFECT", "VEHICLE_TYPE", "VEHICLE_USE"])
write_csv('Dim_crash.csv', dim_crash, fieldnames=["CrashKey", "RD_NO", "POSTED_SPEED_LIMIT", "TRAFFIC_CONTROL_DEVICE", "DEVICE_CONDITION", "TRAFFICWAY_TYPE", "ALIGNMENT", "SAFETY_EQUIPMENT", "AIRBAG_DEPLOYED", "TRAVEL_DIRECTION", "MANEUVER", "OCCUPANT_CNT", "FIRST_CONTACT_POINT"])
write_csv('Fact_damage.csv', fact_damage, fieldnames=["RD_NO", "PersonID", "VehicleID", "DAMAGE_CATEGORY", "DAMAGE", "DateKey", "WeatherID", "LocationID", "CauseID"])

print("Dimension and fact tables saved successfully.")
