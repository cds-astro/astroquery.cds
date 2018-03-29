#!/usr/bin/env python
# -*- coding: utf-8 -*

# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import print_function

import astropy.coordinates as coord
import urllib as ul
from astropy.io import fits
from regions import CircleSkyRegion
from abc import abstractmethod, ABC

from enum import Enum

from sys import maxsize

class Format(Enum):
    id = 1,
    record = 2,
    number = 3,
    moc = 4,
    imoc = 5

class OutputFormat(object):
    def __init__(self, format=Format.id, field_l=[], moc_order=maxsize, case_sensitive=True, maxrec=None):
        if not isinstance(format, Format):
            print("The response format must have value in the ResponseFormat enum")
            raise TypeError

        if not isinstance(field_l, list) or not isinstance(case_sensitive, bool):
            raise TypeError

        self.request_payload = {
            "fmt" : "json",
            "casesensitive" : str(case_sensitive).lower()
        }

        if maxrec and not isinstance(maxrec, int):
            raise TypeError

        if format is Format.id:
            self.request_payload.update({'get' : 'id'})
        elif format is Format.record:
            self.request_payload.update({'get' : 'record'})

        # parse fields
            if field_l:
                fields_str = str(field_l[0])
                for field in field_l[1:]:
                    if not isinstance(field, str):
                        raise TypeError
                    fields_str += ', '
                    fields_str += field

                self.request_payload.update({
                    "fields" : fields_str
                })
        elif format is Format.number:
            self.request_payload.update({'get' : 'number'})
        elif format in (Format.moc, Format.imoc):
            if moc_order != maxsize:
                self.request_payload.update({
                    "order" : moc_order
                })
            else:
                self.request_payload.update({
                    "order" : "max"
                })


            if format is Format.imoc:
                self.request_payload.update({'get' : 'imoc'})
            else:
                self.request_payload.update({'get' : 'moc'})

        if maxrec:
            self.request_payload.update({'MAXREC' : str(maxrec)})

    def get_request_payload(self):
        return self.request_payload
