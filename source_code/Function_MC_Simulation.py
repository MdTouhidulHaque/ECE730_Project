import numpy as np
import pandas as pd
import random

def Function_MC_Simulation(DSSCircuit, DSSSolution, penetration_list, iPenetration, Num_of_TimeStep, Num_of_HVTr, Num_of_DisTransformers, Num_of_HVlines, Loadname, PV_day_potential, Voltage_max, voltage_min, hv_line_list):
    
    
    for iTime in range(Num_of_TimeStep):
        if iTime == 0:
            # All variables are defined before the first simulation (iTime=0)
        
            base_voltage_1 = 14433.75  # For transformers LVTr_51 to LVTr_87
            base_voltage_2 = 1385.64   # For transformers LVTr_88 to LVTr_119

            Non_compliance_low = [] # List of the number of customers with voltage problems (per sim step)
            Non_compliance_high = []
            # New list to store the maximum utilization level for each transformer
            LV_Transformer_Max_Utilization = [[] for _ in range(69)]  # List for utilization levels
            # Node name and number correspondence
            NodeName_dct = {}
            all_node_names = DSSCircuit.AllNodeNames
            for iNodes, node_name in enumerate(all_node_names):
                NodeName_dct[node_name] = iNodes
            
            # Loads dictionary/information 
            LDE_bus1 = [] # Will store the name of each node identificator (bus name, plus their respective phases connection (e.g, busname_1P.1, busname_3P.1, busname_3P.2, busname_3P.3)).
            LDE_bus1_index = [] # Will store the correspondent index for each node in the circuit
            LDE_bus_main = [] # Will store the name of each of the bus name
            LV_Transformer_Max_Voltage = [[] for _ in range(69)]  # List to store max voltages for each LV transformer

            #print(all_node_names)
            
            for icust in range(len(Loadname)):
                DSSCircuit.SetActiveElement('load.'+Loadname[icust])
                phases = int(DSSCircuit.ActiveCktElement.Properties('phases').Val)
                bus1 = DSSCircuit.ActiveCktElement.Properties('bus1').Val
                #print(bus1)
                LDE_bus_main.append(bus1)
            
                if phases == 1: # Appends the bus +".1"
                    LDE_bus1.append(bus1)
                    LDE_bus1_index.append(all_node_names.index(bus1))
                elif phases == 3: # Appends the bus +".1", bus +".2", bus +".3"
                    LDE_bus1.append(bus1+ '.1')
                    LDE_bus1_index.append(all_node_names.index(bus1+ '.1'))
                    LDE_bus1.append(bus1+ '.2')
                    LDE_bus1_index.append(all_node_names.index(bus1+ '.2'))
                    LDE_bus1.append(bus1+ '.3')
                    LDE_bus1_index.append(all_node_names.index(bus1+ '.3'))           
            
            # Head of the Feeder dataframe (Stores Aparent Power for each sim step)
            total_HVT = []

        DSSSolution.Solve()
        
        # Part 1: Power Measurements at the Head of the Feeder

        for iTransformer in range(1, Num_of_HVTr+1):
            DSSCircuit.SetActiveElement('transformer.HVTr_%s'%iTransformer)
            HV_Trans_Capacity = float(DSSCircuit.ActiveCktElement.Properties('kVAs').Val.strip('[').strip(']').split(',')[0])
            P_HVT_temp = (DSSCircuit.ActiveCktElement.Powers[0] + DSSCircuit.ActiveCktElement.Powers[2] + DSSCircuit.ActiveCktElement.Powers[4])
            Q_HVT_temp = (DSSCircuit.ActiveCktElement.Powers[1] + DSSCircuit.ActiveCktElement.Powers[3] + DSSCircuit.ActiveCktElement.Powers[5])
            S_HVT_temp = np.sqrt(P_HVT_temp**2 + Q_HVT_temp**2)
            total_HVT.append(S_HVT_temp)

        # Part 2 & 3: Calculation of feeder voltage profile and level of utilization in all distribution transformers

        # Feeder voltage profile calculation
        for iTransformerIndex in range(69):
            DSSCircuit.SetActiveElement(f'transformer.LVTr_{iTransformerIndex + 51}')  
            number_phases = int(DSSCircuit.ActiveElement.Properties('phases').Val)
            voltages = DSSCircuit.ActiveCktElement.VoltagesMagAng[0::2]  
            max_voltage = max(voltages)
             # Apply per unit conversion based on transformer index
            if 51 <= iTransformerIndex + 51 <= 87:  
                max_voltage_pu = max_voltage / base_voltage_1
            elif 88 <= iTransformerIndex + 51 <= 119:  
                max_voltage_pu = max_voltage / base_voltage_2
            else:
                max_voltage_pu = max_voltage  

            # Calculate utilization of distribution transformer
            Trans_Capacity = float(DSSCircuit.ActiveCktElement.Properties('kVAs').Val.strip('[]').split(',')[0])
            if number_phases == 3:
                P1_LVT = DSSCircuit.ActiveCktElement.Powers[0] + DSSCircuit.ActiveCktElement.Powers[2] + DSSCircuit.ActiveCktElement.Powers[4]
                Q1_LVT = DSSCircuit.ActiveCktElement.Powers[1] + DSSCircuit.ActiveCktElement.Powers[3] + DSSCircuit.ActiveCktElement.Powers[5]
                S1_LVT = np.sqrt(P1_LVT**2 + Q1_LVT**2)
            if number_phases == 1:
                P1_LVT = DSSCircuit.ActiveCktElement.Powers[0] + DSSCircuit.ActiveCktElement.Powers[2] + DSSCircuit.ActiveCktElement.Powers[4]
                Q1_LVT = DSSCircuit.ActiveCktElement.Powers[1] + DSSCircuit.ActiveCktElement.Powers[3] + DSSCircuit.ActiveCktElement.Powers[5]
                S1_LVT = np.sqrt(P1_LVT**2 + Q1_LVT**2)
            utilization = 100 * S1_LVT / Trans_Capacity  

            # Update voltage at each node and utilization of distribution transformer
            LV_Transformer_Max_Utilization[iTransformerIndex].append(utilization)
            LV_Transformer_Max_Voltage[iTransformerIndex].append(max_voltage_pu)

        
        
        # Part 4: Voltage calculation and evaluation on load buses

        LDE_temp = np.array(DSSCircuit.AllBusVmagPu)[LDE_bus1_index] # Selects the voltage values for each node corresponding to a load for the present time step.
        #Non_compliance.append(sum(i > Voltage_max or i < voltage_min for i in LDE_temp)) # Counts all the cases where the load voltages are outside the compliance values for the present time step.            
        Non_compliance_low.append(sum(i < voltage_min for i in LDE_temp))
        Non_compliance_high.append(sum(i > Voltage_max for i in LDE_temp))


    # Storing Results
    output_1 = max(total_HVT) # Maximum feeder load for the day
    output_2 = 100*np.amax(np.array(Non_compliance_low))/len(Loadname) # Percentage of non-compliance customers
    output_3 = 100*np.amax(np.array(Non_compliance_high))/len(Loadname)
    output_4 = LV_Transformer_Max_Voltage  # Max voltage at the primary side for each transformer
    output_5 = LV_Transformer_Max_Utilization  # Max utilization for each LV transformer
    

    retList = [output_1, output_2, output_3, output_4, output_5] 

    return retList