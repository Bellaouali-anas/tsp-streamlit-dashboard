import heapq
import numpy as np

class Node:
    """Class to represent a node in the branch and bound process."""
    def __init__(self, level, path, reduced_matrix, cost, vertex):
        """
        Initialize a Node for the branch and bound search.
        - level: the current depth of the node in the search tree.
        - path: the list of vertices in the current path.
        - reduced_matrix: the reduced distance matrix for this node.
        - cost: the total cost of reaching this node.
        - vertex: the last visited vertex in the path.
        """
        self.level = level
        self.path = path
        self.reduced_matrix = reduced_matrix
        self.cost = cost
        self.vertex = vertex

    def __lt__(self, other):
        """Comparison function to prioritize nodes with lower cost in the priority queue."""
        return self.cost < other.cost


def ensure_no_self_loops(matrix):
    """
    Ensure that the diagonal values of the distance matrix are set to infinity.
    This prevents the algorithm from considering self-loops (traveling from a city to itself).
    If the input matrix is not of float type, it will be safely converted to float.
    """
    # Convert to float if not already
    if not np.issubdtype(matrix.dtype, np.floating):
        matrix = matrix.astype(float)

    # Set diagonal values to infinity
    np.fill_diagonal(matrix, float('inf'))

    return matrix


def reduce_matrix(matrix):
    """
    Apply the matrix reduction technique to reduce the cost of the problem.
    This involves subtracting the minimum value in each row and each column
    to simplify the matrix and speed up the search.
    
    Returns the total reduction cost.
    """
    n = matrix.shape[0]
    
    # Reduce rows: subtract the minimum non-infinity value in each row
    row_red = np.min(matrix, axis=1)
    row_red[row_red == float('inf')] = 0  # Avoid 'inf' values in row reductions
    for i in range(n):
        if row_red[i] > 0:
            matrix[i, :] -= row_red[i]

    # Reduce columns: subtract the minimum non-infinity value in each column
    col_red = np.min(matrix, axis=0)
    col_red[col_red == float('inf')] = 0  # Avoid 'inf' values in column reductions
    for j in range(n):
        if col_red[j] > 0:
            matrix[:, j] -= col_red[j]

    # Return the total cost of reductions (sum of row and column reductions)
    return np.sum(row_red) + np.sum(col_red)


def copy_matrix(matrix):
    """
    Return a deep copy of the input matrix to ensure no side-effects when modifying it.
    """
    return matrix.copy()


def branch_and_bound(distance_matrix):
    """
    Solves the Traveling Salesman Problem (TSP) using Branch and Bound approach.

    Args:
        distance_matrix (np.array): A 2D numpy array where matrix[i][j] represents the distance between cities i and j.
    
    Returns:
        best_path (list): The optimal path (list of vertices) to visit all cities.
        best_cost (float): The minimum cost (distance) to travel the optimal path.
        progress (list): A list tracking the progress of the algorithm (cost at each step).
    """
    # Ensure no self-loops (diagonal values are set to infinity)
    distance_matrix = ensure_no_self_loops(distance_matrix)

    n = distance_matrix.shape[0]
    pq = []  # Priority queue to explore nodes with the smallest cost first

    # Create an initial reduced matrix and compute the cost of reduction
    init_matrix = copy_matrix(distance_matrix)
    cost = reduce_matrix(init_matrix)
    
    # Create the root node for the search tree
    root = Node(0, [0], init_matrix, cost, 0)
    heapq.heappush(pq, root)

    # Variables to store the best solution
    best_cost = float('inf')
    best_path = []
    progress = []

    # Start the branch and bound process
    while pq:
        node = heapq.heappop(pq)  # Get the node with the lowest cost
        i = node.vertex  # Current vertex (city) in the path
        progress.append(node.cost)  # Track the progress (cost at each step)

        # If all cities have been visited, check if it's the optimal path
        if node.level == n - 1:
            last = node.path[-1]
            if distance_matrix[last, 0] != float('inf'):  # Ensure there's a path back to the start
                total_cost = node.cost + distance_matrix[last, 0]  # Add the cost of returning to the start
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_path = node.path + [0]  # Complete the cycle by returning to the starting city
            continue  # No further expansion needed for this node

        # Explore the next possible cities to visit
        for j in range(n):
            if j not in node.path and distance_matrix[i, j] != float('inf'):
                # Create a new path by adding city j to the current path
                new_path = node.path + [j]
                new_matrix = copy_matrix(node.reduced_matrix)

                # Eliminate edges to the previously visited cities and the current city
                for k in range(n):
                    new_matrix[i, k] = float('inf')
                    new_matrix[k, j] = float('inf')
                new_matrix[j, 0] = float('inf')  # Eliminate edge back to the starting city

                cost_to_j = distance_matrix[i, j]  # The cost of traveling from i to j
                reduced_cost = reduce_matrix(new_matrix)  # Apply matrix reduction
                total_cost = node.cost + cost_to_j + reduced_cost  # Total cost to reach city j

                # If the new cost is less than the best known solution, explore this new path
                if total_cost < best_cost:
                    child = Node(node.level + 1, new_path, new_matrix, total_cost, j)
                    heapq.heappush(pq, child)



    return best_path, best_cost, progress
