from flask import Flask, request

import requests
 
app = Flask(__name__)
 
@app.route('/check_service', methods=['GET'])

def check_service():

    # 20240826_fix: if more than one parameter is in the url, following code takes into account just the first one
    # tested with  https://geoserver.epsilon-italia.it/geoserver/LU_sample/ows?service=WFS&amp;version=2.0.0&amp;request=GetCapabilities
    #url = request.args.get('url', default = '', type = None)
    # beginning_fix
    url = request.full_path
    url = url[url.index("=")+1:]
    # end_fix
 
    # Send a GET request to the service

    response = requests.get(url)

    # Check if the response is valid

    if response.status_code == 200:

        # Check if the service is WFS

        if 'WFS_Capabilities' in response.text:

            return {'message': 'The service at ' + url + ' is a valid OGC WFS service.'}

        # Check if the service is OGC API Features

        elif '/conformance' in response.text:

            conformance_url = url + '/conformance'

            conformance_response = requests.get(conformance_url)

            if conformance_response.status_code == 200:

                return {'message': 'The service at ' + url + ' is a valid OGC API Features service.'}

            else:

                return {'message': 'The service at ' + url + ' is not a valid OGC API Features service.'}

        else:

            return {'message': 'The service at ' + url + ' is not a recognized OGC service.'}

    else:

        return {'message': 'The service at ' + url + ' is not valid.'}
 
if __name__ == '__main__':

    app.run(debug=True)
    
# sample tests:
# http://127.0.0.1:5000/check_service?url=https://demo.pygeoapi.io/stable/
# curl -X GET "http://127.0.0.1:5000/check_service?url=https://demo.pygeoapi.io/stable/"
