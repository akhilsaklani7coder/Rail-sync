#include "core_logic.h"
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int main(int argc, char *argv[]) {
  if (argc < 2) {
    std::cout << "{\"error\": \"Missing command argument. Use: allocate, "
                 "dijkstra, or test_mutex\"}\n";
    return 1;
  }

  std::string cmd = argv[1];

  if (cmd == "version") {
    std::cout << "{\"version\": " << get_engine_version()
              << ", \"status\": \"OK\"}\n";
    return 0;
  }

  if (cmd == "allocate") {
    // Expected args: count requested seat1 seat2 seat3 ...
    if (argc < 4) {
      std::cout << "{\"error\": \"Invalid allocate args\"}\n";
      return 1;
    }
    int requested = std::stoi(argv[2]);
    int avail_count = argc - 3;
    std::vector<int> avail(avail_count);
    for (int i = 0; i < avail_count; ++i) {
      avail[i] = std::stoi(argv[3 + i]);
    }

    std::vector<int> out(requested);
    int res = allocate_seats(avail.data(), avail_count, requested, out.data(),
                             requested);

    if (res < 0) {
      std::cout << "{\"status\": \"FAILED\", \"code\": " << res << "}\n";
    } else {
      std::cout << "{\"status\": \"SUCCESS\", \"allocated\": [";
      for (int i = 0; i < res; ++i) {
        std::cout << out[i] << (i + 1 < res ? "," : "");
      }
      std::cout << "], \"method\": \"C++ std::mutex & Contiguous Window "
                   "Heuristic\"}\n";
    }
    return 0;
  }

  if (cmd == "dijkstra") {
    int start = 0;  // NDLS
    int target = 2; // DDN
    if (argc >= 4) {
      start = std::stoi(argv[2]);
      target = std::stoi(argv[3]);
    }

    int num_nodes = 8;
    std::vector<int> src_edges;
    std::vector<int> dst_edges;
    std::vector<int> weight_edges;

    if (argc > 4) {
      num_nodes = std::stoi(argv[4]);
      int num_edge_triplets = (argc - 5) / 3;
      for (int i = 0; i < num_edge_triplets; ++i) {
        src_edges.push_back(std::stoi(argv[5 + i * 3]));
        dst_edges.push_back(std::stoi(argv[6 + i * 3]));
        weight_edges.push_back(std::stoi(argv[7 + i * 3]));
      }
    } else {
      int def_src[] = {0, 0, 1, 0, 0, 0, 5, 6, 3};
      int def_dst[] = {1, 2, 2, 3, 4, 5, 6, 4, 7};
      int def_w[] = {250, 302, 52, 512, 308, 1384, 493, 625, 300};
      src_edges.assign(def_src, def_src + 9);
      dst_edges.assign(def_dst, def_dst + 9);
      weight_edges.assign(def_w, def_w + 9);
    }

    int num_edges = src_edges.size();
    std::vector<int> path(num_nodes + 4, 0);
    int total_dist = 0;
    int len = find_shortest_path_dijkstra(num_nodes, num_edges, src_edges.data(),
                                          dst_edges.data(), weight_edges.data(), start,
                                          target, path.data(), path.size(), &total_dist);

    if (len < 0) {
      std::cout << "{\"status\": \"UNREACHABLE\", \"code\": " << len << ", \"distance_km\": -1, \"path\": []}\n";
    } else {
      std::cout << "{\"status\": \"SUCCESS\", \"distance_km\": " << total_dist
                << ", \"path\": [";
      for (int i = 0; i < len; ++i) {
        std::cout << path[i] << (i + 1 < len ? "," : "");
      }
      std::cout << "], \"nodes_visited\": " << len << "}\n";
    }
    return 0;
  }

  if (cmd == "test_mutex") {
    int iters = (argc >= 3) ? std::stoi(argv[2]) : 5000;
    int final_val = verify_mutex_lock(iters);
    std::cout << "{\"status\": \"SUCCESS\", \"counter\": " << final_val
              << ", \"iterations\": " << iters << "}\n";
    return 0;
  }

  std::cout << "{\"error\": \"Unknown command\"}\n";
  return 1;
}
