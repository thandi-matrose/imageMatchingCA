from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
import dataretrieval.sentinelone.utils as utils

load_dotenv()

class SentinelHub:
    
   
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')


    oauth : OAuth2Session

    def __init__(self):
        
        # Creating a session
        client = BackendApplicationClient(client_id=self.CLIENT_ID)
        self.oauth = OAuth2Session(client=client)

        # Get token for the session
        token = self.oauth.fetch_token(
            token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
            client_secret=self.CLIENT_SECRET, include_client_id=True)
        print("Logged in client " + self.CLIENT_ID)


    def sendRequest(self, request : str):
        url = "https://sh.dataspace.copernicus.eu/api/v1/process"
        response = self.oauth.post(url, json=request)
        return response
    
    def createRequest(self, polarisation : str = "VV", 
                      imgFormat : utils.ImageFormat = utils.ImageFormat.PNG,
                      boundingBox : list = [-50385.6, -3757000.0, -50180.799999999996, -3756795.2]):
        evalscript = rf"""
        //VERSION=3
        function setup() {{
        return {{
            input: ["{polarisation}"],
            output: {{ id: "default", bands: 1 }},
        }}
        }}

        function evaluatePixel(samples) {{
        return [samples.VV]
        }}
        """

        request = {
            "input": {
                "bounds": {
                    "bbox": boundingBox,
                    "properties": {"crs": utils.COORD_REF_SYSTEM},
                },
                "data": [
                    {
                        "type": "sentinel-1-grd",
                        "dataFilter": {
                            "timeRange": {
                                "from": "2024-02-02T00:00:00Z",
                                "to": "2024-04-02T23:59:59Z",
                            }
                        },
                        "resolution": "HIGH",
                        "acquisitionMode": "IW",
                        "processing": {},
                    }
                ],
            },
            "output": {
                "width": 2000,
                "height": 2000,
                "responses": [
                    {
                        "identifier": "default",
                        "format": {"type": (imgFormat)},
                    }
                ],
            },
            "evalscript": evalscript,
        }
        return request
    
    def writeImage(data, polarisation, imageFormat):
        with open("dataretrieval/sentinelone/sentinel1_"+imageFormat+"_"+ polarisation+".png", "wb") as image_file:
            image_file.write(data.content)
    