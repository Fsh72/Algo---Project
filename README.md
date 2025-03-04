# **Bidirectional Dijkstra-Based Contraction Hierarchy (CH)**
This repository contains an implementation of **Bidirectional Dijkstra with Contraction Hierarchy (CH)** to optimize shortest path queries on real-world road networks. 
The project compares **CH-based Bidirectional Dijkstra** across different datasets, including **Falcon, Colorado** for different node ordering.

## **📌 Features**
- **Graph Construction**: Uses OpenStreetMap data to build road networks.
- **Node Ordering Strategies**: Implements various ordering methods for CH preprocessing.
- **Contraction Hierarchy (CH)**: Contracts nodes and adds shortcut edges to optimize query efficiency.
- **Bidirectional Dijkstra**: Implements both Classic and CH-based versions.
- **Performance Comparison**: Measures preprocessing time, query time, and memory usage.

---

## **📂 Project Structure**
```
📁 Project Folder
│-- bidirectional_dijkstra_fixed.py  # Implements Bidirectional Dijkstra
│-- CH_fixed.py                      # Implements Contraction Hierarchy (CH)
│-- Denver.py                         # Runs CH & BiDi on Denver road network
│-- main.py                           # Runs CH & BiDi on Falcon road network
│-- README.md                         # This file (instructions & documentation)
```

---

## **🚀 Installation & Setup**
1. **Clone the repository**
   ```bash
   git clone [https://github.com/Fsh72/Algo---Project]
   cd Algo---Project
   ```

2. **Install dependencies**
   Make sure you have Python 3 installed, then install the required libraries:
   ```bash
   pip install osmnx networkx numpy pandas
   ```

---

## ** Running the Experiments**
### **Falcon, Colorado**
To run CH and Classic BiDi Dijkstra on **Falcon, Colorado**, execute:
```bash
python main.py
```
- This script:
  - Downloads the road network of Falcon.
  - Prepares the graph for CH and Classic BiDi Dijkstra.
  - Runs shortest path queries and measures performance.

---
**Observations:**
- **Falcon (small graph, ~500 nodes):** CH offers **no significant speedup** over Classic BiDi Dijkstra.
- **Denver (large graph):** CH shows a **small improvement** in query time but requires **more preprocessing time**.

---

## **🔧 Implementation Details**
### **1 Contraction Hierarchy (CH)**
- CH preprocesses the graph by:
  - **Ordering nodes** based on heuristic criteria.
  - **Contracting nodes** while preserving shortest paths.
  - **Adding shortcut edges** to optimize query performance.

### **2 Bidirectional Dijkstra**
- Two versions:
  - **Classic BiDi Dijkstra:** Expands search forward from the source and backward from the destination.
  - **CH-based BiDi Dijkstra:** Runs on the **contracted graph**, leading to faster queries.

---

## **🤝 Acknowledgments**
- **Barak's Code**: Node ordering strategies and CH construction were adapted from **Barak's work**.
- **Andy’s Contributions**: Assisted with **debugging** and **understanding core concepts** of CH and Python.
- **ChatGPT Assistance**: Helped in:
  - Converting MATLAB code to Python.
  - Debugging Python scripts.
  - Improving grammar in documentation.

---

## **🔗 GitHub Repository**
[🔗 Click Here to Access the Repository](https://github.com/Fsh72/Algo---Project)
