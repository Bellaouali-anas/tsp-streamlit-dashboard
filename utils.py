import numpy as np
import math
from tsp_algorithms import nearest_neighbor, two_opt, simulated_annealing
from Solveur_fourmis import ant_colony
from branch_Bound import branch_and_bound
import time
import pandas as pd
import psutil
import os
import tracemalloc
from io import BytesIO
import threading


algorithmes = [("Nearest Neighbor",nearest_neighbor),
               ("2-opt",two_opt),
               ("Simulated Annealing", simulated_annealing),
               ( "Ant colony" ,ant_colony),
               ("Branch & Bound", branch_and_bound)
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
   
    distance_matrix = np.zeros((n, n), dtype=float)
    
    for i in range(n):
        for j in range(i+1, n):
            lat1, lon1 = locations[i]["geo_coordinates"]
            lat2, lon2 = locations[j]["geo_coordinates"]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            
            # Make the matrix symmetric
            distance_matrix[i, j] = distance
            distance_matrix[j, i] = distance
    
    return distance_matrix

def sample_cpu_usage(cpu_usages, stop_event):
    while not stop_event.is_set():
        cpu_usages.append(psutil.cpu_percent(interval=None))
        time.sleep(0.1)

           
def run_algorithmes(selected_algo: list, distance_matrix: np.array) -> list:
    process = psutil.Process(os.getpid())
    results = []

    for option, func in algorithmes:
        if option in selected_algo:
            print("Starting execution:", option)

            cpu_usages = []
            stop_event = threading.Event()

            # Start tracing memory
            tracemalloc.start()
            start_mem = process.memory_info().rss
            start_time = time.time()

            # Start sampling CPU usage
            sampling_thread = threading.Thread(target=sample_cpu_usage, args=(cpu_usages, stop_event))
            sampling_thread.start()

            # Run algorithm
            optimized_route, distance, progress_data = func(distance_matrix)

            # Stop sampling and wait for thread
            stop_event.set()
            sampling_thread.join()

            # Stop memory and time tracking
            elapsed_time = time.time() - start_time
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            end_mem = process.memory_info().rss

            delta_mem_mb = round((end_mem - start_mem) / (1024 * 1024), 4)
            peak_mem_mb = round(peak / (1024 * 1024), 4)
            average_cpu = round(sum(cpu_usages) / len(cpu_usages), 2) if cpu_usages else 0.0

            result_dict = {
                "algorithm": option,
                "optimized_route": optimized_route,
                "distance": distance,
                "progress_data": progress_data,
                "time": elapsed_time,
                "memory_MB": max(delta_mem_mb, peak_mem_mb)+0.01,
                "cpu_percent": average_cpu
            }

            print(f"{option} execution ended")
            print(f"time: {elapsed_time:.4f} sec")
            print(f"memory (peak): {peak / 1024 / 1024:.2f} MB")
            print(f"average CPU: {average_cpu}%")

            results.append(result_dict)
        #print(results)
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

# Step 3: Pad each list with its last value
def pad_list(lst: list, target_len: int):
    if not lst:
        return [None] * target_len  # or raise an error depending on your use case
    return lst + [lst[-1]] * (target_len - len(lst))


def assemble_progress(results: dict) -> list:
    
    progress_lists = [ result["progress_data"] for result in results]
    max_len = max(len(lst) for lst in progress_lists)
    return [pad_list(lst, max_len) for lst in progress_lists]

# Function to convert DataFrame to Excel in-memory
def to_excel_bytes(locations):

    locations_list = []
    for loc in locations: 
        dict = {
            "name":loc["name"],
            "latitude" : loc["geo_coordinates"][0],
            "longitude" : loc["geo_coordinates"][1],
        }
        locations_list.append(dict)

    df = pd.DataFrame(locations_list)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue() 