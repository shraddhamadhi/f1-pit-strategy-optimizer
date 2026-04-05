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
    round_number = Column(Integer, nullable=False)
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