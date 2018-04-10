import pyvo as vo
from enum import Enum
from copy import copy


class Dataset:

    # The timeout for a tap service before the request is aborted
    tap_service_timeout = 10

    class ServiceType(Enum):
        cs = 1,
        tap = 2,
        ssa = 4,
        sia = 5

    def __init__(self, **kwargs):
        assert len(kwargs.keys()) >= 1
        self.__properties = kwargs
        self.__services = {}

        # These services are available from the properties of
        # a dataset
        self.__init_service(__class__.ServiceType.tap, vo.dal.TAPService)
        self.__init_service(__class__.ServiceType.cs, vo.dal.SCSService)
        self.__init_service(__class__.ServiceType.ssa, vo.dal.SSAService)
        self.__init_service(__class__.ServiceType.sia, vo.dal.SIAService)

    def __init_service(self, service_type, service_class):
        name_srv_property = service_type.name + '_service_url'

        id_mirror_server = 1
        while True:
            if name_srv_property not in self.__properties.keys():
                break

            new_service = service_class(self.__properties[name_srv_property])

            if service_type not in self.__services.keys():
                self.__services[service_type] = [new_service]
            else:
                self.__services[service_type].append(new_service)

            pos_url = name_srv_property.find('_url')
            name_srv_property = name_srv_property[:(pos_url+4)]

            name_srv_property += '_' + str(id_mirror_server)
            id_mirror_server = id_mirror_server + 1


    @property
    def properties(self):
        return copy(self.__properties)

    @property
    def services(self):
        return [service_type.name for service_type in self.__services.keys()]

    def search(self, service_type, **kwargs):
        """
        Definition of the search function allowing the user to perform queries on the dataset.

        :param service_type:
            Wait for a Dataset.ServiceType object specifying the type of service to query
        :param kwargs:
            The params that PyVO requires to query the services.
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

        if service_type not in self.__services.keys():
            print('The service {0:s} is not available for this dataset'.format(service_type.name))
            print('Available services are the following :\n{0}'.format(self.services))
            raise KeyError

        services_l = self.__services[service_type]

        if service_type is Dataset.ServiceType.tap:
            """ Tap services can be queried asynchronously.
             We query the first service until we get the result or
             we get a vo.dal.DALQueryError (timeout reached). 
             If we get the result, we can fetch the votable from the completed job and destroy the job.
             Otherwise we query the second service and we continue until we get a result.
             If all the services have been queried and have ended by getting an exception then
             we raise this same exception telling the user the services have been queried but have returned nothing."""
            for i in range(len(services_l)):
                try:
                    with services_l[i].submit_job(**kwargs) as job:
                        job.execution_duration = __class__.tap_service_timeout
                        job.run()

                        while True:
                            if job.phase != 'EXECUTING':
                                print(job.phase)
                                job.raise_if_error()
                                return job.fetch_result().votable
                except vo.dal.DALQueryError as dal_query_error:
                    if i == len(services_l) - 1:
                        print("All the tap services have been queried but do not respond. "
                              "Please, retry later.")
                        raise dal_query_error
        else:
            return services_l[0].search(**kwargs).votable

