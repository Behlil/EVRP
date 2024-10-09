import xml.etree.ElementTree as ET
import random
import math
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

class Node:
    def __init__(self, id, type, x, y, has_tech=None):
        self.id = id
        self.type = type
        self.x = x
        self.y = y
        self.has_tech = has_tech

class Link:
    def __init__(self, head, tail, energy_consumption, travel_time):
        self.head = head
        self.tail = tail
        self.energy_consumption = energy_consumption
        self.travel_time = travel_time

    

class Vehicle:
    def __init__(self, capacity, max_travel_time, battery_capacity):
        self.capacity = capacity
        self.max_travel_time = max_travel_time
        self.battery_capacity = battery_capacity


    

class Request:
    def __init__(self, id, node, quantity, service_time):
        self.id = id
        self.node = node
        self.quantity = quantity
        self.service_time = service_time

class GVRP:
    def __init__(self, xml_file):
        self.nodes = {}
        self.links = {}
        self.vehicles = []
        self.requests = {}
        self.parse_xml(xml_file)

    

    def parse_xml(self, xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Parse nodes
        for node in root.findall('.//node'):
            id = int(node.get('id'))
            type = int(node.get('type'))
            x = float(node.find('cx').text)
            y = float(node.find('cy').text)
            has_tech = node.find('.//has_tech')
            has_tech = int(has_tech.text) if has_tech is not None else None
            self.nodes[id] = Node(id, type, x, y, has_tech)

        # Parse links
        for link in root.findall('.//link'):
            head = int(link.get('head'))
            tail = int(link.get('tail'))
            energy_consumption = float(link.find('energy_consumption').text)
            travel_time = float(link.find('travel_time').text)
            self.links[(head, tail)] = Link(head, tail, energy_consumption, travel_time)
            self.links[(tail, head)] = Link(tail, head, energy_consumption, travel_time)  # Assuming symmetry

        # Parse vehicles
        for vehicle in root.findall('.//vehicle_profile'):
            capacity = float(vehicle.find('capacity').text)
            max_travel_time = float(vehicle.find('max_travel_time').text)
            battery_capacity = float(vehicle.find('.//battery_capacity').text)
            num_vehicles = int(vehicle.get('number'))
            for _ in range(num_vehicles):
                self.vehicles.append(Vehicle(capacity, max_travel_time, battery_capacity))

        # Parse requests
        for request in root.findall('.//request'):
            id = int(request.get('id'))
            node = int(request.get('node'))
            quantity = float(request.find('quantity').text)
            service_time = float(request.find('service_time').text)
            if quantity > 0:
                self.requests[id] = Request(id, node, quantity, service_time)
                # print(self.requests[id].node)



    def distance(self, node1, node2):
        return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

    def total_distance(self, route):
        return sum(self.distance(self.nodes[route[i]], self.nodes[route[i+1]]) for i in range(len(route)-1))
    
    def energy_consumption(self, route):
        return sum(self.links[(route[i], route[i+1])].energy_consumption for i in range(len(route)-1))

    
    

    def is_valid_route(self, route, vehicle):
        current_capacity = 0
        current_time = 0
        current_battery = vehicle.battery_capacity

        for i in range(len(route) - 1):
            current_node = self.nodes[route[i]]
            next_node = self.nodes[route[i+1]]
            
            link = self.links.get((current_node.id, next_node.id))
            if not link:
                print('no link', route)
                return False  # No valid link between nodes
            
            current_battery -= link.energy_consumption
            if current_battery < 0:
                # print('out of battery', route)
                return False  # Out of battery
            
            current_time += link.travel_time
            if current_time > vehicle.max_travel_time:
                print('exceeds max travel time', route)
                return False  # Exceeds max travel time
            
            request = self.requests.get(next_node.id)
            if request:
                current_capacity += request.quantity
                if current_capacity > vehicle.capacity:
                    print('exceeds vehicle capacity', route)
                    return False  # Exceeds vehicle capacity
                current_time += request.service_time
            
            if next_node.type == 2:  # Charging station
                current_battery = vehicle.battery_capacity  # Fully recharge
        # print('valid route', route)
        return True

    def generate_initial_solution(self):
        depots = [node.id for node in self.nodes.values() if node.type == 0]
        Charging_stations = [node.id for node in self.nodes.values() if node.type == 2]
        # print(depots)
        solution = []
        unvisited = list(self.requests.keys())
        for vehicle in self.vehicles:
            if not unvisited:
                break
            # start from the depot 
            route = [depots[0]]

            while unvisited:
                next_node = random.choice(unvisited)
                route.append(self.requests[next_node].node)
                unvisited.remove(next_node)
                if not self.is_valid_route(route, vehicle):
                    # try adding a charging station between two nodes
                    for station in Charging_stations:
                        Charging_station = random.choice(Charging_stations)
                        route.insert(random.randint(1, len(route)-1), Charging_station)
                        Charging_stations.remove(Charging_station)
                        if self.is_valid_route(route, vehicle):
                            break
                        else:
                            # remove the charging station and the last node added
                            route.remove(Charging_station)
                            Charging_stations.append(Charging_station)
                if not self.is_valid_route(route, vehicle):
                    route.pop()
                    unvisited.append(next_node)
                    break

            route.append(depots[0])  # Return to depot
            solution.append(route)
            # print("unvisited", unvisited)
            # print("route", route)
        if unvisited:
            # add the unvisited nodes to the last route in random order but not the depot
            route = solution[-1]
            for node in unvisited:
                route.insert(random.randint(1, len(route)-1), self.requests[node].node)
            # print("unvisited", unvisited)
            unvisited.clear()
        print("initial solution", solution)
        # print("unvisited", unvisited)
        return solution

    def objective_function(self, solution):
        return sum(self.energy_consumption(route) for route in solution)

    def neighbor(self, solution):
        """
        generates a neighbor solution by swapping two random nodes in a random route
        repeat the process until a valid solution is generated
        do it in all the routes
        
        """
        new_solution = solution.copy()
        charging_stations = [node.id for node in self.nodes.values() if node.type == 2]
        charging_stations_in_solution = [node for route in new_solution for node in route if node in charging_stations]
        charging_stations = [node for node in charging_stations if node not in charging_stations_in_solution]

        for i in range(len(new_solution)):
            route = new_solution[i]
            if len(route) <= 2:
                continue  # Skip depot-only routes

            while True:
                # Swap two random nodes, but not the depot
                node1, node2 = random.sample(range(1, len(route)-1), 2)

                if node1 != node2:
                    break

            route[node1], route[node2] = route[node2], route[node1]
            #if the new solution is not valid or  the same as the old one, swap back
            while not self.is_valid_route(route, self.vehicles[0]) or route == solution[i]:
                route[node1], route[node2] = route[node2], route[node1]
                node1, node2 = random.sample(range(1, len(route)-1), 2)
                route[node1], route[node2] = route[node2], route[node1]                

            # if the new solution is not valid, add a charging station between two nodes
            if not self.is_valid_route(route, self.vehicles[0]):
                for station in charging_stations:
                    Charging_station = random.choice(charging_stations)
                    route.insert(random.randint(1, len(route)-1), Charging_station)
                    charging_stations.remove(Charging_station)
                    if self.is_valid_route(route, self.vehicles[0]):
                        break
                    else:
                        # remove the charging station and the last node added
                        route.remove(Charging_station)
                        charging_stations.append(Charging_station)

        # try to swap nodes between two routes
        while True:
            route1, route2 = random.sample(range(len(new_solution)), 2)
            node1 = random.randint(1, len(new_solution[route1])-2)
            node2 = random.randint(1, len(new_solution[route2])-2)
            new_solution[route1][node1], new_solution[route2][node2] = new_solution[route2][node2], new_solution[route1][node1]
            if self.is_valid_route(new_solution[route1], self.vehicles[0]) and self.is_valid_route(new_solution[route2], self.vehicles[0]):
                break
            else:
                new_solution[route1][node1], new_solution[route2][node2] = new_solution[route2][node2], new_solution[route1][node1]


            

            
        # print("new solution", new_solution)
        return new_solution

    def simulated_annealing(self, initial_temp=100000, cooling_rate=9999/1000.0, iterations=1000000, final_temp=0.0001):
        try:
            current_solution = self.generate_initial_solution()
            current_cost = self.objective_function(current_solution)
            best_solution = current_solution
            best_cost = current_cost
            temperature = initial_temp

            for i in range(iterations):
                new_solution = self.neighbor(current_solution)
                new_cost = self.objective_function(new_solution)

                if new_cost < current_cost or random.random() < math.exp((current_cost - new_cost) / temperature):
                    current_solution = new_solution
                    current_cost = new_cost

                    if current_cost < best_cost:
                        best_solution = current_solution
                        best_cost = current_cost

                temperature *= cooling_rate
                if temperature < final_temp:
                    break

                

                # if i % 100 == 0:  # Log progress every 100 iterations
                    # print(f"Iteration {i}: Current cost = {current_cost}, Best cost = {best_cost}")

            return best_solution, best_cost
        except Exception as e:
            print(f"An error occurred during simulated annealing: {str(e)}")
            return None, None
        
    def plot_solution(self, solution):
        fig, ax = plt.subplots(figsize=(10, 5))

        # plot the depot in blue and the customers in orange and the charging stations in green and routes in red
        for node in self.nodes.values():
            color = 'blue' if node.type == 0 else 'orange' if node.type == 1 else 'green'
            ax.plot(node.x, node.y, 'o', color=color, markersize=20, alpha=0.7)

        # add node ids inside the markers
        for node in self.nodes.values():
            ax.text(node.x, node.y, node.id, fontsize=12, ha='center', va='center')
        # add the routes with dashed lines and edge colors
        colors = ['grey', 'maroon', 'purple',  'red', 'brown', 'gray']
        for route in solution:
            x = [self.nodes[node].x for node in route]
            y = [self.nodes[node].y for node in route]
            ax.plot(x, y, color=colors.pop(), linewidth=2, linestyle='dashed')
            

        
        plt.title('GVRP solution')
        # turn off the axis
        ax.axis('off')

        plt.show()

        

# Usage
if __name__ == "__main__":
    gvrp = GVRP('C:/Users/lenovo/Downloads/PFE/projet/Dataset_A/Instances/C101-5.xml')
    best_solution, best_cost = gvrp.simulated_annealing()
    print(f"Best solution: {best_solution}")
    print(f"Best cost: {best_cost}")
    # calculate this cost
    # route = [[14, 5, 2, 13, 4, 7, 14], [14, 0, 8, 6, 11, 1, 12, 9, 3, 14]]
    # print("meilleure: ", gvrp.objective_function([route]))
    gvrp.plot_solution(best_solution)