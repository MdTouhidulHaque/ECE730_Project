import numpy as np

# Defining function for PV profile allocation
def PV_Allocation_MC_Simulation(PVcustomer_number, penetration_list, iPenetration, PVname, iRandom, inverter_op, PV_allocation, DSSCircuit, DSSText):   
    np.random.seed(iRandom)
    used_indices = set()  # Use a set to track unique indices

    if penetration_list[iPenetration] != 0:     
        for iPV_status in range(PVcustomer_number):
            # Generate a unique Cust_ran index
            while True:
                Cust_ran = np.random.randint(len(PVname))
                if Cust_ran not in used_indices:  # Check if Cust_ran is unique
                    used_indices.add(Cust_ran)  # Add to the set if unique
                    break

            DSSCircuit.SetActiveElement('PVSystem.' + str(PVname[Cust_ran]))
            DSSCircuit.ActiveElement.Properties('kva').Val = str(PV_allocation[Cust_ran])
            DSSCircuit.ActiveElement.Properties('pmpp').Val = str(PV_allocation[Cust_ran])
            DSSCircuit.ActiveElement.Properties('enabled').Val = 'true'

    #print(used_indices)  # Print the set of unique indices