
from scipy.ndimage import uniform_filter
import numpy as np

def getSpeckleDivergence(intensityBand, window_size:int=9):
    """

    Calculate speckle divergence D = sigma / mu over a sliding window.

    """
     # 1. Calculate local mean (mu)
    mu = uniform_filter(intensityBand, size=window_size, mode='reflect')
    
    image_sq = intensityBand ** 2
    mu_sq = uniform_filter(image_sq, size=window_size, mode='reflect')
    
    variance = mu_sq - (mu ** 2)
    variance[variance < 0] = 0 # Prevent negative values due to floating point precision
    sigma = np.sqrt(variance)
    
    # 4. Calculate Divergence (D = sigma / mu)
    # Avoid division by zero by setting areas with zero mean to 0
    divergence = np.divide(sigma, mu, out=np.zeros_like(sigma), where=mu!=0)
    
    return divergence