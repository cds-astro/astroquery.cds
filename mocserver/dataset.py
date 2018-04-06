import pyvo as vo
from enum import Enum
from copy import copy


class Dataset:
    class ServiceType(Enum):
        SCS = 1,
        TAP = 2,
        SSA = 4,
        SIA = 5,
        SIA2 = 6

    def __init__(self, **kwargs):
        assert len(kwargs.keys()) >= 1
        self.__properties = kwargs
        self.__services = {}

        # These services are available from the properties of
        # a dataset
        if 'cs_service_url' in self.__properties.keys():
            self.__services[__class__.ServiceType.SCS] =\
                vo.dal.SCSService(self.__properties['cs_service_url'])
        if 'tap_service_url' in self.__properties.keys():
            self.__services[__class__.ServiceType.TAP] =\
                vo.dal.TAPService(self.__properties['tap_service_url'])
        if 'ssa_service_url' in self.__properties.keys():
            self.__services[__class__.ServiceType.SSA] = \
                vo.dal.SSAService(self.__properties['ssa_service_url'])
        if 'sia_service_url' in self.__properties.keys():
            self.__services[__class__.ServiceType.SIA] = \
                vo.dal.SIAService(self.__properties['sia_service_url'])
        if 'sia2_service_url' in self.__properties.keys():
            self.__services[__class__.ServiceType.SIA2] = \
                vo.dal.SIAService(self.__properties['sia2_service_url'])

    @property
    def properties(self):
        return copy(self.__properties)

    @property
    def services(self):
        return [service_type.name for service_type in self.__services.keys()]

    def search(self, service_type, **kwargs):
        """
        Definition of the search function that allows the user to perform queries on the dataset.

        :param service_type:
            Wait for a Dataset.ServiceType object specifying the type of service to query
        :param kwargs:
            The params that pyvo requires to query the services.
            These depend on the queried service :
            - a simple cone search requires a pos and radius params expressed in deg
            - a tap search requires a SQL query
            - a ssa (simple spectral access) search requires a pos and a diameter params.
            SSA searches can be extended with two other params : a time and a band such as
            Dataset.search(service_type=Dataset.ServiceType.SSA,
                pos=pos, diameter=size,
                time=time, band=Quantity((1e-13, 1e-12), unit="meter")
            )
            - sia and sia2 searches require a pos and a size params where size defines a
            rectangular region around pos

            For more explanation about what params to use with a service, see the pyvo
            doc available at : http://pyvo.readthedocs.io/en/latest/dal/index.html
        :return:
            a votable containing all the sources from the dataset that match the query

        """

        if not isinstance(service_type, Dataset.ServiceType):
            print("Service {0} not found".format(service_type))
            raise ValueError
        print(kwargs)
        if service_type in self.__services.keys():
            return self.__services[service_type].search(**kwargs).votable
        else:
            print('The service {0:s} is not available for this dataset'.format(service_type.name))
            print('Available services are the following :\n{0}'.format(self.services))
            raise ValueError
