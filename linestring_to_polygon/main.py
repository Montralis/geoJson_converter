from shapely.geometry import LineString, Polygon
from shapely.geometry import mapping, shape
import fiona
from geojson_rewind import rewind


input_file = 'data.geojson'
output_file = 'updated_data.geojson'

# Funktion zum Umwandeln des Linestrings in ein Polygon
def linestring_to_polygon(fili_shps):
    gdf = gpd.read_file(fili_shps) #LINESTRING
    gdf['geometry'] = [Polygon(mapping(x)['coordinates']) for x in gdf.geometry]
    return gdf

# Öffnen der Eingabedatei und Verarbeitung der Geometrie
with fiona.open(input_file) as source:
    # Neue Feature-Liste für die Ausgabedatei
    output_features = []

    for feature in source:
        geom_type = feature['geometry']['type']
        if geom_type == 'LineString':
            line_coords = feature['geometry']['coordinates']
            
            # print(shape(LineString(line_coords)))
            new_polygon = shape(LineString(line_coords)).convex_hull

            # Erstellung eines neuen Features für die Ausgabe
            new_feature = {
                'type': 'Feature',
                'properties': {},
                'geometry': mapping(new_polygon)
            }
            output_features.append(new_feature)

# Schema für die Ausgabedatei erstellen
schema = {
    'geometry': 'Polygon',
    'properties': {}  # Keine spezifischen Eigenschaften definiert
}

# Schreiben der Daten in die Ausgabedatei
with fiona.open(output_file, 'w', driver='GeoJSON', schema=schema) as output:
    for feature in output_features:
        output.write(feature)
