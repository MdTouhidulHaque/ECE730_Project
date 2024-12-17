import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import random
import csv
from scipy.stats import norm

input_file = "E:\Thesis_MSc_Touhid\EV Charging Dataset Norway\Dataset 1_EV charging reports.csv"
output_file = "Dataset_1_EV charging reports_split.csv" 

with open(input_file, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    header = next(reader)
    data = np.ndarray(shape=(6878,15), dtype=object)
    i= 0
    for row in reader:
        data[i]= row
        i += 1
    
#convert array to dataframe
df_Norway= pd.DataFrame(data)
df_Norway.to_csv(output_file, header=None)

#print(df_Norway.head())
#print(df_Norway.shape) 

#Plotting PDF of EV charging start time and duration

start_day = df_Norway.iloc[:, 12].tolist()
start_time = df_Norway.iloc[:, 6].tolist()
charging_duration = df_Norway.iloc[:, 10].tolist()
charging_energy = df_Norway.iloc[:, 9].tolist()

#Data Cleaning
# Function to replace commas with dot in each element of the list
def replace_commas(lst):
    return [str(item).replace(',', '.') for item in lst]

charging_energy_cleaned = replace_commas(charging_energy)


#Separating Weekdays and Weekends
weekday_start_time = []
weekend_start_time = []
weekday_charging_energy = []
weekend_charging_energy = []

for i in range(len(start_day)):
    if start_day[i] == 'Saturday' or start_day[i] == 'Sunday':
        weekend_start_time.append(start_time[i])
        weekend_charging_energy.append(charging_energy_cleaned[i])
    else:
        weekday_start_time.append(start_time[i])
        weekday_charging_energy.append(charging_energy_cleaned[i])


#Setting datatype to float
def safe_float_conversion(element):
    try:
        return float(element)
    except ValueError:
        return 0  # or any default value you want to use

weekday_start_time_float = [safe_float_conversion(element) for element in weekday_start_time]
weekend_start_time_float = [safe_float_conversion(element) for element in weekend_start_time]
weekday_charging_energy_float = [safe_float_conversion(element) for element in weekday_charging_energy]
weekend_charging_energy_float = [safe_float_conversion(element) for element in weekend_charging_energy]

#Converting charging energy to charging duration (in hours) by assuming constant charging power of 3.2kW
def divide_and_round_elements(list, number):
    divide_and_round = []
    for item in list:
        if isinstance(item, (int, float)):
            divided_value = item / number
            rounded_value = round(divided_value, 3)
            divide_and_round.append(rounded_value)
        else:
            divide_and_round.append(item)
    return divide_and_round

weekday_charging_duration = divide_and_round_elements(weekday_charging_energy_float, 3.2)
weekend_charging_duration = divide_and_round_elements(weekend_charging_energy_float, 3.2)


#print(max(weekday_charging_duration))
#print(max(weekend_charging_duration))


#Creating histogram
#For weekdays charging start time
counts1, bin_edges1 = np.histogram(weekday_start_time_float, bins=24, density=True)
bin_edges = np.linspace(0,24,25)
bin_centers1 = (bin_edges1[:-1] + bin_edges1[1:]) / 2
# Fit a normal distribution to the data
mu1, std1 = norm.fit(weekday_start_time_float)
x1 = np.linspace(0, 24, 10000)
pdf_fitted1 = norm.pdf(x1, mu1, std1)

#print(bin_edges1)
#print(bin_edges)
#exit()

#For weekends charging start time
counts2, bin_edges2 = np.histogram(weekend_start_time_float, bins=24, density=True)
bin_edges_duration = np.linspace(0,12,13)
bin_centers2 = (bin_edges2[:-1] + bin_edges2[1:]) / 2
# Fit a normal distribution to the data
mu2, std2 = norm.fit(weekend_start_time_float)
x2 = np.linspace(0, 24, 10000)
pdf_fitted2 = norm.pdf(x2, mu2, std2)

#For weekdays charging duration
counts3, bin_edges3 = np.histogram(weekday_charging_duration, bins=12, density=True)
bin_centers3 = (bin_edges3[:-1] + bin_edges3[1:]) / 2
# Fit a normal distribution to the data
mu3, std3 = norm.fit(weekday_charging_duration)
x3 = np.linspace(0, 12, 10000)
pdf_fitted3 = norm.pdf(x3, mu3, std3)

#For weekends charging duration
counts4, bin_edges4 = np.histogram(weekend_charging_duration, bins=12, density=True)
bin_centers4 = (bin_edges4[:-1] + bin_edges4[1:]) / 2
# Fit a normal distribution to the data
mu4, std4 = norm.fit(weekend_charging_duration)
x4 = np.linspace(0, 12, 10000)
pdf_fitted4 = norm.pdf(x4, mu4, std4)


print(mu1,std1,mu3,std3)
#exit()


y=[i for i in range(25)]
l=[]
for i in range(24): 
      l.append("%s:00"%i)
l.append("0:00")

#def format_time(hour):
#    return f'{int(hour):02d}:00'

#bin_edges_time = [format_time(edge) for edge in bin_edges1]
#bin_centers_time = [format_time(center) for center in bin_centers1]

fig1=plt.figure(figsize=(9,3)) 
plt.hist(weekday_start_time_float, bins=bin_edges, density=True, alpha=0.6, color='skyblue', edgecolor='black', linewidth=2)
#plt.plot(bin_centers1, counts1, 'b--', label='PDF of Charging Starting Time in Weekdays')
#plt.plot(x1, pdf_fitted1, 'r--', label='Fitted Normal Distribution', linewidth= 3)
plt.xlabel("Time (hh:mm)", fontsize = 22)
plt.xticks(fontsize = 18)
#plt.xticks(ticks=np.arange(25), labels=bin_edges_time, rotation=45)
plt.xticks(y, l, fontsize=18, rotation=60)
plt.ylabel('Probability Density', fontsize = 22)
plt.yticks(np.linspace(0, 0.2, 5), fontsize = 18) 
#plt.title('PDF of EV Charging Starting Time in Weekdays', fontsize = 22, weight='bold')
#plt.title('PDF of EV Charging Starting Time', fontsize = 22, weight='bold')
#plt.legend()
#plt.show()
#exit()

fig2=plt.figure(figsize=(9,3))
plt.hist(weekend_start_time_float, bins=bin_edges, density=True, alpha=0.6, color='skyblue', edgecolor='black', linewidth=1.5)
#plt.plot(bin_centers2, counts2, 'b--', label='PDF of Charging Starting Time in Weekends')
plt.plot(x2, pdf_fitted2, 'r--', label='Fitted Normal Distribution')
plt.xlabel("Time (hh:mm)", fontsize = 15)
plt.xticks(fontsize = 10)
plt.xticks(y, l, fontsize=10, rotation=60)
plt.ylabel('Probability', fontsize = 15)
plt.yticks(np.linspace(0, 0.2, 5), fontsize = 10) 
plt.title('PDF of EV Charging Starting Time in Weekends', fontsize = 15)
plt.legend()
#plt.show()  
#exit()

fig3=plt.figure(figsize=(9,3))
plt.hist(weekday_charging_duration, bins=bin_edges_duration, density=True, alpha=0.6, color='skyblue', edgecolor='black', linewidth=2)
#plt.plot(bin_centers3, counts3, 'b--', label='PDF of Charging Duration in Weekdays')
#plt.plot(x3, pdf_fitted3, 'r--', label='Fitted Normal Distribution', linewidth=3)
plt.xlabel("Duration (Hours)", fontsize = 22)
plt.xticks(np.linspace(0, 12, 13), fontsize = 18) 
plt.ylabel('Probability Density', fontsize = 22)
plt.yticks(np.linspace(0, 0.4, 5), fontsize = 18) 
#plt.title('PDF of EV Charging Duration in Weekdays', fontsize = 22, weight='bold')
#plt.title('PDF of EV Charging Duration', fontsize = 22, weight='bold')
#plt.legend()

fig3=plt.figure(figsize=(9,3))
plt.hist(weekend_charging_duration, bins=bin_edges_duration, density=True, alpha=0.6, color='skyblue', edgecolor='black', linewidth=1.5)
#plt.plot(bin_centers4, counts4, 'b--', label='PDF of Charging Duration in Weekends')
plt.plot(x4, pdf_fitted4, 'r--', label='Fitted Normal Distribution')
plt.xlabel("Time (Hours)", fontsize = 15)
plt.xticks(np.linspace(0, 12, 13), fontsize = 10) 
plt.ylabel('Probability', fontsize = 15)
plt.yticks(np.linspace(0, 0.4, 5), fontsize = 10) 
plt.title('PDF of EV Charging Duration in Weekends', fontsize = 15)
plt.legend()
plt.show()








