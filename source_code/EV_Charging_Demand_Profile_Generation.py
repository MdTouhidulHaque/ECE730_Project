import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import random
from scipy.stats import norm, truncnorm

#Parameters for charging start time and duration PDFs
charging_start_mean = 16.631
charging_start_std = 4.094
charging_duration_mean = 3.864
charging_duration_std = 3.553  

#Function to generate random start times and durations
def generate_charging_times_and_durations(num_samples):
    start_times = truncnorm(
        (0 - charging_start_mean) / charging_start_std, 
        (24 - charging_start_mean) / charging_start_std, 
        loc=charging_start_mean, scale=charging_start_std
    ).rvs(num_samples)

    durations = truncnorm(
        (0 - charging_duration_mean) / charging_duration_std, 
        (24 - charging_duration_mean) / charging_duration_std, 
        loc=charging_duration_mean, scale=charging_duration_std
    ).rvs(num_samples)

    return start_times, durations

#Number of data points to generate
num_samples = 10000

#Generate random start times and durations
start_times, durations = generate_charging_times_and_durations(num_samples)

#Generate EV demand profile
ev_demand_profile = []

for start_time, duration in zip(start_times, durations):
    daily_profile = np.zeros(24)
    start_hour = int(np.floor(start_time))
    duration_hours = int(np.ceil(duration))

    for hour in range(start_hour, start_hour + duration_hours):
        if 0 <= hour < 24:
            daily_profile[hour] = 3.2

    ev_demand_profile.append(daily_profile)

#Converting to 30 mintue resolution data
def convert_to_30_min_resolution(load_profiles):
    # Create an empty list to store the converted profiles
    converted_profiles = []

    for profile in load_profiles:
        # Initialize an empty list for the 30-minute resolution profile
        new_profile = []

        # For each hour in the profile, duplicate the value for the two 30-minute intervals
        for value in profile:
            new_profile.append(value)  # First 30-minute interval
            new_profile.append(value)  # Second 30-minute interval

        # Add the new profile to the converted_profiles list
        converted_profiles.append(new_profile)
    
    return converted_profiles

converted_ev_demand_profile = convert_to_30_min_resolution(ev_demand_profile)



#Convert to DataFrame
#ev_demand_df = pd.DataFrame(ev_demand_profile, columns=[f'Hour_{i}' for i in range(24)])
ev_demand_df = pd.DataFrame(converted_ev_demand_profile)
#Save to CSV
#ev_demand_df.to_csv('ev_demand_profile.csv', index=False)

print(ev_demand_df.head())
#exit()

#Plot the EV demand profile for a sample of days
def plot_ev_demand_profile(data, num_samples):
    x=[i for i in range(48)]
    l=[]
    for i in range(24): 
        l.append("%s:00"%i)
        l.append(" ")

    plt.figure(figsize=(9, 3))
    for i in range(num_samples):
        plt.step(data.columns, data.iloc[i], where='pre', label=f'Profile {i+1}', linewidth=2)
    #plt.title('EV Demand Profiles', fontsize = 22, weight='bold')
    plt.xlabel('Time (hh:mm)', fontsize = 22)
    plt.xticks(x, l, fontsize=18, rotation=60)
    plt.ylabel('EV Charging Power (kW)', fontsize = 22)
    plt.yticks(fontsize = 18)
    plt.ylim(0,4)
    #plt.yticks(np.linspace(0, 4, 5), fontsize = 10) 
    plt.ylim(bottom=0)
    plt.legend(fontsize = 18)
    plt.show()

#Plot the demand profile for the first 5 days
plot_ev_demand_profile(ev_demand_df, num_samples=10)
exit()


#Aggregate profiles to get the diversified demand profile
total_demand_profile = np.sum(converted_ev_demand_profile, axis=0)
#print(total_demand_profile)


average_demand_profile = [number / num_samples for number in total_demand_profile]
#print(average_demand_profile)
#exit()

# y=[i for i in range(25)]
# l=[]
# for i in range(24): 
#       l.append("%s:00"%i)
# l.append("0:00")

#fig2 = plt.figure(figsize=(9,3)) 
plt.plot(average_demand_profile, 'r--', linewidth=3, label = 'Diversified EV Demand Profile')
#plt.xlabel("Time (hh:mm)", fontsize = 18)
#plt.xticks(fontsize = 10)
#plt.xticks(y, l, fontsize=12, rotation=60)
#plt.ylabel('EV Charging Power (kW)', fontsize = 18)
#plt.yticks(np.linspace(0, 2, 10), fontsize = 10) 
#plt.title('Diversified EV Demand Profile', fontsize = 15)
#plt.ylim(bottom=0)
plt.legend()
plt.show()


