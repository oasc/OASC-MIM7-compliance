from flask import Flask, request
import geopandas as gpd
import fiona
import os
 
app = Flask(__name__)
 
@app.route('/check_geopackage', methods=['POST'])
def check_geopackage_api():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return {'message': 'No file part in the request.'}
 
    file = request.files['file']
 
    # If the user does not select a file, the browser might submit an empty file part without a filename
    if file.filename == '':
        return {'message': 'No file selected.'}
 
    # Save the file to a temporary location
    filepath = os.path.join('/tmp', file.filename)
    file.save(filepath)
 
    # List all layers in the GeoPackage
    layers = fiona.listlayers(filepath)
 
    # Iterate over all layers
    for layer_name in layers:
        # Load the layer into a GeoDataFrame
        data = gpd.read_file(filepath, layer=layer_name)
 
        # Check if the layer contains geospatial data
        if 'geometry' in data.columns and not data['geometry'].isnull().all():
            # Extract 50 records
            data = data.head(50)
 
            # Check if identifiers are unique and persistent
            if data.index.is_unique and data.index.is_monotonic:
                return {'message': 'The layer ' + layer_name + ' contains geospatial data with unique and persistent identifiers.'}
            else:
                return {'message': 'The layer ' + layer_name + ' contains geospatial data, but identifiers are not unique and/or persistent.'}
 
    return {'message': 'No layer with geospatial data found.'}
 
if __name__ == '__main__':
    app.run(debug=True)
