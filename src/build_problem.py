from matplotlib import pyplot as plt
import xml.etree.ElementTree as ET
import random



class Node:
    def __init__(self, node_id, x, y, type):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.type = type

    def __str__(self):
        return f'Node {self.node_id} ({self.x}, {self.y})'
    
    def get_links(self, links):
        node_links = []
        for link in links:
            if link.first_node == self:
                node_links.append(link)
            elif link.second_node == self:
                node_links.append(link)
        return node_links

    



class Customer(Node):
    def __init__(self, node_id, x, y, type):
        super().__init__(node_id, x, y, type)

    def get_quantity(self, requests):
        for request in requests:
            if request.node_id == self.node_id:
                return request.quantity
        return 0

    def get_service_time(self, requests):
        for request in requests:
            if request.node_id == self.node_id:
                return request.service_time
        return 0



class Depot(Node):
    def __init__(self, node_id, x, y, type):
        super().__init__(node_id, x, y, type)




class ChargingStation(Node):
    def __init__(self, node_id, x, y, type, has_tech):
        super().__init__(node_id, x, y, type)
        self.has_tech = has_tech

        

class Route:
    def __init__(self, id,  path_ids):
        self.path = path_ids
        self.id = id

    def plot(self, nodes):
        # plot the customer nodes in blue and depot nodes in red and charging stations in green and line between them in grey
        for node_id in self.path:
            node = nodes[node_id]
            if isinstance(node, Customer):
                plt.plot(node.x, node.y, 'bo')
            elif isinstance(node, Depot):
                plt.plot(node.x, node.y, 'ro')
            elif isinstance(node, ChargingStation):
                plt.plot(node.x, node.y, 'go')
        for i in range(len(self.path)-1):
            node1 = nodes[self.path[i]]
            node2 = nodes[self.path[i+1]]
            plt.plot([node1.x, node2.x], [node1.y, node2.y], 'grey')
        plt.show()

    def calculate_energy_consumption(self, links):
        energy_consumption = 0
        for i in range(len(self.path)-1):
            for link in links:
                if link.first_node.node_id == self.path[i] and link.second_node.node_id == self.path[i+1]:
                    energy_consumption += link.energy_consumption
        return energy_consumption
    
    def calculate_travel_time(self, links):
        travel_time = 0
        for i in range(len(self.path)-1):
            for link in links:
                if link.first_node.node_id == self.path[i] and link.second_node.node_id == self.path[i+1]:
                    travel_time += link.travel_time
        return travel_time

    


class Link:
    def __init__(self, first_node, second_node, energy_consumption, travel_time):
        self.first_node = first_node
        self.second_node = second_node
        self.energy_consumption = energy_consumption
        self.travel_time = travel_time

    def distance(self):
        distance = ((self.first_node.x - self.second_node.x)**2 + (self.first_node.y - self.second_node.y)**2)**0.5
        return distance
        

class Vehicule:
    def __init__(self, id, type_id, departure_node, arrival_node, capacity, max_travel_time, battery_capacity, gamma, rho):
        self.type_id = type_id
        self.id = id
        self.departure_node = departure_node
        self.arrival_node = arrival_node
        self.capacity = capacity
        self.max_travel_time = max_travel_time
        self.current_travel_time = 0
        self.battery_capacity = battery_capacity
        self.current_battery = battery_capacity  # Niveau actuel de la batterie (en kWh)
        self.gamma = gamma
        self.rho = rho
        self.current_node = departure_node

    def time_to_full_charge(self):
        time_to_full_charge = (self.battery_capacity - self.current_battery) / (self.gamma * self.rho)
        return time_to_full_charge

    def full_charge(self):
        self.current_travel_time += self.time_to_full_charge()
        self.current_battery = self.battery_capacity

    def partial_charge(self, charge):
        self.current_travel_time += charge / self.gamma
        self.current_battery += charge

    def travel_between_2_nodes(self, node1, node2):
        link = Link(node1, node2)
        self.current_travel_time += link.travel_time
        self.current_battery -= link.energy_consumption
        self.current_node = node2

    def travel_to_node(self, node, links):
        # find the link between the current node and the next node
        for link in links:
            if link.first_node == self.current_node and link.second_node == node:
                break


        self.current_travel_time += link.travel_time
        self.current_battery -= link.energy_consumption
        self.current_node = node

    def travel_to_nodes(self, nodes, links):
        for node in nodes:
            self.travel_to_node(node, links)
            if isinstance(node, ChargingStation):
                self.full_charge()
            if self.current_battery < 0:
                return False
        return True
    def enought_battery_between_2_nodes(self, node1, node2):
        link = Link(node1, node2)
        if self.current_battery - link.energy_consumption < 0:
            return False
        return True

    def enough_battery_for_path(self, path, links):
        for i in range(len(path)-1):
            if not self.enought_battery_between_2_nodes(path[i], path[i+1]):
                return False
        return True
                
   
class Request:
    def __init__(self, id, node_id, quantity, service_time):
        self.id = id
        self.node_id = node_id
        self.quantity = quantity
        self.service_time = service_time

        

