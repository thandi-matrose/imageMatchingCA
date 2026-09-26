

from enum import Enum



class TrapezoidalDefinition():
    a : float 
    b : float
    c : float
    d : float
    
    def __init__(self,a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d


class LandClass(Enum):
    
  

    index: int
    displayName: str
    description: str
    atlas_codes: list
    colour: str
    lsdf_terms: list #COCT LSDF CLASSES
    signature: TrapezoidalDefinition()



    UNDEFINED = (
        0,
        "Undefined",
        "Undefined Regions",
        [],
        "#41373700",
        []
    )

    HIGH_DENSITY_URBAN = (
        1,
        "High Density Urban",
        "High density urban fabric",
        ["11100", "11210", "11220"],
        "#914545",
        ["General Residential (GR)", "Mixed Use (MU)", "High Density Residential"]
    )

    MED_DENSITY_URBAN = (
        2,
        "Medium Density Urban",
        "Medium density urban fabric",
        ["11220", "11230"],
        "#DC6868",
        ["General Residential (GR)", "Single Residential (SR)"]
    )

    LOW_DENSITY_URBAN = (
        3,
        "Low Density Urban",
        "Low density urban fabric",
        ["11230", "11240", "11300"],
        "#E388DA",
        ["Single Residential (SR1, SR2)", "Rural Residential"]
    )

    ROADS = (
        4,
        "Roads",
        "Roads and transport infrastructure",
        ["12200", "12210", "12220", "12230"],
        "#282525",
        ["Transport Zoning 1 (TR1)", "Transport Use", "Public Road"]
    )


    INDUSTRY = (
        5,
        "Industry",
        "Industry, commercial and construction",
        ["12100", "12300", "12400", "13100", "13300"],
        "#d8d0bf",
        ["General Industry (GI)", "Mixed Use (MU)", "Port Zoning"]
    )

    VEGETATION = (
        6,
        "Vegetation",
        "Vegetation (green urban areas, forests, grassland)",
        ["14100", "14200", "31000", "32000", "32100", "32200"],
        "#486a48",
        ["Public Open Space (OS2)", "Environmental Conservation (OS1)",
         "Urban Green Area"]
    )

    WATER = (
        7,
        "Water",
        "Water bodies (inland and coastal)",
        ["50000", "51000", "52000", "51100", "51200"],
        "#4A90D9",  
        ["Open Space Zoning (OS)", "Flood Plain", "Watercourse"]
    )

    # ---------------------------------------------------------------

    def __init__(
        self,

        index: int,
        displayName: str,
        description: str,
        atlas_codes: list,
        colour: str,
        lsdf_terms: list
    ):
        self.index = index
        self.displayName = displayName
        self.description = description
        self.atlas_codes = atlas_codes
        self.colour = colour
        self.lsdf_terms = lsdf_terms


    @classmethod
    def from_index(cls, idx: int) -> "LandClass":
        for member in cls:
            if member.index == idx:
                return member
        raise ValueError(f"No LandClass with index {idx}")

    @classmethod
    def from_atlas_code(cls, code: str) -> "LandClass":
        for member in cls:
            if code in member.atlas_codes:
                return member
        raise ValueError(f"No LandClass with atlas code {code}")

    @classmethod
    def all_atlas_codes(cls) -> dict:
        mapping = {}
        for member in cls:
            for code in member.atlas_codes:
                mapping[code] = member.name
        return mapping
    
    @classmethod
    def getNames(self):
        return [member.displayName for member in LandClass]
        
    @classmethod
    def getColours(self):
        return [member.colour for member in LandClass]
    
    @classmethod
    def getValues(self):
        return [member.index for member in LandClass]

    def __repr__(self):
        return f"<LandClass.{self.name}: index={self.index}, '{self.description}'>"


    
if __name__ == "__main__":
    # Print all classes with their Atlas codes
    for cls in LandClass:
        print(f"{cls.index:>2}  {cls.name:<25}  {cls.atlas_codes}")
        
        

