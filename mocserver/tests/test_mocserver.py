# Licensed under a 3-clause BSD style license - see LICENSE.rst
import pytest
import os
import json

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
	'id' : 'cone_search.json',
	'number' : 'cone_search.json',
	'record' : 'cone_search.json',
	'moc' : 'cone_search.json',
	'imoc' : 'cone_search.json'
}

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

def data_path(filename):
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    return os.path.join(data_dir, filename)

@pytest.fixture
def init_spatial_request(getAttribute=None):
    moc_server_constraints = MOCServerConstraints()
    if getAttribute:
        moc_server_format = MOCServerResponseFormat(format=getAttribute)
    else:
        moc_server_format = MOCServerResponseFormat()
    return (moc_server_constraints, moc_server_format)

@pytest.mark.parametrize('RA, DEC, RADIUS',
    [(10.8, 6.5, 0.5),
    (25.6, -23.2, 1.1),
    (150.6, 45.1, 1.5)])
def test_cone_search_spatial_request(RA, DEC, RADIUS, init_spatial_request):
    moc_server_constraints, moc_server_format = init_spatial_request
    center = coordinates.SkyCoord(ra=RA, dec=DEC, unit="deg")
    radius = coordinates.Angle(RADIUS, unit="deg")
    circle_sky_region = CircleSkyRegion(center, radius)

    spatial_constraint = CircleSkyRegionSpatialConstraint(circle_sky_region, intersect="overlaps")
    moc_server_constraints.set_spatial_constraint(spatial_constraint)

    result = MOCServerQuery.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)
    print(result)
    assert result == {'DEC' : str(DEC),
    'RA' : str(RA),
    'SR' : str(RADIUS),
    'fmt' : "json",
    'get' : 'id',
    'intersect' : 'overlaps',
    'casesensitive' : 'true'
    }
    return result

polygon1 = PolygonSkyRegion(vertices=coordinates.SkyCoord([57.376, 56.391, 56.025, 56.616], [24.053, 24.622, 24.049, 24.291], frame="icrs", unit="deg"))
polygon2 = PolygonSkyRegion(vertices=coordinates.SkyCoord([58.376, 53.391, 56.025, 54.616], [24.053, 25.622, 22.049, 27.291], frame="icrs", unit="deg"))
@pytest.mark.parametrize('poly, poly_payload',
[(polygon1, 'Polygon 57.376 24.053 56.391 24.622 56.025 24.049 56.616 24.291'),
(polygon2, 'Polygon 58.376 24.053 53.391 25.622 56.025 22.049 54.616 27.291')])
def test_polygon_spatial_request(poly, poly_payload, init_spatial_request):
    moc_server_constraints, moc_server_format = init_spatial_request
    spatial_constraint = PolygonSkyRegionSpatialConstraint(poly, intersect="overlaps")
    moc_server_constraints.set_spatial_constraint(spatial_constraint)

    result = MOCServerQuery.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)
    print(result)
    assert result == {'stc' : poly_payload,
    'fmt' : "json",
    'get' : 'id',
    'intersect' : 'overlaps',
    'casesensitive' : 'true'
    }
    return result

@pytest.mark.parametrize('get_attr, get_attr_str', [(Format.ID, 'id'),
(Format.record, 'record'),
(Format.number, 'number'),
(Format.moc, 'moc'),
(Format.imoc, 'imoc')])
def test_get_attribute(get_attr, get_attr_str, init_spatial_request):
    moc_server_constraints, moc_server_format = init_spatial_request
    moc_server_format = MOCServerResponseFormat(format=get_attr)
    
    # Simple cone search request
    center = coordinates.SkyCoord(ra=10.8, dec=6.5, unit="deg")
    radius = coordinates.Angle(1.5, unit="deg")
    circle_sky_region = CircleSkyRegion(center, radius)

    spatial_constraint = CircleSkyRegionSpatialConstraint(circle_sky_region, intersect="overlaps")
    moc_server_constraints.set_spatial_constraint(spatial_constraint)

    result = MOCServerQuery.query_region(moc_server_constraints, moc_server_format, get_query_payload=True)

    assert result['get'] == get_attr_str
