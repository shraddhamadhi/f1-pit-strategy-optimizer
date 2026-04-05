import fastf1
import pandas as pd
import requests
import os
from sqlalchemy.orm import Session # Open database session
from sqlalchemy import select
from database import engine # From database.py
from models import Race, Lap, PitStop, SafetyCar, Interval

# Absolute path
cache_path = os.path.join(os.path.dirname(__file__), 'data', 'cache')

# Enable FastF1 cache so data isn't re-downloaded every time
fastf1.Cache.enable_cache(cache_path)

# get_session(year, round_number, session_type)

# Gets the OpenF1 session key for a given race by matching the country name from FastF1 to the correct OpenF1 session
def get_openf1_session_key(year, round_number):
    # Get country name from FastF1 for this round
    event = fastf1.get_event(year, round_number)
    country = event['Country']

    # Get all race sessions for this year from OpenF1
    url = f"https://api.openf1.org/v1/sessions?year={year}&session_name=Race"
    response = requests.get(url) # HTTP GET request to OpenF1
    sessions = response.json() # Converts the response from JSON into Python list of dictionaries - each item in the list is one race session
    
    print(f"Available countries: {[s.get('country_name') for s in sessions]}")

    # Match by country name
    for s in sessions:
        if s.get('country_name', '').lower() == country.lower():
            return s['session_key']
        
    return None

# Fetches interval data from OpenF1 for a given session
# Returns gap to car ahead and position for each driver every 4 seconds
def fetch_openf1_intervals(session_key):
    url = f"https://api.openf1.org/v1/intervals?session_key={session_key}"
    response = requests.get(url)
    return response.json()

# Fetches driver number to three letter acronym mapping from OpenF1 per session
# Link OpenF1 interval data (driver_number) to FastF1 data (three letter code)
def get_driver_mapping(session_key):
    url = f"https://api.openf1.org/v1/drivers?session_key={session_key}"
    response = requests.get(url)
    drivers = response.json()
    
    # Build a dictionary: {driver_number: name_acronym} - {1: 'VER', 44: 'HAM', 16: 'LEC'}
    return {d['driver_number']: d['name_acronym'] for d in drivers}

