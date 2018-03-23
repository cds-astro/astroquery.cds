from astropy import coordinates
from regions import CircleSkyRegion
from MocServerFeature.core import Template

import pprint;

## Query Region Usecases
# Cone Search
centerSkyCoord = coordinates.SkyCoord(10.8, 32.2, unit="deg")
radius = coordinates.Angle(1.5, 'deg')
circleSkyRegion = CircleSkyRegion(centerSkyCoord, radius)
table=Template.query_region(circleSkyRegion)
pprint.pprint(table)
