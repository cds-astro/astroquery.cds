from astropy import coordinates
from regions import CircleSkyRegion, PolygonSkyRegion
from MOCServerAccess.core import MOCServerQuery
from MOCServerAccess.MOCServerConstraints import CircleSkyRegionSpatialConstraint, PolygonSkyRegionSpatialConstraint
from MOCServerAccess.MOCServerConstraints import SpatialConstraint, PropertiesConstraint
from MOCServerAccess.MOCServerConstraints import MOCServerConstraints

from MOCServerAccess.MOCServerConstraints import PropertiesDualExpr, PropertiesUniqExpr, OperandExpr
from MOCServerAccess.MOCServerResponseFormat import MOCServerResponseFormat, Format

import pprint;

from mocpy import MOC

if __name__ == '__main__':
    # Spatial constraint definition
    centerSkyCoord = coordinates.SkyCoord(10.8, 32.2, unit="deg")
    radius = coordinates.Angle(1.5, 'deg')
    circleSkyRegion = CircleSkyRegion(centerSkyCoord, radius)

    polygonSkyRegion = PolygonSkyRegion(vertices=coordinates.SkyCoord([57.376, 56.391, 56.025, 56.616], [24.053, 24.622, 24.049, 24.290], frame="icrs", unit="deg"))
    spatialConstraint = PolygonSkyRegionSpatialConstraint(polygonSkyRegion, "overlaps")

    # Properties constraint definition
    # An expression is defined as a tree-like data structure
    # Each equalities are linked by an operand (AND, OR, NAND) forming the final expression
    # to send to the http mocserver
    expr = PropertiesDualExpr()
    subExpr = PropertiesDualExpr()
    subExpr.addChild(OperandExpr.Union, PropertiesUniqExpr("moc_sky_fraction <= 0.01"), PropertiesUniqExpr("hips* = *"))
    expr.addChild(OperandExpr.Inter, subExpr, PropertiesUniqExpr("ID = *"))
    # definition of the the constraint
    #propertiesConstraint = PropertiesConstraint(expr)
    propertiesConstraint = PropertiesConstraint(PropertiesUniqExpr("ID = CDS/J/A+A/375/*"))

    # A moc server constraints object contains one spatial and/or one properties constraint
    mocServerConstraints = MOCServerConstraints()
    #mocServerConstraints.setSpatialConstraint(spatialConstraint)
    mocServerConstraints.setPropertiesConstraint(propertiesConstraint)
   
    # A query to the MOCServer accepts a : 
    # - MOCServerConstraints object defining all the spatial and properties constraints on the query
    # - MOCServerResponseFormat object defining the response format of the query
    response = MOCServerQuery.query_region(mocServerConstraints,
    	MOCServerResponseFormat(format=Format.moc, mocOrder=14, field_l=['ID', 'moc_sky_fraction']))
    pprint.pprint(response)
		
    skycoord_list = [coordinates.SkyCoord(ra=57, dec=35, unit="deg"), coordinates.SkyCoord(ra=42, dec=34, unit="deg")]
    moc = MOC.from_coo_list(skycoord_list=skycoord_list, max_norder=5)
    #import pdb; pdb.set_trace()
    #moc.write("json_moc_test.txt", format="json")
