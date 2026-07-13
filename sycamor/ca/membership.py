'''
Fuzzy Classification Formulae for Cellular Automata 

'''

def fuzzyClassifyCell(state, neighbourhood, intensity, speckDivergence, energyGLCM, meanGLCM, varianceGLCM):
    '''
    Classifies a cell based on its current state and the values of its features using probabilistic logic.
    
    Parameters:
    - state: The current state of the cell (0 for unclassified, 1 for low-density urban,...).
    - neighbourhood: The states of the neighboring cells.
    - intensity: The log intensity value of the cell.
    - speckDivergence: The speckle divergence value of the cell.
    - energyGLCM: The energy GLCM value of the cell.
    - meanGLCM: The mean GLCM value of the cell.
    - varianceGLCM: The variance GLCM value of the cell.
    
    Returns:
    - The new state of the cell after classification.
    '''
    trapezoidalMembership = lambda x, a, b, c, d: max(0, min((x - a) / (b - a), 1, (d - x) / (d - c)))
    if trapezoidalMembership(intensity, 0.5, 0.6, 0.8, 1) > 0.5 and trapezoidalMembership(speckDivergence, 0, 0.1, 0.2, 0.3) > 0.5 and trapezoidalMembership(energyGLCM, 0.2, 0.3, 0.5, 0.6) > 0.5:
        state = 1  # Low-density urban
    else: #Classify on next time step
        state = 0  # Unclassified
    return state
    
    