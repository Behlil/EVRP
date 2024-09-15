from build_problem import Depot, Customer, ChargingStation
import random

def generate_random_route(nodes):
    # customer nodes must be visited exactly once
    # depot nodes must be visited exactly once
    # charging stations can be visited  or not
    # the first node must be a depot
    # the last node must be a depot

    # generate a random route
    route = []
    depot_nodes = [node for node in nodes.values() if isinstance(node, Depot)]
    depot_node = depot_nodes[0]
    route.append(depot_node.node_id)
    customer_nodes = [node for node in nodes.values() if isinstance(node, Customer)]
    # shuffle the customer nodes
    customer_nodes = random.sample(customer_nodes, len(customer_nodes))
    for customer_node in customer_nodes:
        route.append(customer_node.node_id)
    route.append(depot_node.node_id)
    # choose a random charging station or more
    charging_stations = [node for node in nodes.values() if isinstance(node, ChargingStation)]
    charging_stations = random.sample(charging_stations, random.randint(0, len(charging_stations)))
    # add the charging stations to the route in random order
    for charging_station in charging_stations:
        route.insert(random.randint(1, len(route)-1), charging_station.node_id)
        
    return route

    # export the function
    return generate_random_route
