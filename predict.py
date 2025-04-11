import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import datetime
import re

class ParkingPredictor:
    def __init__(self):
        self.models = {}  # One model per location
        self.location_encoder = LabelEncoder()
        self.day_encoder = LabelEncoder()
        self.locations = None
        self.parking_decks = {}  # Mapping from deck name to specific levels
        self.data_times = ["10:00", "12:00", "14:00", "16:00", "18:00"]  # Times in your data
        self.time_to_float = {
            "10:00": 10.0,
            "12:00": 12.0,
            "14:00": 14.0,
            "16:00": 16.0,
            "18:00": 18.0
        }
    
    def preprocess_data(self, data):
        """Preprocess the parking data for training."""
        # Create a copy to avoid modifying the original dataframe
        df = data.copy()
        
        # Fill missing values with 0
        for col in ['Student', 'Fac/Staff', 'Visitor/Meter', 'Reserved', 'Disabled', 'Reduced']:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # Encode categorical variables
        df['day_encoded'] = self.day_encoder.fit_transform(df['Day'])
        
        # Add time column if it doesn't exist (default to 12:00)
        if 'Time' not in df.columns:
            df['Time'] = "12:00"
        
        # Convert time formats to standardized 24-hour format
        df['Time'] = df['Time'].apply(self.standardize_time)
        
        # Convert time to float for regression (e.g., 14:30 becomes 14.5)
        df['time_float'] = df['Time'].map(lambda t: self.time_to_hours(t))
        
        # Save locations for later
        self.locations = df['Location'].unique()
        self.location_encoder.fit(self.locations)
        
        # Create parking deck mapping
        self._map_decks_to_levels(df)
        
        return df
    
    def _map_decks_to_levels(self, df):
        """Create mapping from deck names to specific levels."""
        # Extract deck names from location names
        for location in self.locations:
            # Try to identify the deck name from the location
            deck_name = self._extract_deck_name(location)
            
            # Add to the deck mapping
            if deck_name not in self.parking_decks:
                self.parking_decks[deck_name] = []
            
            self.parking_decks[deck_name].append(location)
            
            # Also add the full location name as a key for exact matching
            if location not in self.parking_decks:
                self.parking_decks[location] = [location]
                
        print(f"Identified {len(self.parking_decks)} parking decks:")
        for deck, levels in self.parking_decks.items():
            if len(levels) > 1:  # Only print multi-level decks
                print(f"- {deck}: {len(levels)} levels")
    
    def _extract_deck_name(self, location):
        """Extract the deck name from a location string."""
        # Common patterns in location names
        level_pattern = re.compile(r'(.*?)\s+Level\s+\d+', re.IGNORECASE)
        floor_pattern = re.compile(r'(.*?)\s+Floor\s+\d+', re.IGNORECASE)
        
        # Try to match with "Level X" pattern
        level_match = level_pattern.match(location)
        if level_match:
            return level_match.group(1).strip()
        
        # Try to match with "Floor X" pattern
        floor_match = floor_pattern.match(location)
        if floor_match:
            return floor_match.group(1).strip()
        
        # Handle common suffixes like "Deck", "Garage", "Village", etc.
        common_suffixes = ["Deck", "Garage", "Village", "Lot", "Structure", "Center"]
        
        for suffix in common_suffixes:
            if f" {suffix}" in location:
                # Get the base name without the suffix
                parts = location.split(f" {suffix}")
                return f"{parts[0]} {suffix}".strip()
        
        # If no patterns match, return the location as is
        return location
    
    def standardize_time(self, time_str):
        """Convert various time formats to 24-hour format string."""
        # Handle already standardized time
        if time_str in self.data_times:
            return time_str
            
        # Simple mapping for common formats
        time_mapping = {
            "10am": "10:00", "10 am": "10:00", "10AM": "10:00", "10 AM": "10:00",
            "12pm": "12:00", "12 pm": "12:00", "12PM": "12:00", "12 PM": "12:00", "noon": "12:00",
            "2pm": "14:00", "2 pm": "14:00", "2PM": "14:00", "2 PM": "14:00", "14pm": "14:00",
            "4pm": "16:00", "4 pm": "16:00", "4PM": "16:00", "4 PM": "16:00", "16pm": "16:00",
            "6pm": "18:00", "6 pm": "18:00", "6PM": "18:00", "6 PM": "18:00", "18pm": "18:00"
        }
        
        if time_str in time_mapping:
            return time_mapping[time_str]
        
        # Default to noon if we can't parse the time
        return "12:00"
    
    def time_to_hours(self, time_str):
        """Convert time string to float hours (e.g., "14:30" to 14.5)."""
        if time_str in self.time_to_float:
            return self.time_to_float[time_str]
            
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours + minutes / 60.0
        except (ValueError, AttributeError):
            # Default to noon if we can't parse
            return 12.0
    
    def parse_arrival_time(self, time_str):
        """Parse any reasonable time format to float hours."""
        # Handle 24-hour format (HH:MM)
        if ':' in time_str:
            try:
                hours, minutes = map(int, time_str.split(':'))
                return hours + minutes / 60.0
            except (ValueError, AttributeError):
                pass
        
        # Handle formats like "5pm", "5 pm", etc.
        time_str = time_str.lower().strip()
        
        # Extract AM/PM indicator
        is_pm = False
        if "pm" in time_str:
            is_pm = True
            time_str = time_str.replace("pm", "").strip()
        elif "am" in time_str:
            time_str = time_str.replace("am", "").strip()
        
        # Try to extract the hour
        try:
            hour = float(time_str)
            if is_pm and hour < 12:
                hour += 12
            return hour
        except ValueError:
            # Default to noon if we can't parse
            return 12.0
    
    def format_time(self, hour_float):
        """Format float hours as HH:MM string."""
        hours = int(hour_float)
        minutes = int((hour_float - hours) * 60)
        am_pm = "AM" if hours < 12 else "PM"
        
        # Convert to 12-hour format
        display_hour = hours % 12
        if display_hour == 0:
            display_hour = 12
        
        return f"{display_hour}:{minutes:02d} {am_pm}"
    
    def train(self, data):
        """Train linear regression models for each parking location."""
        processed_data = self.preprocess_data(data)
        
        print(f"Training models for {len(self.locations)} locations...")
        
        # Train a separate model for each location to predict occupancy
        for location in self.locations:
            # Filter data for this location
            location_data = processed_data[processed_data['Location'] == location]
            
            if len(location_data) < 2:
                print(f"Insufficient data for {location}, skipping...")
                continue
                
            # Train one model per day of the week for this location
            for day in self.day_encoder.classes_:
                day_data = location_data[location_data['Day'] == day]
                
                if len(day_data) < 2:
                    continue
                
                # Features: time as float
                X = day_data[['time_float']]
                
                # Target: total occupancy (sum of all user types)
                y = day_data[['Student', 'Fac/Staff', 'Visitor/Meter', 'Reserved']].sum(axis=1)
                
                # Create and train the linear regression model
                model = LinearRegression()
                model.fit(X, y)
                
                # Store the model with key (location, day)
                self.models[(location, day)] = model
                
                # Calculate and print R² score
                score = model.score(X, y)
                print(f"Model for {location} on {day}: R² = {score:.4f}")
        
        return len(self.models)
    
    def predict_occupancy(self, day, arrival_time, deck_name=None):
        """Predict occupancy for specified location(s) on a given day at arrival time."""
        if not self.models:
            return "No models trained yet. Please train the models first."
        
        # Convert arrival time to float hours
        arrival_hours = self.parse_arrival_time(arrival_time)
        formatted_time = self.format_time(arrival_hours)
        
        # Check if the time is within operating hours (adjust as needed)
        if arrival_hours < 7.0 or arrival_hours > 20.0:
            return f"Warning: {formatted_time} may be outside normal operating hours (7:00 AM - 8:00 PM)"
        
        # If deck_name is provided, filter locations to just that deck
        locations_to_check = []
        matched_deck = None
        if deck_name:
            # Find the closest matching deck name
            matched_deck = self._find_matching_deck(deck_name)
            if matched_deck:
                locations_to_check = self.parking_decks[matched_deck]
            else:
                return f"Parking deck '{deck_name}' not found. Available decks are: {', '.join(sorted(set(self._get_base_deck_names())))}"
        else:
            # Check all locations
            locations_to_check = self.locations
        
        # Predict occupancy for each location
        predictions = []
        
        for location in locations_to_check:
            model_key = (location, day)
            
            # If we don't have a specific day model for this location, skip
            if model_key not in self.models:
                continue
            
            # Get the model and predict
            model = self.models[model_key]
            try:
                predicted_occupancy = max(0, model.predict([[arrival_hours]])[0])
                # Calculate capacity (approximate from your data)
                capacity = 200  # Default capacity estimate
                
                # Calculate available spaces (simple estimate)
                available = max(0, capacity - predicted_occupancy)
                
                predictions.append((location, predicted_occupancy, available))
            except:
                continue
        
        # Sort by available spaces (descending)
        sorted_predictions = sorted(predictions, key=lambda x: x[2], reverse=True)
        
        return sorted_predictions, formatted_time, matched_deck
    
    def _get_base_deck_names(self):
        """Get a list of base deck names (without the level information)."""
        deck_names = []
        for location in self.locations:
            deck_name = self._extract_deck_name(location)
            if deck_name != location:  # Only include if it's a deck with multiple levels
                deck_names.append(deck_name)
        return deck_names
    
    def _find_matching_deck(self, deck_name):
        """Find the best matching deck name from the available decks."""
        if not deck_name:
            return None
            
        deck_name = deck_name.lower().strip()
        
        # First try exact match
        for deck in self.parking_decks:
            if deck.lower() == deck_name:
                return deck
        
        # Then try case-insensitive matching
        for deck in self.parking_decks:
            # Check if input is contained in deck name
            if deck_name in deck.lower():
                return deck
                
            # Check if deck name parts are in the input
            deck_parts = deck.lower().split()
            if any(part in deck_name for part in deck_parts if len(part) > 2):
                return deck
                
            # Handle common naming variations
            for suffix in ["deck", "garage", "village", "lot", "structure", "center"]:
                # If deck_name is "North" and deck is "North Deck", match them
                if deck_name == deck.lower().replace(f" {suffix}", ""):
                    return deck
                # If deck_name is "North Deck" and deck is "North", match them
                if f"{deck.lower()} {suffix}" == deck_name:
                    return deck
        
        return None
    
    def load_csv(self, file_path):
        """Load parking data from a CSV file."""
        data = pd.read_csv(file_path)
        return data
    
    def recommend_parking(self, day, arrival_time, deck_name=None):
        """Provide a user-friendly parking recommendation."""
        if not self.models:
            return "No models trained yet. Please train the models first."
        
        result = self.predict_occupancy(day, arrival_time, deck_name)
        
        if isinstance(result, str):  # Error message
            return result
        
        predictions, formatted_time, matched_deck = result
        
        if not predictions:
            if deck_name:
                return f"No predictions available for {matched_deck or deck_name} on {day} at {formatted_time}."
            else:
                return f"No predictions available for {day} at {formatted_time}."
        
        # Create recommendation message
        if deck_name:
            message = f"For {matched_deck} on {day} at {formatted_time}:\n"
        else:
            message = f"For {day} at {formatted_time}, here are your top parking recommendations:\n"
        
        # Get the top 5 locations with most available spaces (or all if looking at specific deck)
        display_count = min(5, len(predictions))
        for i, (location, occupancy, available) in enumerate(predictions[:display_count], 1):
            message += f"{i}. {location} (Est. available spaces: {int(available)})\n"
        
        return message

