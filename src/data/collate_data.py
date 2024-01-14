import os
import pandas as pd

# Set the directory where your CSV files are located
directory_path = 'bond_data/'

# Initialize an empty DataFrame to store the merged data
dfs = []

# Loop through the CSV files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.csv'):
        print(f"Getting data for: {filename}")
        # Extract the date from the filename
        date_collected = '_'.join(filename.split('_')[2:5]).split(".")[0]  # Assumes the date is in the third position (dd_mm_yyyy)
        date_collected = pd.to_datetime(date_collected, format='%d_%m_%Y').date()

        # Read the CSV file
        file_path = os.path.join(directory_path, filename)
        df = pd.read_csv(file_path)

        # Add the "Date Collected" column with the extracted date
        df['Date Collected'] = date_collected

        # Append the data to the merged DataFrame
        dfs.append(df)
    else:
        print(f"Not getting data for: {filename}")

merged_data = pd.concat(dfs, ignore_index=True)
# Save the merged data to a new CSV file
merged_data.to_csv('all_bond_data.csv', index=False)
