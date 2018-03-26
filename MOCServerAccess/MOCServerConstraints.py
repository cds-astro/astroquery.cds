# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import print_function

import astropy.coordinates as coord
import urllib as ul
from astropy.io import fits
from regions import CircleSkyRegion
from regions import PolygonSkyRegion
from abc import abstractmethod, ABC

from enum import Enum

class SpatialConstraint(ABC):
    @abstractmethod
    # By default, the intersection of the region must overlaps with the MOCS in the MOCServer
    def __init__(self, intersect="overlaps"):
        assert intersect in ("overlaps", "enclosed", "covers"), "intersect parameters must have a value in ('overlaps', 'enclosed', 'covers')"

        self.intersectRegion = intersect
        self.request_payload = {
            'intersect' : self.intersectRegion
        }

    def __repr__(self):
        str = "Spatial constraint having request payload :\n{0}".format(self.request_payload)
        return str

class CircleSkyRegionSpatialConstraint(SpatialConstraint):
    def __init__(self, circleSkyRegion, intersect):
        super(CircleSkyRegionSpatialConstraint, self).__init__(intersect)
        self.circleSkyRegion = circleSkyRegion
        self.request_payload.update({
            'DEC' : circleSkyRegion.center.dec.to_string(decimal=True),
            'RA' : circleSkyRegion.center.ra.to_string(decimal=True),
            'SR' : str(circleSkyRegion.radius.value)
        })

class PolygonSkyRegionSpatialConstraint(SpatialConstraint):
    def __init__(self, polygonSkyRegion, intersect):
        super(PolygonSkyRegionSpatialConstraint, self).__init__(intersect)

        if not isinstance(polygonSkyRegion, PolygonSkyRegion):
            raise TypeError

        #test if the polygon has at least 3 vertices
        if len(polygonSkyRegion.vertices.ra) < 3:
            print("A polygon must have at least 3 vertices")
            raise AttributeError

        self.request_payload.update({
            'stc' : self._to_STC(polygonSkyRegion)    
        })
    
    def _to_STC(self, polygonSkyRegion):
        polygonSTC = "Polygon"
        for i in range(len(polygonSkyRegion.vertices.ra)):
            polygonSTC += " " + polygonSkyRegion.vertices.ra[i].to_string(decimal=True) + " " + polygonSkyRegion.vertices.dec[i].to_string(decimal=True)
        print(polygonSTC)
        return polygonSTC


class PropertiesConstraint(object):
    def __init__(self, propertiesExpr):
        if not isinstance(propertiesExpr, PropertiesExpr):
            raise TypeError

        self.propertiesExpr = propertiesExpr
        self.computePayload()

    def computePayload(self):
        self.request_payload = {'expr' : self.propertiesExpr.eval()}

    def __repr__(self):
        str = "Properties constraints' request payload :\n{0}".format(self.request_payload)
        return str

class OperandExpr(Enum):
    Inter = 1,
    Union = 2,
    Subtr = 3

class PropertiesExpr(ABC):
    @abstractmethod
    def eval(self):
        pass

class PropertiesUniqExpr(PropertiesExpr):
    def __init__(self, condition):
        assert condition is not None
        self.condition = condition

    def eval(self):
        return str(self.condition)

class PropertiesDualExpr(PropertiesExpr):
    def __init__(self):
        self.exprLeft = None
        self.exprRight = None
        self.operand = None

    def addChild(self, operand, exprLeft, exprRight):
        if not isinstance(exprRight, PropertiesExpr) or not isinstance(exprLeft, PropertiesExpr):
            raise TypeError

        if operand not in (OperandExpr.Inter, OperandExpr.Union, OperandExpr.Subtr):
            raise TypeError

        self.exprLeft = exprLeft
        self.exprRight = exprRight
        self.operand = operand

    def eval(self):
        if self.operand is None:
            raise AttributeError
        leftExprString = self.exprLeft.eval()
        rightExprString = self.exprRight.eval()
       
        operandStr = " !& "
        if self.operand is OperandExpr.Inter:
            operandStr = " && "
        elif self.operand is OperandExpr.Union:
            operandStr = " || "

        if isinstance(self.exprLeft, PropertiesDualExpr):
            leftExprString = '(' + leftExprString + ')'
        if isinstance(self.exprRight, PropertiesDualExpr):
            rightExprString = '(' + rightExprString + ')'
        return leftExprString + operandStr + rightExprString         
 
class MOCServerConstraints(object):
    def __init__(self):
        self.spatialConstraint = None
        self.propertiesConstraint = None

    def setSpatialConstraint(self, spatialConstraint):
        self.spatialConstraint = spatialConstraint
   
    def setPropertiesConstraint(self, propertiesConstraint):
        self.propertiesConstraint = propertiesConstraint
  
    # get the union of the payloads from the spatial and properties constraints 
    def getRequestPayload(self):
        request_payload = {}
        if self.spatialConstraint:
            request_payload.update(self.spatialConstraint.request_payload)
        if self.propertiesConstraint:
            request_payload.update(self.propertiesConstraint.request_payload)
        return request_payload 
