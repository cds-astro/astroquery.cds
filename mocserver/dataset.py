import pyvo as vo
from enum import Enum
from copy import copy


class Dataset:
    class ServiceType(Enum):
        SCS = 1,
        TAP = 2,
        HIPS = 3,
        SSA = 4,
        SIA = 5,
        SIA2 = 6

    def __init__(self, **kwargs):
        assert len(kwargs.keys()) >= 1
        self.__properties = kwargs
        self.__services = {}

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
        if 'hips_service_url' in self.__properties.keys():
            self.__services[__class__.ServiceType.HIPS] = None

    @property
    def properties(self):
        return copy(self.__properties)

    @property
    def services(self):
        return [service_type.name for service_type in self.__services.keys()]

    def search(self, service_type, **kwargs):
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
