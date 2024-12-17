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
import PV_Profile_Allocation_MC_Simulation_PV_Fixed
import seaborn as sns
import pickle
import h5py

mydir = os.getcwd()
print("The files are located in the following path: mydir = %s" %mydir)

Definitions.compile_dss_circuit(mydir)

# Load PV generation profile and household load profile dataset. This dataset is collected from Australian LV consumers dataset.
houseData30minutes = np.load(mydir + '\\Residential load data 30-min resolution.npy') # Put the directory of originial file location
PVData30minutes = np.load(mydir + '\\PV_half_hourly_normalized_data.npy')  # Put the directory of originial file location
#Load home EV charging demand profile
home_ev_charging_demand_profile = pd.read_csv('E:\Fall_24_Courses\ECE_730\Project_ECE730\ev_demand_profile.csv') # Put the directory of originial file location
home_ev_charging_demand_profile = home_ev_charging_demand_profile.to_numpy()

# Visualize dataset
shape_profiles  = houseData30minutes.shape
noProfiles = shape_profiles[0]
PV_shape_profiles  = PVData30minutes.shape
no_EV_Profiles = home_ev_charging_demand_profile.shape[0]


print("The shape of the load profile is:", shape_profiles) 
print("The shape of the PV profiles is:", PV_shape_profiles)


# Getting load names and line names
Loadname = Definitions.DSSCircuit.Loads.AllNames
Linenames = Definitions.DSSCircuit.Lines.AllNames

# Initialize empty lists for "hv line" and "lv line"
hv_line_list = []
lv_line_list = []

# Loop through each string in the original line list
for s in Linenames:
    if s.startswith("hv"):
        hv_line_list.append(s)
    elif s.startswith("lvl"):
        lv_line_list.append(s)
#exit()


## Conducting Monte Carlo Simulations

Num_Run = 20 # Setting Number of run in Monte Carlo Simulations

penetration_list = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100] # penetration percentages to evaluate
EVcustomer_number = [int(np.ceil(Definitions.Num_of_Customers*x/100)) for x in penetration_list] # Number of customers with EV for each penetration percentage scenario
PVcustomer_number = [int(np.ceil(Definitions.Num_of_Customers*x/100)) for x in penetration_list] 


Penetration_results_dct = {}
for iPenetration in range(len(penetration_list)):
   Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]]= [] 

#Monte Carlo Simulation
start_time = time.time()

inverter_op = False # Variable to allow the inclusion of VoltWatt control on each of the PVSystems.

