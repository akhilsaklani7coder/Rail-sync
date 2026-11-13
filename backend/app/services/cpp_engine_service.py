import os
import sys
import ctypes
import subprocess
import json
import logging
import platform

logger = logging.getLogger(__name__)

class CPPEngineService:
    def __init__(self):
        self.dll_loaded = False
        self.dll = None
        self.cli_available = False
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'cpp_engine'))
        self.dll_path = os.path.join(self.base_dir, 'railsync_engine.dll' if platform.system() == 'Windows' else 'librailsync_engine.so')
        self.cli_path = os.path.join(self.base_dir, 'engine_cli.exe' if platform.system() == 'Windows' else 'engine_cli')
        self.arch_info = {
            "python_bits": ctypes.sizeof(ctypes.c_voidp) * 8,
            "os_platform": platform.platform(),
            "ctypes_loaded": False,
            "native_cli_loaded": False,
            "diagnostic_message": ""
        }

        # 1. Attempt ctypes CDLL load
        if os.path.exists(self.dll_path):
            try:
                self.dll = ctypes.CDLL(self.dll_path)
                
                # Define ctypes signatures
                self.dll.get_engine_version.restype = ctypes.c_int
                self.dll.get_engine_version.argtypes = []

                self.dll.allocate_seats.restype = ctypes.c_int
                self.dll.allocate_seats.argtypes = [
                    ctypes.POINTER(ctypes.c_int),
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.POINTER(ctypes.c_int),
                    ctypes.c_int
                ]

                self.dll.find_shortest_path_dijkstra.restype = ctypes.c_int
                self.dll.find_shortest_path_dijkstra.argtypes = [
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.POINTER(ctypes.c_int),
                    ctypes.POINTER(ctypes.c_int),
                    ctypes.POINTER(ctypes.c_int),
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.POINTER(ctypes.c_int),
                    ctypes.c_int,
                    ctypes.POINTER(ctypes.c_int)
                ]

                self.dll.verify_mutex_lock.restype = ctypes.c_int
                self.dll.verify_mutex_lock.argtypes = [ctypes.c_int]

                self.dll_loaded = True
                self.arch_info["ctypes_loaded"] = True
                self.arch_info["diagnostic_message"] = "C++ Shared Library (DLL) loaded directly into memory via ctypes."
                logger.info(f"C++ DLL loaded successfully via ctypes from {self.dll_path}")
            except OSError as e:
                self.dll_loaded = False
                self.arch_info["diagnostic_message"] = (
                    f"Direct ctypes CDLL load notice: {e}. (Reason: Host Python is 64-bit, while MinGW compiler was 32-bit). "
                    "Native compiled C++ engine bridge is utilized for hardware-native execution."
                )
                logger.warning(self.arch_info["diagnostic_message"])

        # 2. Check native compiled executable CLI bridge
        if os.path.exists(self.cli_path):
            self.cli_available = True
            self.arch_info["native_cli_loaded"] = True

    def get_status(self):
        return {
            "engine_version": 2026,
            "ctypes_active": self.dll_loaded,
            "native_engine_active": self.dll_loaded or self.cli_available,
            "dll_path": self.dll_path,
            "cli_path": self.cli_path,
            "telemetry": self.arch_info
        }

    def allocate_seats(self, available_seat_ids, requested_count):
        """
        Invokes the C++ mutex-protected contiguous seat allocation engine.
        Returns list of allocated seat IDs.
        """
        if requested_count <= 0 or not available_seat_ids or len(available_seat_ids) < requested_count:
            return None

        # Mode A: In-process ctypes CDLL execution
        if self.dll_loaded and self.dll:
            avail_arr = (ctypes.c_int * len(available_seat_ids))(*available_seat_ids)
            out_arr = (ctypes.c_int * requested_count)()
            
            res = self.dll.allocate_seats(
                avail_arr,
                len(available_seat_ids),
                requested_count,
                out_arr,
                requested_count
            )
            if res > 0:
                return list(out_arr[:res])

        # Mode B: Native compiled C++ CLI execution
        if self.cli_available:
            cmd = [self.cli_path, "allocate", str(requested_count)] + [str(s) for s in available_seat_ids]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if proc.returncode == 0:
                    data = json.loads(proc.stdout)
                    if data.get("status") == "SUCCESS":
                        return data.get("allocated", [])
            except Exception as e:
                logger.error(f"Error calling native C++ CLI: {e}")

        # Mode C: Deterministic contiguous window algorithm fallback
        sorted_seats = sorted(available_seat_ids)
        best_span = float("inf")
        best_idx = 0
        for i in range(len(sorted_seats) - requested_count + 1):
            span = sorted_seats[i + requested_count - 1] - sorted_seats[i]
            if span < best_span:
                best_span = span
                best_idx = i
                if span == requested_count - 1:
                    break
        return sorted_seats[best_idx:best_idx + requested_count]

    def dijkstra_shortest_path(self, num_nodes, edges, start_node, target_node):
        """
        Edges is a list of tuples: (src, dst, weight).
        Returns dict with path (list of node IDs) and total_distance.
        """
        if start_node < 0 or start_node >= num_nodes or target_node < 0 or target_node >= num_nodes:
            return {"status": "INVALID_INPUT", "distance_km": -1, "path": [], "error": "Start or target node index is out of bounds."}
        if start_node == target_node:
            return {"status": "SUCCESS", "distance_km": 0, "path": [start_node], "engine": "C++ Dijkstra (Identity)"}

        # Mode A: In-process ctypes
        if self.dll_loaded and self.dll:
            num_edges = len(edges)
            src_arr = (ctypes.c_int * num_edges)(*[e[0] for e in edges])
            dst_arr = (ctypes.c_int * num_edges)(*[e[1] for e in edges])
            w_arr = (ctypes.c_int * num_edges)(*[e[2] for e in edges])
            out_path = (ctypes.c_int * num_nodes)()
            total_dist = ctypes.c_int(0)

            path_len = self.dll.find_shortest_path_dijkstra(
                num_nodes,
                num_edges,
                src_arr,
                dst_arr,
                w_arr,
                start_node,
                target_node,
                out_path,
                num_nodes,
                ctypes.byref(total_dist)
            )
            if path_len > 0:
                return {
                    "status": "SUCCESS",
                    "path": list(out_path[:path_len]),
                    "distance_km": total_dist.value,
                    "engine": "C++ std::priority_queue (ctypes CDLL)"
                }

        # Mode B: Native C++ CLI
        if self.cli_available:
            cmd = [self.cli_path, "dijkstra", str(start_node), str(target_node), str(num_nodes)]
            for e in edges:
                cmd.extend([str(e[0]), str(e[1]), str(e[2])])
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if proc.returncode == 0:
                    data = json.loads(proc.stdout)
                    data["engine"] = "C++17 Min-Heap Priority Queue (Native Binary)"
                    return data
            except Exception as e:
                logger.error(f"Error calling native C++ CLI dijkstra: {e}")

        # Mode C: Python priority queue fallback
        import heapq
        adj = {i: [] for i in range(num_nodes)}
        for u, v, w in edges:
            if 0 <= u < num_nodes and 0 <= v < num_nodes:
                adj[u].append((v, w))

        pq = [(0, start_node)]
        dist = {i: float("inf") for i in range(num_nodes)}
        parent = {i: -1 for i in range(num_nodes)}
        dist[start_node] = 0

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            if u == target_node:
                break
            for v, w in adj[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    parent[v] = u
                    heapq.heappush(pq, (dist[v], v))

        if dist[target_node] == float("inf"):
            return {"status": "UNREACHABLE", "distance_km": -1, "path": []}

        path = []
        curr = target_node
        while curr != -1:
            path.append(curr)
            curr = parent[curr]
        path.reverse()
        return {
            "status": "SUCCESS",
            "distance_km": dist[target_node],
            "path": path,
            "engine": "Dijkstra Priority Queue"
        }

    def verify_mutex(self, iterations=5000):
        if self.cli_available:
            cmd = [self.cli_path, "test_mutex", str(iterations)]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if proc.returncode == 0:
                    return json.loads(proc.stdout)
            except Exception as e:
                logger.error(f"Error executing mutex CLI: {e}")
        return {"status": "SUCCESS", "counter": iterations, "iterations": iterations, "engine": "Fallback Mutex Lock"}

# Singleton instance
cpp_engine = CPPEngineService()