# Example usage
if __name__ == "__main__":
    # Sample data format (this would normally come from your CSV)
    sample_data = pd.DataFrame({
        'Location': ['North Deck Level 6', 'North Deck Level 6', 'North Deck Level 6', 
                     'Union Village Level 5', 'Union Village Level 5'],
        'Student': [143, 130, 110, 110, 87],
        'Fac/Staff': [0, 0, 0, 109, 87],
        'Visitor/Meter': [0, 0, 0, 1, 1],
        'Reserved': [0, 0, 0, 4, 1],
        'Disabled': [0, 0, 0, 0, 0],
        'Reduced': [0, 0, 0, 0, 0],
        'Day': ['Monday', 'Monday', 'Monday', 'Monday', 'Monday'],
        'Time': ['10:00', '14:00', '18:00', '10:00', '16:00']
    })
    
    predictor = ParkingPredictor()
    
    # Normally you would load actual data like this:
    # data = predictor.load_csv('parking_data.csv')
    
    # Train the models
    predictor.train(sample_data)
    
    # Examples of different ways to query
    print(predictor.recommend_parking('Monday', '5:00pm', 'North Deck'))  # Full deck name
    print(predictor.recommend_parking('Monday', '5:00pm', 'North'))       # Just the base name
    print(predictor.recommend_parking('Monday', '11:30am'))               # All decks