for iRandom in range(Num_Run): # Starts the loop according to the number of simulations to perform in the Monte Carlo study
    np.random.seed(iRandom)
    
    start_time_temp = time.time()

    run = iRandom + 1
    print('Simulating run number %s.' %run)


    # Part 1: Randomisation on day profile 
    for selected_day in range(30):
        Day_Num = selected_day + 181
        Day_Num_PV = selected_day + 1
        print('Day number: %s, ' %Day_Num + 'PV Day number: %s.' %Day_Num_PV )

        Definitions.DSSText.Command = 'clear'
        Definitions.compile_dss_circuit(mydir)
        # Part 2: Randomisation on load profile allocation:
        
        for ii in range(len(houseData30minutes)):
            Definitions.DSSCircuit.LoadShapes.New('Load_shape_%s'%(ii))
            Definitions.DSSCircuit.LoadShapes.Npts = 48
            Definitions.DSSCircuit.LoadShapes.MinInterval = 30
            Definitions.DSSCircuit.LoadShapes.UseActual = 1
            Definitions.DSSCircuit.LoadShapes.Name = 'Load_shape_%s'%(ii)
            Definitions.DSSCircuit.LoadShapes.Pmult = houseData30minutes[ii, Day_Num, :].tolist() 
        
        Residential_Load_Profile_Allocation_MC_Simulation.Residential_load_profile_allocation_MC_simulation(Loadname, iRandom, Definitions.DSSCircuit, houseData30minutes)
        
        
        # Part 3: Selection and randomisation on PV system allocation:
        # PV profile initialization
        for iPV_status in range(len(Loadname)):
            Definitions.DSSCircuit.SetActiveElement('load.' + str(Loadname[iPV_status]))
            phases = int(Definitions.DSSCircuit.ActiveCktElement.Properties('phases').Val)
            bus1 = Definitions.DSSCircuit.ActiveCktElement.Properties('bus1').Val
            if phases == 1:
                Definitions.DSSText.Command = 'new PVSystem.PV_' + str(Loadname[iPV_status])\
                        + ' phases=1'  \
                        + ' irradiance=1' \
                        + ' %cutin=0.05' \
                        + ' %cutout=0.05' \
                        + ' vmaxpu=1.05' \
                        + ' vminpu=0.95' \
                        + ' kva=0' \
                        + ' pmpp=0' \
                        + ' bus1=' + str(bus1) \
                        + ' pf=1' \
                        + ' enabled=false' \
                        + ' kv=0.12' \
                        + ' daily=pvshape1'\
                        + ' VarFollowInverter=True' 

            
        # Selection of the PV curve according to the selected day
        Definitions.DSSCircuit.LoadShapes.Name='pvshape1'
        Definitions.DSSCircuit.LoadShapes.Pmult=PVData30minutes[Day_Num_PV,:].tolist()    
        PV_day_potential =  PVData30minutes[Day_Num_PV,:] # Normalized curve for the selected day
        
        # Part 4: Assignation of PV size
        PV_allocation_size = [] # List that will store the PV sizes for each of the customers
        
        PVname = Definitions.DSSCircuit.PVSystems.AllNames
        np.random.seed(iRandom)
        for iPV in range(len(PVname)):
            PV_allocation_size.append(np.random.choice([2.5,3.5,5.5,8], p=[0.08,0.24,0.52,0.16])) # Random assignation 
        
        
        PV_penetration_list = [penetration_list[0]]
        PVcustomer_number_EV = PVcustomer_number[0]
        for iPenetration in range(len(PV_penetration_list)):
            PV_Profile_Allocation_MC_Simulation_PV_Fixed.PV_Allocation_MC_Simulation(PVcustomer_number_EV, PV_penetration_list, iPenetration, PVname, iRandom, inverter_op, PV_allocation_size, Definitions.DSSCircuit, Definitions.DSSText)
            

        # Selection of the PV curve according to the selected day for 3N Energy
        Definitions.DSSCircuit.LoadShapes.New('pvshape2')
        Definitions.DSSCircuit.LoadShapes.Npts = 48
        Definitions.DSSCircuit.LoadShapes.MinInterval = 30
        Definitions.DSSCircuit.LoadShapes.UseActual = 1
        Definitions.DSSCircuit.LoadShapes.Name='pvshape2'
        Definitions.DSSCircuit.LoadShapes.Pmult=PVData30minutes[Day_Num_PV,:].tolist()    
        PV_day_potential =  PVData30minutes[Day_Num_PV,:] # Normalized curve for the selected day
        Definitions.DSSCircuit.SetActiveElement('PVSystem.3N_PV')
        Definitions.DSSCircuit.ActiveElement.Properties('daily').Val = str('pvshape2')
        
        # Part 4: Assignation of EV fleet to customers

        random.seed(iRandom)
        for iPenetration in range(len(penetration_list)):     
            EV_Profile_Allocation_MC_Simulation.EV_Profile_Allocation_MC_Simulation(EVcustomer_number, penetration_list, iPenetration, Loadname, iRandom, Definitions.DSSCircuit, Definitions.DSSText, home_ev_charging_demand_profile, no_EV_Profiles)
            Definitions.DSSText.Command = 'Set ControlMode=static' 
            Definitions.DSSText.Command = 'Reset'   
            Definitions.DSSText.Command = 'Set Mode=daily number=1 stepsize=%s' %Definitions.Time_Resolution +'m' 
            
            Penetration_results_dct['penetration=%s'%penetration_list[iPenetration]].append(Function_MC_Simulation.Function_MC_Simulation(Definitions.DSSCircuit, Definitions.DSSSolution, penetration_list, iPenetration, Definitions.Num_of_TimeStep, Definitions.Num_of_HVTr, Definitions.Num_of_DisTransformers, Definitions.Num_of_HVlines, Loadname, PV_day_potential, Definitions.Voltage_max, Definitions.Voltage_min, hv_line_list))


