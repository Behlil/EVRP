import xml.etree.ElementTree as ET
import numpy as np
from pyswarm import pso

# Load and parse the XML file
tree = ET.parse('C:/Users/lenovo/Downloads/PFE/data/Dataset_A/Instances/RC108-15.xml')
root = tree.getroot()
print(root.tag)

# Extract node, link, and request data
nodes = root.find('network').find('nodes')
links = root.find('network').find('links')
requests = root.find('requests')
vehicle_profile = root.find('fleet').find('vehicle_profile')

node_ids = []
cx_values = []
cy_values = []
node_types = []
time_windows = {}
requests_dict = {}
battery_capacity = float(vehicle_profile.find('custom').find('battery_capacity').text)
vehicle_capacity = float(vehicle_profile.find('capacity').text)
max_travel_time = float(vehicle_profile.find('max_travel_time').text)
charging_techs = vehicle_profile.find('custom').find('charging_techs')

for node in nodes.findall('node'):
    node_id = node.get('id')
    cx = float(node.find('cx').text)
    cy = float(node.find('cy').text)
    
    node_ids.append(node_id)
    cx_values.append(cx)
    cy_values.append(cy)

# Extract request time windows and quantities
for request in requests.findall('request'):
    request_id = request.get('id')
    node = request.get('node')
    quantity = int(request.find('quantity').text)
    service_time = int(request.find('service_time').text)
    requests_dict[request_id] = (node, quantity, service_time)

# Extract the links for energy consumption and travel time
link_dict = {}
for link in links.findall('link'):
    head = link.get('head')
    tail = link.get('tail')
    energy_consumption = float(link.find('energy_consumption').text)
    travel_time = float(link.find('travel_time').text)
    
    link_dict[(head, tail)] = (energy_consumption, travel_time)
    link_dict[(tail, head)] = (energy_consumption, travel_time)  # Symmetric links

# Objective function: Minimize total energy consumption and respect constraints
def objective_function(positions):
    total_energy = 0
    total_travel_time = 0
    current_load = 0
    current_battery = battery_capacity
    current_time = 0

    # Re-assign node positions
    node_dict = {}
    for i, node_id in enumerate(node_ids):
        node_dict[node_id] = (positions[i * 2], positions[i * 2 + 1])

    # Iterate through requests
    for request_id, (node, quantity, service_time) in requests_dict.items():
        # Check travel to node
        if request_id == "0":  # Assuming vehicle starts at depot node "0"
            prev_node = "0"
        else:
            prev_node = requests_dict[str(int(request_id) - 1)][0]  # Previous node
            
        if (prev_node, node) in link_dict:
            energy, travel_time = link_dict[(prev_node, node)]
            
            # Add travel time and energy consumption
            total_travel_time += travel_time
            total_energy += energy

            # Check time windows and service time
            if total_travel_time > max_travel_time:
                return float('inf')  # Violates time window

            # Check battery capacity and charging
            if current_battery - energy < 0:  # Needs charging
                if nodes.find(f"node[@id='{node}']").find('custom').find('has_tech').text == '1':
                    # Charge vehicle at the node
                    current_battery = battery_capacity
                else:
                    return float('inf')  # Cannot reach the node without charging

            current_battery -= energy
            current_load += quantity

            # Check vehicle capacity
            if current_load > vehicle_capacity:
                return float('inf')  # Exceeds vehicle capacity

            current_time += travel_time + service_time  # Update time after service

    return total_energy  # Objective: Minimize energy consumption

# Define the bounds for the PSO (the range of node positions)
lower_bounds = [0] * len(cx_values) * 2  # Assuming all coordinates are positive
upper_bounds = [100] * len(cx_values) * 2  # Example upper bound for coordinates

# Initial positions (flattened cx and cy values)
initial_positions = np.array(cx_values + cy_values)

# Run PSO to optimize the positions
best_positions, best_energy = pso(objective_function, lower_bounds, upper_bounds, 
                                  swarmsize=50, maxiter=100)

# Update the node positions with the optimized values
for i, node_id in enumerate(node_ids):
    new_cx, new_cy = best_positions[i * 2], best_positions[i * 2 + 1]
    print(f"Optimized Node ID: {node_id}, New Position: ({new_cx}, {new_cy})")

# Plot the optimized positions (optional, you can reuse the previous plot code)
