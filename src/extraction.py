import xml.etree.ElementTree as ET

# Function to parse the XML file and extract the relevant information
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
            'custom': {}
        }
        custom = node.find('custom')
        if custom is not None:
            node_data['custom']['has_tech'] = int(custom.find('has_tech').text)
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

# Example Usage:
file_path = "C:/Users/lenovo/Downloads/PFE/projet/Dataset_A/Instances/C101-5.xml"  # replace with the actual path to the XML file
gvrp_data = parse_gvrp_xml(file_path)

# Printing the parsed data (for verification)
import pprint
pprint.pprint(gvrp_data)

# Now you can use the `gvrp_data` dictionary for optimization purposes.
# The dictionary contains the parsed nodes, links, fleet, and requests data.
