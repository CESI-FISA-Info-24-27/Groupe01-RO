import random
import math
import time
import copy
import networkx as nx
from contraints import shuffle_graph

class Algorithms:
    def __init__(self):
        pass

    @staticmethod
    def simulated_annealing(graph, initial_temp, min_temp, cooling_rate, max_iterations, num_vehicles):
        """
        Simulated annealing algorithm for the multi-vehicle TSP problem.
        """
        start_time = time.time()

        nodes = list(graph.graph.nodes)
        start_node = random.choice(nodes)
        nodes.remove(start_node)

        current_solution = Algorithms.initialize_solution(nodes, start_node, num_vehicles, graph)
        best_solution = copy.deepcopy(current_solution)
        current_cost = Algorithms.compute_total_cost(graph, current_solution)
        best_cost = current_cost

        print(f"Initial solution cost: {current_cost:.2f}")

        for vehicle_id, path in best_solution.items():
            graph.set_tsp_path(vehicle_id, path)

        temp = initial_temp

        while temp > min_temp:
            for _ in range(max_iterations):
                neighbor_solution = Algorithms.generate_neighbor_multi_vehicle(graph, current_solution)
                neighbor_cost = Algorithms.compute_total_cost(graph, neighbor_solution)

                delta = neighbor_cost - current_cost
                if delta < 0 or random.random() < math.exp(-delta / temp):
                    current_solution = neighbor_solution
                    current_cost = neighbor_cost

                    if neighbor_cost < best_cost:
                        best_solution = copy.deepcopy(neighbor_solution)
                        best_cost = neighbor_cost

                        for vehicle_id, path in best_solution.items():
                            graph.set_tsp_path(vehicle_id, path)

            print(f"Temperature: {temp:.2f}, Current cost: {current_cost:.2f}, Best cost: {best_cost:.2f}")
            temp *= cooling_rate

        # Validate the final solution
        if not Algorithms.validate_solution(graph, best_solution):
            raise ValueError("The solution is invalid: some edges do not exist or tours are incomplete.")

        elapsed_time = time.time() - start_time
        print(f"Final solution cost: {best_cost:.2f}")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        return best_solution, elapsed_time
    
    @staticmethod
    def validate_solution(graph, solution):
        """
        Validates the solution to ensure all tours are complete and use only existing edges.

        Args:
            graph (Graph): The graph object.
            solution (dict): The solution to validate, where keys are vehicle IDs and values are lists of nodes.

        Returns:
            bool: True if the solution is valid, False otherwise.
        """
        for vehicle_id, tour in solution.items():
            # Check if the tour starts and ends at the same node
            if tour[0] != tour[-1]:
                print(f"Vehicle {vehicle_id} does not complete a tour: {tour}")
                return False

            # Check if all edges in the tour exist in the graph
            for i in range(len(tour) - 1):
                if not graph.graph.has_edge(tour[i], tour[i + 1]):
                    print(f"Invalid edge ({tour[i]}, {tour[i + 1]}) for vehicle {vehicle_id}")
                    return False

        return True

    @staticmethod
    def initialize_solution(nodes, start_node, num_vehicles, graph):
        """
        Initializes a solution by distributing nodes among vehicles.
        Ensures that all edges in the solution exist in the graph, even if it requires using multiple edges.

        Args:
            nodes (list): List of nodes to distribute.
            start_node (any): The starting node for all vehicles.
            num_vehicles (int): Number of vehicles.
            graph (Graph): The graph object.

        Returns:
            dict: A valid initial solution.
        """
        random.shuffle(nodes)
        solution = {v: [start_node] for v in range(num_vehicles)}

        for i, node in enumerate(nodes):
            vehicle_id = i % num_vehicles
            last_node = solution[vehicle_id][-1]

            # Ensure the edge exists before adding the node
            if graph.graph.has_edge(last_node, node):
                solution[vehicle_id].append(node)
            else:
                # Find a valid path using the shortest path algorithm
                try:
                    path = nx.shortest_path(graph.graph, source=last_node, target=node, weight='weight')
                    # Add the intermediate nodes to the solution
                    solution[vehicle_id].extend(path[1:])  # Exclude the last_node as it's already in the solution
                except nx.NetworkXNoPath:
                    raise ValueError(f"No path exists between {last_node} and {node} in the graph.")

        # Complete the tour by returning to the start node
        for v in solution:
            last_node = solution[v][-1]
            if graph.graph.has_edge(last_node, start_node):
                solution[v].append(start_node)
            else:
                # Find a valid path back to the start node
                try:
                    path = nx.shortest_path(graph.graph, source=last_node, target=start_node, weight='weight')
                    solution[v].extend(path[1:])  # Exclude the last_node as it's already in the solution
                except nx.NetworkXNoPath:
                    raise ValueError(f"No path exists between {last_node} and {start_node} in the graph.")

        return solution

    @staticmethod
    def generate_neighbor_multi_vehicle(graph, solution):
        """
        Generates a neighboring solution by modifying the tours of the vehicles.
        Ensures that all edges in the solution exist in the graph.

        Args:
            graph (Graph): The graph object.
            solution (dict): The current solution.

        Returns:
            dict: A neighboring solution.
        """
        neighbor = copy.deepcopy(solution)
        vehicle_ids = list(neighbor.keys())

        move_type = random.choice(["swap_within", "move_between"])

        if move_type == "swap_within":
            # Swap two nodes within the same vehicle's tour
            v = random.choice(vehicle_ids)
            if len(neighbor[v]) > 3:  # At least two real nodes
                i, j = random.sample(range(1, len(neighbor[v]) - 1), 2)
                neighbor[v][i], neighbor[v][j] = neighbor[v][j], neighbor[v][i]

                # Ensure the modified path is valid
                for k in range(len(neighbor[v]) - 1):
                    if not graph.graph.has_edge(neighbor[v][k], neighbor[v][k + 1]):
                        return solution  # Return the original solution if invalid

        else:  # move_between
            v1, v2 = random.sample(vehicle_ids, 2)
            if len(neighbor[v1]) > 2:
                idx = random.randint(1, len(neighbor[v1]) - 2)
                node = neighbor[v1].pop(idx)
                insert_pos = random.randint(1, len(neighbor[v2]) - 1)
                neighbor[v2].insert(insert_pos, node)

                # Ensure the modified paths are valid
                for k in range(len(neighbor[v1]) - 1):
                    if not graph.graph.has_edge(neighbor[v1][k], neighbor[v1][k + 1]):
                        return solution  # Return the original solution if invalid
                for k in range(len(neighbor[v2]) - 1):
                    if not graph.graph.has_edge(neighbor[v2][k], neighbor[v2][k + 1]):
                        return solution  # Return the original solution if invalid

        return neighbor

    @staticmethod
    def compute_total_cost(graph, solution):
        """
        Calculates the total cost of a solution.
        """
        total_cost = 0
        for vehicle_id, tour in solution.items():
            for i in range(len(tour) - 1):
                total_cost += graph.get_edge_weight(tour[i], tour[i + 1])
        return total_cost
    
    @staticmethod
    def optimize_truck_loads(num_packages, truck_capacity):
        """
        Optimizes the number of trucks and the number of packages per truck using a knapsack-like approach.

        Args:
            num_packages (int): Total number of packages.
            truck_capacity (int): Maximum capacity of a single truck.

        Returns:
            tuple: (number_of_trucks, packages_per_truck)
        """
        # Calculate the minimum number of trucks needed
        num_trucks = math.ceil(num_packages / truck_capacity)

        # Distribute packages among trucks
        packages_per_truck = [truck_capacity] * (num_trucks - 1)
        last_truck_load = num_packages - sum(packages_per_truck)
        packages_per_truck.append(last_truck_load)

        return num_trucks, packages_per_truck