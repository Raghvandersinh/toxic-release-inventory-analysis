import json

queries = {
    "Waste_By_Location":
 """
        WITH waste_data AS (
            SELECT 
                tfh.city,
                tfh.county,
                tfh.state,
                trf.doc_ctrl_num,
                trf.reporting_year,
                ROUND(SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC), 2) AS total_release
            FROM tri_reporting_form trf
            JOIN tri_facility_history tfh ON trf.tri_facility_id = tfh.tri_facility_id
            JOIN tri_form_total tft ON trf.doc_ctrl_num = tft.doc_ctrl_num
            GROUP BY tfh.city, tfh.county, tfh.state, trf.doc_ctrl_num, trf.reporting_year
            Order By total_release DESC
        )
        SELECT 
            city,
            county,
            state,
            SUM(total_release) AS total_release
        FROM waste_data
        GROUP BY city, county, state
        ORDER BY total_release DESC;
""",
    
    "Waste_By_Location_2020s": 
    """
        WITH waste_data AS (
            SELECT 
                tfh.city,
                tfh.county,
                tfh.state,
                trf.doc_ctrl_num,
                trf.reporting_year,
                ROUND(SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC), 2) AS total_release
            FROM tri_reporting_form trf
            JOIN tri_facility_history tfh ON trf.tri_facility_id = tfh.tri_facility_id
            JOIN tri_form_total tft ON trf.doc_ctrl_num = tft.doc_ctrl_num
            WHERE trf.reporting_year >= 2020
            GROUP BY tfh.city, tfh.county, tfh.state, trf.doc_ctrl_num, trf.reporting_year
            Order By total_release DESC
        )
        SELECT 
            city,
            county,
            state,
            SUM(total_release) AS total_release
        FROM waste_data
        GROUP BY city, county, state
        ORDER BY total_release DESC;
    """,

    "Total_Waste_Throughout_top_10": """
        WITH release_totals AS (
            SELECT 
                trf.tri_facility_id,
                SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) AS Total_Release
            FROM tri_form_total tft
            JOIN tri_reporting_form trf ON tft.doc_ctrl_num = trf.doc_ctrl_num
            GROUP BY trf.tri_facility_id
        ),
        
        top_10_facilities AS (
            SELECT 
                tfh.tri_facility_id,
                MAX(tfh.name) AS name,
                SUM(rt.Total_Release) AS total_facility_release
            FROM release_totals rt
            JOIN tri_facility_history tfh ON rt.tri_facility_id = tfh.tri_facility_id
            GROUP BY tfh.tri_facility_id
            ORDER BY total_facility_release DESC
            LIMIT 10
        )
        
        SELECT
            t10.name,
            ROUND(SUM(rt.Total_Release), 2) AS total_release,
            DATE_TRUNC('month', tfh.create_date) AS create_month
        FROM top_10_facilities t10
        JOIN tri_facility_history tfh ON t10.tri_facility_id = tfh.tri_facility_id
        JOIN release_totals rt ON tfh.tri_facility_id = rt.tri_facility_id
        GROUP BY t10.name, DATE_TRUNC('month', tfh.create_date)
        ORDER BY create_month, name;
    """
}

for x in queries:
    queries[x] = queries[x].replace('\n', ' ')
    queries[x] = " ".join(queries[x].split())
with open('queries.json', 'w') as f:
    json.dump(queries, f, indent=4)