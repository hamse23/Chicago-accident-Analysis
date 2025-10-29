import pyodbc
import csv

# Establish connection to SQL Server
def connect_to_sql_server(connection_string):
    try:
        conn = pyodbc.connect(connection_string)
        print("Connection to SQL Server successful.")
        return conn
    except Exception as e:
        print(f"Error connecting to SQL Server: {e}")
        raise

# Function to read CSV data
def read_csv(file_path):
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            data = [row for row in reader]
            print(f"Loaded {len(data)} rows from {file_path}")
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        raise

# Function to remove duplicate rows based on primary key
def remove_duplicates(data, key_columns):
    """
    Removes duplicate rows from the data based on key_columns.
    :param data: List of dictionaries representing rows from the CSV.
    :param key_columns: List of column names that make up the primary key.
    :return: Deduplicated list of rows.
    """
    seen_keys = set()
    deduplicated_data = []
    for row in data:
        # Create a tuple of key values for each row
        key = tuple(row[col] for col in key_columns)
        if key not in seen_keys:
            seen_keys.add(key)
            deduplicated_data.append(row)
    return deduplicated_data

# Function to insert data into SQL Server table with batch processing and progress tracking
def insert_data_batch(cursor, table_name, data, columns, batch_size=1000):
    try:
        placeholders = ", ".join(["?"] * len(columns))
        columns_string = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({columns_string}) VALUES ({placeholders})"
        batch = []
        total_rows = len(data)  # Total rows in the file
        rows_inserted = 0      # Counter for inserted rows

        for row in data:
            values = []
            for col in columns:
                if col == "AGE" or col == "VEHICLE_YEAR":  # Handle numeric conversions
                    try:
                        values.append(int(float(row[col])) if row[col] else None)
                    except ValueError:
                        values.append(None)  # Handle invalid or missing values
                else:
                    values.append(row[col])  # Leave other values as-is
            batch.append(values)

            if len(batch) == batch_size:
                cursor.executemany(query, batch)
                rows_inserted += len(batch)  # Update rows inserted count
                print(f"Inserted {rows_inserted}/{total_rows} rows into {table_name}...")
                batch = []  # Clear the batch

        # Insert any remaining rows
        if batch:
            cursor.executemany(query, batch)
            rows_inserted += len(batch)  # Update rows inserted count
            print(f"Inserted {rows_inserted}/{total_rows} rows into {table_name}...")

        print(f"Finished inserting all rows into {table_name}.")
    except Exception as e:
        print(f"Error inserting data into {table_name}: {e}")
        raise

# Define connection details
server = 'tcp:lds.di.unipi.it'
database = 'Group_ID_34_DB'
username = 'Group_ID_34'
password = '3GJ5KJ74'
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

# Connect to SQL Server
try:
    cnxn = connect_to_sql_server(connection_string)
    cursor = cnxn.cursor()
except Exception as e:
    print("Could not establish database connection. Exiting.")
    exit(1)

# Define files and their corresponding tables and columns
files_and_tables = [
    {"file": "Dim_date.csv", "table": "Dim_date", "columns": ["DateKey", "CRASH_DATE", "CRASH_HOUR", "CRASH_DAY_OF_WEEK", "CRASH_MONTH", "Year"]},
    {"file": "Dim_location.csv", "table": "Dim_location", "columns": ["LocationID", "STREET_NO", "STREET_DIRECTION", "STREET_NAME", "BEAT_OF_OCCURRENCE", "LATITUDE", "LONGITUDE"]},
    {"file": "Dim_weather.csv", "table": "Dim_weather", "columns": ["WeatherID", "WEATHER_CONDITION", "LIGHTING_CONDITION", "ROADWAY_SURFACE_COND"]},
    {"file": "Dim_cause.csv", "table": "Dim_cause", "columns": ["CauseID", "PRIM_CONTRIBUTORY_CAUSE", "SEC_CONTRIBUTORY_CAUSE"]},
    {"file": "Dim_people.csv", "table": "Dim_people", "columns": ["PersonID", "RD_NO", "PERSON_TYPE", "SEX", "AGE"]},
    {"file": "Dim_vehicle.csv", "table": "Dim_vehicle", "columns": ["VehicleID", "MAKE", "MODEL", "LIC_PLATE_STATE", "VEHICLE_YEAR", "VEHICLE_DEFECT", "VEHICLE_TYPE", "VEHICLE_USE"]},
    {"file": "Dim_crash.csv", "table": "Dim_crash", "columns": ["CrashKey", "RD_NO", "POSTED_SPEED_LIMIT", "TRAFFIC_CONTROL_DEVICE", "DEVICE_CONDITION", "TRAFFICWAY_TYPE", "ALIGNMENT", "SAFETY_EQUIPMENT", "AIRBAG_DEPLOYED", "TRAVEL_DIRECTION", "MANEUVER", "OCCUPANT_CNT", "FIRST_CONTACT_POINT"]},
    {"file": "Fact_damage.csv", "table": "Fact_damage", "columns": ["RD_NO", "PersonID", "VehicleID", "DAMAGE_CATEGORY", "DAMAGE", "DateKey", "WeatherID", "LocationID", "CauseID"]}
]

# Populate tables with all data using batch insertion and progress tracking
try:
    for item in files_and_tables:
        print(f"Populating table {item['table']} with data from file {item['file']}...")
        data = read_csv(item["file"])
        
        # Deduplicate data for Fact_damage
        if item["table"] == "Fact_damage":
            data = remove_duplicates(data, ["RD_NO", "PersonID", "VehicleID"])
            print(f"Deduplicated Fact_damage: {len(data)} rows remain after removing duplicates.")
        
        insert_data_batch(cursor, item["table"], data, item["columns"])
    cnxn.commit()
    print("Population of all tables completed successfully.")
except Exception as e:
    print(f"An error occurred: {e}")
    cnxn.rollback()
finally:
    cursor.close()
    cnxn.close()
    print("Database connection closed.")