# Fetch race data for given year and round number from FastF1 and stores it in PostgreSQL database
# Saves race info, lap times, pit stops, safety car periods, and intervals
def fetch_race(year, round_number):
    # Loading 2024 round 1...
    print(f"Loading {year} round {round_number}...")
    # Store race session in session
    session = fastf1.get_session(year, round_number, 'R')
    # Download data
    session.load()

    track_name = session.event['EventName']
    print(f"Track: {track_name}")

    # Opens connection to database
    with Session(engine) as db:

        # Check if this race already exists
        existing = db.execute(
            select(Race).where(Race.year == year, Race.round_number == round_number)
        ).first()
        if existing:
            print(f"{track_name} {year} already exists.")
            return

        # Save race to races table:
        # Create new Race object
        race = Race(
            year = year,
            round_number = round_number,
            track_name = track_name
        )

        # Stage
        db.add(race)
        # Send staged data to database
        db.flush() # Flush to get race.id before saving related data

        print(f"Saved race: {track_name} {year} with id {race.id}")

        # Save laps:
        print("Saving laps...")
        laps = session.laps # Get all laps from the session as a pandas DataFrame

        for _, lap in laps.iterrows(): # Loop through the table one row at a time (_ = row index, lap = row data)
            # LapTime timedelta object -> convert to seconds (float)
            lap_time = lap['LapTime'].total_seconds() if pd.notna(lap['LapTime']) else None # pd.notna() checks if a value is NOT missing (missing = False)
            db.add(Lap(
                race_id = race.id, # Links this lap to the race just saved
                driver = lap['Driver'],
                lap_number = int(lap['LapNumber']), # Which lap of the race
                lap_time_seconds = lap_time, # Lap duration in seconds
                compound = lap['Compound'] if pd.notna(lap['Compound']) else None, # SOFT, MEDIUM, HARD
                tyre_life = int(lap['TyreLife']) if pd.notna(lap['TyreLife']) else None, # Laps on this tire
                stint = int(lap['Stint']) if pd.notna(lap['Stint']) else None, # Which stint number
                is_pit_lap = 1 if pd.notna(lap['PitInTime']) else 0  # 1 if pitted this lap
            ))
        
        print("Saved laps")

        # Save pit stops:
        print("Saving pit stops...")
        # 'laps' DataFrame has PitInTime column - most laps are empty (no pit stop)
        pit_laps = laps[laps['PitInTime'].notna()] # Only laps where driver ptited

        # Loop through each pit stop lap
        for _, lap in pit_laps.iterrows():
            # PitOutTime is on the next lap, not the same lap as PitInTime
            # Get the next lap for this driver
            # Filters the entire laps DataFrame to find the next lap for specific driver
            next_lap = laps[
                (laps['Driver'] == lap['Driver']) & # Same driver
                (laps['LapNumber'] == lap['LapNumber'] + 1) # Lap number is current lap + 1
            ]
            
            # not next_nap.empty - next lap exists
            # pd.notna(next_lap.iloc[0]['PitOutTime']) - PitOutTime exists on that lap
            # .iloc[0] - gets the first (and only) row from the filtered result
            if not next_lap.empty and pd.notna(next_lap.iloc[0]['PitOutTime']):
                # Get first row from the next lap DataFrame and give PitOutTime value
                pit_out = next_lap.iloc[0]['PitOutTime']
                # Subtract PitInTime from PitOutTime (next lap)
                pit_duration = (pit_out - lap['PitInTime']).total_seconds()
            else:
                pit_duration = None
            
            # Create new PitStop object
            db.add(PitStop(
                race_id = race.id,
                driver = lap['Driver'],
                lap_number_pitted = int(lap['LapNumber']),
                pit_duration_seconds = pit_duration
            ))

        print("Pit stops saved")

        # Save safety cars:
        print("Saving safety cars...")
        track_status = session.track_status # track_status object - green flag, yellow flag, SC, VSC, red flag
        # Active safety car period?
        sc_start = None
        sc_type = None

        # Loop through each status change
        # Status = status code, lap = lap which it happened on
        for _, row in track_status.iterrows():
            status = row['Status']
            lap = row['Lap'] if 'Lap' in row else None

            # 4 = Safety Car, 6 = Virtual Safety Car
            # If not already tracking a safety car period, record the start lap and type
            if status in ['4', '6'] and sc_start is None:
                sc_start = lap
                sc_type = 'SC' if status == '4' else 'VSC'

            # 1 = Green flag - safety car period has ended
            # Save safety card period with start and end lap
            elif status == '1' and sc_start is not None:
                db.add(SafetyCar(
                    race_id = race.id,
                    start_lap = sc_start,
                    end_lap = lap,
                    sc_type = sc_type
                ))  

                # Reset for next safety car
                sc_start = None
                sc_type = None
    
        print("Safety cars saved")

        # Save intervals from F1:
        print("Saving intervals...")
        session_key = get_openf1_session_key(year, round_number) # Gets OpenF1 session key for this race
        driver_mapping = get_driver_mapping(session_key) # Gets the dictionary mapping driver numbers to three letter codes for this specific race
        intervals = fetch_openf1_intervals(session_key) # Fetches all interval readings for this race

        for interval in intervals: # Loops through each interval reading
            # Convert driver number to three letter code using mapping
            driver_number = interval['driver_number'] # Gets the driver number from this reading
            driver = driver_mapping.get(driver_number) # Looks up driver number in mapping: 1 -> 'VER'

            # Interval field is gap to car ahead - None if leading or lapped
            # interval['interval] is gap to car ahead in seconds
            if interval['interval'] is None or isinstance(interval['interval'], str):
                gap = None
            else:
                gap = float(interval['interval'])

            # Interval object
            db.add(Interval(
                race_id = race.id,
                driver_number = driver_number,
                driver = driver,
                timestamp = interval['date'],
                gap_to_ahead = gap,
                position = None
            ))
        
        print("Intervals saved")

        db.commit()

fetch_race(2023, 1)
fetch_race(2024, 1)
fetch_race(2025, 1)
fetch_race(2026, 1)