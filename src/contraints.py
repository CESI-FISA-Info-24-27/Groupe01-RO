import random
from graph import Graph
from datetime import datetime

def random_biased_low():
    """
    Generates a random number between 1 and 4, with a bias towards lower numbers.
    """
    r1 = 1 + 3 * random.random()
    r2 = 1 + 3 * random.random()
    r3 = 1 + 3 * random.random()
    r4 = 1 + 3 * random.random()
    return min(r1, r2, r3, r4)

def poucentage_regard_to_hour(time_str):
    """
    Returns the percentage of busy road at a given hour.
    """
    percentages = [
        0.17, 0.07, 0.05, 4.53, 0.05, 0.07, 0.13, 0.53,
        1.91, 1.88, 0.93, 0.92, 1.13, 1.23, 1.29, 1.69,
        2.51, 3.78, 4.49, 2.99, 1.37, 0.55, 0.21, 0.08
    ]
    hour, minute = map(int, time_str.split(":"))

    if 0 <= hour <= 23 and 0 <= minute < 60:
        ratio = minute / 60
        next_hour = (hour + 1) % 24 # Wrap around to 0 after 23
        return ((1 - ratio) * percentages[hour] + ratio * percentages[next_hour]) /100
    else:
        return None


def shuffle_graph(graph, time = datetime.now().strftime("%H:%M")):
    """
    Changes the graph by modifying the value of edges.
    """
    for u, v in graph.edges():
        if random.random() <= poucentage_regard_to_hour(time):
            graph[u][v]['weight'] *= random_biased_low()
            graph[v][u]['weight'] = round(graph[u][v]['weight'], 2)
    return graph