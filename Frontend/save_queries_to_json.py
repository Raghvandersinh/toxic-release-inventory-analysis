import json

queries = {
    "Waste_By_Location":
 """
       WITH get_waste_data AS (
            SELECT trf.tri_facility_id, 
                ROUND(SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC), 2) AS total_release,
                ROUND(SUM(tft.total_land_release::NUMERIC),2) as total_land_release,
                ROUND(SUM(tft.total_air_release::NUMERIC),2) as total_air_release,
                ROUND(SUM(tft.total_water_release::NUMERIC),2) as total_water_release,
                tri_chem_id
            FROM tri_reporting_form trf
            JOIN tri_form_total tft ON tft.doc_ctrl_num = trf.doc_ctrl_num
            GROUP BY trf.tri_facility_id, tri_chem_id
            HAVING SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) <> 0
            Order By total_release DESC
        ),
        sort_by_location AS(
        Select tfh.city, tfh.county, tfh.state,
               Round(SUM(gwd.total_release), 2) as total_release, 
               Round(SUM(gwd.total_land_release), 2) as total_land_release, 
               Round(SUM(gwd.total_air_release),2) as total_air_release,
               ROUND(SUM(gwd.total_water_release),2) as total_water_release, 
               tri_chem_id
            FROM tri_facility_history tfh
            JOIN get_waste_data gwd ON gwd.tri_facility_id = tfh.tri_facility_id
            GROUP BY tfh.city, tfh.county, tfh.state, gwd.tri_chem_id
            HAVING SUM(gwd.total_release) <> 0
            ORDER BY total_release
        )
        SELECT sbl.*, 
        tci.chem_name, 
        tci.caac_ind, 
        tci.carc_ind,
        tci.feds_ind,
        tci.metal_ind,
        tci.pbt_ind,
        tci.pfas_ind
        FROM sort_by_location sbl
        JOIN tri_chem_info tci ON sbl.tri_chem_id = tci.tri_chem_id
        Order By sbl.total_release DESC;
""",
    
    "Waste_By_Location_2020s": 
    """
       WITH get_waste_data AS (
            SELECT trf.tri_facility_id, 
                ROUND(SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC), 2) AS total_release,
                ROUND(SUM(tft.total_land_release::NUMERIC),2) as total_land_release,
                ROUND(SUM(tft.total_air_release::NUMERIC),2) as total_air_release,
                ROUND(SUM(tft.total_water_release::NUMERIC),2) as total_water_release,
                trf.tri_chem_id
            FROM tri_reporting_form trf
            JOIN tri_form_total tft ON tft.doc_ctrl_num = trf.doc_ctrl_num
            Where trf.reporting_year >= 2020
            GROUP BY trf.tri_facility_id, trf.tri_chem_id
            HAVING SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) <> 0
            Order By total_release DESC
        ),
        sort_by_location AS(
        Select tfh.city, tfh.county, tfh.state,
               Round(SUM(gwd.total_release), 2) as total_release, 
               Round(SUM(gwd.total_land_release), 2) as total_land_release, 
               Round(SUM(gwd.total_air_release),2) as total_air_release,
               ROUND(SUM(gwd.total_water_release),2) as total_water_release, 
               tri_chem_id
            FROM tri_facility_history tfh
            JOIN get_waste_data gwd ON gwd.tri_facility_id = tfh.tri_facility_id 
            GROUP BY tfh.city, tfh.county, tfh.state, gwd.tri_chem_id
            HAVING SUM(gwd.total_release) <> 0
            ORDER BY total_release
        )
        SELECT sbl.*, 
        tci.chem_name, 
        tci.caac_ind, 
        tci.carc_ind,
        tci.feds_ind,
        tci.metal_ind,
        tci.pbt_ind,
        tci.pfas_ind
        FROM sort_by_location sbl
        JOIN tri_chem_info tci ON sbl.tri_chem_id = tci.tri_chem_id
        Order By sbl.total_release DESC;
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
        WITH distinct_facility AS (
            SELECT DISTINCT ON (tri_facility_id) 
                tri_facility_id,
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
            ORDER BY tri_facility_id
        ),
        get_doc_ctrl_num AS (
            Select df.facility_name, df.tri_facility_id, trf.doc_ctrl_num From distinct_facility df
            Join tri_reporting_form trf ON trf.tri_facility_id = df.tri_facility_id
        ),
        ranked_facilities AS(
            SELECT 
                gd.facility_name,
                SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) AS total_release,
                RANK() OVER (ORDER BY SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) DESC) AS rank
            FROM get_doc_ctrl_num gd
            JOIN tri_form_total tft ON gd.doc_ctrl_num = tft.doc_ctrl_num
            GROUP BY gd.facility_name
        ),
        total_waste AS (
            SELECT SUM(total_release) AS grand_total
            FROM ranked_facilities
        )
        SELECT DISTINCT
            'Top 10 Facilities' AS category,
            COUNT(*) AS num_facilities,
            ROUND(SUM(rf.total_release), 2) AS total_release,
            ROUND((SUM(rf.total_release) / MAX(tw.grand_total)) * 100.0, 2) AS percentage_of_total
        FROM ranked_facilities rf
        CROSS JOIN total_waste tw
        WHERE rf.rank <= 10

        UNION ALL

        SELECT DISTINCT
            'All Other Facilities' AS category,
            COUNT(*) AS num_facilities,
            ROUND(SUM(rf.total_release), 2) AS total_release,
            ROUND((SUM(rf.total_release) / MAX(tw.grand_total)) * 100.0, 2) AS percentage_of_total
        FROM ranked_facilities rf
        CROSS JOIN total_waste tw
        WHERE rf.rank > 10

        UNION ALL

        SELECT DISTINCT
            'TOTAL' AS category,
            COUNT(*) AS num_facilities,
            ROUND(SUM(rf.total_release), 2) AS total_release,
            100.00 AS percentage_of_total
        FROM ranked_facilities rf;
        """,
    "Total_Waste_By_Industry": 
    """
        With get_naics_name AS (
            Select nc.name as national_industry, nc.type, tsn.doc_ctrl_num, tsn.naics_code, tsn.industry_code
            from tri_submission_naics tsn
            LEFT JOIN naics_code nc ON nc.naics_code = tsn.naics_code
        ),
        get_industry_code_name AS (
            Select Distinct nc.name as industry_name, nc.type, tsn.industry_code from tri_submission_naics tsn
            JOIN naics_code nc ON nc.naics_code = tsn.industry_code
        ),
        join_naics_industry_code AS (
            Select gn.national_industry, gi.industry_name, gn.doc_ctrl_num, count(*) OVER() from get_naics_name gn
            LEFT JOIN get_industry_code_name gi ON gi.industry_code = gn.industry_code
        ),
        get_total_waste AS (
            Select trf.doc_ctrl_num, 
            SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) OVER(partition by trf.doc_ctrl_num) AS total_release
            FROM tri_reporting_form trf
            JOIN tri_form_total tft ON tft.doc_ctrl_num = trf.doc_ctrl_num
        )
        Select DISTINCT jn.national_industry, jn.industry_name, 
        SUM(gt.total_release) OVER(partition by jn.national_industry, jn.industry_name) as total_release
        FROM join_naics_industry_code jn
        JOIN get_total_waste gt ON gt.doc_ctrl_num = jn.doc_ctrl_num
        ORDER BY total_release DESC; 
    """,
    'Waste_By_Industry_with_facility':
    
    '''
    With get_naics_name AS (
            Select nc.name as national_industry, nc.type, tsn.doc_ctrl_num, tsn.naics_code, tsn.industry_code, tsn.tri_facility_id
            from tri_submission_naics tsn
            LEFT JOIN naics_code nc ON nc.naics_code = tsn.naics_code
        ),
        get_industry_code_name AS (
            Select Distinct nc.name as industry_name, nc.type, tsn.industry_code from tri_submission_naics tsn
            JOIN naics_code nc ON nc.naics_code = tsn.industry_code
        ),
        join_naics_industry_code AS (
            Select gn.national_industry, gi.industry_name, gn.doc_ctrl_num, count(*) OVER(), gn.tri_facility_id 
            from get_naics_name gn
            LEFT JOIN get_industry_code_name gi ON gi.industry_code = gn.industry_code
        ),
        get_total_waste AS (
            Select trf.doc_ctrl_num, 
            SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) OVER(partition by trf.doc_ctrl_num) AS total_release
            FROM tri_reporting_form trf
            JOIN tri_form_total tft ON tft.doc_ctrl_num = trf.doc_ctrl_num
        ),
        get_industry_facility_total AS (
            Select DISTINCT jn.national_industry, jn.industry_name, jn.tri_facility_id,
            SUM(gt.total_release) OVER(partition by jn.national_industry, jn.industry_name, jn.tri_facility_id) as total_release
            FROM join_naics_industry_code jn
            JOIN get_total_waste gt ON gt.doc_ctrl_num = jn.doc_ctrl_num
            ORDER BY total_release DESC
        )
        Select DISTINCT gi.national_industry, gi.industry_name, tfh.parent_name, ROUND(gi.total_release,2) as total_release
        From get_industry_facility_total gi
        JOIN tri_facility_history tfh ON gi.tri_facility_id = tfh.tri_facility_id
        Where gi.national_industry LIKE '%Pulp%'
        Order by total_release DESC;
    ''',
    
    'Select_Individaul_County':
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
                    END AS facility_name,
                    city,
                    county,
                    state
                FROM tri_facility_history 
        ),
        get_sum_total_waste AS(
            SELECT trf.tri_facility_id, trf.tri_chem_id, 
            SUM(tft.total_offsite_release::NUMERIC + tft.total_onsite_release::NUMERIC) OVER(partition by trf.tri_facility_id, trf.tri_chem_id) AS total_release
            FROM tri_reporting_form trf
            JOIN tri_form_total tft ON tft.doc_ctrl_num = trf.doc_ctrl_num   
        )
        Select DISTINCT df.facility_name, df.city, df.county, df.state, gs.total_release, tci.chem_name FROM distinct_facility df
        JOIN get_sum_total_waste gs ON gs.tri_facility_id = df.id
        JOIN tri_chem_info tci ON tci.tri_chem_id = gs.tri_chem_id
        WHERE df.county LIKE '%GILA%'
        ORDER BY gs.total_release DESC;
    ''',
    'Most_Dumped_Chemical':
    '''
        WITH get_facility_released_chem AS (
            Select trf.tri_chem_id, trf.doc_ctrl_num, tca.produce FROM tri_chem_activity tca
            JOIN tri_reporting_form trf ON trf.doc_ctrl_num = tca.doc_ctrl_num
            Where tca.produce = True
        )
        Select tci.chem_name, COUNT(tci.chem_name) as reported_chem_count,
        ROW_NUMBER() OVER(ORDER BY COUNT(tci.chem_name) DESC)
        FROM tri_chem_info tci
        JOIN get_facility_released_chem gf ON tci.tri_chem_id = gf.tri_chem_id 
        GROUP BY tci.chem_name
        LIMIT 5;
    '''
}

for x in queries:
    queries[x] = queries[x].replace('\n', ' ')
    queries[x] = " ".join(queries[x].split())
with open('queries.json', 'w') as f:
    json.dump(queries, f, indent=4)



