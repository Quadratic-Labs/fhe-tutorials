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
A demo streamlit app is available on HuggingFace: https://huggingface.co/spaces/tzamoj-quadratic/FHETravelRouting

It can also be deployed locally in the usual way:

  1. Create a python virtual environnement and activate it.
  1. Install dependencies from requirements.txt:  pip install -r requirements.txt
  1. Launch the app: streamlit run app.py
  
The app depends also on files found in data/ folder:

  1. circuit.zip : use generate_circuit.py to recompile the circuit if necessary (on new network data).
  1. key.zip : cached keys. If not present, they will be generated.
  1. paris_quadratic_edges.geojson: map data extracted from OSM (overpass-turbo API). See Getting-Started.ipynb for more information.