def parse_gvrp_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = {
        'info': {},
        'network': {
            'nodes': [],
            'links': []
        },
        'fleet': [],
        'requests': []
    }

    # Parsing <info>
    info = root.find('info')
    data['info']['dataset'] = info.find('dataset').text
    data['info']['name'] = info.find('name').text

    # Parsing <network>
    network = root.find('network')

    # Parsing <nodes>
    for node in network.find('nodes'):
        node_data = {
            'id': int(node.attrib['id']),
            'type': int(node.attrib['type']),
            'cx': int(node.find('cx').text),
            'cy': int(node.find('cy').text),
            'has_tech': {}
        }
        custom = node.find('custom')
        if custom is not None:
            node_data['has_tech'] = int(custom.find('has_tech').text)
        data['network']['nodes'].append(node_data)

    # Parsing <links>
    for link in network.find('links'):
        link_data = {
            'head': int(link.attrib['head']),
            'tail': int(link.attrib['tail']),
            'energy_consumption': int(link.find('energy_consumption').text),
            'travel_time': int(link.find('travel_time').text)
        }
        data['network']['links'].append(link_data)

    # Parsing <fleet>
    fleet = root.find('fleet')
    for vehicle_profile in fleet.findall('vehicle_profile'):
        vehicle_data = {
            'type': int(vehicle_profile.attrib['type']),
            'number': int(vehicle_profile.attrib['number']),
            'departure_node': int(vehicle_profile.find('departure_node').text),
            'arrival_node': int(vehicle_profile.find('arrival_node').text),
            'capacity': int(vehicle_profile.find('capacity').text),
            'max_travel_time': int(vehicle_profile.find('max_travel_time').text),
            'custom': {
                'battery_capacity': int(vehicle_profile.find('custom').find('battery_capacity').text),
                'charging_techs': []
            }
        }
        # Parsing <charging_techs>
        charging_techs = vehicle_profile.find('custom').find('charging_techs')
        for tech in charging_techs.findall('function'):
            tech_data = {
                'has_tech': int(tech.attrib['has_tech']),
                'gamma': float(tech.find('gamma').text),
                'rho': float(tech.find('rho').text)
            }
            vehicle_data['custom']['charging_techs'].append(tech_data)

        data['fleet'].append(vehicle_data)

    # Parsing <requests>
    requests = root.find('requests')
    for request in requests:
        request_data = {
            'id': int(request.attrib['id']),
            'node': int(request.attrib['node']),
            'quantity': int(request.find('quantity').text),
            'service_time': int(request.find('service_time').text)
        }
        data['requests'].append(request_data)

    return data

def build_nodes(data):
    nodes = {}
    for node_data in data['network']['nodes']:
        if node_data['type'] == 1:
            node = Customer(node_data['id'], node_data['cx'], node_data['cy'], node_data['type'])
        elif node_data['type'] == 0:
            node = Depot(node_data['id'], node_data['cx'], node_data['cy'], node_data['type'])
        elif node_data['type'] == 2:
            node = ChargingStation(node_data['id'], node_data['cx'], node_data['cy'], node_data['type'], node_data['has_tech'])
        nodes[node_data['id']] = node
    return nodes

def build_links(data, nodes):
    links = []
    for link_data in data['network']['links']:
        link = Link(nodes[link_data['head']], nodes[link_data['tail']], link_data['energy_consumption'], link_data['travel_time'])
        links.append(link)
    return links

def build_requests(data):
    requests = []
    for request_data in data['requests']:
        request = Request(request_data['id'], request_data['node'], request_data['quantity'], request_data['service_time'])
        requests.append(request)
    return requests

def build_vehicles(data):
    vehicles = []
    for i in range(data['fleet'][0]['number']):
        vehicle_data = data['fleet'][0]
        vehicle = Vehicule(i, vehicle_data['type'], vehicle_data['departure_node'], vehicle_data['arrival_node'], vehicle_data['capacity'], vehicle_data['max_travel_time'], vehicle_data['custom']['battery_capacity'], vehicle_data['custom']['charging_techs'][1]['gamma'], vehicle_data['custom']['charging_techs'][1]['rho'])
        vehicles.append(vehicle)
    return vehicles




def build_problem(file_path):
    data = parse_gvrp_xml(file_path)
    nodes = build_nodes(data)
    links = build_links(data, nodes)
    requests = build_requests(data)
    vehicles = build_vehicles(data)
    return nodes, links, requests, vehicles

# data = parse_gvrp_xml('C:/Users/lenovo/Downloads/PFE/projet/Dataset_A/Instances/C101-5.xml')
# nodes, links, requests, vehicles, routes = build_problem('C:/Users/lenovo/Downloads/PFE/projet/Dataset_A/Instances/C101-5.xml')
# print(generate_random_route(nodes))

def get_consumption_matrix(links):
    consumption_matrix = {}
    for link in links:
        if link.first_node.node_id not in consumption_matrix:
            consumption_matrix[link.first_node.node_id] = {}
        consumption_matrix[link.first_node.node_id][link.second_node.node_id] = link.energy_consumption
        # convert the matrix to a numpy array

    return consumption_matrix

