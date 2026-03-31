from rasterio.crs import CRS

SIZE_RANGE = (4096, 64)
AREA_SHP_FILE = "woodstock-saltriver.shp"

EPSG = 2048 #https://epsg.io/2048#:~:text=PROJCS%5B%22Hartebeesthoek94%20/%20Lo19%22,EPSG%22%2C%222048%22%5D%5D
COORD_REF_SYSTEM = CRS.from_epsg(3005)