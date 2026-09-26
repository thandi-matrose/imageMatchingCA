

from sycamor.ca.features.localHeterogeneity import getSpeckleDivergence
from sycamor.ca.features.logIntensity import getLogIntensity
from sycamor.ca.features.parallelTexture import TextureAnalyser
#from sycamor.ca.membership import fuzzyClassifyCell
from sycamor.retrieval.dataset import Dataset
from sycamor.visualisation.plot import distributionFeature, plotFeatureSet, plotRadar, plotHistogram
from sycamor.ca.features.set import ClassifiedRaster, Feature
from scipy import stats

def getFeatureSet(dataset : Dataset, gridCell="W45A_12"):
    '''
    Returns a list of features to be used for classification.
    
    The features are extracted from the input raster and include:
    - Logarithmic Intensity
    - Speckle Divergence (local heterogeneity)
    - Texture features (energy, mean, variance) from GLCM
    '''
    if gridCell is None:
        raster, record = dataset.getRandomRaster()
    else:
        raster, record = dataset.getRaster(gridCell)
    #plotRadar(raster, record)
    
    features = {}
    
    #Band 1
    band1 = raster.read(1)
    band2 = raster.read(2)
   
    features[Feature.LOG_INTENSITY] = (getLogIntensity(band1), getLogIntensity(band2))
    
    #Band 2
    features[Feature.SPECKLE_DIVERGENCE] = (getSpeckleDivergence(features[Feature.LOG_INTENSITY][0]), getSpeckleDivergence(features[Feature.LOG_INTENSITY][1]))
       
    analyser = (TextureAnalyser(features[Feature.LOG_INTENSITY][0]), TextureAnalyser(features[Feature.LOG_INTENSITY][0]))
    textureFeatures = (analyser[0].calculateGLCM() , analyser[1].calculateGLCM())
    #Band 3
    features[Feature.ENERGY_GLCM] = (textureFeatures[0]["energy"], textureFeatures[1]["energy"])
   
    #Band 4
    features[Feature.MEAN_GLCM] = (textureFeatures[0]["mean"], textureFeatures[1]["mean"])
    
    #Band 5
    features[Feature.VARIANCE_GLCM] = (textureFeatures[0]["variance"], textureFeatures[1]["variance"])
    
    #Plot 
    #plotFeatures(features, record=record)
    
    return features

def plotFeatures(features, record):
    
    for feat in Feature:
        #TODO uncomment!
        #distributionFeature(features[feat][0], feat, record)
        print(type(features[feat][0])+ " "+ str(features[feat][0]))
    plotFeatureSet(features, record.Hart94Filename)
    



if __name__ == "__main__":
    DATASET = Dataset();
    getFeatureSet(DATASET, "W57C_7")
    