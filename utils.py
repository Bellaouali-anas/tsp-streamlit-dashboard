import numpy as np
import math
from tsp_algorithms import nearest_neighbor, two_opt, simulated_annealing
from Solveur_fourmis import ant_colony
import time


algorithmes = [("Nearest Neighbor",nearest_neighbor),
               ("2-opt",two_opt),
               ("Simulated Annealing", simulated_annealing),
               ( "ant colony" ,ant_colony)
               ]

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def generate_distance_matrix(locations):
    """
    Generate a distance matrix for a list of locations
    
    Args:
        locations: List of (latitude, longitude) tuples
    
    Returns:
        distance_matrix: 2D numpy array of distances between locations
    """
   
    n = len(locations)
   
    distance_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i+1, n):
            lat1, lon1 = locations[i]["Geocordinate"]
            lat2, lon2 = locations[j]["Geocordinate"]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            
            # Make the matrix symmetric
            distance_matrix[i, j] = distance
            distance_matrix[j, i] = distance
    
    return distance_matrix

               
def run_algorithmes(selected_algo: list, distance_matrix: np.array) -> list :
    
    results = []
    # Check and run functions
    for option, func in algorithmes:
        
        if option in selected_algo:
            
            start_time = time.time()
            optimized_route, distance, progress_data = func(distance_matrix)
            dict = {
                "algorithm" : option,
                "optimized_route" : optimized_route,
                "distance" : distance,
                "progress_data" : progress_data,
                "time" : time.time() - start_time 
            }
            results.append(dict)

    
    return results

def convert_to_float(data_list):
    return [float(x) for x in data_list]

def equalize_length(l1, l2, l3):
    max_len = max(len(l1), len(l2), len(l3))

    def extend_list(lst):
        if not lst:
            return [None] * max_len
        return lst + [lst[-1]] * (max_len - len(lst))

    return extend_list(l1), extend_list(l2), extend_list(l3)

