import geopandas as gpd
import config
import numpy



def get():
    all_restaurants = gpd.read_file(config.restaurants_filepath)  
    sub_restaurants = all_restaurants.sample(config.total_restaurants_number, random_state = 42)
    point_coordinates = [list([int(point.coords[0][0])%10000, 
                                int(point.coords[0][1])%10000]) 
                        for point in sub_restaurants['geometry'].to_crs("epsg:2154")]
    point_coordinates = numpy.array(point_coordinates)

    return sub_restaurants, point_coordinates


