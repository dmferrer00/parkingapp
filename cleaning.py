# Importing required libraries
import pandas as pd

# Define correct time blocks based on your spreadsheet layout
TIME_LABELS = ["10:00", "12:00", "14:00", "16:00", "18:00"]
BASE_COLUMNS = ['Student', 'Fac/Staff', 'Visitor/Meter', 'Reserved', 'Disabled', 'Reduced']

# Target parking decks
target_parking_decks = [
    "North Level 1", "North Level 2", "North Level 3", "North Level 4", "North Level 5", "North Level 6",
    "Union Level 1", "Union Level 2", "Union Level 3", "Union Level 4", "Union Level 5", "Union Level 6",
    "CRI Deck 1 Level 1", "CRI Deck 1 Level 2", "CRI Deck 1 Level 3", "CRI Deck 1 Level 4", "CRI Deck 1 Level 5", "CRI Deck 1 Level 6", "CRI Deck 1 Level 7",
    "West Level 1", "West Level 2", "West Level 3", "West Level 4", "West Level 5",
    "Cone 1", "Cone 2", "South Village Level 1", "South Village Level 2", "South Village Level 3",
    "South Village Level 4", "South Village Level 5", "South Village Level 6",
    "East 1 Level 1","East 1 Level 2", "East 1 Level 3","East 1 Level 4","East 2 Level 1","East 2 Level 2", "East 2 Level 3","East 2 Level 4","East 3 Level 1","East 3 Level 2","East 3 Level 3","East 3 Level 4","East 3 Level 5"
]

# Load and clean a single day's sheet
def load_and_reshape_day(filename, sheet_name):
    df = pd.read_excel(filename, sheet_name=sheet_name, header=1)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.strip()

    reshaped = []
    for i, time in enumerate(TIME_LABELS):
        suffix = '' if i == 0 else f'.{i}'
        time_columns = [f"{col}{suffix}" for col in BASE_COLUMNS if f"{col}{suffix}" in df.columns]

        if len(time_columns) == len(BASE_COLUMNS):
            sub_df = df[['Location'] + time_columns].copy()
            sub_df.columns = ['Location'] + BASE_COLUMNS
            sub_df['Time'] = time
            sub_df['Day'] = sheet_name
            reshaped.append(sub_df)

    return pd.concat(reshaped, ignore_index=True)

# Load and reshape all weekday data
filename = "ParkingSpring2025.xlsx"
df_all_days = pd.concat([
    load_and_reshape_day(filename, "Monday"),
    load_and_reshape_day(filename, "Tuesday"),
    load_and_reshape_day(filename, "Wednesday"),
    load_and_reshape_day(filename, "Thursday"),
    load_and_reshape_day(filename, "Friday"),
], ignore_index=True)

# Filter by location
df_all_days = df_all_days[df_all_days['Location'].isin(target_parking_decks)]

# Save final cleaned data
df_all_days.to_csv("cleaned_parking_data_all_days.csv", index=False)
