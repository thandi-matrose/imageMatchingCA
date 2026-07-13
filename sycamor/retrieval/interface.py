from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
import sycamor.retrieval as utils

load_dotenv()

EPSG = 4326
COORD_REF_SYSTEM = "http://www.opengis.net/def/crs/EPSG/0/" + str(EPSG)

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
        response = self.oauth.post(url, json=request, headers={"Accept": "image/tiff"})
        return response
    
    def createRequest(self,
                      boundingBox : list = [-50385.6, -3757000.0, -50180.799999999996, -3756795.2]):
        
        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: ["VV", "VH"],
                output: { id: "default", bands: 2 },
            }
        }

        function evaluatePixel(samples) {
        return [samples.VV, samples.VH]
        }
        """

        request = {
            "input": {
                "bounds": {
                    "bbox": boundingBox,
                    "properties": {"crs": COORD_REF_SYSTEM},},
                "data": [
                    {
                        "type": "sentinel-1-grd",
                        "dataFilter": {
                            "timeRange": {
                                "from": "2025-01-01T00:00:00Z",
                                "to": "2025-03-01T23:59:59Z",
                            },
                            "acquisitionMode": "IW",
                            "polarization": "DV",
                            "orbitDirection ": "DESCENDING",
                            "resolution": "HIGH",
                        },
                        "processing": {
                            "orthorectify": "true",
                            "speckleFilter": {
                                "type": "LEE",
                                "windowSizeX": 7,
                                "windowSizeY": 7
                            },
                            "demInstance": "COPERNICUS_30",
                            
                        },
                    }
                ],
            },
            "output": {
                "responses": [
                    {
                        "identifier": "default",
                        "format": {"type": "image/tiff"},
                    },
                ],
            },
            "evalscript": evalscript,
        }

        return request
    
    def me():
     '''
     "demInstance": "COPERNICUS_30",
                            "speckleFilter": {
                                "type": "LEE",
                                "windowSizeX": 7,
                                "windowSizeY": 7
                            }
                            '''