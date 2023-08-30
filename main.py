import json
import sys
import math
from shapely.geometry import Point, Polygon
from shapely.ops import transform
import pyproj
from pyproj.crs import ProjectedCRS
from pyproj.crs.coordinate_operation import AzimuthalEquidistantConversion
from geopy.distance import geodesic

def find_closest_point(origin, points):
    min_distance = float('inf')
    closest_point = None
    for point in points:
        distance = geodesic((origin[1], origin[0]), (point[1], point[0])).meters
        if distance < min_distance:
            min_distance = distance
            closest_point = point
    return closest_point

# Function to calculate the geodesic point buffer taking into account the projection
def geodesic_point_buffer(lon, lat, radius_m):
    proj_crs = ProjectedCRS(
        conversion=AzimuthalEquidistantConversion(lat, lon)
    )
    proj_wgs84 = pyproj.Proj('EPSG:4326')
    Trans = pyproj.Transformer.from_proj(
        proj_crs,
        proj_wgs84,
        always_xy=True
    ).transform

    return transform(Trans, Point(0, 0).buffer(radius_m))
    R = 6378137   # Earth radius in kilometers

    dlat = math.radians(x2 - x1)
    dlon = math.radians(y2 - y1)

    a = math.sin(dlat / 2)**2 + math.cos(math.radians(x1)) * math.cos(math.radians(x2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def calculate_midpoint(point1, point2):
    return [(point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2]

def remove_overlapping_points(original_polygon, overlapping_polygon):
        # Transform the circle into a GeoJSON-compatible polygon
    overlapping_polygon_geojson = {
        "type": "Polygon",
        "coordinates": [list(overlapping_polygon.exterior.coords)[::-1]]  # Reverse the coordinates for clockwise winding
    }

    original_polygon_geojson = Polygon(original_polygon)
    # Remove points from circle_geojson that are inside the original polygon
    overlapping_polygon_filtered = []
    for point in overlapping_polygon_geojson['coordinates'][0]:
        point_inside_polygon = Point(point[0], point[1]).within(original_polygon_geojson)
        if not point_inside_polygon:
            overlapping_polygon_filtered.append(point)

    return overlapping_polygon_filtered

def main():
    # Load the original GeoJSON file
    with open('data.geojson', 'r') as f:
        geojson_data = json.load(f)
    
    # Load the configuration file
    with open('config.json', 'r') as f:
        config_data = json.load(f)
    
    for config in config_data:
        polygon_number = config['polygonnumber']
        insert_between = config['insertBetween']

        polygon_coordinates = geojson_data['features'][polygon_number - 1]['geometry']['coordinates'][0]

        num_inserted_points = 0 
        for points in insert_between:
            point_index_1, point_index_2 = points

            point_1 = polygon_coordinates[point_index_1 + num_inserted_points]
            point_2 = polygon_coordinates[point_index_2 + num_inserted_points]


            # Calculate the midpoint between the input points
            midpoint = calculate_midpoint(point_1, point_2)

            distance_meters = geodesic((point_1[1], point_1[0]), (point_2[1], point_2[0])).meters
            radius = distance_meters / 2

            # Generate the circle as a Shapely polygon considering the projection
            circle = geodesic_point_buffer(midpoint[0], midpoint[1], radius)

            filtered_circle_points = remove_overlapping_points(polygon_coordinates, circle)
            inserted_points = []
            current_point = (point_1[0], point_1[1])

            while filtered_circle_points:
                closest_point = find_closest_point(current_point, filtered_circle_points)
                inserted_points.append(closest_point)
                filtered_circle_points.remove(closest_point)
                current_point = closest_point

            # Insert filtered circle points between the specified index points
            polygon_coordinates = (
                polygon_coordinates[:point_index_1 + 1 + num_inserted_points]
                + inserted_points
                + polygon_coordinates[point_index_1 + 1 + num_inserted_points:]
            )

            num_inserted_points += len(inserted_points)

        geojson_data['features'][polygon_number - 1]['geometry']['coordinates'][0] = polygon_coordinates

    # Create a new GeoJSON file with the circle
    with open('with_circle.geojson', 'w') as f:
        json.dump(geojson_data, f, indent=2)


if __name__ == "__main__":
    main()