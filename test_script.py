from astropy import coordinates
from regions import CircleSkyRegion
from MOCServerAccess.core import MOCServerQuery
from MOCServerAccess.MOCServerConstraints import CircleSkyRegionSpatialConstraint
from MOCServerAccess.MOCServerConstraints import SpatialConstraint, PropertiesConstraint
from MOCServerAccess.MOCServerConstraints import MOCServerConstraints

from MOCServerAccess.MOCServerConstraints import PropertiesDualExpr, PropertiesUniqExpr, OperandExpr
from MOCServerAccess.MOCServerResponseFormat import MOCServerResponseFormat, Format

import pprint;

if __name__ == '__main__':
    # Spatial constraint definition
    centerSkyCoord = coordinates.SkyCoord(10.8, 32.2, unit="deg")
    radius = coordinates.Angle(1.5, 'deg')
    circleSkyRegion = CircleSkyRegion(centerSkyCoord, radius)
    spatialConstraint = CircleSkyRegionSpatialConstraint(circleSkyRegion, "overlaps")

    # Properties constraint definition
    # An expression is defined as a tree-like data structure
    # Each equalities are linked by an operand (AND, OR, NAND) forming the final expression
    # to send to the http mocserver
    expr = PropertiesDualExpr()
    subExpr = PropertiesDualExpr()
    subExpr.addChild(OperandExpr.OROP, PropertiesUniqExpr("moc_sky_fraction <= 0.01"), PropertiesUniqExpr("hips* = *"))
    expr.addChild(OperandExpr.ANDOP, subExpr, PropertiesUniqExpr("ID = *"))
    # definition of the the constraint
    propertiesConstraint = PropertiesConstraint(expr)

    # A moc server constraints object contains one spatial and/or one properties constraint
    mocServerConstraints = MOCServerConstraints()
    mocServerConstraints.setSpatialConstraint(spatialConstraint)
    mocServerConstraints.setPropertiesConstraint(propertiesConstraint)
   
    # A query to the MOCServer accepts a : 
    # - MOCServerConstraints object defining all the spatial and properties constraints on the query
    # - MOCServerResponseFormat object defining the response format of the query
    response = MOCServerQuery.query_region(mocServerConstraints,
    	MOCServerResponseFormat(responseFormat=Format.number, field_l=['ID', 'moc_sky_fraction']))
    pprint.pprint(response)
