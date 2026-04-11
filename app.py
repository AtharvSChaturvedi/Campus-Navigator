from flask import Flask, render_template, request, jsonify
from queue import PriorityQueue
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL    = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL  = os.environ.get("RECEIVER_EMAIL")

# KIIT Campus locations with REAL coordinates
LOCATIONS = {
    "Campus 3":  {"lat": 20.3531, "lng": 85.8165},
    "Campus 6":  {"lat": 20.3525, "lng": 85.8195},
    "Campus 8":  {"lat": 20.3512, "lng": 85.8194},
    "Campus 12": {"lat": 20.3545, "lng": 85.8194},
    "Campus 13": {"lat": 20.3565, "lng": 85.8185},
    "Campus 14": {"lat": 20.3561, "lng": 85.8154},
    "Campus 15": {"lat": 20.3487, "lng": 85.8148},
    "Campus 17": {"lat": 20.3492, "lng": 85.8194},
    "Campus 20": {"lat": 20.3540, "lng": 85.8162},
    "Campus 25": {"lat": 20.3640, "lng": 85.8162},
}

# Graph - Connected based on actual road topology
GRAPH = {
    "Campus 3":  [("Campus 20", 0.059), ("Campus 14", 0.4),  ("Campus 15", 0.5)],
    "Campus 6":  [("Campus 3",  0.4),   ("Campus 12", 0.16), ("Campus 8",  0.45)],
    "Campus 8":  [("Campus 6",  0.45),  ("Campus 17", 0.26)],
    "Campus 12": [("Campus 6",  0.16),  ("Campus 13", 0.3)],
    "Campus 13": [("Campus 12", 0.3),   ("Campus 14", 0.4)],
    "Campus 14": [("Campus 13", 0.4),   ("Campus 25", 1.2),  ("Campus 20", 0.35)],
    "Campus 15": [("Campus 3",  0.5),   ("Campus 17", 0.55)],
    "Campus 17": [("Campus 8",  0.26),  ("Campus 15", 0.55)],
    "Campus 20": [("Campus 3",  0.059), ("Campus 14", 0.35)],
    "Campus 25": [("Campus 14", 1.2)],
}

def heuristic(node1, node2):
    loc1 = LOCATIONS[node1]
    loc2 = LOCATIONS[node2]
    lat_diff = (loc1["lat"] - loc2["lat"]) * 111000
    lng_diff = (loc1["lng"] - loc2["lng"]) * 111000 * math.cos(math.radians(loc1["lat"]))
    distance = math.sqrt(lat_diff**2 + lng_diff**2) / 1000
    return distance

def astar_search(start, goal):
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

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    return path, cost_so_far.get(goal, 0), nodes_explored

@app.route('/')
def index():
    locations_list = sorted(LOCATIONS.keys())
    return render_template('index.html', locations=locations_list, locations_dict=LOCATIONS)

@app.route('/voice_command', methods=['POST'])
def voice_command():
    """
    Voice input via microphone is not supported in serverless/cloud deployments.
    This endpoint is intentionally disabled. Use the Web Speech API on the
    frontend (navigator.mediaDevices / SpeechRecognition) instead — it runs
    entirely in the browser and sends the recognised text to /find_path directly.
    """
    return jsonify({
        'error': 'Server-side voice recognition is not available in this deployment. '
                 'Please use the on-screen controls to select your route.'
    }), 501

@app.route('/find_path', methods=['POST'])
def find_path():
    data = request.json
    start       = data.get('start')
    destination = data.get('destination')

    if not start or not destination:
        return jsonify({'error': 'Missing parameters'}), 400
    if start not in LOCATIONS or destination not in LOCATIONS:
        return jsonify({'error': 'Invalid location'}), 400

    path, distance, nodes_explored = astar_search(start, destination)
    coordinates = [
        {'lat': LOCATIONS[n]['lat'], 'lng': LOCATIONS[n]['lng'], 'name': n}
        for n in path
    ]
    return jsonify({
        'algorithm': 'A* Search',
        'path': path,
        'distance': round(distance, 2),
        'nodes_explored': nodes_explored,
        'coordinates': coordinates,
    })

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data    = request.json
    name    = data.get('name')
    email   = data.get('email')
    comment = data.get('comment')

    if not name or not email or not comment:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400

    try:
        msg = MIMEMultipart()
        msg['From']    = SENDER_EMAIL
        msg['To']      = RECEIVER_EMAIL
        msg['Subject'] = f"Campus Navigator Feedback from {name}"
        body = f"Name: {name}\nEmail: {email}\n\nFeedback:\n{comment}"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()

        return jsonify({'success': True, 'message': 'Feedback sent!'})
    except Exception as e:
        print(f"SMTP Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
