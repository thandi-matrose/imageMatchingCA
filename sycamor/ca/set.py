
#Feature indices
import math

import numpy as np

from sycamor.ca.classification.scheme import LandClass
from sycamor.ca.parallel_utils import AtomicCounter


LOG_INTENSITY = 1
SPECKLE_DIVERGENCE = 2
ENERGY_GLCM = 3
MEAN_GLCM = 4
VARIANCE_GLCM = 5

#Cellular Automaton Parameters
NEIGHBOURHOOD_SIZE = 5

#Processing
CHUNK = 10

class ClassifiedRaster:
    
    '''
    A class representing a raster grid for land classification.
    '''
    
    raster = []
    undefinedCells = AtomicCounter()
    
    def __init__(self, height: int, width: int):
        self.raster = np.zeros((height, width))
        self.undefinedCells.increment(width*height)
        
    @property
    def getHeight(self):
        return len(self.raster)
    
    @property
    def getWidth(self):
        return len(self.raster[0])
    
    @property
    def getCellState(self, row:int , column: int):
        return self.raster[row][column]
    
    @property
    def getNeighbourhood(self, row:int , column: int):
        radius = math.floor(NEIGHBOURHOOD_SIZE/2)
        return self.raster[row-radius:row+radius][column-radius: column+radius]
    
    def classifyCell(self, row:int , column: int, landClass: LandClass):
        self.raster[row][column] = landClass.index
        self.undefinedCells.decrement(1)
    
    def getUndefinedCellCount(self):
        return self.undefinedCells.getValue()
    
    def getRaster(self):
        return self.raster
    
    def countUndefined(rasterSubset):
        return np.count_nonzero(rasterSubset == 0)
        
