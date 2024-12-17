import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import random
import time
import Definitions
import Function_MC_Simulation
import Residential_Load_Profile_Allocation_MC_Simulation
import EV_Profile_Allocation_MC_Simulation
import PV_Profile_Allocation_MC_Simulation
import seaborn as sns
import pickle


penetration_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100] # penetration percentages to evaluate


with open('E:\Fall_24_Courses\ECE_730\Project_ECE730\Results_rev2\PV_Fixed_Summer\PV_0_Percent\Penetration_results_dct_PV_Summer_0_Percent.pkl', 'rb') as file:  # Put actual directory
#with open('Penetration_results_dct.pkl', 'rb') as file:
    Penetration_results_dct = pickle.load(file)

print("Dictionary loaded successfully.")

# Set the directory to save the plots
save_directory = "E:\Fall_24_Courses\ECE_730\Project_ECE730\Results_rev2\PV_Fixed_Summer\PV_0_Percent"  # Put actual directory
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Percentage of customers with low voltage issues
fig1 = plt.figure(figsize=(16,9))
plt.rc('font', family='Times New Roman')
plt.rc('font', size=20)
plt.rc('figure', figsize=(4,4))
plt.rc('lines', linewidth=2)
Load_nonCompliance = []
for iPenetration in range(len(penetration_list)):
    Load_nonCompliance_temp = np.array(Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]],dtype=object)[:,1]
    Load_nonCompliance.append(Load_nonCompliance_temp)
# Customizing the boxplot
boxprops = dict(color="blue", linewidth=2)
medianprops = dict(color="red", linewidth=2)
whiskerprops = dict(color="green", linewidth=2)
capprops = dict(color="green", linewidth=2)
#flierprops = dict(marker="o", color="orange", alpha=0.5)
#plt.boxplot(Load_nonCompliance)
plt.boxplot(Load_nonCompliance, boxprops=boxprops, medianprops=medianprops,
            whiskerprops=whiskerprops, capprops=capprops, showfliers=False)

plt.legend(['Non_compliance (low voltage issues)'])
plt.title('Impact of EV Charging Loads on Voltage Profile of Consumers', fontsize = 24, fontweight='bold')
plt.ylabel('Voltage Non-Compliant Consumers, %', fontsize = 20, fontweight='bold')
plt.ylim([0, 120])
plt.xlabel('EV Penetration Level, %', fontsize = 20, fontweight='bold')
plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'])

plt.text(3.5, 110, 'PV Penetration Level = 0%', fontsize=20, color='green', ha='center')
#plt.grid(visible=True, linestyle='--', alpha=0.3)
#plt.show()
#plt.close()
#exit()
# Save the plot
plt.savefig(os.path.join(save_directory, 'Low_Voltage_NonCompliance.pdf'), format='pdf')
#save_full_size_plot('Low_Voltage_NonCompliance.pdf')
plt.close()
#exit()

# Percentage of customers with voltage issues (high)
fig2 = plt.figure(figsize=(16,9))
plt.rc('font', family='Times New Roman')
plt.rc('font', size=20)
plt.rc('figure', figsize=(4,4))
plt.rc('lines', linewidth=2)
Load_nonCompliance = []
for iPenetration in range(len(penetration_list)):
    Load_nonCompliance_temp = np.array(Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]],dtype=object)[:,2]
    Load_nonCompliance.append(Load_nonCompliance_temp)
# Customizing the boxplot
boxprops = dict(color="blue", linewidth=2)
medianprops = dict(color="red", linewidth=2)
whiskerprops = dict(color="green", linewidth=2)
capprops = dict(color="green", linewidth=2)
#flierprops = dict(marker="o", color="orange", alpha=0.5)
#plt.boxplot(Load_nonCompliance)
plt.boxplot(Load_nonCompliance, boxprops=boxprops, medianprops=medianprops,
            whiskerprops=whiskerprops, capprops=capprops, showfliers=False)

plt.legend(['Non_compliance (high voltage issues)'])
plt.title('Impact of EV Charging Loads on Voltage Profile of Consumers', fontsize = 24, fontweight='bold')
plt.ylabel('Voltage Non-Compliant Consumers, %', fontsize = 20, fontweight='bold')
plt.ylim([0, 120])
plt.xlabel('EV Penetration Level, %', fontsize = 20, fontweight='bold')
plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'])
plt.text(3.5, 110, 'PV Penetration Level = 0%', fontsize=20, color='green', ha='center')
#plt.grid(visible=True, linestyle='--', alpha=0.5)
#plt.show()
#exit()
# Save the plot
plt.savefig(os.path.join(save_directory, 'High_Voltage_NonCompliance.pdf'), format='pdf')
plt.close()

