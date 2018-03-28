#!/usr/bin/env python
# -*- coding: utf-8 -*

# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import print_function

import astropy.coordinates as coord
from regions import CircleSkyRegion
from regions import PolygonSkyRegion
from mocpy import MOC

from abc import abstractmethod, ABC

from os import remove

class MOCServerConstraints(object):
    def __init__(self):
        self.spatial_constraint = None
        self.properties_constraint = None

    def set_spatial_constraint(self, spatial_constraint):
        self.spatial_constraint = spatial_constraint

    def set_properties_constraint(self, properties_constraint):
        self.properties_constraint = properties_constraint

    # get the union of the payloads from the spatial and properties constraints 
    def get_request_payload(self):
        request_payload = {}
        if self.spatial_constraint:
            request_payload.update(self.spatial_constraint.request_payload)
        if self.properties_constraint:
            request_payload.update(self.properties_constraint.request_payload)
        return request_payload

class SpatialConstraint(ABC):
	"""
	This abstract class provides an interface for spatial constraints

	The user can define a spatial constraint when querying
	the MOCServer. This class is an interface for different
	possible spatial constraints. Those are defined below
	such as CircleSkyRegionSpatialConstraint and
	PolygonSkyRegionSpatialConstraint
	"""

	@abstractmethod
	def __init__(self, intersect="overlaps"):
		"""
		SpatialConstraint's constructor

		Parameters:
		----
		intersect : string
			specify if the defined region must overlaps,
			covers or encloses the mocs from each dataset
			stored in the MOCServer

		Exceptions:
		----
		ValueError :
			- intersect must have its value in (overlaps, enclosed, covers)

		"""

		if intersect not in ("overlaps", "enclosed", "covers"):
			print("intersect parameters must have a value in ('overlaps', 'enclosed', 'covers')")
			raise ValueError

		self.intersectRegion = intersect
		self.request_payload = {'intersect' : self.intersectRegion}

	def __repr__(self):
		str = "Spatial constraint having request payload :\n{0}".format(self.request_payload)
		return str

class CircleSkyRegionSpatialConstraint(SpatialConstraint):
	"""
	Class defining a circle sky region

	Inherits from SpatialConstraint class
	and implements the cone search method

	"""

	def __init__(self, circleSkyRegion, intersect):
		"""
		CircleSkyRegionSpatialConstraint's constructor

		Parameters:
		----
		circleSkyRegion : regions.CircleSkyRegion
			defines a circle of center(ra, dec) and radius given
			specifying the region in which one can ask for the datasets
			intersecting it

		Exceptions:
		----
		TypeError:
			- circleSkyRegion must be of type regions.CircleSkyRegion

		"""

		if not isinstance(circleSkyRegion, CircleSkyRegion):
			raise TypeError

		super(CircleSkyRegionSpatialConstraint, self).__init__(intersect)
		self.circleSkyRegion = circleSkyRegion
		self.request_payload.update({
            'DEC' : circleSkyRegion.center.dec.to_string(decimal=True),
            'RA' : circleSkyRegion.center.ra.to_string(decimal=True),
            'SR' : str(circleSkyRegion.radius.value)
		})

class PolygonSkyRegionSpatialConstraint(SpatialConstraint):
    """
	Class defining a spatial polygon region

	Inherits from SpatialConstraint class
	and gives the user the possibility to defines
	a polygon as the region of interest for finding
	all the datasets intersecting it

	"""

    def __init__(self, polygonSkyRegion, intersect):
        """
		PolygonSkyRegionSpatialConstraint's constructor

		Parameters:
		----
		polygonSkyRegion : regions.PolygonSkyRegion
			defines a Polygon expressed as a list of vertices
			of type regions.SkyCoord

		Exceptions:
		----
		TypeError :
			- polygonSkyRegion must be of type regions.PolygonSkyRegion

		AttributeError :
			- the SkyCoord referring to the vertices of the polygon
			needs to have at least 3 vertices otherwise it is
			not a polygon but a line or a single vertex

		"""

        if not isinstance(polygonSkyRegion, PolygonSkyRegion):
            raise TypeError

        super(PolygonSkyRegionSpatialConstraint, self).__init__(intersect)

        #test if the polygon has at least 3 vertices
        if len(polygonSkyRegion.vertices.ra) < 3:
            print("A polygon must have at least 3 vertices")
            raise AttributeError

        self.request_payload.update({'stc' : self._to_stc(polygonSkyRegion)})

    def _to_stc(self, polygonSkyRegion):
        """
		Convert a regions.PolygonSkyRegion instance to a string

		MOCServer requests for a polygon expressed in a STC format
		i.e. a string beginning with 'Polygon' and iterating through
		all the vertices' ra and dec

		"""
        polygonSTC = "Polygon"
        for i in range(len(polygonSkyRegion.vertices.ra)):
            polygonSTC += " " + polygonSkyRegion.vertices.ra[i].to_string(decimal=True) + " " + polygonSkyRegion.vertices.dec[i].to_string(decimal=True)
        print(polygonSTC)
        return polygonSTC

class MocSpatialConstraint(SpatialConstraint):

    def __init__(self, moc, intersect):
        if not isinstance(moc, MOC):
            raise TypeError

        super(MocSpatialConstraint, self).__init__(intersect)
        moc.write('tmp_moc.json', format='json')

        with open('tmp_moc.json', 'r') as f_in:
            content = f_in.read()

        remove('tmp_moc.json')
        self.request_payload.update({'moc' : content})
        print(self.request_payload)

