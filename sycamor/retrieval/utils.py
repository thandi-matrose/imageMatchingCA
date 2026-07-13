from enum import Enum




EPSG = 4326

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

class BackCoefficient(Enum):
    BETA0 = 0
    SIGMA0_ELLIPSOID = 1
    GAMMA0_ELLIPSOID = 2
    GAMMA0_TERRAIN = 3

class OrbitDirection(Enum):
    ASCENDING = 0
    DESCENDING = 1
