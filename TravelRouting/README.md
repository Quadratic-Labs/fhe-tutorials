# Travel Routing
## Introduction
Geolocalisation is sensitive personal data that can easily be used to identify and deduce further information about oneself such as home address, work, favourite foods, hobbies, and more.
Nonetheless, almost all of us use some form of maps on smartphones to compute best itinerairies when traveling.
We thus accept to send our localisation to an external party who could potentially use it for other purposes.

We propose in this tutorial to showcase how Zama's homomorphic encryption could be used to preserve our localisation's privacy while still offering an itinerary computation service. 
In this scenario, the server does not learn anything about a client's position at anytime as it sees only encrypted data.

## Achieving Privacy
In our application demo:

  1. The client owns its position and its target destination. The client never shares this information in clear with the server.
  1. The server owns map data. It only shares with the client local map data useful for the itinerary.

To achieve this, FHE is used to implement what is known as Oblivious Transfer (OT): the server precomputes for each origin and destination pair its corresponding shortest path, and the client retrieves the shortest path for one pair without the server gaining any information as to which pair was selected.

Oblivious transfer is easily implemented using Zama's concrete library by a single Table Lookup (TLU).

## Demo App
A demo streamlit app is available on HuggingFace: https://huggingface.co/spaces/Quadratic-Labs/PrivateTravelRouting-FHE

It can also be deployed locally in the usual way:

  1. Create a python virtual environnement and activate it.
  1. Install dependencies from requirements.txt:  pip install -r requirements.txt
  1. Launch the app: streamlit run app.py
  
The app depends also on files found in data/ folder:

  1. circuit.zip : use generate_circuit.py to recompile the circuit if necessary (on new network data).
  1. key.zip : cached keys. If not present, they will be generated.
  1. paris_quadratic_edges.geojson: map data extracted from OSM (overpass-turbo API). See Getting-Started.ipynb for more information.


## Exploring Shortest-Paths Algorithms
The demo app uses a single oblivious transfert to achieve privacy, relying on the server to pre-compute every possible combinations. However, the server might also want to include trafic data from its users to gain information about estimated time at arrival (ETA). In this case, it would be probably infeasible to compute all possible combinations.

We started this project by investigating solutions where the server would compute shortest-paths on the fly given a graph. 
There are several algorithms to choose from, of which we looked at dijkstra, bellman-ford and floyd-warshall. However, their performances are not as expected due to hidden information.

In fact, a brute force approach like floyd-warshall takes O(N^3)-time. Other methods make use of optimisations using stopping criteria, priority queues and other similar constructs. It is unclear whether these can bring any advantage in encrypted world as we cannot do if-else constructs. Still, this can be subject of further investigation, for exemple via heap implementations.

## Size of the map
Origins and destinations are currently restricted to a set of intersections of street segments on a localised region. There are 2 improvements that we would like to further investigate.

The first is to be able to select any point on the network for origin and destination. One way to do it would be to compute distance between the origin and the 2 closest intersections (nodes), same for destination, and proceed with current algorithm 4 times. However, we expect this to be a rather inefficient way of doing things.

The second improvement would be the ability to select points far apart, departing from the very localised map to a much larger map. Today, this seems to be a hard task to do. One possible approach would be to approximate optimum via aggregations first. However, this is still very much open.
