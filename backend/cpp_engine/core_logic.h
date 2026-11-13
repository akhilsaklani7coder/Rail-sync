#ifndef CORE_LOGIC_H
#define CORE_LOGIC_H

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32
    #define EXPORT_API __declspec(dllexport)
#else
    #define EXPORT_API __attribute__((visibility("default")))
#endif

/**
 * C++ Critical Section & Deterministic Seat Allocator
 * Uses std::mutex to protect shared allocator state and provides contiguous/optimal seat selection.
 *
 * @param available_seats Pointer to array of available seat IDs
 * @param available_count Total available seats in array
 * @param requested_count Number of seats requested by passenger(s)
 * @param out_allocated Pointer to caller-allocated buffer for chosen seat IDs
 * @param max_out Capacity of out_allocated buffer
 * @return Number of allocated seats, or -1 on insufficient seats, -2 on invalid arguments
 */
EXPORT_API int allocate_seats(
    const int* available_seats,
    int available_count,
    int requested_count,
    int* out_allocated,
    int max_out
);

/**
 * Dijkstra Shortest Path Calculation over Station Network Graph
 * Implemented using C++17 std::priority_queue (Min-Heap).
 *
 * @param num_nodes Total number of nodes (stations)
 * @param num_edges Total number of directed/undirected edges
 * @param edges_src Array of source node IDs (0-indexed or 1-indexed normalized)
 * @param edges_dst Array of destination node IDs
 * @param edges_weight Array of edge distances (positive integers)
 * @param start_node ID of origin station
 * @param target_node ID of destination station
 * @param out_path Caller-allocated buffer for reconstructed path (node sequence)
 * @param max_path_len Capacity of out_path buffer
 * @param out_total_distance Pointer to int receiving total shortest distance
 * @return Number of nodes in path, or -1 if target unreachable, -2 on invalid input
 */
EXPORT_API int find_shortest_path_dijkstra(
    int num_nodes,
    int num_edges,
    const int* edges_src,
    const int* edges_dst,
    const int* edges_weight,
    int start_node,
    int target_node,
    int* out_path,
    int max_path_len,
    int* out_total_distance
);

/**
 * Mutex Concurrency Verification
 * Demonstrates mutual exclusion by executing concurrent increment operations in a critical section.
 *
 * @param iterations Number of iterations
 * @return Current value of protected shared counter
 */
EXPORT_API int verify_mutex_lock(int iterations);

/**
 * Engine Diagnostic and ABI Version
 */
EXPORT_API int get_engine_version();

#ifdef __cplusplus
}
#endif

#endif // CORE_LOGIC_H
