import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

# Correct the file path
data_path = r'E:\Thesis_MSc_Touhid\Fort_Chipewyan_Network\normalized_Fortchip_PV_data_365x24.csv'  # Use a raw string

# Load the normalized data from the CSV file
data = pd.read_csv(data_path, header=None).to_numpy()

# Add a 24th column by duplicating the 23rd column
data = np.column_stack((data, data[:, -1]))

# Function to replace missing or zero values with the average of their neighbors
def replace_with_neighbors(data_row):
    for j in range(len(data_row)):
        if np.isnan(data_row[j]) or data_row[j] == 0:  # Adjust condition to identify missing or incorrect values
            neighbors = []
            if j > 0:  # Left neighbor
                neighbors.append(data_row[j - 1])
            if j < len(data_row) - 1:  # Right neighbor
                neighbors.append(data_row[j + 1])
            if neighbors:
                data_row[j] = np.mean(neighbors)  # Replace with the average of neighbors
    return data_row

# Ensure all rows have 24 valid values
for i in range(365):
    data[i] = replace_with_neighbors(data[i])  # Replace missing/incorrect values

# Create a new array to hold the half-hourly data
half_hour_array = np.zeros((365, 48))

# Perform linear interpolation for each day to get 48 half-hourly values
for i in range(365):
    x = np.arange(24)  # Original hourly points (0 to 23 hours)
    y = data[i]        # Data for interpolation
    x_new = np.linspace(0, 23, 48)  # New half-hourly points evenly spaced between 0 and 23
    f = interp1d(x, y, kind='linear')
    half_hour_array[i] = f(x_new)

# Round the data to 2 decimal places
half_hour_array = np.round(half_hour_array, 2)

# Save the half-hourly data as a CSV file
output_csv_path = 'half_hourly_normalized_data.csv'  # Desired output file name
pd.DataFrame(half_hour_array).to_csv(output_csv_path, index=False, header=False)

print(f"Half-hourly data has been saved to {output_csv_path}")


# Load the data from the CSV file
csv_path = 'half_hourly_normalized_data.csv'  # Path to your CSV file
data = pd.read_csv(csv_path, header=None).to_numpy()

# Save the data as a NumPy file
numpy_path = 'half_hourly_normalized_data.npy'  # Desired output file name
np.save(numpy_path, data)

print(f"Data has been converted to NumPy format and saved to {numpy_path}")