# Loop through each penetration level from 0% to 100% (assuming increments of 10%)
for penetration_level in range(0, 101, 10):  # Adjust the range as needed
    # Extract results for the current penetration level
    penetration_level_index = penetration_list.index(penetration_level)
    LV_transformer_max_voltages = [
        result[3]  # Access the output_5 from Function_MC_Simulation
        for result in Penetration_results_dct[f'penetration={penetration_level}']
    ]

    # Ensure the data is a 2D list suitable for box plotting
    LV_transformer_max_voltages_transposed = [list(v) for v in zip(*LV_transformer_max_voltages)]

    # Flatten and convert all nested structures to floats
    LV_transformer_max_voltages_transposed_cleaned = []
    for sublist in LV_transformer_max_voltages_transposed:
        cleaned_sublist = []
        for value in sublist:
            if isinstance(value, list):
                # If value is a list, flatten it and convert each element to float
                cleaned_sublist.extend([float(v) for v in value])
            else:
                # Otherwise, convert the value to float
                cleaned_sublist.append(float(value))
        LV_transformer_max_voltages_transposed_cleaned.append(cleaned_sublist)

    # Flatten and prepare data for seaborn
    data = []
    transformer_indices = []

    for i, sublist in enumerate(LV_transformer_max_voltages_transposed_cleaned):
        data.extend(sublist)  # Add all values from the sublist to the data
        transformer_indices.extend([i + 1] * len(sublist))  # Add transformer index for each value

    # Create a DataFrame for seaborn
    df = pd.DataFrame({
        'Transformer Index': transformer_indices,
        'Maximum Voltage (pu)': data
    })

    # Plot using seaborn with outliers removed
    plt.figure(figsize=(16, 9))
    sns.boxplot(x='Transformer Index', y='Maximum Voltage (pu)', data=df, color='lightblue', showfliers=False)
    plt.axhline(y=1.05, color='red', linestyle='--', linewidth=1.5, label='1.05 pu')  # Upper limit line
    plt.axhline(y=0.95, color='red', linestyle='--', linewidth=1.5, label='0.95 pu')  # Lower limit line
    plt.title(f'Voltage Profile for Each Node of the Distribution System at {penetration_level}% EV & 0% PV Penetration', fontsize=18, fontweight='bold')
    plt.xlabel('Nodes along the feeder (1 to 69)', fontsize=16, fontweight='bold')
    plt.ylabel('Voltage (pu)', fontsize=16, fontweight='bold')
    plt.yticks(fontsize=12)
    plt.xticks(rotation=45, fontsize=12)  # Adjust font size as needed
    plt.legend(fontsize=16)  # Add a legend to label the dashed lines
    #plt.grid(visible=True, linestyle='--', alpha=0.5)
    #plt.text(5, 1.03, 'PV Penetration Level = 0%', fontsize=16, color='green', ha='center')
    #plt.text(5, 1.02, f'EV Penetration Level = {penetration_level}%', fontsize=16, color='green', ha='center')
    #plt.show()
    # Save the plot
    plt.savefig(os.path.join(save_directory, f'Voltage_Profile_{penetration_level}_EV_Penetration.pdf'), format='pdf')
    plt.close()


# Loop through each penetration level from 0% to 100% (assuming increments of 10%)
for penetration_level in range(0, 101, 10):  # Adjust the range as needed
    # Extract results for the current penetration level
    penetration_level_index = penetration_list.index(penetration_level)
    LV_transformer_max_utilization = [
        result[4]  # Access the output_6 from Function_MC_Simulation
        for result in Penetration_results_dct[f'penetration={penetration_level}']
    ]

    # Ensure the data is a 2D list suitable for box plotting
    LV_transformer_max_utilization_transposed = [list(v) for v in zip(*LV_transformer_max_utilization)]

    # Flatten and convert all nested structures to floats
    LV_transformer_max_utilization_transposed_cleaned = []
    for sublist in LV_transformer_max_utilization_transposed:
        cleaned_sublist = []
        for value in sublist:
            if isinstance(value, list):
                # If value is a list, flatten it and convert each element to float
                cleaned_sublist.extend([float(v) for v in value])
            else:
                # Otherwise, convert the value to float
                cleaned_sublist.append(float(value))
        LV_transformer_max_utilization_transposed_cleaned.append(cleaned_sublist)

    # Flatten and prepare data for seaborn
    data = []
    transformer_indices = []

    for i, sublist in enumerate(LV_transformer_max_utilization_transposed_cleaned):
        data.extend(sublist)  # Add all values from the sublist to the data
        transformer_indices.extend([i + 1] * len(sublist))  # Add transformer index for each value

    # Create a DataFrame for seaborn
    df = pd.DataFrame({
        'Transformer Index': transformer_indices,
        'Maximum Utilization (%)': data
    })

    # Plot using seaborn with outliers removed
    plt.figure(figsize=(16, 9))
    sns.boxplot(x='Transformer Index', y='Maximum Utilization (%)', data=df, color='lightblue', showfliers=False)
    plt.axhline(y=100, color='red', linestyle='--', linewidth=1.5, label='100% Utilization')  # Maximum utilization line
    plt.title(f'Utilization Level for Each Distribution Transformer at {penetration_level}% EV & 0% PV Penetration', fontsize=18, fontweight='bold')
    plt.xlabel('Distribution Transformer Index (1 to 69)', fontsize=16, fontweight='bold')
    plt.ylabel('Utilization (%)', fontsize=16, fontweight='bold')
    plt.yticks(fontsize=12)
    plt.xticks(rotation=45, fontsize=12)  # Adjust font size as needed
    plt.legend(fontsize=12)  # Add a legend to label the dashed line
    #plt.grid(visible=True, linestyle='--', alpha=0.5)
    #plt.text(5, 110, 'PV Penetration Level = 0%', fontsize=16, color='green', ha='center')
    #plt.text(5, 110, f'EV Penetration Level = {penetration_level}%', fontsize=16, color='green', ha='center')
    # Save the plot
    plt.savefig(os.path.join(save_directory, f'LV_Tr_Utilization_Profile_{penetration_level}_EV_Penetration.pdf'), format='pdf')
    plt.close()
    #plt.show()



