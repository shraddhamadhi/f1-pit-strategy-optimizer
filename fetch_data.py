import fastf1
import pandas as pd
from sqlalchemy.orm import Session # Open database session
from sqlalchemy import select
from database import engine # From database.py
from models import Race, Lap, PitStop, SafetyCar
import os

# Absolute path
cache_path = os.path.join(os.path.dirname(__file__), 'data', 'cache')

# Enable FastF1 cache so data isn't re-downloaded every time
fastf1.Cache.enable_cache(cache_path)

# get_session(year, round_number, session_type)

# Fetch race data for given year and round number from FastF1 and stores it in PostgreSQL database
# Saves...
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
                stint = int(lap['Stint']) if pd.notna(lap['Stint']) else None # Which stint number
            )   
            )
        
        print("Saved laps")

        # Save pit stops:






        # Save safety cars:





        # Save intervals:


        db.commit()

fetch_race(2024, 1)


"""

# Fetch race data for given year and round number from FastF1 and stores it in PostgreSQL database
# Saves race info, lap times, pit stops, and safety car periods
def fetch_store_race(year, round_number):
    # Load race session from FastF1
    print(f"Loading {year} round {round_number}...")
    session = fastf1.get_session(year, round_number, 'R')
    session.load

    track_name = session.event['EventName']
    print(f"Track: {track_name}")

    with Session(engine) as db:

        # Save race to races table
        race = Race(
            year = year,
            round_number = round_number,
            track_name = track_name
        )

        db.add(race)
        db.flush() # Flush to get the race id before saving related data

        # Save laps
        laps = session.laps
        for _, lap in laps.itterows():
            lap_time = lap['LapTime'].total_seconds

"""