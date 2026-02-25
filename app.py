from flask import Flask, render_template, request, jsonify
from queue import PriorityQueue
import math

app = Flask(__name__)

# KIIT Campus locations with REAL coordinates
LOCATIONS = {
    "Campus 1": {"lat": 20.3461, "lng": 85.8236},
    "Campus 2": {"lat": 20.3532, "lng": 85.8197},
    "Campus 3": {"lat": 20.3531, "lng": 85.8165},
    "Campus 4": {"lat": 20.3538, "lng": 85.8202},
    "Campus 5 (KIMS)": {"lat": 20.3527, "lng": 85.8140},
    "Campus 6 (Convention Center)": {"lat": 20.3525, "lng": 85.8195},
    "Campus 7 (KSOM)": {"lat": 20.3507, "lng": 85.8195},
    "Campus 8": {"lat": 20.3512, "lng": 85.8194},
    "Campus 9": {"lat": 20.3534, "lng": 85.8117},
    "Campus 10": {"lat": 20.3596, "lng": 85.8180},
    "Campus 11": {"lat": 20.3606, "lng": 85.8229},
    "Campus 12": {"lat": 20.3545, "lng": 85.8194},
    "Campus 13": {"lat": 20.3565, "lng": 85.8185},
    "Campus 14": {"lat": 20.3561, "lng": 85.8154},
    "Campus 15": {"lat": 20.3487, "lng": 85.8148},
    "Campus 16": {"lat": 20.3617, "lng": 85.8228},
    "Campus 17": {"lat": 20.3492, "lng": 85.8194},
    "Campus 18": {"lat": 20.3558, "lng": 85.8236},
    "Campus 19": {"lat": 20.3538, "lng": 85.8196},
    "Campus 20": {"lat": 20.3540, "lng": 85.8162},
    "Campus 21": {"lat": 20.3502, "lng": 85.8157},
    "Campus 22": {"lat": 20.3540, "lng": 85.8148},
    "Campus 23": {"lat": 20.3481, "lng": 85.8204},
    "Campus 24": {"lat": 20.3490, "lng": 85.8150},
    "Campus 25": {"lat": 20.3640, "lng": 85.8162}
}

