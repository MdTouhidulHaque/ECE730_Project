import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# Load the 30-minute resolution load data
mydir = os.getcwd()
print("The files are located in the following path: mydir = %s" % mydir)
houseData30minutes = np.load(mydir + '\\Residential load data 30-min resolution.npy')

# Visualize dataset dimensions
shape_profiles = houseData30minutes.shape
print(shape_profiles)
noProfiles = shape_profiles[0]

# Scaling up the load profiles
houseData30minutes = 3.5 * houseData30minutes  #For month of July
#houseData30minutes = 5 * houseData30minutes

# Create time labels for plotting
x = [i for i in range(48)]
time_labels = []
for i in range(24):
    time_labels.append(f"{i}:00")
    time_labels.append(" ")

# Plot diversified load profiles for January (days 1 to 31)
plt.figure(figsize=(16, 9))
#for day in range(31):  # January has 31 days
for day in range(152, 181):
    average_profile = houseData30minutes[:, day, :].mean(axis=0)  # Average across all households
    plt.plot(average_profile, label=f'Day {day + 1}', alpha=0.7)

plt.xlabel("Time (hh:mm)", fontsize=22)
plt.xticks(x, time_labels, fontsize=16, rotation=60)
plt.ylabel("Active Power (kW)", fontsize=22)
plt.yticks(fontsize=18)
#plt.title("Diversified Residential Load Profiles for the Month of January", fontsize=14)
#plt.grid(visible=True, linestyle="--", alpha=0.5)
#plt.show()

#exit()
# Plot diversified load profiles for July (days 182 to 212)
plt.figure(figsize=(16, 9))
for day in range(334, 365):  # July: days 182 to 212
    average_profile = houseData30minutes[:, day, :].mean(axis=0)  # Average across all households
    plt.plot(average_profile, label=f'Day {day - 181}', alpha=0.7)

plt.xlabel("Time (hh:mm)", fontsize=22)
plt.xticks(x, time_labels, fontsize=18, rotation=60)
plt.ylabel("Active Power (kW)", fontsize=22)
plt.yticks(fontsize=18)
plt.ylim(0,6)
#plt.title("Diversified Residential Load Profiles for the Month of July", fontsize=14)
#plt.grid(visible=True, linestyle="--", alpha=0.5)
plt.show()