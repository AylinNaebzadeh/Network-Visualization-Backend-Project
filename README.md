# Network Visualization Backend Project

## Overview

This repository contains the **backend part of the final project** developed for the **Complex Dynamic Networks** course.  

The full **project report** can be found here:

🔗 [Project Report PDF](https://github.com/AylinNaebzadeh/Network-Visualization-Backend-Project/blob/main/99522185_Aylin_Naebzadeh_Project.pdf)

The backend is implemented as a **Django REST API**, which provides data and computations for the [frontend network visualization app](https://github.com/AylinNaebzadeh/Network-Visualization-Frontend-Project). The APIs are implemented in ```complex_network_analyzer/analysis/views.py``` file.

---

## Dataset
For this project, we were given two Excel files. 
### `nodes.xlsx`

The dataset contains node information, including node IDs and labels. The dataset has 8 distinct labels from L1 to L7, plus Unknown label.

| #   | NodeId   | Labels   |
|-----|----------|---------|
| 1   | 35       | L2    |
| 2   | 40       | L2  |
| 3   | 114       | L5  |
| 4   | 117       | L5 |
| 5   | 128       | L5 |
| ... | ...      | ...     |
| 2705| 1154520  | Unknown |
| 2706| 1154524  | Unknown |
| 2707| 1154525  | Unknown |
| 2708| 1155073  | Unknown |

---

### `edges.xlsx`

The dataset contains edges between nodes:

| sourceNodeId | targetNodeId |
|--------------|--------------|
| 35           | 1033         |
| 35           | 103482       |
| 35           | 103515       |
| 35           | 1050679      |
| 35           | 1103960      |
| ...          | ...          |
| 853155       | 853116       |
| 1140289      | 853118       |
| 853118       | 853155       |
| 1155073      | 954315       |

---

## Technology Stack

- **Django REST** – Backend API framework  

### Important Libraries

- **NetworkX** – For network analysis  
- **Openpyxl** – Reading Excel files  
- **Pandas** – Data manipulation and processing  
- **NumPy** – Numerical operations
