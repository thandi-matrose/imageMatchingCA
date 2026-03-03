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
from matplotlib import gridspec
import xarray as xr

from rasterio.plot import show
import rasterio as rast


import xarray



load_dotenv()

def sample():
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

    # Create a session
    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)

    # Get token for the session
    token = oauth.fetch_token(
        token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
        client_secret=CLIENT_SECRET, include_client_id=True)

    evalscript = """
    //VERSION=3
    function setup() {
    return {
        input: ["VV"],
        output: { id: "default", bands: 1 },
    }
    }

    function evaluatePixel(samples) {
    return [2 * samples.VV]
    }
    """

    request = {
        "input": {
            "bounds": {
                "bbox": [
                    1360000,
                    5121900,
                    1370000,
                    5131900,
                ],
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/3857"},
            },
            "data": [
                {
                    "type": "sentinel-1-grd",
                    "dataFilter": {
                        "timeRange": {
                            "from": "2019-02-02T00:00:00Z",
                            "to": "2019-04-02T23:59:59Z",
                        }
                    },
                    "processing": {"orthorectify": "true"},
                }
            ],
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [
                {
                    "identifier": "default",
                    "format": {"type": "image/png"},
                }
            ],
        },
        "evalscript": evalscript,
    }

    url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    response = oauth.post(url, json=request)
    print(response)

def getImg():
    connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
    aoi = {
    "type": "Polygon",
    "coordinates": [
        [
            [48.325487506118264, 28.742803969343313],
            [48.325487506118264, 28.414218984218607],
            [48.75387693420447, 28.414218984218607],
            [48.75387693420447, 28.742803969343313],
            [48.325487506118264, 28.742803969343313],
        ]
    ],
}
    s1_image = connection.load_collection(
    "SENTINEL1_GRD",
    temporal_extent=["2025-08-09", "2025-08-11"],
    spatial_extent=aoi,
    bands=["VV"],
)

    s1_image = s1_image.sar_backscatter(coefficient="sigma0-ellipsoid")
    
    #s1_image = s1_image.apply(process=lambda data: 10 * openeo.processes.log(data, base=10))

    s1_image = s1_image.rename_labels(dimension="bands", target=["amplitude"])
    oil_spill = s1_image.band("amplitude")
    oil_spill.execute_batch(title="Oil Spill Data", outputfile="OilSpill.nc")
def readOil():
    
    oilspill = xr.load_dataset("OilSpill.nc")
    print(oilspill._variables)
    rast.open(r'netcdf:./OilSpill.nc')
    show(oilspill)
    data = oilspill[["var"]].to_array(dim="bands")
    print("hi")
    cmap = matplotlib.colors.ListedColormap(["black", "#FFFFED"])
    values = ["Absence", "Presence"]
    colors = ["black", "#FFFFED"]

    oilspill_array = data.squeeze().values[600:-600, 600:-600]
    fig, axes = plt.subplots(ncols=1, figsize=(5, 5), dpi=100)
    axes.imshow(oilspill_array, cmap=cmap)
    axes.set_title("Oil Spill Image")
    print(oilspill_array)

    patches = [
        mpatches.Patch(color=colors[i], label="Oil {l}".format(l=values[i]))
        for i in range(len(values))
    ]
    fig.legend(handles=patches, bbox_to_anchor=(0.9, 0.3), loc=1)
    axes.axes.get_xaxis().set_visible(False)
    axes.axes.get_yaxis().set_visible(False)
 

def main():
    #readOil()
    print("Run")

if __name__ == "__main__":
    main()