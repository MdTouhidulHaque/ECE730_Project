import numpy as np
import math

# Defining function for load profile allocation
def Residential_load_profile_allocation_MC_simulation(Loadname, iRandom, DSSCircuit, houseData30minutes):
    np.random.seed(iRandom)
    #customer =[]
    for icust, cust in enumerate(Loadname):    
        DSSCircuit.SetActiveElement('load.'+ cust) 
        #phases = int(DSSCircuit.ActiveElement.Properties('phases').Val) # it gets the phase of the customer
        Cust_ran = np.random.randint(len(houseData30minutes)) # randomly selects a curve from the pool  
        DSSCircuit.ActiveElement.Properties('daily').Val='Load_shape_' + str(Cust_ran) # Assign the loadshape
        #customer.append(Cust_ran)
    #print(customer)
          
