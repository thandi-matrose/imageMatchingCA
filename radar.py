from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from PIL import Image
import io
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import matplotlib.patches as mpatches

import openeo

import matplotlib

import matplotlib.pyplot as plt
import xarray as xr

from rasterio.plot import show
import rasterio as rast

from dataretrieval.sentinelone import interface
from dataretrieval.woodstocksaltriver.datasetManager import DatasetManager

load_dotenv()
DATA_DIR = os.getenv('DATA_DIR')
#os.chdir(DATA_DIR)
print(f"Working directory to: {os.getcwd()}")

def main():
    hub = interface.SentinelHub() 
    aerialDataManager = DatasetManager()
    request = hub.createRequest(boundingBox=[])
    #data = hub.sendRequest(request)

    print("Encoding" + str(data.apparent_encoding))
    print("Content:" + str(data.content))
    print("Headers:" + str(data.headers))
    print("Content:" + str(data.status_code))
    with open("tryingagain.png", "wb") as image_file:
        image_file.write(data.content)

if __name__ == "__main__":
    main()