
from flask import Flask, request, render_template,session
from neo4j import GraphDatabase
import pandas as pd
import plotly.express as px
import json

# To be configured as required

# Neo4j connection
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"


app = Flask(__name__)
app.secret_key = 'your_secret_key'


driver = GraphDatabase.driver(uri, auth=(username, password))


# Dropdown Population
def get_dropdown_values():
    with driver.session() as session:
        diagnoses = session.run("""
            MATCH (d:Diagnosis)
            WHERE d.primary_diagnosis IS NOT NULL
            RETURN DISTINCT d.primary_diagnosis AS val
            ORDER BY val
        """)
        statuses = session.run("""
            MATCH (d:Demographic)
            WHERE d.vital_status IS NOT NULL
            RETURN DISTINCT d.vital_status AS val
            ORDER BY val
        """)
        genders = session.run("""
            MATCH (d:Demographic)
            WHERE d.gender IS NOT NULL
            RETURN DISTINCT d.gender AS val
            ORDER BY val
        """)
        treatments = session.run("""
            MATCH (t:Treatment)
            WHERE t.treatment_type IS NOT NULL
            RETURN DISTINCT t.treatment_type AS val
            ORDER BY val
        """)
        return (
            [r["val"] for r in diagnoses],
            [r["val"] for r in statuses],
            [r["val"] for r in genders],
            [r["val"] for r in treatments],
        )


# Data Query Function
def query_data(filters):
    query_parts = []
    query_parts.append("""
    MATCH (demo:Demographic)-[:LINKED_TO]->(diag:Diagnosis)
    MATCH (diag)-[:TREATED_BY]->(t:Treatment)
    """)
    where_conditions = []
    params = {}


    if filters["diagnosis"] != 'All':
        where_conditions.append("diag.primary_diagnosis = $diagnosis")
        params["diagnosis"] = filters["diagnosis"]
    if filters["status"] != 'All':
        where_conditions.append("demo.vital_status = $status")
        params["status"] = filters["status"]
    if filters["gender"] != 'All':
        where_conditions.append("demo.gender = $gender")
        params["gender"] = filters["gender"]
    if filters["treatment"] != 'All':
        where_conditions.append("t.treatment_type = $treatment")
        params["treatment"] = filters["treatment"]
    if where_conditions:
        query_parts.append("WHERE " + " AND ".join(where_conditions))


    query_parts.append("""
    RETURN diag.primary_diagnosis AS Diagnosis,
           demo.vital_status AS Status,
           demo.gender AS Gender,
           t.treatment_type AS TreatmentType,
           COUNT(*) AS Count
    ORDER BY Count DESC
    """)
    full_query = "\n".join(query_parts)


    with driver.session() as session:
        records = session.run(full_query, **params)
        return [record.data() for record in records]


# Root Route
@app.route("/", methods=["GET", "POST"])
def index():
    filters = {
        "Diagnosis": request.form.get("diagnosis", "All"),
        "Status": request.form.get("status", "All"),
        "Gender": request.form.get("gender", "All"),
        "Treatment Type": request.form.get("treatment", "All")
    }
    result = []
    applied_filters = {}
    if request.method == "POST":
        applied_filters = {k: v for k, v in filters.items() if v != "All"}
        result = query_data({
            "diagnosis": filters["Diagnosis"],
            "status": filters["Status"],
            "gender": filters["Gender"],
            "treatment": filters["Treatment Type"]
        })

    diagnoses, statuses, genders, treatments = get_dropdown_values()
    session['analysis_data'] = json.dumps(result)
    return render_template('index.html',
        filters={k.lower().replace(" ", "_"): v for k, v in filters.items()},
        result=result,
        diagnoses=diagnoses,
        statuses=statuses,
        genders=genders,
        treatments=treatments,
        applied_filters=applied_filters
    )


# Analysis Route
@app.route("/analysis", methods=["GET"])
def analysis():
    data_json = session.get('analysis_data')
    if not data_json:
        return "<h3>No analysis data found. Please perform a search first.</h3>"

    data = json.loads(data_json)
    df = pd.DataFrame(data)

    # Plotly figures
    bar_fig = px.bar(df, x="TreatmentType", y="Count", color="Gender", barmode="group", title="Treatment Type by Gender")
    pie_fig = px.pie(df, names="Status", values="Count", title="Vital Status Distribution")
   
    # Convert to HTML strings
    bar_html = bar_fig.to_html(full_html=False)
    pie_html = pie_fig.to_html(full_html=False)
   
    return render_template("analysis.html",
                           bar_html=bar_html,
                           pie_html=pie_html)

# Run the App
if __name__ == "__main__":
    app.run(debug=True)
