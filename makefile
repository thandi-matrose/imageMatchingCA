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
run: env_create
	@echo "Running Python module within $(ENV_NAME) environment..."
	conda activate $(ENV_NAME)
	python -m src.main 

# Target to clean up the environment
clean:
	@echo "Removing conda environment $(ENV_NAME)..."
	$(CONDA_BIN) env remove -n $(ENV_NAME)
