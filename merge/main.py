from shapely.geometry import shape, mapping
from shapely.ops import unary_union
import fiona
import geojson

# Open the input file
with fiona.open('data.geojson') as input:
    # Read all geometries and their properties
    features = [feature for feature in input]

# Extract the geometries
geometries = [shape(feature['geometry']) for feature in features]

# Union all geometries into a single polygon
merged_geometry = unary_union(geometries)

# Create a schema for the output file (e.g., with a 'name' field)
schema = {
    'geometry': 'Polygon',
    'properties': {'name': 'str'},
}

# Write the merged polygon into a GeoJSON object
merged_geojson = geojson.Feature(
    geometry=mapping(merged_geometry),
    properties={'name': 'Merged Polygon'}
)

# Format the GeoJSON object and save it to a file
with open('merged_polygon.geojson', 'w') as output_file:
    geojson.dump(merged_geojson, output_file, indent=2)
