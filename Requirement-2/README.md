This directory provides tests written in Python to check compliance to Requirement 2 of _MIM7 - Places_:

- `R2-R3_check_encoding_GPKG.py` checks whether a given dataset is encoded in GeoPackage (checks the first four GeoPackage Requirements "https://www.geopackage.org/spec140/index.html"), includes geospatial data with unique and persistent identifiers.
- `R2-R3_check_service_WFS-OAPIF_API.py` exposes the check as an API.

Something is not working as expected when more than one request is sent to the API.
Please restart it after each request. 