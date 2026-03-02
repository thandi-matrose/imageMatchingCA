from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from PIL import Image
import io
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()

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