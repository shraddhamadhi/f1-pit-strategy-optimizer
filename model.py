import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine

# Set random seed for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# Loads lap data for a specific track and compound from the database
# Excludes pit stop laps, safety car laps, and outliers
# Calculates delta - how much slower each lap is compared to the second lap in that stint
def load_lap_data(track_name, compound):
    with Session(engine) as db:
        # Select tyre life and lap time from the laps table
        # Join with races table to filter by track name
        # 1 and r = aliases
        # WHERE = only get laps from the specific track and compound being analyzed (:track_name and :compound placeholders)
        # Exclude rows where either value is missing
        # Exclude first lap on a tire (cold tires)
        # Exclude pit stop laps (time spent in pit stop)
        # Exclude any lap over 150 seconds
        # Exclude laps with safety cars - existence check in safety car table, sc in same race, check if this lap falls within a sc period
        result = db.execute(text("""
            SELECT tyre_life, delta FROM (
                SELECT l.tyre_life,
                    l.lap_time_seconds - FIRST_VALUE(l.lap_time_seconds) OVER (
                        PARTITION BY l.race_id, l.driver, l.stint
                        ORDER BY l.tyre_life
                    ) as delta
                FROM laps l
                JOIN races r ON l.race_id = r.id
                WHERE r.track_name = :track_name
                AND l.compound = :compound
                AND l.lap_time_seconds IS NOT NULL
                AND l.tyre_life IS NOT NULL
                AND l.tyre_life >= 2
                AND l.is_pit_lap = 0
                AND l.lap_time_seconds < 150
                AND NOT EXISTS (
                    SELECT 1 FROM safety_cars sc
                    WHERE sc.race_id = l.race_id
                    AND l.lap_number BETWEEN sc.start_lap AND sc.end_lap
                )
            ) subquery
            WHERE delta >= -2
        """), {'track_name': track_name, 'compound': compound})
        
        # Convert the database results into a DataFrame with two columns
        rows = result.fetchall()
        return pd.DataFrame(rows, columns=['tyre_life', 'delta'])

# Neural network that predicts lap time delta based on tyre life
# Delta = how much slower than the second lap of the stint
# Input: tyre life (how many laps on this tire)
# Output: predicted delta in seconds
class TyreDegradationModel(nn.Module):
    def __init__(self):
        # Calls the parent nn.Module constructor
        super(TyreDegradationModel, self).__init__()
        # Container that chains layers together in order
        self.network = nn.Sequential(
            # Why choose these numbers?
            nn.Linear(1, 16), # 1 input (tyre life), 16 outputs
            nn.ReLU(), # If the value is negative, make it 0, otherwise keep it
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1) # 8 inputs, 1 output - predicted lap time in seconds
        )

    # x = input (tyre life)
    def forward(self, x):
        return self.network(x)

# Trains the TyreDegradationModel on historical lap data for a specific track and compound
# Predicts lap time delta based on tyre life
def train_model(track_name, compound):
    # Load training data
    df = load_lap_data(track_name, compound)

    if df.empty:
        print(f"No data for {track_name} - {compound}")
        return None
    
    # Convert to PyTorch tensors
    # reshape(-1, 1) makes each a column vector
    # X is input (tyre life)
    # Y is lap time delta
    X = torch.tensor(df['tyre_life'].values, dtype=torch.float32).reshape(-1, 1)
    y = torch.tensor(df['delta'].values, dtype=torch.float32).reshape(-1, 1)

    # Create model
    model = TyreDegradationModel()

    # Loss function and optimizer
    criterion = nn.MSELoss() # Measures how wrong the model's predictions are (Mean Squared Error)
    # Why choose Adam?
    optimizer = torch.optim.Adam(model.parameters(), lr = 0.001) # Adjusts the model's weights to reduce the loss, lr=0.01 is learning rate (how big each adjustment step is)

    # Train for 5000 epochs (each iteration, the model sees all the data, makes predictions, measures how wrong it is, and adjusts its weights)
    for epoch in range(5000):
        # Forward pass - feed tyre life values through the network, get predicted lap times, measure how wrong they are
        predictions = model(X)
        loss = criterion(predictions, y)

        # Backward pass
        optimizer.zero_grad() # Clear previous gradients so they don't accumulate
        loss.backward() # Calculate how much each weight contributed to the error
        optimizer.step() # Adjust weights to reduce the error

        if epoch % 500 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

    print(f"Model trained for {track_name} - {compound}")
    return model

# Uses the trained model to predict lap time delta for a given tyre life
# Returns predicted delta in seconds
def predict_lap_time(model, tyre_life):
    # Convert tyre life to tensor
    x = torch.tensor([[float(tyre_life)]], dtype = torch.float32)

    # No gradient needed for prediction - don't track (no adjustments)
    with torch.no_grad():
        prediction = model(x) # Passes tyre life through the trained network and gets a predicted lap time back
    
    # .item() converts tensor back into Python float
    return prediction.item()

# Calculates average lap time loss per lap between two tyre life values
# Returns degradation rate in seconds per lap
def get_degradation_rate(model, start_tyre_life, end_tyre_life):
    start_delta = predict_lap_time(model, start_tyre_life)
    end_delta = predict_lap_time(model, end_tyre_life)

    laps = end_tyre_life - start_tyre_life
    return (end_delta - start_delta) / laps

# Calculates average time lost by pitting at a specific track
# Filters to realistic pit stop durations (15 - 35 seconds) to exclude outliers (mech issues, drive-throughs)
# Returns average pit loss in seconds, defaults to 25.0 if no data
def get_pit_loss_time(track_name):
    with Session(engine) as db:
        # SELECT - calculates average pit stop duration across all pit stops at this track
        # Gets pit stops and joins with races to filter by track name
        # WHERE - only look at pit stops from this specific track
        # AND - exclude pit stops where duration wasn't recorded
        # AND - exclude pit stops below 15 seconds or above 35 seconds
        result = db.execute(text("""
            SELECT AVG(p.pit_duration_seconds)
            FROM pit_stops p
            JOIN races r ON p.race_id = r.id
            WHERE r.track_name = :track_name
            AND p.pit_duration_seconds IS NOT NULL
            AND p.pit_duration_seconds BETWEEN 15 AND 35
        """), {'track_name': track_name})

        # .scalar() gets a single value from the result
        avg_pit_loss = result.scalar()
        # Round to 3 decimal places
        return round(avg_pit_loss, 3) if avg_pit_loss else 25.0

# Test
pit_loss = get_pit_loss_time('Bahrain Grand Prix')
print(f"Average pit loss at Bahrain: {pit_loss}s")