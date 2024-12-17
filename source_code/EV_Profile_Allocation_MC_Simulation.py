import numpy as np
import math
import random

# Defining function for PV profile allocation
def EV_Profile_Allocation_MC_Simulation(EVcustomer_number, penetration_list, iPenetration, Loadname, iRandom, DSSCircuit, DSSText, home_ev_charging_demand_profile, no_EV_Profiles):   
    if penetration_list[iPenetration] == 0 :
        global Count # defining it as a global variable for not returning it every time that the function is called.
        Count = 0
    else:
        while Count < EVcustomer_number[iPenetration]: 
            for icust, cust in enumerate(Loadname):
                if random.random() < (penetration_list[iPenetration]-penetration_list[iPenetration-1])/(100-penetration_list[iPenetration-1]):                           
                    random_home_ev_profile = np.random.randint(no_EV_Profiles)
                    individual_home_ev_charging_demand_profile = home_ev_charging_demand_profile[random_home_ev_profile, :]
                    DSSCircuit.SetActiveElement('load.'+ cust)
                    loadshape_name = DSSCircuit.ActiveElement.Properties('daily').Val
                    DSSCircuit.LoadShapes.Name = loadshape_name
                    existing_pmult = DSSCircuit.LoadShapes.Pmult
                    new_pmult_values = individual_home_ev_charging_demand_profile.tolist()
                    combined_pmult = existing_pmult + new_pmult_values
                    DSSCircuit.LoadShapes.Pmult = combined_pmult
                    Count = Count + 1
                    if Count == EVcustomer_number[iPenetration]:
                        break 
