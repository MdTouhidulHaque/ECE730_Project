import numpy as np
import math
import random

# Defining function for PV profile allocation
def PV_Allocation_MC_Simulation(PVcustomer_number, penetration_list, iPenetration, PVname, iRandom, inverter_op, PV_allocation, DSSCircuit, DSSText):   
    if penetration_list[iPenetration] == 0 :
        global Count, PV_status_dct # defining it as a global variable for not returning it every time that the function is called.
        Count = 0
        PV_status_dct = [] # Global variable to keep track of which PVsystem is enabled or not through all the scenarios
        
        for iPV_status in range(len(PVname)):
            PV_status_dct.append('false') # Initially, all PV systems are disabled (enabled='false').
    else:
        while Count < PVcustomer_number[iPenetration]:
            for iPV_status in range(len(PVname)):
                if PV_status_dct[iPV_status] == 'false':
                    if random.random() < (penetration_list[iPenetration]-penetration_list[iPenetration-1])/(100-penetration_list[iPenetration-1]):
                        PV_status_dct[iPV_status] = 'true'                            
                        DSSCircuit.SetActiveElement('PVSystem.' + str(PVname[iPV_status]))
                        DSSCircuit.ActiveElement.Properties('kva').Val=str(PV_allocation[iPV_status])
                        DSSCircuit.ActiveElement.Properties('pmpp').Val=str(PV_allocation[iPV_status])
                        DSSCircuit.ActiveElement.Properties('enabled').Val='true'
                        Count = Count + 1
                        if Count == PVcustomer_number[iPenetration]:
                            break 
        
        if (inverter_op==True) and (iRandom == 0):
            DSSText.Command = 'New XYCurve.vw_curve'+ str(iPenetration)+' npts=4 Yarray=(1.0, 1.0, 0.2, 0.2) XArray=(0.5, 1.1, 1.13, 2.0)' 
            DSSText.Command = 'New InvControl.InvPVCtrl'  + str(iPenetration) + ' mode=voltwatt voltwatt_curve=vw_curve'+ str(iPenetration) +' DeltaP_factor=0.05'             
            DSSText.Command = 'calcv'
            DSSText.Command = 'set maxcontroliter=1000'
            DSSText.Command = 'set maxiterations=1000'
            DSSText.Command = 'calcvoltagebases'         
            DSSText.Command = 'calcv'
