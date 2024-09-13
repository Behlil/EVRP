
# GVRP-Multitech 

## Overview
The **GVRP-Multitech Dataset** is designed for solving the **Green Vehicle Routing Problem (GVRP)**, a type of Vehicle Routing Problem where the fleet consists of electric vehicles (EVs) with limited battery capacity. This dataset contains details about the locations (nodes), paths (links), vehicle profiles, and delivery requests, including the associated energy consumption and service constraints.

## Structure of the XML Files

### 1. **Instance**
The root element of the dataset file is `<instance>`. It encapsulates the entire dataset and is subdivided into several key sections: `info`, `network`, `fleet`, and `requests`.

### 2. **Info Section**
The `<info>` section contains metadata:
- `<dataset>`: The name of the dataset.
- `<name>`: The name or location of the specific instance being described.

### 3. **Network Section**
The network defines the locations (nodes) and paths (links) that form the routing space.

#### a. **Nodes**
Nodes represent different types of locations, such as depots, customers, and charging stations.
- `<node>`: Each node has an `id`, a `type`, and coordinates (`cx`, `cy`).
  - `type="0"`: Depot (central hub where vehicles depart and return).
  - `type="1"`: Customer location (where deliveries need to be made).
  - `type="2"`: Charging station (where vehicles can recharge).
- `<custom>`: This subsection may indicate whether a charging station has specific technology (`has_tech=1` for yes, `0` for no).

Example:
```xml
<node id="0" type="1">
    <cx>20</cx>
    <cy>55</cy>
</node>
```
This defines a customer node at coordinates (20, 55).

#### b. **Links**
Links represent paths between two nodes. Each `<link>` includes:
- `head`: The starting node.
- `tail`: The ending node.
- `<energy_consumption>`: The energy required to travel the path.
- `<travel_time>`: The time taken to travel between the two nodes.

Example:
```xml
<link head="0" tail="1">
    <energy_consumption>31</energy_consumption>
    <travel_time>31</travel_time>
</link>
```

### 4. **Fleet Section**
The fleet consists of electric vehicles with specific profiles that define their capacity and travel constraints. Each `<vehicle_profile>` contains:
- `type`: Vehicle type identifier.
- `number`: The number of vehicles of this type available.
- `<departure_node>` and `<arrival_node>`: The node IDs where the vehicles start and finish their routes.
- `<capacity>`: The maximum load capacity of the vehicle.
- `<max_travel_time>`: The maximum allowable travel time for the vehicle before it must return to the depot.
- `<battery_capacity>`: The total battery capacity of the vehicle.
- `<charging_techs>`: Charging technologies available to the vehicle, including charging efficiency (`gamma`) and charging rate (`rho`).

Example:
```xml
<vehicle_profile type="0" number="2">
    <departure_node>8</departure_node>
    <arrival_node>8</arrival_node>
    <capacity>200</capacity>
    <max_travel_time>1236</max_travel_time>
    <custom>
        <battery_capacity>77</battery_capacity>
    </custom>
</vehicle_profile>
```

### 5. **Requests Section**
The requests represent the deliveries that must be made to customer nodes. Each `<request>` includes:
- `id`: Unique request identifier.
- `node`: The node ID where the delivery is required.
- `<quantity>`: The quantity of goods to be delivered.
- `<service_time>`: The time required to perform the delivery at the node.

Example:
```xml
<request id="0" node="0">
    <quantity>10</quantity>
    <service_time>90</service_time>
</request>
```

### Summary of Key Elements:
- **Nodes**: Define customer locations, charging stations, and depots with their coordinates.
- **Links**: Define paths between nodes, with energy consumption and travel time details.
- **Fleet**: Specifies the fleet of electric vehicles, including capacity, battery life, and charging technology.
- **Requests**: Represent the delivery requests, specifying the quantity to deliver and the required service time at each node.

## Use Case
The dataset is intended for research and optimization purposes in green logistics and electric vehicle routing problems. It allows users to simulate vehicle routes that account for delivery constraints, energy consumption, charging needs, and vehicle capacities, providing a realistic challenge for route optimization algorithms.

## Citation
> Goeke, Dominik (2019), “E-VRPTW instances”, Mendeley Data, V1, doi: 10.17632/h3mrm5dhxw.1
