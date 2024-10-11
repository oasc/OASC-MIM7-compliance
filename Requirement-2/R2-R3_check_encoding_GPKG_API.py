from flask import Flask, request
import geopandas as gpd
import fiona
import warnings
import os

# The warnings raised if the geopackage fails one of the first four requirements will be only raised in the first request.
# Please restart the app if you need to test more than one geopackage

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
    try:
        layers = fiona.listlayers(filepath)
    # catch when non req1 compliant
    except fiona.errors.DriverError:
        return('The file is not a conform geopackage (Requirement 1 : The first 16 bytes of a GeoPackage SHALL be the null-terminated ASCII string "SQLite format 3".)')
                        
    # Iterate over all layers
    for layer_name in layers:
        
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            
            # Load the layer into a GeoDataFrame
            try:
                data = gpd.read_file(filepath, layer=layer_name)
            except Exception as e:
                return(str(e))
        
        # Look for a warning related to Req2, 3 or 4 failure
        for warning in caught_warnings:
            # When non req2 compliant
            if "GPKG: bad application_id" in str(warning.message):
                return {'message': 'The file is not a conform geopackage (Requirement 2 : A GeoPackage SHALL contain a value of 0x47504B47 ("GPKG" in ASCII) in the "application_id" field of the SQLite database header.) Please refer to "https://www.geopackage.org/spec140/index.html".'}
            # When non req3 compliant
            elif "has GPKG application_id, but non conformant file extension" in str(warning.message):
                return {'message': 'The file is not a conform geopackage (Requirement 3 : A GeoPackage SHALL have the file extension name ".gpkg".) Please refer to "https://www.geopackage.org/spec140/index.html".'}
            # When non req4 compliant
            elif "is referenced in gpkg_contents" in str(warning.message):
                return {'message': 'The file is not a conform geopackage. ' + str(warning.message) + '. (Requirement 4 : A GeoPackage SHALL contain the data elements (tables, columns or values) and SQL constructs (views, constraints, or triggers) specified in the core of this encoding standard.) Please refer to "https://www.geopackage.org/spec140/index.html".'}
                           
        # Check if the layer contains geospatial data
        if 'geometry' in data.columns and not data['geometry'].isnull().all():
            # Extract 50 records
            data = data.head(50)
            
            # Check if identifiers are unique
            if data.index.is_unique:
                # Check if identifiers are persistent
                if data.index.is_monotonic_increasing:
                    return {'message': 'The layer ' + layer_name + ' contains geospatial data with unique and persistent identifiers.'}
                else:
                    return {'message': 'The layer ' + layer_name + ' contains geospatial data with unique but not persistent identifiers.'}
            else:
                # Check if identifiers are persistent
                if data.index.is_monotonic_increasing:
                    return {'message': 'The layer ' + layer_name + ' contains geospatial data with persistent but not unique identifiers.'}
                else:
                    return {'message': 'The layer ' + layer_name + ' contains geospatial data with neither unique nor persistent identifiers.'}
                
    return {'message': 'No layer with geospatial data found.'}
 
if __name__ == '__main__':
    app.run(debug=True)
