#!/usr/bin/env python
# -*- coding: utf-8 -*

# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import print_function

# put all imports organized as shown below
# 1. standard library imports

# 2. third party imports
import astropy.units as u
import astropy.coordinates as coord
import astropy.io.votable as votable
from astropy.table import Table
from astropy.io import fits
from regions import CircleSkyRegion
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
from .MOCServerConstraints import MOCServerConstraints
from .MOCServerResponseFormat import MOCServerResponseFormat

# export all the public classes and methods
__all__ = ['MOCServerQuery', 'MOCServerQueryClass']

# declare global variables and constants if any


# Now begin your main class
# should be decorated with the async_to_sync imported previously
@async_to_sync
class MOCServerQueryClass(BaseQuery):

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

    def query_object_async(self, object_name, get_query_payload=False,
        cache=True):
        """
        This method is for services that can parse object names. Otherwise
        use :meth:`astroquery.template_module.TemplateClass.query_region`.
        Put a brief description of what the class does here.

        Parameters
        ----------
        object_name : str
            name of the identifier to query.
        get_query_payload : bool, optional
            This should default to False. When set to `True` the method
            should return the HTTP request parameters as a dict.

        Returns
        -------
        response : `requests.Response`
            The HTTP response returned from the service.
            All async methods should return the raw HTTP response.

        Examples
        --------
        While this section is optional you may put in some examples that
        show how to use the method. The examples are written similar to
        standard doctests in python.
            """
    # the async method should typically have the following steps:
    # 1. First construct the dictionary of the HTTP request params.
    # 2. If get_query_payload is `True` then simply return this dict.
    # 3. Else make the actual HTTP request and return the corresponding
    #    HTTP response
    # All HTTP requests are made via the `BaseQuery._request` method. This
    # use a generic HTTP request method internally, similar to
    # `requests.Session.request` of the Python Requests library, but
    # with added caching-related tools.

	# See below for an example:

	# first initialize the dictionary of HTTP request parameters
        request_payload = dict()

	# Now fill up the dictionary. Here the dictionary key should match
	# the exact parameter name as expected by the remote server. The
	# corresponding dict value should also be in the same format as
	# expected by the server. Additional parsing of the user passed
	# value may be required to get it in the right units or format.
	# All this parsing may be done in a separate private `_args_to_payload`
	# method for cleaner code.

	# similarly fill up the rest of the dict ...
        if get_query_payload:
            return request_payload
	# BaseQuery classes come with a _request method that includes a
	# built-in caching system
        response = self._request('GET', self.URL, params=request_payload, timeout=self.TIMEOUT)

        return response

    # For services that can query coordinates, use the query_region method.
    # The pattern is similar to the query_object method. The query_region
    # method also has a 'radius' keyword for specifying the radius around
    # the coordinates in which to search. If the region is a box, then
    # the keywords 'width' and 'height' should be used instead. The coordinates
    # may be accepted as an `astropy.coordinates` object or as a string, which
    # may be further parsed.

    # similarly we write a query_region_async method that makes the
    # actual HTTP request and returns the HTTP response
    def query_region(self, constraints, responseFormat=MOCServerResponseFormat(), get_query_payload=False):
        response = self.query_region_async(constraints, responseFormat, get_query_payload)
        if get_query_payload:
            return response

        #TODO MOCServerResponse
        print(response)
        import pdb; pdb.set_trace()
        result = self._parse_result_region(response)
        return result

    def query_region_async(self, constraints, responseFormat, get_query_payload, cache=True):
        """
        Queries a region around the specified coordinates.

        Parameters
        ----------
        coordinates : str or `astropy.coordinates`.
            coordinates around which to query
        radius : str or `astropy.units.Quantity`.
            the radius of the cone search
        intersect : determines if the region must overlap (default),
            enclosed, or cover the matching collection coverages
        get_query_payload : bool, optional
            Just return the dict of HTTP request parameters.
        verbose : bool, optional
            Display VOTable warnings or not.

        Returns
        -------
        response : `requests.Response`
        The HTTP response returned from the service.
        All async methods should return the raw HTTP response.
        """
        request_payload = {}
        if not isinstance(constraints, MOCServerConstraints):
            print("Invalid constraints. Must be of MOCServerConstraints type")
            raise TypeError
        else:
            request_payload = constraints.get_request_payload()

        if not isinstance(responseFormat, MOCServerResponseFormat):
            print("Invalid response format. Must be of MOCServerResponseFormat type")
            raise TypeError
        else:
            request_payload.update(responseFormat.getRequestPayload())

        if get_query_payload:
            return request_payload

        print('Final Request payload before requesting to alasky')
        pprint(request_payload)
        response = self._request('GET', url=self.URL, params=request_payload, timeout=self.TIMEOUT, cache=cache)
        return response

    def _parse_result_region(self, response, verbose=False):
        # if verbose is False then suppress any VOTable related warnings
        if not verbose:
            commons.suppress_vo_warnings()
	# try to parse the result into an astropy.Table, else
	# return the raw result with an informative error message.
        return response.json()

    # the methods above call the private _parse_result method.
    # This should parse the raw HTTP response and return it as
    # an `astropy.table.Table`. Below is the skeleton:

    """
    def _parse_result(self, response, get, verbose=False):
	# if verbose is False then suppress any VOTable related warnings
	if not verbose:
	    commons.suppress_vo_warnings()
	# try to parse the result into an astropy.Table, else
	# return the raw result with an informative error message.
	results = response.json()
	res = None
	try:
	    # do something with regex to get the result into
	    # astropy.Table form. return the Table.
	    if get == 'ID':
		res = Table([results], names=('a'))
	    elif get == 'number':
		res = int(results["number"])
	    elif get == 'record':
		properties_all_s = set()
		for record_d in results:
		    properties_all_s = properties_all_s | set(record_d.keys())
		ordered_columns_t = tuple(sorted(properties_all_s))
		rows_l = [] 
		for record_d in results:
		    full_record_d = {propertie: None for propertie in properties_all_s}
		    for key, value in record_d.items():
			full_record_d.update({key : str(value)})

		    row_l = []
		    for k in ordered_columns_t:
			row_l.append(full_record_d[k])
		    rows_l.append(tuple(row_l))
		#import pprint; pprint.pprint(rows_l)
		res = Table(rows=rows_l, names=ordered_columns_t)
	    elif get == 'moc' or get == 'imoc':
		res = results;

	except ValueError:
	    # catch common errors here, but never use bare excepts
	    # return raw result/ handle in some way
	    pass
	return res
    """

# the default tool for users to interact with is an instance of the Class
MOCServerQuery = MOCServerQueryClass()

# once your class is done, tests should be written
# See ./tests for examples on this

# Next you should write the docs in astroquery/docs/module_name
# using Sphinx.
