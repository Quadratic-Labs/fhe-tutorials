# Travel Routing
## Introduction
Geolocalisation is sensitive personal data that can easily be used to identify and deduce further information about oneself such as home address, work, favourite foods, hobbies, and more.
Nonetheless, almost all of us use some form of maps on smartphones to compute best itinerairies when traveling.
We thus accept to send our localisation to an external party who could potentially use it for other purposes.

We propose in this tutorial to showcase how Zama's homomorphic encryption could be used to preserve our localisation's privacy while still offering an itinerary computation service. 
In this scenario, the server does not learn anything about a client's position at anytime as it sees only encrypted data.

## Achieving Privacy
We identify 2 ways to achieve privacy that can be used in different usecases:

  1. Server owns map data, client owns origin and destination: this is similar to oblivious transfert (OT). The server knows a collection of shortest routes between all origins and destinations. The client chooses anonymously one such route (origin and destination pair). With OT, the server learns nothing new, while the client learns only the shortest path selected.
  1. Client owns map data: in this case, the server provides the algorithm and compute power. The map data is sent encrypted to the server, which learns nothing at all from the map, origin and destination altogether.

There is also a variant where the client does not know which destination to choose, but instead would like the nearest destinations having some attributes: for example, being restaurants.

## Shortest-Paths Algorithms
There are several algorithms to choose from. We have explored dijkstra, bellman-ford, floyd-warshall. However, there performances must be reviewed taking into account the following remark:

> Choosing 1 element out of N anonymously requires O(N)-time. In essence, we would like to be able to index an array with an encrypted index. However, that is not possible as is, but requires performing a dot-product with a selector array. For example, to choose the first element of an array of 3, we would send (encrypted) the selector [1, 0, 0].

Now, when we analyse performances for the different algorithms, we obtain:

  1. Dijkstra : todo
  1. Bellman-Ford: todo
  1. Floyd-Warshall: todo
  1. Simple: todo

At any rate, we obtain:

  1. O(N^3)-time for selecting a path from a precomputed array of N^2 paths of length O(N).
  1. O(N^3)-time for finding shortest path on an encrypted graph.

TODO