# Expanded Graph - Connected based on actual road topology
GRAPH = {
    "Campus 1": [
        ("Campus 2", 0.25), ("Campus 3", 0.4), ("Campus 4", 0.4), ("Campus 5 (KIMS)", 0.4),
        ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4), ("Campus 9", 0.4),
        ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4), ("Campus 13", 0.4),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 2": [
        ("Campus 1", 0.25), ("Campus 3", 0.4), ("Campus 4", 0.2), ("Campus 5 (KIMS)", 0.4),
        ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4), ("Campus 9", 0.4),
        ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4), ("Campus 13", 0.4),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 3": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 4", 0.35), ("Campus 5 (KIMS)", 0.4),
        ("Campus 6 (Convention Center)", 0.5), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4), ("Campus 9", 0.4),
        ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4), ("Campus 13", 0.4),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 4": [
        ("Campus 1", 0.4), ("Campus 2", 0.2), ("Campus 3", 0.35), ("Campus 5 (KIMS)", 0.4),
        ("Campus 6 (Convention Center)", 0.3), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4), ("Campus 9", 0.4),
        ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4), ("Campus 13", 0.4),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 5 (KIMS)": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.5), ("Campus 8", 0.4), ("Campus 9", 0.4),
        ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4), ("Campus 13", 0.4),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.1), ("Campus 25", 0.4),
    ],
    "Campus 6 (Convention Center)": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.5), ("Campus 4", 0.3),
        ("Campus 5 (KIMS)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.3), ("Campus 9", 0.4),
        ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.8), ("Campus 13", 0.405),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 7 (KSOM)": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.5), ("Campus 6 (Convention Center)", 0.4), ("Campus 8", 0.4), ("Campus 9", 0.2),
        ("Campus 10", 0.3), ("Campus 11", 0.4), ("Campus 12", 0.4), ("Campus 13", 0.4),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 8": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.3), ("Campus 7 (KSOM)", 0.4), ("Campus 9", 0.4),
        ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4), ("Campus 13", 0.4),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 9": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.2), ("Campus 8", 0.4),
        ("Campus 10", 0.15), ("Campus 11", 0.4), ("Campus 12", 0.4), ("Campus 13", 0.4),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 10": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.3), ("Campus 8", 0.4),
        ("Campus 9", 0.15), ("Campus 11", 0.3), ("Campus 12", 0.4), ("Campus 13", 0.4),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 11": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.3), ("Campus 12", 0.2), ("Campus 13", 0.4),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 12": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.8), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.2), ("Campus 13", 0.15),
        ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 13": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.405), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.15),
        ("Campus 14", 0.15), ("Campus 15", 0.4), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 1.2),
    ],
    "Campus 14": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.15), ("Campus 15", 0.15), ("Campus 16", 0.4), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 15": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.4), ("Campus 14", 0.15), ("Campus 16", 0.3), ("Campus 17", 0.4),
        ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 16": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.4), ("Campus 14", 0.4), ("Campus 15", 0.3), ("Campus 17", 0.15),
        ("Campus 18", 0.4), ("Campus 19", 0.2), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 17": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.4), ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.15),
        ("Campus 18", 0.15), ("Campus 19", 0.4), ("Campus 20", 0.4), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 18": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.4), ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4),
        ("Campus 17", 0.15), ("Campus 19", 0.4), ("Campus 20", 0.2), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 19": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.4), ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.2),
        ("Campus 17", 0.4), ("Campus 18", 0.4), ("Campus 20", 0.1), ("Campus 21", 0.4),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 20": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.4), ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4),
        ("Campus 17", 0.4), ("Campus 18", 0.2), ("Campus 19", 0.1), ("Campus 21", 0.1),
        ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 21": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.4), ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4),
        ("Campus 17", 0.4), ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.1),
        ("Campus 22", 0.1), ("Campus 23", 0.4), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 22": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.4), ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4),
        ("Campus 17", 0.4), ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4),
        ("Campus 21", 0.1), ("Campus 23", 0.1), ("Campus 24", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 23": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.4), ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4),
        ("Campus 17", 0.4), ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4),
        ("Campus 21", 0.4), ("Campus 22", 0.1), ("Campus 24", 0.4), ("Campus 25", 0.15),
    ],
    "Campus 24": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.1), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 0.4), ("Campus 14", 0.4), ("Campus 15", 0.4), ("Campus 16", 0.4),
        ("Campus 17", 0.4), ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4),
        ("Campus 21", 0.4), ("Campus 22", 0.4), ("Campus 23", 0.4), ("Campus 25", 0.4),
    ],
    "Campus 25": [
        ("Campus 1", 0.4), ("Campus 2", 0.4), ("Campus 3", 0.4), ("Campus 4", 0.4),
        ("Campus 5 (KIMS)", 0.4), ("Campus 6 (Convention Center)", 0.4), ("Campus 7 (KSOM)", 0.4), ("Campus 8", 0.4),
        ("Campus 9", 0.4), ("Campus 10", 0.4), ("Campus 11", 0.4), ("Campus 12", 0.4),
        ("Campus 13", 1.4), ("Campus 14", 1.2), ("Campus 15", 0.4), ("Campus 16", 0.4),
        ("Campus 17", 0.4), ("Campus 18", 0.4), ("Campus 19", 0.4), ("Campus 20", 0.4),
        ("Campus 21", 0.4), ("Campus 22", 0.4), ("Campus 23", 0.15), ("Campus 24", 0.4),
    ],
}

def heuristic(node1, node2):
    """Calculate Euclidean distance as heuristic"""
    loc1 = LOCATIONS[node1]
    loc2 = LOCATIONS[node2]
    
    # Convert lat/lng to approximate meters
    lat_diff = (loc1["lat"] - loc2["lat"]) * 111000
    lng_diff = (loc1["lng"] - loc2["lng"]) * 111000 * math.cos(math.radians(loc1["lat"]))
    
    distance = math.sqrt(lat_diff**2 + lng_diff**2) / 1000  # Convert to km
    return distance

def astar_search(start, goal):
    """A* Search Algorithm - Optimal pathfinding using heuristic"""
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    nodes_explored = 0
    
    while not frontier.empty():
        _, current = frontier.get()
        nodes_explored += 1
        
        if current == goal:
            break
        
        for neighbor, edge_cost in GRAPH.get(current, []):
            new_cost = cost_so_far[current] + edge_cost
            
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, goal)
                frontier.put((priority, neighbor))
                came_from[neighbor] = current
    
    # Reconstruct path
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    
    return path, cost_so_far.get(goal, 0), nodes_explored

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_path', methods=['POST'])
def find_path():
    data = request.json
    start = data.get('start')
    destination = data.get('destination')
    
    if not start or not destination:
        return jsonify({'error': 'Missing parameters'}), 400
    
    if start not in LOCATIONS or destination not in LOCATIONS:
        return jsonify({'error': 'Invalid location'}), 400
    
    # Use A* algorithm
    path, distance, nodes_explored = astar_search(start, destination)
    
    # Get coordinates for the path with names
    coordinates = [{'lat': LOCATIONS[node]['lat'], 'lng': LOCATIONS[node]['lng'], 'name': node} for node in path]
    
    return jsonify({
        'algorithm': 'A* Search',
        'path': path,
        'distance': round(distance, 2),
        'nodes_explored': nodes_explored,
        'coordinates': coordinates
    })

if __name__ == '__main__':
    app.run(debug=True)