import random
import math
import time
import copy
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

        current_solution = Algorithms.initialize_solution(nodes, start_node, num_vehicles)
        best_solution = copy.deepcopy(current_solution)
        current_cost = Algorithms.compute_total_cost(graph, current_solution)
        best_cost = current_cost

        for vehicle_id, path in best_solution.items():
            graph.set_tsp_path(vehicle_id, path)

        temp = initial_temp

        while temp > min_temp:
            graph = shuffle_graph(graph)

            for _ in range(max_iterations):
                neighbor_solution = Algorithms.generate_neighbor_multi_vehicle(current_solution)
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

            temp *= cooling_rate

        elapsed_time = time.time() - start_time
        return best_solution, elapsed_time

    @staticmethod
    def initialize_solution(nodes, start_node, num_vehicles):
        """
        Initializes a solution by distributing nodes among vehicles.
        """
        random.shuffle(nodes)
        solution = {v: [start_node] for v in range(num_vehicles)}
        for i, node in enumerate(nodes):
            solution[i % num_vehicles].append(node)
        for v in solution:
            solution[v].append(start_node)
        return solution

    @staticmethod
    def generate_neighbor_multi_vehicle(solution):
        """
        Generates a neighboring solution by modifying the tours of the vehicles.
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

        else:  # move_between
            v1, v2 = random.sample(vehicle_ids, 2)
            if len(neighbor[v1]) > 2:
                idx = random.randint(1, len(neighbor[v1]) - 2)
                node = neighbor[v1].pop(idx)
                insert_pos = random.randint(1, len(neighbor[v2]) - 1)
                neighbor[v2].insert(insert_pos, node)

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