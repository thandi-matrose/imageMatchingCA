
from sycamor.ca.classification.scheme import LandClass
from sycamor.ca.features.localHeterogeneity import getSpeckleDivergence
from sycamor.ca.features.logIntensity import getLogIntensity
from sycamor.ca.features.texture import PROPERTIES, getTextureBands
from sycamor.ca.membership import fuzzyClassifyCell
from sycamor.ca.parallel_utils import AtomicCounter
from sycamor.retrieval import dataset
from sycamor.visualisation.plot import distributionLogIntensity, plotFeatureSet, plotRadar, plotHistogram
from sycamor.ca.set import ClassifiedRaster, Feature
from scipy import stats

def getFeatureSet(dataset):
    '''
    Returns a list of features to be used for classification.
    
    The features are extracted from the input raster and include:
    - Logarithmic Intensity
    - Speckle Divergence (local heterogeneity)
    - Texture features (energy, mean, variance) from GLCM
    '''
    
    raster, record = dataset.getRandomRaster()
    plotRadar(raster, record)
    
    features = {}
    
    #Band 1
    band1 = raster.read(1)
    band2 = raster.read(2)
   
    features[Feature.LOG_INTENSITY] = (getLogIntensity(band1), getLogIntensity(band2))
    
    #Band 2
    features[Feature.SPECKLE_DIVERGENCE] = (getSpeckleDivergence(features[Feature.LOG_INTENSITY][0]), getSpeckleDivergence(features[Feature.LOG_INTENSITY][1]))
       
    
    textureFeatures = (getTextureBands(features[Feature.LOG_INTENSITY][0]),  getTextureBands(features[Feature.LOG_INTENSITY][1]))
    #Band 3
    features[Feature.ENERGY_GLCM] = (textureFeatures[0]["energy"], textureFeatures[1]["energy"])
   
    #Band 4
    features[Feature.MEAN_GLCM] = (textureFeatures[0]["mean"], textureFeatures[1]["mean"])
    
    #Band 5
    features[Feature.VARIANCE_GLCM] = (textureFeatures[0]["variance"], textureFeatures[1]["variance"])
    
    plotFeatures(features, record=record)
    return features

def plotFeatures(features, record):
    distributionLogIntensity(features[Feature.LOG_INTENSITY][0], record)
    plotHistogram(features[Feature.SPECKLE_DIVERGENCE][0], title="Speckle Divergence Histogram")
    plotHistogram(features[Feature.ENERGY_GLCM][1], title="Energy GLCM Histogram")
    plotHistogram(features[Feature.MEAN_GLCM][0], title="Mean GLCM Histogram")
    plotHistogram(features[Feature.VARIANCE_GLCM][0], title="Variance GLCM Histogram")
    
    plotFeatureSet(features, record.Hart94Filename)
    
def applyTransitionRule(raster: ClassifiedRaster, featureSet, row: int, column:int, nextRaster : ClassifiedRaster):
    '''
    A
    
    '''
    cell = raster.getCell(row,column)
    neighbourhood =raster.getNeighbourhood(row, column)
    
    #Weights
    intensity = featureSet[LOG_INTENSITY][row][column]
    speckDivergence = featureSet[SPECKLE_DIVERGENCE][row][column]
    energyGLCM = featureSet[ENERGY_GLCM][row][column]
    varianceGLCM = featureSet[VARIANCE_GLCM][row][column]
    varianceGLCM = featureSet[VARIANCE_GLCM][row][column]
    
    #Apply membership function
    nextRaster.classifyCell(fuzzyClassifyCell(cell, neighbourhood, intensity, speckDivergence, energyGLCM, varianceGLCM))
    
    return raster   
    
def seed(featureSet, row: int, column:int):
    pass

def recursiveParallelClassify(raster: ClassifiedRaster, featureSet, startInd:int, endInd:int):
    if (endInd - startInd <= CHUNK):
        for i in range(startInd, endInd):
            for j in range(raster.getWidth):
                applyTransitionRule(raster, featureSet, i, j)
    else:
        recursiveParallelClassify(raster, featureSet, startInd, (startInd + endInd) // 2)
        recursiveParallelClassify(raster, featureSet, (startInd + endInd) // 2, endInd)      
        
    
#MAIN WORKFLOW
def classify(dataset):
    #features = getFeatureSet(dataset)
    #print(features[Feature.LOG_INTENSITY])
    print(Feature.__module__)
    #seed = seed(features)
    
    #classifiedRaster = applyTransitionRule(seed, features)
    
    #return classifiedRaster


if __name__ == "__main__":
    DATASET = dataset.Dataset()
    classify(DATASET)