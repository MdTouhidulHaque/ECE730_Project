import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load the CSV file
csv_file_path = 'E:\Fall_24_Courses\ECE_730\Project_ECE730\half_hourly_normalized_data.csv'  # Replace with your local path
irradiance_data = pd.read_csv(csv_file_path).to_numpy()

# Extract data for January (days 1 to 31) and July (days 182 to 212)
january_data = irradiance_data[0:31, :]  # January: days 1-31
july_data = irradiance_data[181:212, :]  # July: days 182-212

# Create time axis for one day (48 half-hour intervals)
time_axis = np.linspace(0, 24, 48)

# Plot PV generation profiles for each day in January
plt.figure(figsize=(4, 3))
for day in range(31):
    plt.plot(time_axis, january_data[day], label=f'Day {day+1}', alpha=0.7)
#plt.title('Daily PV Generation Profiles for the Month of January', fontsize=16)
plt.xlabel('Time (hh:mm)', fontsize=22)
plt.ylabel('Normalized PV Generation', fontsize=22)
plt.xticks(np.arange(0, 25, 1), [f"{int(hour):02d}:00" for hour in np.arange(0, 25, 1)], rotation = 45, fontsize=18)
#plt.grid(visible=True, linestyle='--', alpha=0.5)
plt.yticks(fontsize=18)
plt.ylim(0,1)
plt.show()
#exit()
# Plot PV generation profiles for each day in July
plt.figure(figsize=(4, 3))
for day in range(31):
    plt.plot(time_axis, july_data[day], label=f'Day {day+1}', alpha=0.7)
#plt.title('Daily PV Generation Profiles for the Month of July', fontsize=16)
plt.xlabel('Time (hh:mm)', fontsize=22)
plt.ylabel('Normalized PV Generation', fontsize=22)
plt.xticks(np.arange(0, 25, 1), [f"{int(hour):02d}:00" for hour in np.arange(0, 25, 1)], rotation = 45, fontsize=18)
plt.yticks(fontsize=18)
plt.ylim(0,1)
#plt.grid(visible=True, linestyle='--', alpha=0.5)
plt.show()