

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple

import numpy as np

@dataclass
class GaussianDefinition:
    """Gaussian membership function: μ(x) = exp(-(x - centre)² / (2σ²))."""
    centre: float
    sigma: float
    method: str = "unknown"
    n_samples: int = 0

    def membership(self, x):
        return np.exp(-((np.asarray(x) - self.centre) ** 2) / (2 * self.sigma ** 2))

    def fwhm(self) -> float:
        """Full width at half maximum."""
        return 2 * np.sqrt(2 * np.log(2)) * self.sigma

    def inflection_width(self) -> float:
        """Distance between inflection points (always 2σ)."""
        return 2 * self.sigma

    def support(self, n_sigma: float = 3.0) -> Tuple[float, float]:
        """Range where membership is effectively non-zero."""
        return (self.centre - n_sigma * self.sigma,
                self.centre + n_sigma * self.sigma)

    def width_at(self, membership: float) -> float:
        """Full width where membership >= given level."""
        if membership <= 0 or membership >= 1:
            return 0.0 if membership >= 1 else np.inf
        return 2 * self.sigma * np.sqrt(-2 * np.log(membership))

    def core_width(self) -> float:
        return self.fwhm()

    def support_width(self, n_sigma: float = 3.0) -> float:
        return 2 * n_sigma * self.sigma

    def to_dict(self):
        return {"centre": self.centre, "sigma": self.sigma,
                "method": self.method, "n_samples": self.n_samples}

@dataclass
class TrapezoidalDefinition:
    a: float
    b: float
    c: float
    d: float
    method: str
    n_samples: int

    def __post_init__(self):
        # Enforce monotonicity a <= b <= c <= d
        vals = sorted([self.a, self.b, self.c, self.d])
        self.a, self.b, self.c, self.d = vals

    def as_tuple(self) -> Tuple[float, float, float, float]:
        return (self.a, self.b, self.c, self.d)
    def as_dict(self) :
            return {"a":self.a, "b":self.b, "c":self.c, "d":self.d}
    
    def support_width(self) -> float:
        return self.d - self.a

    def core_width(self) -> float:
        return self.c - self.b

    def membership(self, x: float) -> float:
        if x <= self.a or x >= self.d:
            return 0.0
        if self.b <= x <= self.c:
            return 1.0
        if x < self.b:
            return (x - self.a) / max(self.b - self.a, 1e-12)
        return (self.d - x) / max(self.d - self.c, 1e-12)

    def to_dict(self) -> Dict[str, float]:
        return {"a": self.a, "b": self.b, "c": self.c, "d": self.d}

    
    def getDimensions(self) -> list:
        return [self.a, self.b, self.c, self.d]
        


class LandClass(Enum):
    
  

    index: int
    displayName: str
    description: str
    atlas_codes: list
    colour: str
    lsdf_terms: list #COCT LSDF CLASSES



    UNDEFINED = (
        0,
        "Undefined",
        "Undefined Regions",
        [],
        "#ffffff",
        []
    )

    HIGH_DENSITY_URBAN = (
        1,
        "High Density Urban",
        "High density urban fabric",
        ["11100", "11210", "11220"],
        "#FE1212",
        ["General Residential (GR)", "Mixed Use (MU)", "High Density Residential"]
    )

    MED_DENSITY_URBAN = (
        2,
        "Medium Density Urban",
        "Medium density urban fabric",
        ["11220", "11230"],
        "#FFAE00",
        ["General Residential (GR)", "Single Residential (SR)"]
    )

    LOW_DENSITY_URBAN = (
        3,
        "Low Density Urban",
        "Low density urban fabric",
        ["11230", "11240", "11300"],
        "#FFE100",
        ["Single Residential (SR1, SR2)", "Rural Residential"]
    )

    ROADS = (
        4,
        "Roads",
        "Roads and transport infrastructure",
        ["12200", "12210", "12220", "12230"],
        "#FF00AA",
        ["Transport Zoning 1 (TR1)", "Transport Use", "Public Road"]
    )


    INDUSTRY = (
        5,
        "Industry",
        "Industry, commercial and construction",
        ["12100", "12300", "12400", "13100", "13300"],
        "#807a85",
        ["General Industry (GI)", "Mixed Use (MU)", "Port Zoning"]
    )

    VEGETATION = (
        6,
        "Vegetation",
        "Vegetation (green urban areas, forests, grassland)",
        ["14100", "14200", "31000", "32000", "32100", "32200"],
        "#23a937",
        ["Public Open Space (OS2)", "Environmental Conservation (OS1)",
         "Urban Green Area"]
    )

    WATER = (
        7,
        "Water",
        "Water bodies (inland and coastal)",
        ["50000", "51000", "52000", "51100", "51200"],
        "#00A2FF",  
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
    def getIndices(self):
        return [member.index for member in LandClass]
        
    @classmethod
    def getValues(self):
        return [member.index for member in LandClass]

    def __repr__(self):
        return f"<LandClass.{self.name}: index={self.index}, '{self.description}'>"



    
if __name__ == "__main__":
    # Print all classes with their Atlas codes
    for cls in LandClass:
        print(f"{cls.index:>2}  {cls.name:<25}  {cls.atlas_codes}")
        
        

