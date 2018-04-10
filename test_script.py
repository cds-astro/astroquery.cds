#!/usr/bin/env python
# -*- coding: utf-8 -*

from astropy import coordinates
from cds.core import cds
from cds.spatial_constraints import *
from cds.constraints import Constraints

from cds.property_constraint import *

from cds.output_format import *

from cds.dataset import Dataset

if __name__ == '__main__':
    # Spatial constraint definition
    center = coordinates.SkyCoord(10.8, 32.2, unit="deg")
    radius = coordinates.Angle(1.5, 'deg')
    circle_sky_region = CircleSkyRegion(center, radius)

    # polygon_sky_region = PolygonSkyRegion(vertices=coordinates.SkyCoord(
    # [57.376, 56.391, 56.025, 56.616], [24.053, 24.622, 24.049, 24.290], frame="icrs", unit="deg"))
    # spatial_constraint = PolygonSkyRegionSpatialConstraint(polygon_sky_region, "overlaps")

    spatial_constraint = Cone(circle_sky_region, intersect='overlaps')
    # spatial_constraint = Moc.from_file(filename='mocserver/tests/data/moc.fits', intersect='overlaps')
    # spatial_constraint = MocSpatialConstraint.from_url(url='http://alasky.u-strasbg.fr/SDSS/DR9/color/Moc.fits',
    # intersect='overlaps')
    '''
    properties_constraint = PropertyConstraint(ParentNode(
    OperandExpr.Inter,
    ParentNode(
        OperandExpr.Union,
        ChildNode("moc_sky_fraction <= 0.01"),
        ChildNode("hips* = *")
    ),
    ChildNode("ID = *")
    ))
    '''

    properties_constraint = PropertyConstraint('ID = *CDS*')
    # A moc server constraints object contains one spatial and/or one properties constraint
    moc_server_constraints = Constraints(sc=spatial_constraint, pc=properties_constraint)
    datasets = cds.query_region(moc_server_constraints,
                                      OutputFormat(format=OutputFormat.Type.record,
                                                   field_l=['ID',
                                                            'cs_service_url',
                                                            'dataproduct_type',
                                                            'tap_service_url']))

    for id, dataset in list(datasets.items()):
        if 'dataproduct_type' in dataset.properties.keys():
            dataproduct_type = dataset.properties['dataproduct_type']

        if 'tap' in dataset.services:
            print(dataset.search(Dataset.ServiceType.tap, query="""SELECT * FROM basic JOIN ident ON oidref = oid"""))

        #if 'cs' in dataset.services:
        #    print(dataset.search(Dataset.ServiceType.cs, pos=center, radius=radius))
        #    exit()
