import dss

DSSCircuit = None
DSSText = None
DSSSolution = None
ControlQueue = None

def compile_dss_circuit(mydir):
    global DSSCircuit, DSSText, DSSSolution, ControlQueue, Time_Resolution, Num_of_TimeStep, Num_of_HVTr, Num_of_DisTransformers, Num_of_HVlines, Num_of_Customers, Voltage_max, Voltage_min
    # Setting up DSS engine
    dss_engine = dss.DSS
    DSSText = dss_engine.Text                                                      
    DSSCircuit = dss_engine.ActiveCircuit                                            
    DSSSolution = dss_engine.ActiveCircuit.Solution                                      
    ControlQueue = dss_engine.ActiveCircuit.CtrlQueue                                          
    dss_engine.AllowForms = 0

    # Network Parameters
    Time_Resolution = 30 # in minutes
    Num_of_TimeStep = 48 # number of total time steps (48*30 min = 24 hours)
    Num_of_HVTr = 3  
    Num_of_DisTransformers = 69
    Num_of_HVlines = 89
    Num_of_Customers = 345
    Voltage_max = 1.05 # 1.1 of 208V = 228.9V
    Voltage_min = 0.95 # 0.95 of 208V = 197.6V

    # Load Fort Chipwyan network model
    DSSText.Command = 'Clear'                               
    DSSText.Command = 'Compile ' + mydir +  '\\Test1\\master.dss'    
    DSSText.Command = 'Set VoltageBases = [4.16 25.0 4.2 0.208 0.12]'
    DSSText.Command = 'calcvoltagebases'