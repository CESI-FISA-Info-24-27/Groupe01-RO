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
        start_time = time.perf_counter()

        nodes = list(graph.graph.nodes)
        start_node = random.choice(nodes)
        nodes.remove(start_node)

        current_solution = Algorithms.initialize_solution(nodes, start_node, num_vehicles, graph)
        best_solution = copy.deepcopy(current_solution)
        current_cost = Algorithms.compute_total_cost(graph, current_solution)
        best_cost = current_cost

        for vehicle_id, path in best_solution.items():
            graph.set_tsp_path(vehicle_id, path)

        temp = initial_temp

        number_iterations = 0
        number_saves = 0
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
                if number_iterations % 500 == 0:
                    graph.tsp_paths = current_solution
                    #graph.save_graph_png("./data/results/gif/result_graph_{}.png".format(number_saves), True, current_solution)
                    number_saves += 1
                number_iterations += 1

            #print(f"Temperature: {temp:.2f}, Current cost: {current_cost:.2f}, Best cost: {best_cost:.2f}")
            temp *= cooling_rate

        # Display best solution during 3s in the GIF
        # for k in range(10):
        #     graph.save_graph_png("./data/results/gif/result_graph_{}.png".format(number_saves+k), True, best_solution)
        # Validate the final solution
        if not Algorithms.validate_solution(graph, best_solution):
            raise ValueError("The solution is invalid: some edges do not exist or tours are incomplete.")

        elapsed_time = time.perf_counter() - start_time
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
                return False

            # Check if all edges in the tour exist in the graph
            for i in range(len(tour) - 1):
                if not graph.graph.has_edge(tour[i], tour[i + 1]):
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
        Optimizes the number of trucks and the number of packages per truck using a balanced approach.

        Args:
            num_packages (int): Total number of packages.
            truck_capacity (int): Maximum capacity of a single truck.

        Returns:
            tuple: (number_of_trucks, packages_per_truck)
        """
        # Calculate the minimum number of trucks needed
        num_trucks = math.ceil(num_packages / truck_capacity)

        # Calculate the average load per truck
        avg_load = num_packages // num_trucks
        remainder = num_packages % num_trucks

        # Distribute packages among trucks
        packages_per_truck = [avg_load] * num_trucks

        # Distribute the remainder evenly
        for i in range(remainder):
            packages_per_truck[i] += 1

        return packages_per_truck
    
    @staticmethod
    def genetic_algorithm(graph, population_size, generations, mutation_rate, num_vehicles):
        """
        Genetic algorithm for the multi-vehicle TSP problem.

        Args:
            graph (Graph): The graph object.
            population_size (int): Number of individuals in the population.
            generations (int): Number of generations to evolve.
            mutation_rate (float): Probability of mutation.
            num_vehicles (int): Number of vehicles.

        Returns:
            tuple: (best_solution, best_cost)
        """
        def initialize_population():
            """Initializes the population with random valid solutions."""
            population = []
            for _ in range(population_size):
                nodes = list(graph.graph.nodes)
                start_node = random.choice(nodes)
                nodes.remove(start_node)
                random.shuffle(nodes)  # Shuffle nodes for diversity
                solution = Algorithms.initialize_solution(nodes, start_node, num_vehicles, graph)
                population.append(solution)
            return population

        def fitness(solution):
            """Calculates the fitness of a solution (lower cost is better)."""
            return 1 / (1 + Algorithms.compute_total_cost(graph, solution))

        def select_parents(population):
            """Selects two parents using a roulette wheel selection."""
            fitness_values = [fitness(ind) for ind in population]
            total_fitness = sum(fitness_values)
            probabilities = [f / total_fitness for f in fitness_values]
            parents = random.choices(population, weights=probabilities, k=2)
            return parents

        def crossover(parent1, parent2):
            """Performs crossover between two parents to produce an offspring."""
            offspring = {}
            for vehicle_id in parent1.keys():
                if random.random() < 0.5:
                    offspring[vehicle_id] = parent1[vehicle_id]
                else:
                    offspring[vehicle_id] = parent2[vehicle_id]

            # Ensure all nodes are covered and vehicles return to their start
            all_nodes = set(graph.graph.nodes)
            covered_nodes = set(node for tour in offspring.values() for node in tour)
            missing_nodes = all_nodes - covered_nodes

            # Distribute missing nodes among vehicles
            for node in missing_nodes:
                vehicle_id = random.choice(list(offspring.keys()))
                last_node = offspring[vehicle_id][-1]
                if graph.graph.has_edge(last_node, node):
                    offspring[vehicle_id].append(node)
                else:
                    # Find a valid path to the node
                    path = nx.shortest_path(graph.graph, source=last_node, target=node, weight='weight')
                    offspring[vehicle_id].extend(path[1:])

            # Ensure each vehicle returns to its start node
            for vehicle_id, tour in offspring.items():
                if tour[0] != tour[-1]:
                    last_node = tour[-1]
                    start_node = tour[0]
                    if graph.graph.has_edge(last_node, start_node):
                        tour.append(start_node)
                    else:
                        # Find a valid path back to the start node
                        path = nx.shortest_path(graph.graph, source=last_node, target=start_node, weight='weight')
                        tour.extend(path[1:])

            return offspring

        def mutate(solution):
            """Mutates a solution by swapping nodes or moving nodes between vehicles."""
            if random.random() < mutation_rate:
                neighbor = Algorithms.generate_neighbor_multi_vehicle(graph, solution)
                if Algorithms.validate_solution(graph, neighbor):
                    return neighbor
            return solution

        def validate_population(population):
            """Ensures all solutions in the population are valid."""
            return [ind for ind in population if Algorithms.validate_solution(graph, ind)]

        # Initialize population
        population = initialize_population()

        # Evolve population over generations
        best_solution = None
        best_cost = float('inf')

        for generation in range(generations):
            new_population = []

            for _ in range(population_size):
                # Select parents
                parent1, parent2 = select_parents(population)

                # Perform crossover
                offspring = crossover(parent1, parent2)

                # Perform mutation
                offspring = mutate(offspring)

                # Add offspring to the new population
                new_population.append(offspring)

            # Validate the new population
            population = validate_population(new_population)

            # Update the best solution
            for individual in population:
                cost = Algorithms.compute_total_cost(graph, individual)
                if cost < best_cost:
                    best_solution = individual
                    best_cost = cost

            #print(f"Generation {generation + 1}: Best cost = {best_cost:.2f}")

        # Update tsp_path in the graph with the best solution
        for vehicle_id, path in best_solution.items():
            graph.set_tsp_path(vehicle_id, path)

        return best_solution, best_cost