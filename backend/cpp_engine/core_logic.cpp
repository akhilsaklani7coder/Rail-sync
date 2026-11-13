#include "core_logic.h"
#include <vector>
#include <queue>
#include <algorithm>
#include <climits>
#include <cstring>

// Cross-platform Mutex & Lock Guard supporting both C++17 std::mutex and Win32 Critical Section
#if defined(_WIN32)
#include <windows.h>
class SystemMutex {
private:
    CRITICAL_SECTION cs;
public:
    SystemMutex() { InitializeCriticalSection(&cs); }
    ~SystemMutex() { DeleteCriticalSection(&cs); }
    void lock() { EnterCriticalSection(&cs); }
    void unlock() { LeaveCriticalSection(&cs); }
};
#else
#include <mutex>
class SystemMutex {
private:
    std::mutex m;
public:
    void lock() { m.lock(); }
    void unlock() { m.unlock(); }
};
#endif

class MutexGuard {
private:
    SystemMutex& m_ref;
public:
    explicit MutexGuard(SystemMutex& m) : m_ref(m) { m_ref.lock(); }
    ~MutexGuard() { m_ref.unlock(); }
};

// Global mutex guarding the critical section of the seat allocator
static SystemMutex g_allocator_mutex;

// Global counter for mutex verification tests
static SystemMutex g_counter_mutex;
static long long g_shared_counter = 0;

extern "C" {

EXPORT_API int get_engine_version() {
    return 2026;
}

EXPORT_API int allocate_seats(
    const int* available_seats,
    int available_count,
    int requested_count,
    int* out_allocated,
    int max_out
) {
    if (!available_seats || !out_allocated || requested_count <= 0 || max_out < requested_count) {
        return -2; // Invalid arguments
    }

    // Critical Section: Acquire mutual exclusion lock
    MutexGuard lock(g_allocator_mutex);

    if (available_count < requested_count) {
        return -1; // Insufficient seats
    }

    // Deterministic selection heuristic:
    // Sort / pick contiguous or best-span seats
    std::vector<int> candidates(available_seats, available_seats + available_count);
    std::sort(candidates.begin(), candidates.end());

    // Best-fit contiguous window search
    int best_start_idx = 0;
    int best_span = INT_MAX;

    for (int i = 0; i <= available_count - requested_count; ++i) {
        int span = candidates[i + requested_count - 1] - candidates[i];
        if (span < best_span) {
            best_span = span;
            best_start_idx = i;
            if (span == requested_count - 1) {
                // Perfect contiguous block found!
                break;
            }
        }
    }

    // Copy selected seats into caller's output buffer
    for (int k = 0; k < requested_count; ++k) {
        out_allocated[k] = candidates[best_start_idx + k];
    }

    return requested_count;
}

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
) {
    if (!edges_src || !edges_dst || !edges_weight || !out_path || !out_total_distance) {
        return -2;
    }
    if (num_nodes <= 0 || start_node < 0 || target_node < 0 ||
        start_node >= num_nodes || target_node >= num_nodes) {
        return -2;
    }

    if (start_node == target_node) {
        out_path[0] = start_node;
        *out_total_distance = 0;
        return 1;
    }

    // Adjacency list: node -> vector of (neighbor, weight)
    std::vector<std::vector<std::pair<int, int> > > adj(num_nodes);
    for (int i = 0; i < num_edges; ++i) {
        int u = edges_src[i];
        int v = edges_dst[i];
        int w = edges_weight[i];
        if (u >= 0 && u < num_nodes && v >= 0 && v < num_nodes && w >= 0) {
            adj[u].push_back(std::make_pair(v, w));
        }
    }

    // Min-heap priority queue: (distance, node)
    typedef std::pair<int, int> PII;
    std::priority_queue<PII, std::vector<PII>, std::greater<PII> > pq;

    std::vector<int> dist(num_nodes, INT_MAX);
    std::vector<int> parent(num_nodes, -1);

    dist[start_node] = 0;
    pq.push(std::make_pair(0, start_node));

    while (!pq.empty()) {
        PII top = pq.top();
        pq.pop();
        int d = top.first;
        int u = top.second;

        if (d > dist[u]) continue;
        if (u == target_node) break; // Reached target with shortest distance

        for (size_t idx = 0; idx < adj[u].size(); ++idx) {
            int v = adj[u][idx].first;
            int weight = adj[u][idx].second;

            if (dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                parent[v] = u;
                pq.push(std::make_pair(dist[v], v));
            }
        }
    }

    if (dist[target_node] == INT_MAX) {
        *out_total_distance = -1;
        return -1; // Unreachable
    }

    // Reconstruct path
    std::vector<int> path;
    for (int curr = target_node; curr != -1; curr = parent[curr]) {
        path.push_back(curr);
    }
    std::reverse(path.begin(), path.end());

    int path_length = static_cast<int>(path.size());
    if (path_length > max_path_len) {
        return -2; // Buffer too small
    }

    for (int i = 0; i < path_length; ++i) {
        out_path[i] = path[i];
    }
    *out_total_distance = dist[target_node];

    return path_length;
}

EXPORT_API int verify_mutex_lock(int iterations) {
    MutexGuard lock(g_counter_mutex);
    for (int i = 0; i < iterations; ++i) {
        g_shared_counter++;
    }
    return static_cast<int>(g_shared_counter);
}

} // extern "C"
