# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import os
import json
from sys import getsizeof

from mocserver.core import mocserver

from mocserver.constraints import Constraints
from mocserver.spatial_constraints import *
from mocserver.property_constraint import *
from mocserver.output_format import *

from astroquery.utils.testing_tools import MockResponse
from astroquery.utils import commons

from astropy import coordinates
from regions import CircleSkyRegion, PolygonSkyRegion

DATA_FILES = {
	'CONE_SEARCH' : 'cone_search.json',
	'POLYGON_SEARCH' : 'polygon_search.json',
	'PROPERTIES_SEARCH' : 'properties.json',
	'HIPS_FROM_SAADA_AND_ALASKY' : 'hips_from_saada_alasky.json',
	'HIPS_GAIA' : 'hips_gaia.json'
}

def data_path(filename):
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    return os.path.join(data_dir, filename)

@pytest.fixture
def init_request():
    moc_server_constraints = Constraints()
    moc_server_format = OutputFormat()
    return (moc_server_constraints, moc_server_format)

@pytest.fixture
def patch_get(request):
    try:
        mp = request.getfixturevalue("monkeypatch")
    except AttributeError:  # pytest < 3
        mp = request.getfuncargvalue("monkeypatch")
    mp.setattr(MOCServerQuery, '_request', get_mockreturn)
    return mp

def get_mockreturn(method, url, params=None, timeout=10, **kwargs):
    filename = data_path(DATA_FILES[params['get']])
    content = open(filename, 'rb').read()
    return MockResponse(content)

@pytest.fixture
def get_request_results(init_request):
    """Perform the request using the astroquery.MocServer  API"""

    def process_query(spatial_constraint=None, property_constraint=None):
        assert spatial_constraint or property_constraint
        moc_server_constraints, moc_server_format = init_request

        moc_server_constraints.spatial_constraint = spatial_constraint
        moc_server_constraints.properties_constraint = property_constraint

        request_result = mocserver.query_region(moc_server_constraints, moc_server_format)
        return request_result
    return process_query

@pytest.fixture
def get_true_request_results():
    """
    Get the results of the MocServer

    obtained by performing the request on http://alasky.unistra.fr/MocServer/query
    and saving it into the data directory

    """

    def load_true_result_query(data_file_id):
        filename = data_path(DATA_FILES[data_file_id])
        content = None
        with open(filename, 'r') as f_in:
            content = f_in.read()
        return json.loads(content)

    return load_true_result_query

"""List of all the constraint we want to test"""
# SPATIAL CONSTRAINTS DEFINITIONS
center = coordinates.SkyCoord(ra=10.8, dec=6.5, unit="deg")
radius = coordinates.Angle(1.5, unit="deg")
circle_sky_region = CircleSkyRegion(center, radius)
cone_search_constraint = CircleSkyRegionSpatialConstraint(circle_sky_region, intersect='overlaps')

polygon1 = PolygonSkyRegion(vertices=coordinates.SkyCoord([57.376, 56.391, 56.025, 56.616], [24.053, 24.622, 24.049, 24.291], frame="icrs", unit="deg"))
polygon2 = PolygonSkyRegion(vertices=coordinates.SkyCoord([58.376, 53.391, 56.025, 54.616], [24.053, 25.622, 22.049, 27.291], frame="icrs", unit="deg"))
polygon_search_constraint = PolygonSkyRegionSpatialConstraint(polygon1, intersect='overlaps')

# PROPERTY CONSTRAINTS DEFINITIONS
properties_ex = PropertyConstraint(ParentNode(
    OperandExpr.Inter,
    ParentNode(
        OperandExpr.Union,
        ChildNode("moc_sky_fraction <= 0.01"),
        ChildNode("hips* = *")
    ),
    ChildNode("ID = *")
))

properties_hips_from_saada_alasky = \
        PropertyConstraint(ParentNode(
            OperandExpr.Inter,
            ChildNode("hips_service_url*=http://saada*"),
            ChildNode("hips_service_url*=http://alasky.*"))
        )

properties_hips_gaia = PropertyConstraint(
    ParentNode(OperandExpr.Subtr,
                       ParentNode(OperandExpr.Inter,
                                          ParentNode(OperandExpr.Union,
                                                             ChildNode("obs_*=*gaia*"),
                                                             ChildNode("ID=*gaia*")),
                                          ChildNode("hips_service_url=*")),
                       ChildNode("obs_*=*simu")))

