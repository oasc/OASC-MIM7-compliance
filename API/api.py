from flask import Flask, request, jsonify
from flasgger import Swagger
import requests
import geopandas as gpd
import fiona
import os
from werkzeug.utils import secure_filename
import logging
from datetime import datetime

# Set up loggers
request_logger = logging.getLogger('request')
request_logger.setLevel(logging.INFO)
request_handler = logging.FileHandler('request.log')
request_logger.addHandler(request_handler)

response_logger = logging.getLogger('response')
response_logger.setLevel(logging.INFO)
response_handler = logging.FileHandler('response.log')
response_logger.addHandler(response_handler)

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/r1', methods=['GET'])
def check_service():
    """
    Check Service
    ---
    parameters:
      - name: url
        in: query
        type: string
        required: true
        description: The url of the service to check
    responses:
      200:
        description: Service status
    """
    url = request.args.get('url', default = '', type = str)
    wfs_url = url + "?SERVICE=WFS&REQUEST=GetCapabilities&VERSION=2.0.0"
    request_logger.info(f"{datetime.now()}: Checking WFS: {wfs_url}")
    wfs_response = requests.get(wfs_url)
    response_logger.info(f"{datetime.now()}: Response: {wfs_response.text}")
    if wfs_response.status_code == 200 and 'WFS_Capabilities' in wfs_response.text:
        return {'message': 'The service at ' + url + ' is a valid MIM-7 OGC WFS service.'}
    
    request_logger.info(f"{datetime.now()}: Checking OGC API: {url}")
    ogc_response = requests.get(url)
    response_logger.info(f"{datetime.now()}: Response: {ogc_response.text}")
    if ogc_response.status_code == 200:
        conformance_url = url + '/conformance'
        conformance_response = requests.get(conformance_url)
        if conformance_response.status_code == 200:
            return {'message': 'The service at ' + url + ' is a valid MIM-7 OGC API Features service.'}
        else:
            return {'message': 'The service at ' + url + ' is not a valid MIM-7 standards-based web service interface.'}

    else:
        return {'message': 'The service at ' + url + ' is not a valid MIM-7 standards-based web service interface.'}

@app.route('/r2', methods=['POST'])
def check_geopackage():
    """
    Check GeoPackage
    ---
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: The file to check
    responses:
      200:
        description: File check result
    """
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join('/tmp', filename)
    file.save(filepath)
    result = check_geopackage_func(filepath)
    os.remove(filepath)
    return jsonify(result)

def check_geopackage_func(filename):
    layers = fiona.listlayers(filename)
    for layer_name in layers:
        data = gpd.read_file(filename, layer=layer_name)
        if 'geometry' in data.columns and not data['geometry'].isnull().all():
            data = data.head(50)
            result = {
                'layer_name': layer_name,
                'contains_geospatial_data': True,
                'identifiers_unique': data.index.is_unique,
                'identifiers_persistent': data.index.is_monotonic_increasing
            }
            return result
    return {'message': 'No geospatial data found in any layer'}

if __name__ == '__main__':
    app.run(host='localhost', debug=True)