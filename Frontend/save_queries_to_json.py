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
                trf.tri_chem_id,
                ROUND(SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC), 2) AS total_release,
                ROUND(SUM(tft.total_land_release::NUMERIC),2) as total_land_release,
                ROUND(SUM(tft.total_air_release::NUMERIC),2) as total_air_release,
                ROUND(SUM(tft.total_water_release::NUMERIC),2) as total_water_release
            FROM tri_reporting_form trf
            JOIN tri_facility_history tfh ON trf.tri_facility_id = tfh.tri_facility_id
            JOIN tri_form_total tft ON trf.doc_ctrl_num = tft.doc_ctrl_num
            GROUP BY tfh.city, tfh.county, tfh.state, trf.doc_ctrl_num, trf.reporting_year, trf.tri_chem_id
            Order By total_release DESC
        )
        SELECT 
            city,
            county,
            state,
            COUNT(DISTINCT tri_chem_id) AS unique_chemical_count,
            SUM(total_release) AS total_release,
            SUM(total_land_release) AS total_land_release,
            SUM(total_water_release) AS total_water_release,
            SUM(total_air_release) AS total_air_release,
            ARRAY_AGG(DISTINCT tri_chem_id ORDER BY tri_chem_id) AS chemical_ids

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
                COUNT(DISTINCT tri_chem_id) AS unique_chemical_count,
                trf.doc_ctrl_num,
                trf.reporting_year,
                trf.tri_chem_id,
                ROUND(SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC), 2) AS total_release,
                ROUND(SUM(tft.total_land_release::NUMERIC),2) as total_land_release,
                ROUND(SUM(tft.total_air_release::NUMERIC),2) as total_air_release,
                ROUND(SUM(tft.total_water_release::NUMERIC),2) as total_water_release
            FROM tri_reporting_form trf
            JOIN tri_facility_history tfh ON trf.tri_facility_id = tfh.tri_facility_id
            JOIN tri_form_total tft ON trf.doc_ctrl_num = tft.doc_ctrl_num
            WHERE trf.reporting_year >= 2020
            GROUP BY tfh.city, tfh.county, tfh.state, trf.doc_ctrl_num, trf.reporting_year, trf.tri_chem_id
            Order By total_release DESC
        )
        SELECT
            city,
            county,
            state,
            COUNT(DISTINCT tri_chem_id) AS unique_chemical_count,
            SUM(total_release) AS total_release,
            SUM(total_land_release) AS total_land_release,
            SUM(total_water_release) AS total_water_release,
            SUM(total_air_release) AS total_air_release,
            ARRAY_AGG(DISTINCT tri_chem_id ORDER BY tri_chem_id) AS chemical_ids
        FROM waste_data
        GROUP BY city, county, state
        ORDER BY total_release DESC;
    """,

    "Total_Waste_Throughout_top_10": 
    '''       
        WITH distinct_facility AS (
            SELECT DISTINCT ON(tri_facility_id)
                tri_facility_id as id,
                CASE
                    WHEN parent_name IS NOT NULL 
                        AND UPPER(parent_name) NOT IN ('NA', 'NAN', 'N/A', 'NULL') 
                        THEN parent_name
                    WHEN epa_standardized_parent IS NOT NULL 
                        AND UPPER(epa_standardized_parent) NOT IN ('NA', 'NAN', 'N/A', 'NULL')
                        THEN epa_standardized_parent
                    WHEN name IS NOT NULL 
                        AND UPPER(name) NOT IN ('NA', 'NAN', 'N/A', 'NULL')
                        THEN name
                    WHEN epa_standardized_foreign_parent IS NOT NULL 
                        AND UPPER(epa_standardized_foreign_parent) NOT IN ('NA', 'NAN', 'N/A', 'NULL')
                        THEN epa_standardized_foreign_parent
                    ELSE NULL
                END AS facility_name
            FROM tri_facility_history 
        ),
        distinct_facility_by_year AS (
            SELECT DISTINCT df.facility_name as facility_name, trf.reporting_year as year, trf.doc_ctrl_num as doc_ctrl_num
            FROM distinct_facility df
            JOIN tri_reporting_form trf ON trf.tri_facility_id = df.id
            Where df.facility_name IS NOT NULL 
            ORDER BY trf.reporting_year
        ),
        
        top_10_facilities AS (
            SELECT DISTINCT
                df.facility_name as facility_name,
                SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) AS total_release,
                DENSE_RANK() OVER(ORDER BY SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) DESC) as most_waste_rank
            FROM distinct_facility_by_year df
            JOIN tri_form_total tft ON df.doc_ctrl_num = tft.doc_ctrl_num
            GROUP BY df.facility_name
        ),
        
        facility_yearly_totals AS (
            SELECT DISTINCT
                df.facility_name as facility_name,
                df.year as year,
                SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) AS total_release
            FROM distinct_facility_by_year df
            JOIN tri_form_total tft ON df.doc_ctrl_num = tft.doc_ctrl_num
            GROUP BY df.facility_name, df.year
            ORDER BY year
        )
                
        SELECT fyt.facility_name as name, fyt.year as reporting_year, fyt.total_release as total_release
        FROM facility_yearly_totals fyt
        JOIN top_10_facilities ttf ON ttf.facility_name = fyt.facility_name
        WHERE ttf.most_waste_rank <= 30
        Order By reporting_year;
    ''',
    
    "Total_Waste_Top_10_Vs_Rest_Facilities":
        """
        WITH latest_facility_location AS (
            SELECT DISTINCT ON (tri_facility_id) 
                tri_facility_id,
                epa_standardized_parent
            FROM tri_facility_history
            ORDER BY tri_facility_id, create_date DESC
        ),
        ranked_facilities AS (
            SELECT 
                trf.tri_facility_id,
                SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) AS total_release,
                RANK() OVER (ORDER BY SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) DESC) AS rank
            FROM tri_reporting_form trf
            JOIN tri_form_total tft ON trf.doc_ctrl_num = tft.doc_ctrl_num
            GROUP BY trf.tri_facility_id
        ),
        total_waste AS (
            SELECT SUM(total_release) AS grand_total
            FROM ranked_facilities
        )
        SELECT 
            'Top 10 Facilities' AS category,
            COUNT(*) AS num_facilities,
            ROUND(SUM(rf.total_release), 2) AS total_release,
            ROUND((SUM(rf.total_release) / MAX(tw.grand_total)) * 100, 2) AS percentage_of_total
        FROM ranked_facilities rf
        CROSS JOIN total_waste tw
        WHERE rf.rank <= 10

        UNION ALL

        SELECT 
            'All Other Facilities' AS category,
            COUNT(*) AS num_facilities,
            ROUND(SUM(rf.total_release), 2) AS total_release,
            ROUND((SUM(rf.total_release) / MAX(tw.grand_total)) * 100, 2) AS percentage_of_total
        FROM ranked_facilities rf
        CROSS JOIN total_waste tw
        WHERE rf.rank > 10

        UNION ALL

        SELECT 
            'TOTAL' AS category,
            COUNT(*) AS num_facilities,
            ROUND(SUM(rf.total_release), 2) AS total_release,
            100.00 AS percentage_of_total
        FROM ranked_facilities rf;
        """,
        "Chemical_Info":
        """
            SELECT 
                tri_chem_id,
                chem_name,
                caac_ind,
                carc_ind,
                feds_ind,
                classification,
                metal_ind,
                pbt_ind,
                pfas_ind
        FROM tri_chem_info;
        """
        
        
}

for x in queries:
    queries[x] = queries[x].replace('\n', ' ')
    queries[x] = " ".join(queries[x].split())
with open('queries.json', 'w') as f:
    json.dump(queries, f, indent=4)

 """
        WITH get_chemical_per_year AS(
            SELECT doc_ctrl_num, tri_facility_id, tri_chem_id
        )
        WITH waste_data AS (
            SELECT 
                tfh.city,
                tfh.county,
                tfh.state,
                trf.doc_ctrl_num,
                trf.reporting_year,
                trf.tri_chem_id,
                ROUND(SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC), 2) AS total_release,
                ROUND(SUM(tft.total_land_release::NUMERIC),2) as total_land_release,
                ROUND(SUM(tft.total_air_release::NUMERIC),2) as total_air_release,
                ROUND(SUM(tft.total_water_release::NUMERIC),2) as total_water_release
            FROM tri_reporting_form trf
            JOIN tri_facility_history tfh ON trf.tri_facility_id = tfh.tri_facility_id
            JOIN tri_form_total tft ON trf.doc_ctrl_num = tft.doc_ctrl_num
            GROUP BY tfh.city, tfh.county, tfh.state, trf.doc_ctrl_num, trf.reporting_year, trf.tri_chem_id
            Order By total_release DESC
        )
        SELECT 
            city,
            county,
            state,
            COUNT(DISTINCT tri_chem_id) AS unique_chemical_count,
            SUM(total_release) AS total_release,
            SUM(total_land_release) AS total_land_release,
            SUM(total_water_release) AS total_water_release,
            SUM(total_air_release) AS total_air_release,
            ARRAY_AGG(DISTINCT tri_chem_id ORDER BY tri_chem_id) AS chemical_ids

        FROM waste_data
        GROUP BY city, county, state
        ORDER BY total_release DESC;
"""