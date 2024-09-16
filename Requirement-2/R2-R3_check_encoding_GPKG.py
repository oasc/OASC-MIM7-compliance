import geopandas as gpd
import fiona
import os

def check_geopackage(filename):
    
    # Verify file extension
    _, extension = os.path.splitext(filename)
    
    if extension == ".gpkg":
        
        print('The file is a .gpkg')
        
        # List all layers in the GeoPackage
        layers = fiona.listlayers(filename)
    
        # Iterate over all layers
        for layer_name in layers:
            # Load the layer into a GeoDataFrame
            data = gpd.read_file(filename, layer=layer_name)
    
            # Check if the layer contains geospatial data
            if 'geometry' in data.columns and not data['geometry'].isnull().all():
                # Extract 50 records
                data = data.head(50)
    
                print('The layer ' + layer_name + ' contains geospatial data.')
    
                # Check if identifiers are unique and persistent
                if data.index.is_unique:
                    print('The identifiers are unique.')
                else:
                    print('The identifiers are not unique.')
    
                # Check if identifiers are persistent
                if data.index.is_monotonic_increasing:
                    print('The identifiers are persistent.')
                else:
                    print('The identifiers are not persistent.')
    
                # Stop iterating after finding the first layer with geospatial data
                break
    
    else:
        print("The file extension is not .gpkg, it couldn't be a valid GeoPackage.")
 
# Test the function with your GeoPackage file
check_geopackage('example.gpkg')
