from enum import Enum


EPSG = 4326
COORD_REF_SYSTEM = "http://www.opengis.net/def/crs/EPSG/0/" + str(EPSG)



# class syntax
class ImageFormat(str, Enum):
    PNG = "image/png"
    GEOTIFF = "image/tiff"
    JPG = "image/jpeg"
    JSON = "application/json"
    TAR_ARCHIVE = "application/tar"
    X_TAR_ARCHIVE = "application/x-tar"
    MIXED_MEDIA = "multipart/mixed"
    OCTET_STREAM = "application/octet-stream"
