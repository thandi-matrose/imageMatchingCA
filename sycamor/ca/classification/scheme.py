from enum import Enum


class LandClass(Enum):
    
    index: int
    description:str 
    atlasCodes: list
    colour: str
    
    # lulc class
    LOW_DENSITY_URBAN = (1,"Low density urban", [], "#E388DA")
    MED_DENSITY_URBAN   = (2,"Medium density urban", [], "#DC6868")
    HIGH_DENSITY_URBAN   = (3,"High density urban", [], "#914545")
    ROADS    = (4,"Roads like highways and streets", [], "#282525")
    INDUSTRY    = (5,"Industry and construction", [], "#d8d0bf")
    VEGETATION    = (6,"Vegetation such as forests and grasslands", [], "#486a48")
    WATER    = (7,"Water bodies", [], "#FFFFF")

    def __init__(self, index: int, description:str , atlasCodes: list, colour: str):
        self.index = index
        self.description = description
        self.atlasCodes = atlasCodes
        self.colour = colour

    
    
