from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base

# Base class that all models inherit from
Base = declarative_base()

# Represents a single F1 race weekend
# Stores track, year, and round number
class Race(Base):
    __tablename__ = 'races'

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    round_number = Column(Integer, nullable=False) # which race in season
    track_name = Column(String, nullable=False)

# Represents a single lap driven by a driver in one race
# Stores lap time, tire info, and which race it belongs to
class Lap(Base):
    __tablename__ = 'laps'

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False) # links lap to specific race
    driver = Column(String, nullable=False) # VER, RUS, PIA
    lap_number = Column(Integer, nullable=False)
    lap_time_seconds = Column(Float, nullable=True) # Not all laps have recorded time (out of pit, accident)
    compound = Column(String, nullable=True) # SOFT, MEDIUM, HARD
    tyre_life = Column(Integer, nullable=True) # How many laps tire has been on the car
    stint = Column(Integer, nullable=True) # Stint 1 is before first pit stop, stint 2 is after, etc.
    is_pit_lap = Column(Integer, nullable=False, default=0) # 1 if driver pitted this lap

# Represents a single pit stop made by a driver during the race
# Stores which lap they pitted and how long the stop took
class PitStop(Base):
    __tablename__ = 'pit_stops'

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False) # Links pit stop to specific race
    driver = Column(String, nullable=False) # Which driver made the pit stop
    lap_number_pitted = Column(Integer, nullable=False) # Which lap they pitted on
    pit_duration_seconds = Column(Float, nullable=True)

# Represents a safety car or virtual safety car
# Stores start and end lap to calculate duration in laps
class SafetyCar(Base):
    __tablename__ = 'safety_cars'

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False) # Links safety car to specific race
    start_lap = Column(Integer, nullable=False)
    end_lap = Column(Integer, nullable=True) # SC active at end of race?
    sc_type = Column(String, nullable=False) # SC, VSC

# Represents a real-time interval reading from OpenF1
# Stores gap to car ahead and race position every 4 seconds
class Interval(Base):
    __tablename__ = 'intervals'

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False) # Links interval to specific race
    driver_number = Column(Integer, nullable=False)
    driver = Column(String, nullable=True) # three letter code
    timestamp = Column(String, nullable=False)  # UTC datetime string from OpenF1
    gap_to_ahead = Column(Float, nullable=True)  # Gap to car ahead in seconds, null if leading
    position = Column(Integer, nullable=True)  # Race position at this moment