#!/usr/bin/env python
# -*- coding: utf-8 -*

from astropy import coordinates
from regions import CircleSkyRegion, PolygonSkyRegion
from mocserver.core import MOCServerQuery
from mocserver.MOCServerConstraints import CircleSkyRegionSpatialConstraint, PolygonSkyRegionSpatialConstraint
from mocserver.MOCServerConstraints import SpatialConstraint
from mocserver.MOCServerConstraints import MOCServerConstraints

from mocserver.MOCServerPropertiesConstraints import PropertiesConstraint
from mocserver.MOCServerPropertiesConstraints import PropertiesDualExpr, PropertiesUniqExpr, OperandExpr
from mocserver.MOCServerResponseFormat import MOCServerResponseFormat, Format

import pprint;

from mocpy import MOC

if __name__ == '__main__':
    # Spatial constraint definition
    center = coordinates.SkyCoord(10.8, 32.2, unit="deg")
    radius = coordinates.Angle(1.5, 'deg')
    circle_sky_region = CircleSkyRegion(center, radius)

    polygon_sky_region = PolygonSkyRegion(vertices=coordinates.SkyCoord([57.376, 56.391, 56.025, 56.616], [24.053, 24.622, 24.049, 24.290], frame="icrs", unit="deg"))
    spatial_constraint = PolygonSkyRegionSpatialConstraint(polygon_sky_region, "overlaps")

    # Properties constraint definition
    # An expression is defined as a tree-like data structure
    # Each equalities are linked by an operand (AND, OR, NAND) forming the final expression
    # to send to the http mocserver
    # definition of the the constraint
    properties_constraint = PropertiesConstraint(PropertiesDualExpr(
        OperandExpr.Inter,
        PropertiesDualExpr(
            OperandExpr.Union,
            PropertiesUniqExpr("moc_sky_fraction <= 0.01"),
            PropertiesUniqExpr("hips* = *")
        ),
        PropertiesUniqExpr("ID = *")
    ))
    #propertiesConstraint = PropertiesConstraint(PropertiesUniqExpr("ID = CDS/J/A+A/375/*"))

    # A moc server constraints object contains one spatial and/or one properties constraint
    moc_server_constraints = MOCServerConstraints()
    #mocServerConstraints.set_spatial_constraint(spatial_constraint)
    moc_server_constraints.set_properties_constraint(properties_constraint)

    # A query to the MOCServer accepts a : 
    # - MOCServerConstraints object defining all the spatial and properties constraints on the query
    # - MOCServerResponseFormat object defining the response format of the query
    response = MOCServerQuery.query_region(moc_server_constraints,
                                           MOCServerResponseFormat(format=Format.moc,
                                                                   moc_order=14,
                                                                   field_l=['ID', 'moc_sky_fraction']))
    pprint.pprint(response)

    skycoord_list = [coordinates.SkyCoord(ra=57, dec=35, unit="deg"), coordinates.SkyCoord(ra=42, dec=34, unit="deg")]
    moc = MOC.from_coo_list(skycoord_list=skycoord_list, max_norder=5)
    #import pdb; pdb.set_trace()
    #moc.write("json_moc_test.txt", format="json")
