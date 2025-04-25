import random
import math
import time

class Algorithms:
    def __init__(self):
        pass

    @staticmethod
    def simulated_annealing_multi_vehicle(graph, initial_temp, min_temp, cooling_rate, max_iterations, num_vehicles):
        """
        Simulated annealing algorithm for the multi-vehicle TSP problem.

        Args:
            graph (Graph): Instance of the Graph class containing the graph.
            initial_temp (float): Initial temperature.
            min_temp (float): Minimum temperature.
            cooling_rate (float): Cooling factor (0 < cooling_rate < 1).
            max_iterations (int): Maximum number of iterations at each temperature.
            num_vehicles (int): Number of vehicles.

        Returns:
            dict: Best tours for each vehicle.
            float: Execution time of the algorithm.
        """
        start_time = time.time()

        # Choose a random starting node
        nodes = list(graph.graph.nodes)
        start_node = random.choice(nodes)

        # Initialization
        nodes.remove(start_node)  # Exclude the starting node
        current_solution = Algorithms.initialize_solution(nodes, start_node, num_vehicles)
        best_solution = current_solution.copy()
        best_cost = Algorithms.compute_total_cost(graph, current_solution)

        # Update tsp_paths with the initial solution
        for vehicle_id, path in best_solution.items():
            graph.set_tsp_path(vehicle_id, path)

        temp = initial_temp

        while temp > min_temp:
            for _ in range(max_iterations):
                # Generate a neighboring solution
                neighbor_solution = Algorithms.generate_neighbor_multi_vehicle(graph, current_solution)

                # Calculate the cost of the solutions
                current_cost = Algorithms.compute_total_cost(graph, current_solution)
                neighbor_cost = Algorithms.compute_total_cost(graph, neighbor_solution)

                # Acceptance criterion
                delta = neighbor_cost - current_cost
                if delta < 0 or random.random() < math.exp(-delta / temp):
                    current_solution = neighbor_solution

                    # Update the best solution
                    if neighbor_cost < best_cost:
                        best_solution = neighbor_solution
                        best_cost = neighbor_cost

                        # Update tsp_paths with the best solution
                        for vehicle_id, path in best_solution.items():
                            graph.set_tsp_path(vehicle_id, path)

            # Cooling
            temp *= cooling_rate

        end_time = time.time()
        elapsed_time = end_time - start_time

        return best_solution, elapsed_time

    @staticmethod
    def initialize_solution(nodes, start_node, num_vehicles):
        """
        Initializes a solution by distributing nodes among vehicles.

        Args:
            nodes (list): List of nodes to visit.
            start_node (int): Common starting node.
            num_vehicles (int): Number of vehicles.

        Returns:
            dict: Initial solution with the tours for each vehicle.
        """
        random.shuffle(nodes)
        solution = {v: [start_node] for v in range(num_vehicles)}
        for i, node in enumerate(nodes):
            solution[i % num_vehicles].append(node)
        # Add the starting node at the end of each tour
        for v in range(num_vehicles):
            solution[v].append(start_node)
        return solution

    @staticmethod
    def generate_neighbor_multi_vehicle(graph, solution):
        """
        Generates a neighboring solution by modifying the tours of the vehicles.

        Args:
            graph (Graph): Instance of the Graph class.
            solution (dict): Current solution (tours of the vehicles).

        Returns:
            dict: New neighboring solution.
        """
        neighbor = {v: tour[:-1] for v, tour in solution.items()}  # Copy the solution without the return node
        vehicle_ids = list(neighbor.keys())

        # Randomly choose two vehicles
        v1, v2 = random.sample(vehicle_ids, 2)

        # Move a node from one tour to another
        if len(neighbor[v1]) > 1:  # Ensure at least one node remains
            idx = random.randint(1, len(neighbor[v1]) - 1)
            node = neighbor[v1].pop(idx)
            neighbor[v2].append(node)

        # Add the starting node at the end of each tour
        for v in neighbor:
            neighbor[v].append(solution[v][0])  # Add the starting node

        return neighbor

    @staticmethod
    def compute_total_cost(graph, solution):
        """
        Calculates the total cost of a solution.

        Args:
            graph (Graph): Instance of the Graph class.
            solution (dict): Current solution (tours of the vehicles).

        Returns:
            float: Total cost of the solution.
        """
        total_cost = 0
        for vehicle_id, tour in solution.items():
            for i in range(len(tour) - 1):
                total_cost += graph.get_edge_weight(tour[i], tour[i + 1])
        return total_cost