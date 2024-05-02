import requests
 
def check_service(url):

    # Send a GET request to the service

    response = requests.get(url)

    # Check if the response is valid

    if response.status_code == 200:

        # Check if the service is WFS

        if 'WFS_Capabilities' in response.text:

            print('The service at ' + url + ' is a valid OGC WFS service.')

        # Check if the service is OGC API Features

        elif '/conformance' in response.text:

            conformance_url = url + '/conformance'

            conformance_response = requests.get(conformance_url)

            if conformance_response.status_code == 200:

                print('The service at ' + url + ' is a valid OGC API Features service.')

            else:

                print('The service at ' + url + ' is not a valid OGC API Features service.')

        else:

            print('The service at ' + url + ' is not a recognized OGC service.')

    else:

        print('The service at ' + url + ' is not valid.')


# Test the function with your service URLs

check_service('https://geoserver.epsilon-italia.it/geoserver/LU_sample/ows?service=WFS&amp;version=2.0.0&amp;request=GetCapabilities')

check_service('https://demo.pygeoapi.io/stable/')

check_service('https://www.google.com')