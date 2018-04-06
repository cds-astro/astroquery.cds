#!/usr/bin/env python
# -*- coding: utf-8 -*

# Licensed under a 3-clause BSD style license - see LICENSE.rst

# put all imports organized as shown below
# 1. standard library imports

# 2. third party imports
from pprint import pprint

# 3. local imports - use relative imports
# commonly required local imports shown below as example
# all Query classes should inherit from BaseQuery.
from astroquery.query import BaseQuery
# has common functions required by most modules
from astroquery.utils import commons
# async_to_sync generates the relevant query tools from _async methods
from astroquery.utils import async_to_sync
# import configurable items declared in __init__.py
from . import conf
# import MOCServerConstraints and MOCServerResults
from .constraints import Constraints
from .output_format import OutputFormat
from .dataset import Dataset

# export all the public classes and methods
__all__ = ['mocserver', 'MocserverClass']
# declare global variables and constants if any

# Now begin your main class
# should be decorated with the async_to_sync imported previously


@async_to_sync
class MocserverClass(BaseQuery):
    """
    Not all the methods below are necessary but these cover most of the common
    cases, new methods may be added if necessary, follow the guidelines at
    <http://astroquery.readthedocs.io/en/latest/api.html>
    """
    # use the Configuration Items imported from __init__.py to set the URL,
    # TIMEOUT, etc.
    URL = conf.server
    TIMEOUT = conf.timeout

    # all query methods are implemented with an "async" method that handles
    # making the actual HTTP request and returns the raw HTTP response, which
    # should be parsed by a separate _parse_result method.   The query_object
    # method is created by async_to_sync automatically.  It would look like
    # this:
    """
    def query_object(object_name, get_query_payload=False)
    response = self.query_object_async(object_name, get_query_payload=get_query_payload)
    if get_query_payload:
        return response
    result = self._parse_result(response, verbose=verbose)
    return result
    """

    # For services that can query coordinates, use the query_region method.
    # The pattern is similar to the query_object method. The query_region
    # method also has a 'radius' keyword for specifying the radius around
    # the coordinates in which to search. If the region is a box, then
    # the keywords 'width' and 'height' should be used instead. The coordinates
    # may be accepted as an `astropy.coordinates` object or as a string, which
    # may be further parsed.

    # similarly we write a query_region_async method that makes the
    # actual HTTP request and returns the HTTP response
    def query_region(self, constraints, output_format=OutputFormat(), get_query_payload=False):
        response = self.query_region_async(constraints, output_format, get_query_payload)

        if get_query_payload:
            return response

        result = MocserverClass.__parse_result_region(response, output_format)

        # Once the result is parsed we create Dataset objects from it
        if output_format.format is OutputFormat.Type.record:
            return dict([d['ID'], Dataset(**dict([k, MocserverClass.__remove_duplicate(d.get(k))] for k in (d.keys() - set('ID'))))] for d in result)

        return result

    @staticmethod
    def __remove_duplicate(value_l):
        if isinstance(value_l, list):
            value_l = list(set(value_l))
            if len(value_l) == 1:
                return value_l[0]

        return value_l

    def query_region_async(self, constraints, output_format, get_query_payload, cache=True):
        """
        Queries a region around the specified coordinates.

        Parameters
        ----------
        constraints : Constraints
            Contains all the spatial and properties constraints for the query
        output_format : OutputFormat
            Contains the format of return. By default the request will return python compatible
            objects such as lists and dicts describing the dataset found with respect to the constraints
            mentioned before
        get_query_payload : bool, optional
            Just return the dict of HTTP request parameters.
        cache : bool

        Returns
        -------
        response : `requests.Response`
        The HTTP response returned from the service.
        All async methods should return the raw HTTP response.
        """
        request_payload = dict()
        if not isinstance(constraints, Constraints):
            print("Invalid constraints. Must be of MOCServerConstraints type")
            raise TypeError
        else:
            request_payload.update(constraints.payload)

        if not isinstance(output_format, OutputFormat):
            print("Invalid response format. Must be of MOCServerResponseFormat type")
            raise TypeError
        else:
            request_payload.update(output_format.request_payload)

        if get_query_payload:
            return request_payload

        print('Final Request payload before requesting to alasky')
        pprint(request_payload)

        if 'moc' in request_payload:
            filename = request_payload['moc']
            with open(filename, 'rb') as f:
                request_payload.pop('moc')

                response = self._request('GET', url=self.URL, params=request_payload, timeout=self.TIMEOUT, cache=False, files={'moc': f})
        else:
            response = self._request('GET', url=self.URL, params=request_payload, timeout=self.TIMEOUT, cache=cache)

        return response

    @staticmethod
    def __parse_to_float(value):
        try:
            return float(value)
        except Exception:
            return value

    @staticmethod
    def __parse_result_region(response, output_format, verbose=False):
        # if verbose is False then suppress any VOTable related warnings
        if not verbose:
            commons.suppress_vo_warnings()
        # try to parse the result into an astropy.Table, else
        # return the raw result with an informative error message.

        r = response.json()
        parsed_r = None
        if output_format.format is OutputFormat.Type.record:
            parsed_r = [dict([k, MocserverClass.__parse_to_float(v)] for k, v in di.items()) for di in r]
        elif output_format.format is OutputFormat.Type.number:
            parsed_r = dict(number=int(r['number']))
        else:
            parsed_r = r

        return parsed_r

    # the methods above call the private _parse_result method.
    # This should parse the raw HTTP response and return it as
    # an `astropy.table.Table`. Below is the skeleton:


# the default tool for users to interact with is an instance of the Class
mocserver = MocserverClass()

# once your class is done, tests should be written
# See ./tests for examples on this

# Next you should write the docs in astroquery/docs/module_name
# using Sphinx.