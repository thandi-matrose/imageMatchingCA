# Define variables for convenience
ENV_NAME = sycamor
CONDA_BIN = $(shell conda info --base)/bin/conda

.ONESHELL:
SHELL = /bin/bash

# Target to create and update the conda environment
env_create:
	@echo "Creating/updating conda environment $(ENV_NAME)..."
	$(CONDA_BIN) env create -f environment.yml || $(CONDA_BIN) env update -f environment.yml

# Target to run a Python module within the environment
run: 
	@echo "Running Python module within $(ENV_NAME) environment..."
	conda activate $(ENV_NAME)
	python -m sycamor.texture 
opticalClassify:
	python -m optical.classify
evaluate:
	python -m evaluation.growcut.segment
getRadar:
	python -m sycamor.retrieval.main

dataset:
	python -m sycamor.ca.classification.merged.ClassifiedDataset

make model:
	python -m optical.randomforest

make plotFeature:
	python -m sycamor.visualisation.plotFeatures
make despeckle:
	python -m optical.despeckle
plotSeed:
	python -m sycamor.visualisation.seedData

summarise:
	python -m sycamor.ca.classification.summariser
plotGrowth:
	python -m sycamor.visualisation.growth
plotRandomForest:
	python -m sycamor.visualisation.randomforest

	
plotGrowCut:
	python -m sycamor.visualisation.growcut
plotTrapez:
	python -m sycamor.visualisation.plotters.trapez

plotTables:
	python -m sycamor.visualisation.tables
classify:
	python -m sycamor.ca.main

convertECW:
	python -m sycamor.retrieval.ecwToGeotiff

match:
	python -m sycamor.matching.main
matchPlain:
	python -m sycamor.matching.plain
sample:
	python -m sycamor.ca.classification.plot

merge:
	python -m sycamor.ca.classification.merge

seedA:
	python -m sycamor.ca.seed.main

plotMerge:
	python -m sycamor.visualisation.plotMerge

runner:
	python -m sycamor.visualisation.seedPlotter

plot:
	python -m sycamor.visualisation.plot


regionGrow:
	python -m sycamor.ca.region_growing.main

# Target to clean up the environment
clean:
	@echo "Removing conda environment $(ENV_NAME)..."
	$(CONDA_BIN) env remove -n $(ENV_NAME)

test:
	python -m sycamor.ca.features.parallelTexture

aerial:
	python -m sycamor.retrieval.aerial.main

tiles:
	python -m sycamor.retrieval.coctTiles



#MAIN WORKFLOW

extract:
	python -m sycamor.ca.features.main

seed:
	python -m sycamor.ca.seed.main