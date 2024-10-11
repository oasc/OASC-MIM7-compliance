import geopandas as gpd
import fiona
import warnings

def check_geopackage(filename):
    
    # List all layers in the GeoPackage
    try:
        layers = fiona.listlayers(filename)
    # catch when non req1 compliant
    except fiona.errors.DriverError:
        print('The file is not a conform geopackage (Requirement 1 : The first 16 bytes of a GeoPackage SHALL be the null-terminated ASCII string "SQLite format 3".) Please refer to "https://www.geopackage.org/spec140/index.html".')
        return
    
    # Iterate over all layers
    for layer_name in layers:
        
        # Catch the warnings
        with warnings.catch_warnings(record=True) as caught_warnings:
            
            # Load the layer into a GeoDataFrame
            try:
                data = gpd.read_file(filename, layer=layer_name)
            except Exception as e:
                print(str(e))
                return
            
        # Look for a warning related to Req2, 3 or 4 failure
        for warning in caught_warnings:
            # When non req2 compliant
            if "GPKG: bad application_id" in str(warning.message):
                print('The file is not a conform geopackage (Requirement 2 : A GeoPackage SHALL contain a value of 0x47504B47 ("GPKG" in ASCII) in the "application_id" field of the SQLite database header.) Please refer to "https://www.geopackage.org/spec140/index.html".')
                return
            # When non req3 compliant
            elif "has GPKG application_id, but non conformant file extension" in str(warning.message):
                print('The file is not a conform geopackage (Requirement 3 : A GeoPackage SHALL have the file extension name ".gpkg".) Please refer to "https://www.geopackage.org/spec140/index.html".')
                return
            # When non req4 compliant
            elif "is referenced in gpkg_contents" in str(warning.message):
                print('The file is not a conform geopackage. ' + str(warning.message) + '. (Requirement 4 : A GeoPackage SHALL contain the data elements (tables, columns or values) and SQL constructs (views, constraints, or triggers) specified in the core of this encoding standard.) Please refer to "https://www.geopackage.org/spec140/index.html".')
                return
            # Else print the warnings
            else:
                print(str(warning.message))
                    
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
     
# Examples :     
     
# Passing example
print("TEST 1 ---")
check_geopackage('examples/example.gpkg')

# Failing Req1 example
print("TEST 2 ---")
check_geopackage('examples/example-TEST_2.gpkg')

# Failing Req2 example
print("TEST 3 ---")
check_geopackage('examples/example-TEST_3.gpkg')

# Failing Req3 example
print("TEST 4 ---")
check_geopackage('examples/example-TEST_4.gpk')

# Failing Req4 example
print("TEST 5 ---")
check_geopackage('examples/example-TEST_5.gpkg')