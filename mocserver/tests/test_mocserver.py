# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import os
import json
from sys import getsizeof

from mocserver.core import MOCServerQuery, MOCServerQueryClass

from mocserver.MOCServerConstraints import MOCServerConstraints
from mocserver.MOCServerConstraints import CircleSkyRegionSpatialConstraint
from mocserver.MOCServerConstraints import PolygonSkyRegionSpatialConstraint

from mocserver.MOCServerResponseFormat import MOCServerResponseFormat, Format

from astroquery.utils.testing_tools import MockResponse
from astroquery.utils import commons

from astropy import coordinates
from regions import CircleSkyRegion, PolygonSkyRegion

DATA_FILES = {
	'CONE_SEARCH' : 'cone_search.json',
}

@pytest.fixture
def patch_get(request):
    try:
        mp = request.getfixturevalue("monkeypatch")
    except AttributeError:  # pytest < 3
        mp = request.getfuncargvalue("monkeypatch")
    mp.setattr(MOCServerQuery, '_request', get_mockreturn)
    return mp

@pytest.fixture
def get_request_results(init_request):
    """Perform the request using the astroquery.MocServer  API"""

    def process_query(spatial_constraint=None, property_constraint=None):
        assert spatial_constraint or property_constraint
        moc_server_constraints, moc_server_format = init_request
        if spatial_constraint:
            moc_server_constraints.set_spatial_constraint(spatial_constraint)

        if property_constraint:
            moc_server_constraints.set_properties_constraint(property_constraint)

        request_result = MOCServerQuery.query_region(moc_server_constraints, moc_server_format)
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

def test_request_results(get_true_request_results, get_request_results):
    """
    Compare the request result obtained with the astroquery.Mocserver API

    with the one obtained on the http://alasky.unistra.fr/MocServer/query
    """


    center = coordinates.SkyCoord(ra=10.8, dec=6.5, unit="deg")
    radius = coordinates.Angle(1.5, unit="deg")
    circle_sky_region = CircleSkyRegion(center, radius)

    spatial_constraint = CircleSkyRegionSpatialConstraint(circle_sky_region, intersect='overlaps')
    request_results, true_request_results = get_request_results(spatial_constraint=spatial_constraint), \
    get_true_request_results(data_file_id='CONE_SEARCH')
    assert getsizeof(request_results) == getsizeof(true_request_results)
    assert request_results == true_request_results

def get_mockreturn(method, url, params=None, timeout=10, **kwargs):
    filename = data_path(DATA_FILES[params['get']])
    content = open(filename, 'rb').read()
    return MockResponse(content)

def data_path(filename):
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    return os.path.join(data_dir, filename)

@pytest.fixture
def init_request():
    moc_server_constraints = MOCServerConstraints()
    moc_server_format = MOCServerResponseFormat()
    return (moc_server_constraints, moc_server_format)

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
    moc_server_constraints.set_spatial_constraint(spatial_constraint)

    request_payload = MOCServerQuery.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)
    assert request_payload['DEC'] == str(DEC) and \
    request_payload['RA'] == str(RA) and \
    request_payload['SR'] == str(RADIUS)

polygon1 = PolygonSkyRegion(vertices=coordinates.SkyCoord([57.376, 56.391, 56.025, 56.616], [24.053, 24.622, 24.049, 24.291], frame="icrs", unit="deg"))
polygon2 = PolygonSkyRegion(vertices=coordinates.SkyCoord([58.376, 53.391, 56.025, 54.616], [24.053, 25.622, 22.049, 27.291], frame="icrs", unit="deg"))
@pytest.mark.parametrize('poly, poly_payload',
[(polygon1, 'Polygon 57.376 24.053 56.391 24.622 56.025 24.049 56.616 24.291'),
(polygon2, 'Polygon 58.376 24.053 53.391 25.622 56.025 22.049 54.616 27.291')])
def test_polygon_spatial_request(poly, poly_payload, init_request):
    moc_server_constraints, moc_server_format = init_request
    spatial_constraint = PolygonSkyRegionSpatialConstraint(poly, intersect="overlaps")
    moc_server_constraints.set_spatial_constraint(spatial_constraint)

    request_payload = MOCServerQuery.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)
    assert request_payload['stc'] == poly_payload

@pytest.mark.parametrize('intersect',
['enclosed', 'overlaps', 'covers'])
def test_intersect_param(intersect, init_request):
    moc_server_constraints, moc_server_format = init_request
    center = coordinates.SkyCoord(ra=10.8, dec=6.5, unit="deg")
    radius = coordinates.Angle(1.5, unit="deg")
    circle_sky_region = CircleSkyRegion(center, radius)

    spatial_constraint = CircleSkyRegionSpatialConstraint(circle_sky_region, intersect=intersect)
    moc_server_constraints.set_spatial_constraint(spatial_constraint)

    request_payload = MOCServerQuery.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)

    assert request_payload['intersect'] == intersect
"""
Properties Constraints requests

We check for several properties expressions if the returned payloads are correct

"""

@pytest.mark.parametrize('get_attr, get_attr_str', [(Format.ID, 'id'),
(Format.record, 'record'),
(Format.number, 'number'),
(Format.moc, 'moc'),
(Format.imoc, 'imoc')])
def test_get_attribute(get_attr, get_attr_str, init_request):
    """Test if the request parameter 'get' works for a basic cone search request"""
    moc_server_constraints, moc_server_format = init_request
    moc_server_format = MOCServerResponseFormat(format=get_attr)

    # Simple cone search request
    center = coordinates.SkyCoord(ra=10.8, dec=6.5, unit="deg")
    radius = coordinates.Angle(1.5, unit="deg")
    circle_sky_region = CircleSkyRegion(center, radius)

    spatial_constraint = CircleSkyRegionSpatialConstraint(circle_sky_region, intersect="overlaps")
    moc_server_constraints.set_spatial_constraint(spatial_constraint)

    result = MOCServerQuery.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)

    assert result['get'] == get_attr_str


