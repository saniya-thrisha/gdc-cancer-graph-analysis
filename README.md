# 🧪 GDC Cancer Data Analysis using Neo4j and Flask

This project focuses on analyzing cancer-related clinical data from the **National Cancer Institute's Genomic Data Commons (GDC)** using a graph-based approach. By leveraging **Neo4j** and **Flask**, this project transforms traditionally tabular datasets into graph structures to uncover deeper, more meaningful insights that are difficult to extract from relational databases.

---

## 📊 Project Overview

The GDC hosts **86 projects** across **69 primary sites**. For this project, I selected data from the **"HCMI-CMDC"** project under the **"Bronchus and Lung"** primary site.

Instead of analyzing data in conventional table formats, this project models it as a **graph of interconnected entities and relationships**. This transformation allows for more flexible, dynamic, and meaningful querying of complex, linked clinical data.

---

## 🚀 Technologies Used

- Python 3
- Flask
- Pandas
- Neo4j (Graph Database)
- Plotly (Visualization)
- Jinja2 (Templating)
- HTML / CSS (Frontend)

---

## 🧰 Architecture Diagram

> ![Image](https://github.com/user-attachments/assets/39f1781b-c085-4287-bf2e-8f43e9a9a6b1)
> `![Architecture Diagram](path/to/architecture.png)`

---

## ✅ Steps and Methodology

### 1. 🔍 Data Cleaning

- Downloaded raw `.tsv` data from the GDC portal.
- Dropped columns with more than 50% missing values.
- Filled missing values:
  - **Numerical columns** → filled with mean
  - **Categorical columns** → filled with mode
- Saved cleaned data as `.csv` for Neo4j import.

---

### 2. 🧠 Creating the Graph Database (Neo4j)

Using the **Neo4j Python Driver**, I built a graph database from the cleaned data via Cypher queries.

#### **Entities**:
- `Project` – Unique cancer study/project
- `Case` – Individual patient record
- `Demographic` – Age, gender, ethnicity info
- `Diagnosis` – Disease-specific details (e.g., stage, morphology)
- `Treatment` – Therapy or treatment administered

#### **Relationships**:
- `Project → HAS_CASE → Case`
- `Case → HAS_DEMOGRAPHIC_INFO → Demographic`
- `Case → HAS_DIAGNOSIS → Diagnosis`
- `Demographic → LINKED_TO → Diagnosis`
- `Case → RECEIVED_TREATMENT → Treatment`
- `Diagnosis → TREATED_BY → Treatment`

This structure supports powerful graph queries that enable highly contextual insights.

---

### 3. 🔎 Querying the Graph with Neo4j Driver

- Dropdown values (Diagnosis, Status, Gender, Treatment) are populated dynamically by querying the graph.
- User filters are converted into dynamic Cypher `WHERE` clauses.
- Results are retrieved and formatted for visualization.

---

### 4. 🌐 Flask + Plotly Web Interface

The interface is built using Flask with two main routes:

- `/` – Filter form + tabular results
- `/analysis` – Visualization page with charts

**Plotly** is used for:
- **Grouped Bar Charts** (e.g., Treatment Type by Gender)
- **Pie Charts** (e.g., Vital Status distribution)

---

## 🖼️ Application Screenshots

### Home Page:
> Filter clinical data and view results in a table

![Image](https://github.com/user-attachments/assets/5320e4a3-c251-4886-803c-307ed82b12d2)

### Analysis Page:
> Shows insights on filtered data

![Image](https://github.com/user-attachments/assets/c32336a7-e933-4ada-83c6-14ffadbd5fe4)

![Image](https://github.com/user-attachments/assets/81b5c0b1-1e2a-4764-aa37-7962be8d5a56)

---

## 📙 Reference

- GDC Cancer Portal: [https://portal.gdc.cancer.gov/](https://portal.gdc.cancer.gov/)

---
