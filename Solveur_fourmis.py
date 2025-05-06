
import random


# Fonction d'initialisation des phéromones
def initialize_pheromones(loc_num):
    pheromones = {}
    for loc_1 in range(loc_num):
      for loc_2 in range(loc_num):
        if loc_1 == loc_2 :
          continue  
        pheromones[(loc_1, loc_2)] = 1.0
        pheromones[(loc_2 , loc_1)] = 1.0  # Assurer la symétrie
    return pheromones

# Fonction pour calculer la probabilité de transition
def calculate_transition_probabilities(Distance_matrix, loc_num, pheromones, alpha, beta, current_node, visited):
    probabilities = {}
    total_sum = 0.0
    for neighbor in range(loc_num):
        if neighbor == current_node :
          continue

        if neighbor not in visited:
            distance = Distance_matrix[current_node, neighbor]
            probabilities[neighbor] = (pheromones[(current_node, neighbor)] ** alpha) * \
                                      ((1.0 / distance) ** beta)
            total_sum += probabilities[neighbor]
    
    if total_sum == 0:
        return None

    for neighbor in probabilities:
        probabilities[neighbor] /= total_sum
    
    return probabilities

# Fonction pour trouver un chemin pour une fourmi
def find_path(Distance_matrix, loc_num, pheromones, alpha, beta, start_node):
    path = [start_node]
    visited = set(path)
    current_node = start_node
    while len(visited) < loc_num :
        probabilities = calculate_transition_probabilities(Distance_matrix, loc_num, pheromones, alpha, beta, current_node, visited)
        if probabilities is None:
            return None
        next_node = random.choices(list(probabilities.keys()), weights=list(probabilities.values()))[0]
        path.append(next_node)
        visited.add(next_node)
        current_node = next_node
    path.append(start_node)  # Retourner au point de départ
    return path

# Fonction pour mettre à jour les phéromones
def update_pheromones(Distance_matrix, loc_num , pheromones, paths, decay):
    for edge in pheromones:
        pheromones[edge] *= (1 - decay)
    for path in paths:
        length = calculate_path_length(Distance_matrix, loc_num, path)
        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i + 1]
            if (from_node, to_node) in pheromones:
                pheromones[(from_node, to_node)] += 1.0 / length
                pheromones[(to_node, from_node)] += 1.0 / length  # Assurer la symétrie

# Fonction pour calculer la longueur d'un chemin
def calculate_path_length(Distance_matrix, loc_num, path):
    length = 0
    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i + 1]
        length += Distance_matrix[from_node, to_node]

    length += Distance_matrix[path[-1], path[0]]  # Retourner au point de départ
    return length

# Fonction principale de l'algorithme
def ant_colony_optimization(Distance_matrix, num_ants, num_iterations, decay, alpha, beta, show_progress=True):
  
    loc_num = len(Distance_matrix)
    pheromones = initialize_pheromones(loc_num)
    #print("pheromones:" ,pheromones)
    best_path = None
    best_length = float('inf')
    lengths_per_iteration = []

    
    # Sélectionnez la méthode d'itération en fonction du paramètre show_progress
    #iterations = tqdm(range(num_iterations), desc="Iterations") if show_progress else range(num_iterations)
    
    for _ in range(num_iterations):
        paths = []
        for i in range(num_ants):
            start_node = random.choice(range(loc_num))
            path = find_path(Distance_matrix, loc_num, pheromones, alpha, beta, start_node)
            #print(f"path{i} : ", path )
            if path is None:
                continue
            length = calculate_path_length(Distance_matrix, loc_num, path)
            if length == float('inf'):
                continue
            paths.append(path)
            if length < best_length:
                best_length = length
                best_path = path
                
        update_pheromones(Distance_matrix, loc_num , pheromones, paths, decay)
        #print("new pheromones :" ,pheromones)
        lengths_per_iteration.append(best_length)
        #print(f"Iteration {iteration+1}/{num_iterations}, Best length: {best_length}")
    return best_path, best_length, lengths_per_iteration

def ant_colony(Distance_matrix):

     # Paramètres de l'algorithme
    num_ants = 100
    num_iterations = len(Distance_matrix)*2
    decay = 0.5
    alpha = 1
    beta = 2

    return ant_colony_optimization(Distance_matrix, num_ants, num_iterations, decay, alpha, beta)

