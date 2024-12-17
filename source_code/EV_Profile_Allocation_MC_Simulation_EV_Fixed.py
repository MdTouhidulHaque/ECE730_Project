import numpy as np

# Defining function for PV profile allocation
def EV_Profile_Allocation_MC_Simulation(EVcustomer_number, penetration_list, iPenetration, Loadname, iRandom, DSSCircuit, DSSText, home_ev_charging_demand_profile, no_EV_Profiles):   
    np.random.seed(iRandom)
    used_indices = set()  # Use a set to track unique indices

    if penetration_list[iPenetration] != 0:
        for iEV_status in range(EVcustomer_number):
            # Generate a unique random index for the EV profile
            random_home_ev_profile = np.random.randint(no_EV_Profiles)
            individual_home_ev_charging_demand_profile = home_ev_charging_demand_profile[random_home_ev_profile, :]

            # Generate a unique Cust_ran index
            while True:
                Cust_ran = np.random.randint(len(Loadname))
                if Cust_ran not in used_indices:  # Check if Cust_ran is unique
                    used_indices.add(Cust_ran)  # Add to the set if unique
                    break

            customer = Loadname[Cust_ran]
            DSSCircuit.SetActiveElement('load.' + customer)
            loadshape_name = DSSCircuit.ActiveElement.Properties('daily').Val
            DSSCircuit.LoadShapes.Name = loadshape_name
            existing_pmult = DSSCircuit.LoadShapes.Pmult
            new_pmult_values = individual_home_ev_charging_demand_profile.tolist()
            combined_pmult = existing_pmult + new_pmult_values
            DSSCircuit.LoadShapes.Pmult = combined_pmult

    #print(used_indices)

