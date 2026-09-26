#MAIN WORKFLOW
from sycamor.ca.features.main import getFeatureSet


def classify(dataset, grid=None):
    
    #Step 1: Feature Extraction
    if (grid is None):
        features = getFeatureSet(dataset)
    else:
        features = getFeatureSet(dataset, grid)
   
    #Step 2: Seeding Function
    #seed = seed(features)
    
    #Step 3: Apply Region Growing Rule
    #classifiedRaster = applyTransitionRule(seed, features)
    
    #return classifiedRaster


if __name__ == "__main__":
    classify(DATASET, "W57C_7")