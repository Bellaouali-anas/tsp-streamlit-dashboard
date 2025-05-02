import numpy as np
import random
import math


def nearest_neighbor(distance_matrix):
    """
    Nearest Neighbor algorithm for solving TSP
    
    Args:
        distance_matrix: 2D numpy array of distances between locations
    
    Returns:
        tour: List of indices representing the order of locations to visit
        total_distance: Total distance of the tour
        progress_data: List of distances at each step of the algorithm
    """
    n = len(distance_matrix)
    
    # Start from node 0
    current = 0
    tour = [current]
    unvisited = set(range(1, n))
    total_distance = 0
    progress_data = [0]  # Start with zero distance
    
    # Visit each unvisited node
    while unvisited:
        next_node = min(unvisited, key=lambda x: distance_matrix[current][x])
        unvisited.remove(next_node)
        tour.append(next_node)
        total_distance += distance_matrix[current][next_node]
        current = next_node
        progress_data.append(total_distance)
    
    # Return to starting point
    total_distance += distance_matrix[tour[-1]][tour[0]]
    
    return tour, total_distance, progress_data

def calculate_tour_distance(tour, distance_matrix):
    """
    Calculate the total distance of a given tour
    
    Args:
        tour: List of indices representing the order of locations to visit
        distance_matrix: 2D numpy array of distances between locations
    
    Returns:
        total_distance: Total distance of the tour
    """
    total_distance = 0
    n = len(tour)
    
    for i in range(n):
        from_city = tour[i]
        to_city = tour[(i + 1) % n]  # Wrap around to start
        total_distance += distance_matrix[from_city][to_city]
    
    return total_distance

def two_opt(distance_matrix, max_iterations=1000):
    """
    2-opt algorithm for solving TSP
    
    Args:
        distance_matrix: 2D numpy array of distances between locations
        max_iterations: Maximum number of iterations to perform
    
    Returns:
        best_tour: List of indices representing the best tour found
        best_distance: Total distance of the best tour
        progress_data: List of distances at each improvement of the algorithm
    """
    n = len(distance_matrix)
    
    # Start with a random tour
    current_tour = list(range(n))
    random.shuffle(current_tour)
    
    best_distance = calculate_tour_distance(current_tour, distance_matrix)
    best_tour = current_tour.copy()
    
    progress_data = [best_distance]
    improvement = True
    iteration = 0
    
    while improvement and iteration < max_iterations:
        improvement = False
        iteration += 1
        
        # Try all possible 2-opt swaps
        for i in range(n - 1):
            for j in range(i + 1, n):
                # Skip adjacent edges
                if j - i == 1:
                    continue
                
                # Create a new tour with the 2-opt swap
                new_tour = current_tour[:i+1] + current_tour[j:i:-1] + current_tour[j+1:]
                new_distance = calculate_tour_distance(new_tour, distance_matrix)
                
                # If the new tour is better, accept it
                if new_distance < best_distance:
                    best_distance = new_distance
                    best_tour = new_tour.copy()
                    current_tour = new_tour.copy()
                    progress_data.append(best_distance)
                    improvement = True
                    break
            
            if improvement:
                break
    
    return best_tour, best_distance, progress_data

def simulated_annealing(distance_matrix, initial_temp=1000, cooling_rate=0.95, min_temp=1e-6, max_iterations=1000):
    """
    Simulated Annealing algorithm for solving TSP
    
    Args:
        distance_matrix: 2D numpy array of distances between locations
        initial_temp: Initial temperature for simulated annealing
        cooling_rate: Rate at which temperature decreases
        min_temp: Minimum temperature at which to stop
        max_iterations: Maximum number of iterations
    
    Returns:
        best_tour: List of indices representing the best tour found
        best_distance: Total distance of the best tour
        progress_data: List of distances at each improvement of the algorithm
    """
    n = len(distance_matrix)
    
    # Start with a random tour
    current_tour = list(range(n))
    random.shuffle(current_tour)
    
    current_distance = calculate_tour_distance(current_tour, distance_matrix)
    best_tour = current_tour.copy()
    best_distance = current_distance
    
    progress_data = [best_distance]
    
    # Initialize temperature
    temp = initial_temp
    iteration = 0
    
    # Continue until temperature reaches minimum or max iterations
    while temp > min_temp and iteration < max_iterations:
        iteration += 1
        
        # Pick two random indices to swap
        i, j = sorted(random.sample(range(n), 2))
        
        # Create a new tour by swapping the segments
        new_tour = current_tour[:i] + current_tour[i:j+1][::-1] + current_tour[j+1:]
        new_distance = calculate_tour_distance(new_tour, distance_matrix)
        
        # Calculate acceptance probability
        delta = new_distance - current_distance
        accept_prob = math.exp(-delta / temp) if delta > 0 else 1.0
        
        # Accept the new solution based on probability
        if random.random() < accept_prob:
            current_tour = new_tour
            current_distance = new_distance
            
            # Update best solution if improved
            if new_distance < best_distance:
                best_distance = new_distance
                best_tour = new_tour.copy()
                progress_data.append(best_distance)
        
        # Cool down the temperature
        temp *= cooling_rate
    
    return best_tour, best_distance, progress_data