"""
Combination of one spatial with a property constraint

Each tuple(spatial, property) characterizes a specific query and is tested
with regards to the true results stored in a file located in the data directory

"""

@pytest.mark.parametrize('spatial_constraint, property_constraint, data_file_id',
    [(cone_search_constraint, None, 'CONE_SEARCH'),
    (polygon_search_constraint, None, 'POLYGON_SEARCH'),
    (None, properties_ex, 'PROPERTIES_SEARCH'),
    (None, properties_hips_from_saada_alasky, 'HIPS_FROM_SAADA_AND_ALASKY'),
    (None, properties_hips_gaia, 'HIPS_GAIA')])
def test_request_results(spatial_constraint, property_constraint, data_file_id, \
get_true_request_results, get_request_results):
    """
    Compare the request result obtained with the astroquery.Mocserver API

    with the one obtained on the http://alasky.unistra.fr/MocServer/query
    """
    request_results, true_request_results = \
    get_request_results(spatial_constraint=spatial_constraint, property_constraint=property_constraint), \
    get_true_request_results(data_file_id=data_file_id)

    assert getsizeof(request_results) == getsizeof(true_request_results)
    assert request_results == true_request_results

"""
Spatial Constraints requests

We test a polygon/cone/moc search and ensure the
request param 'intersect' is correct

"""

@pytest.mark.parametrize('RA, DEC, RADIUS',
    [(10.8, 6.5, 0.5),
    (25.6, -23.2, 1.1),
    (150.6, 45.1, 1.5)])
def test_cone_search_spatial_request(RA, DEC, RADIUS, init_request):
    moc_server_constraints, moc_server_format = init_request
    center = coordinates.SkyCoord(ra=RA, dec=DEC, unit="deg")
    radius = coordinates.Angle(RADIUS, unit="deg")
    circle_sky_region = CircleSkyRegion(center, radius)

    spatial_constraint = CircleSkyRegionSpatialConstraint(circle_sky_region, intersect="overlaps")
    moc_server_constraints.spatial_constraint = spatial_constraint

    request_payload = mocserver.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)
    assert request_payload['DEC'] == str(DEC) and \
    request_payload['RA'] == str(RA) and \
    request_payload['SR'] == str(RADIUS)

@pytest.mark.parametrize('poly, poly_payload',
[(polygon1, 'Polygon 57.376 24.053 56.391 24.622 56.025 24.049 56.616 24.291'),
(polygon2, 'Polygon 58.376 24.053 53.391 25.622 56.025 22.049 54.616 27.291')])
def test_polygon_spatial_request(poly, poly_payload, init_request):
    moc_server_constraints, moc_server_format = init_request
    spatial_constraint = PolygonSkyRegionSpatialConstraint(poly, intersect="overlaps")
    moc_server_constraints.spatial_constraint = spatial_constraint

    request_payload = mocserver.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)
    assert request_payload['stc'] == poly_payload

@pytest.mark.parametrize('intersect',
['enclosed', 'overlaps', 'covers'])
def test_intersect_param(intersect, init_request):
    moc_server_constraints, moc_server_format = init_request
    center = coordinates.SkyCoord(ra=10.8, dec=6.5, unit="deg")
    radius = coordinates.Angle(1.5, unit="deg")
    circle_sky_region = CircleSkyRegion(center, radius)

    spatial_constraint = CircleSkyRegionSpatialConstraint(circle_sky_region, intersect=intersect)
    moc_server_constraints.spatial_constraint = spatial_constraint

    request_payload = mocserver.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)

    assert request_payload['intersect'] == intersect

@pytest.mark.parametrize('get_attr, get_attr_str', [(Format.id, 'id'),
(Format.record, 'record'),
(Format.number, 'number'),
(Format.moc, 'moc'),
(Format.imoc, 'imoc')])
def test_get_attribute(get_attr, get_attr_str, init_request):
    """Test if the request parameter 'get' works for a basic cone search request"""
    moc_server_constraints, moc_server_format = init_request
    moc_server_format = OutputFormat(format=get_attr)

    # Simple cone search request
    center = coordinates.SkyCoord(ra=10.8, dec=6.5, unit="deg")
    radius = coordinates.Angle(1.5, unit="deg")
    circle_sky_region = CircleSkyRegion(center, radius)

    spatial_constraint = CircleSkyRegionSpatialConstraint(circle_sky_region, intersect="overlaps")
    moc_server_constraints.spatial_constraint = spatial_constraint

    result = mocserver.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)

    assert result['get'] == get_attr_str
