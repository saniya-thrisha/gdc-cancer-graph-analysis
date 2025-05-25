from neo4j import GraphDatabase
import pandas as pd
import numpy as np

# To be configured as required
TSV_READ_LOCATION="C:\\Users\\user\\Downloads\\clinical.tsv"
CSV_WRITE_LOCATION="C:\\Users\\user\\Downloads\\clinical_cleaned.csv"

# Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"

# Load and clean the data
df = pd.read_csv(TSV_READ_LOCATION, sep='\t', dtype=str)
df = df.apply(lambda col: col.str.strip() if col.dtype == 'object' else col)
df.replace(r"^'--\s*$", np.nan, regex=True, inplace=True)

# Drop columns with more than 50% missing values
threshold = len(df) * 0.5
df = df.dropna(axis=1, thresh=threshold)

# Fill numerical columns with mean and categorical with mode
num_cols = df.select_dtypes(include=['number']).columns
cat_cols = df.select_dtypes(include=['object', 'category']).columns

for col in num_cols:
    df[col] = df[col].fillna(df[col].mean())

for col in cat_cols:
    mode = df[col].mode()
    if not mode.empty:
        df[col] = df[col].fillna(mode[0])

# Save cleaned dataframe to CSV for Neo4j import (Neo4j must access this file from its import dir)
df.to_csv(CSV_WRITE_LOCATION, index=False)



driver = GraphDatabase.driver(uri, auth=(username, password))

# Cypher query to import CSV and create nodes/relationships
query = """
LOAD CSV WITH HEADERS FROM 'file:///clinical_cleaned.csv' AS row


MERGE (p:Project {project_id: row.`project.project_id`})
ON CREATE SET p.name = row.`cases.submitter_id`

MERGE (c:Case {case_id: row.`cases.case_id`})
ON CREATE SET c.disease_type = row.`cases.disease_type`,
              c.index_date = row.`cases.index_date`,
              c.primary_site = row.`cases.primary_site`,
              c.submitter_id = row.`cases.submitter_id`
MERGE (p)-[:HAS_CASE]->(c)

MERGE (d:Demographic {demographic_id: row.`demographic.demographic_id`})
ON CREATE SET d.age_is_obfuscated = row.`demographic.age_is_obfuscated`,
              d.days_to_birth = row.`demographic.days_to_birth`,
              d.ethnicity = row.`demographic.ethnicity`,
              d.gender = row.`demographic.gender`,
              d.race = row.`demographic.race`,
              d.submitter_id = row.`demographic.submitter_id`,
              d.vital_status = row.`demographic.vital_status`,
              d.year_of_birth = row.`demographic.year_of_birth`
MERGE (c)-[:HAS_DEMOGRAPHIC_INFO]->(d)

MERGE (diag:Diagnosis {diagnosis_id: row.`diagnoses.diagnosis_id`})
ON CREATE SET diag.age_at_diagnosis = row.`diagnoses.age_at_diagnosis`,
              diag.ajcc_pathologic_m = row.`diagnoses.ajcc_pathologic_m`,
              diag.ajcc_pathologic_n = row.`diagnoses.ajcc_pathologic_n`,
              diag.ajcc_pathologic_stage = row.`diagnoses.ajcc_pathologic_stage`,
              diag.ajcc_pathologic_t = row.`diagnoses.ajcc_pathologic_t`,
              diag.ajcc_staging_system_edition = row.`diagnoses.ajcc_staging_system_edition`,
              diag.classification_of_tumor = row.`diagnoses.classification_of_tumor`,
              diag.days_to_last_follow_up = row.`diagnoses.days_to_last_follow_up`,
              diag.diagnosis_is_primary_disease = row.`diagnoses.diagnosis_is_primary_disease`,
              diag.icd_10_code = row.`diagnoses.icd_10_code`,
              diag.metastasis_at_diagnosis = row.`diagnoses.metastasis_at_diagnosis`,
              diag.morphology = row.`diagnoses.morphology`,
              diag.primary_diagnosis = row.`diagnoses.primary_diagnosis`,
              diag.prior_malignancy = row.`diagnoses.prior_malignancy`,
              diag.prior_treatment = row.`diagnoses.prior_treatment`,
              diag.site_of_resection_or_biopsy = row.`diagnoses.site_of_resection_or_biopsy`,
              diag.submitter_id = row.`diagnoses.submitter_id`,
              diag.tissue_or_organ_of_origin = row.`diagnoses.tissue_or_organ_of_origin`,
              diag.tumor_grade = row.`diagnoses.tumor_grade`
MERGE (c)-[:HAS_DIAGNOSIS]->(diag)
MERGE (d)-[:LINKED_TO]->(diag)

MERGE (t:Treatment {treatment_id: row.`treatments.treatment_id`})
ON CREATE SET t.days_to_treatment_start = row.`treatments.days_to_treatment_start`,
              t.initial_disease_status = row.`treatments.initial_disease_status`,
              t.submitter_id = row.`treatments.submitter_id`,
              t.treatment_intent_type = row.`treatments.treatment_intent_type`,
              t.treatment_or_therapy = row.`treatments.treatment_or_therapy`,
              t.treatment_type = row.`treatments.treatment_type`
MERGE (c)-[:RECEIVED_TREATMENT]->(t)
MERGE (diag)-[:TREATED_BY]->(t)
"""

# Function to run query in a transaction
def import_data(tx):
    tx.run(query)

# Run the query in a session
with driver.session() as session:
    session.execute_write(import_data)


driver.close()