print("Monte Carlo simulation time (in seconds) = ", np.round(time.time()-start_time,3))


#exit()

# Save the dictionary using pickle
with open('Penetration_results_dct.pkl', 'wb') as file:
    pickle.dump(Penetration_results_dct, file)

print("Dictionary saved successfully as 'Penetration_results_dct.pkl'")
#exit()


# Percentage of customers with low voltage issues
fig3 = plt.figure(figsize=(4,4))
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
plt.title('Impact of EV Charging Loads with Fixed PV Generation on Voltage Profile of Consumers', fontsize = 24, fontweight='bold')
plt.ylabel('Voltage Non-Compliant Consumers, %', fontsize = 20, fontweight='bold')
plt.ylim([0, 120])
plt.xlabel('EV Penetration Level, %', fontsize = 20, fontweight='bold')
plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'])
#plt.show()
#plt.close()
#exit()

# Percentage of customers with voltage issues (high)
fig4 = plt.figure(figsize=(4,4))
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
plt.title('Impact of EV Charging Loads with Fixed PV Generation on Voltage Profile of Consumers', fontsize = 24, fontweight='bold')
plt.ylabel('Voltage Non-Compliant Consumers, %', fontsize = 20, fontweight='bold')
plt.ylim([0, 120])
plt.xlabel('EV Penetration Level, %', fontsize = 20, fontweight='bold')
plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], ['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'])
plt.show()
exit()

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

    # Plot using seaborn
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Transformer Index', y='Maximum Voltage (pu)', data=df, color='lightblue')
    plt.axhline(y=1.05, color='red', linestyle='--', linewidth=1.5, label='1.05 pu')  # Upper limit line
    plt.axhline(y=0.95, color='red', linestyle='--', linewidth=1.5, label='0.95 pu')  # Lower limit line
    plt.title(f'Voltage Profile for Each HV Node of the Distribution System at {penetration_level}% EV Penetration', fontsize=16, fontweight='bold')
    plt.xlabel('Nodes along the feeder (1 to 69)', fontsize=14, fontweight='bold')
    plt.ylabel('Voltage (pu)', fontsize=14, fontweight='bold')
    plt.yticks(fontsize=12)
    plt.xticks(rotation=45, fontsize=12)  # Adjust font size as needed
    plt.legend(fontsize=16)  # Add a legend to label the dashed lines
    plt.grid(visible=True, linestyle='--', alpha=0.5)
    plt.show()


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

    # Plot using seaborn
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Transformer Index', y='Maximum Utilization (%)', data=df, color='lightblue')
    plt.axhline(y=100, color='red', linestyle='--', linewidth=1.5, label='100% Utilization')  # Maximum utilization line
    plt.title(f'Utilization Level for Each Distribution Transformer {penetration_level}% EV Penetration', fontsize=18, fontweight='bold')
    plt.xlabel('Distribution Transformer Index (1 to 69)', fontsize=16, fontweight='bold')
    plt.ylabel('Utilization (%)', fontsize=16, fontweight='bold')
    plt.yticks(fontsize=12)
    plt.xticks(rotation=45, fontsize=12)  # Adjust font size as needed
    plt.legend(fontsize=12)  # Add a legend to label the dashed line
    plt.grid(visible=True, linestyle='--', alpha=0.5)
    plt.show()




