import os

def get_package_data():
    paths_test = [os.path.join('data', '*.json')]

    return {'mocserver.tests': paths_test}
