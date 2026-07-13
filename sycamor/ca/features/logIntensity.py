import numpy as np
def getLogIntensity(data):
    
    logInt = 10 * np.log10(np.maximum(data, 1e-10))
    
    return logInt