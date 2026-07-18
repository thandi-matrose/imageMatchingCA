import numpy as np
def getLogIntensity(data):
    '''
    Calculates logarithmic intensity
    Returns:
    - logarithmicInt: 
    '''
    logInt = 10 * np.log10(np.maximum(data, 1e-10))
    
    return logInt