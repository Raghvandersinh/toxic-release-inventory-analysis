# Toxic Release Inventory (TRI) ELT & Analysis

A fully functional Python project that creates a TRI database model and implements a data extraction pipeline to insert clean data for comprehensive environmental analysis.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Basic Profiling](#basic-profiling)
  - [Facility Rankings](#facility-rankings)
  - [State Rankings](#state-rankings)
  - [County Rankings](#county-rankings)
  - [Industry Rankings](#industry-rankings)
  - [Top 10 vs Rest](#top-10-vs-rest)
- [Specific Analysis](#specific-analysis)
- [Interactive Dashboards](#interactive-dashboards)
- [Technical Process](#technical-process)
- [Data Sources](#data-sources)

---

## Project Overview

**Goal:** Answer critical questions about toxic waste release patterns, responsible parties, and environmental impacts across the United States using EPA Toxic Release Inventory data.

---

## Basic Profiling

### Facility Rankings

**Question:** What facilities were involved in dumping the most pounds of waste throughout the years (Ranks 1–5)?

---

#### Rank 1: Cominco Alaska Inc (Red Dog Mine) — 1998–2024

![Cominco Alaska Waste Trend](Frontend/chart/line_chart/Comico_Alaska.png)

**Trend Analysis:** From 1998–2014 we see an upward trend of total releases, followed by volatile up-and-down spikes from 2014–2024.

Red Dog Mine is the world's largest producer of Zinc and Lead. They are the largest U.S. toxic polluter — a finding confirmed by our database, where Cominco Alaska Inc. ranks #1 by total toxic waste released per facility. They are also the reason why Alaska (37.1 million lbs) and the Arctic (481.6 million lbs) are the top two locations for toxic release per pound.

According to the EPA, Alaska ranked first in the nation for the largest total releases of chemicals in 2002, with 545.5 million pounds of toxics coming from the mining industry. The hard rock mining industry is the nation's largest toxic polluter, releasing 1.3 billion lbs (27% of toxics released by U.S. industry). According to Pam Miller, the hardrock industry releases toxins such as lead, copper, zinc, and other heavy metals that pollute land, water, and air.

![Alaska Waste Map](Frontend/chart/state_map/Alsaka_Waste.png)

> **Source:** [Alaska Community Action on Toxics — Red Dog and Subsistence Analysis](https://www.akaction.org/publications/red-dog-and-subsistence-analysis-of-reports-on-elevated-levels-of-heavy-metals-in-plants-used-for-subsistence-near-red-dog-mine-alaska/)

---

#### Rank 2: Kerr-McGee Corp — 1987–2001

![Kerr-McGee Corp Waste Trend](Frontend/chart/line_chart/Kerr_Mcgee_Corp.png)

Analysis of the total waste chart reveals a massive gap between Kerr-McGee Corp and other facilities around 1987 — approximately 5.2 billion pounds of waste difference.

**Documented Environmental Incidents:**

- **Navassa, North Carolina (1979–1980):** According to the DARRP (Damage Assessment, Remediation, and Restoration Program), Kerr-McGee dismantled a creosote wood-treating facility on a 250-acre parcel adjacent to the Cape Fear River, Brunswick River, and Sturgeon Creek. This released creosote and sludge, leading to SVOC (Semi-Volatile Organic Compound) contamination — specifically PAH (Polycyclic Aromatic Hydrocarbon) — in soils, groundwater, and surrounding marsh sediments. According to EPA data, PAH is a cancer-causing PBT chemical.

- **Cimarron City, Oklahoma (1965–1975):** According to the NRC (Nuclear Regulatory Commission), Kerr-McGee fabricated enriched uranium and mixed oxide fuels for nuclear reactors. The site contained several buildings, collection ponds, sanitary lagoons, storage areas, and burial areas.

- **Navajo Nation, Arizona (1940s–1980s):** According to the EPA, Kerr-McGee mined over 7 million tons of uranium in northeastern Arizona, Chapter Cove, consisting of 50 Abandoned Uranium Mines (AUMs). This affected air, water, future land use, health, and workforce development of communities near Lukachukai and Carrizo Mountains. Through 2000–2020, remediation efforts have been undertaken by the EPA, AML (Abandoned Mine Lands) programs, and ASPECT (Airborne Spectral Photometric Environmental Collection Technology).

Kerr-McGee's activities stopped in 2001 due to legal pushback, culminating in acquisition by Anadarko Petroleum in 2006.

> **Sources:**
> - [NOAA DARRP — Kerr-McGee Chemical Corp](https://darrp.noaa.gov/hazardous-waste/kerr-mcgee-chemical-corp-tronox)
> - [NRC — Kerr-McGee Cimarron Facility](https://www.nrc.gov/info-finder/decommissioning/complex/kerr-mcgee-cimarron-corporation-former-fuel-fabrication-facility)
> - [EPA — Navajo Nation Uranium Cleanup](https://www.epa.gov/navajo-nation-uranium-cleanup/cove-area-mines)
> - [SEC — Anadarko Acquisition Filing](https://www.sec.gov/Archives/edgar/data/773910/000095012906007908/h38749exv99w1.htm)

---
**Rank 3: Rio Tinto — 1997–2024**

![Rio Tinto Waste Trend](Frontend/chart/line_chart/Rio_Tinto.png)

A huge spike in waste occurred in 1999, followed by a gradual decline until 2002, then moderate upward and downward spikes through 2024.

---

**Global Environmental Footprint**

---

**Panguna Mine** — Bougainville, Papua New Guinea
- Billions of tons of toxic waste in rivers
- Polluted major bays and Pacific Ocean
- Caused illness (asthma, TB, respiratory infections)
- War caused approximately 10,000 deaths between 1990–1997

---

**Grasberg Mine** — West Papua, Indonesia
- Joint venture with Freeport McMoRan
- 3.5 billion metric tons of waste dumped into local streams

---

**Kelian Gold Mine** — Indonesia
- 100 million metric tons of contaminated waste rock
- Approximately 1,100 kg cyanide released in rivers (1996)

---

**Flambeau Mine** — Ladysmith, Wisconsin, USA
- Produced 181,000 tons of copper (1993–1997)
- 2009 lawsuit exposed groundwater pollution
- Copper contamination found in crayfish

---

**QMM Mine** — Fort-Dauphin, Madagascar
- Construction began 2006
- Contains 75+ million tons of ilmenite (titanium oxide) deposits

---

**Rössing Uranium Mine** — Namibia
- Rio Tinto owns approximately 69%
- Produces 20 million tons of sulphuric-acid-soaked radioactive rock annually

---

**Sources:**
- [London Mining Network — Rio Tinto Report](https://londonminingnetwork.org/2010/04/rio-tinto-a-shameful-history-of-human-and-labour-rights-abuses-and-environmental-degradation-around-the-globe/)
- [Human Rights Law Centre — Panguna Mine Impacts](https://www.hrlc.org.au/reports/2024-12-6-panguna-mine-impacts/)
---

#### Rank 4: Barrick Gold — 1998–2024

![Barrick Gold Waste Trend](Frontend/chart/line_chart/Barrick_Gold.png)

**Key Findings:**

- **Lake Cowal, Australia:** Required 6,613 tons of cyanide per year for gold leaching. A 1992 train crash at Condobolin spread 40 metric tons of cyanide pellets across the ground.
- **Porgera, Papua New Guinea:** Mining operations began in 1990, dumping 6.6 tons of waste per ounce of gold by 2000, increasing to ~97.6 tons by 2006.
- **Pascua Lama & Veladero, Chile/Argentina:** Dust emissions containing lead, arsenic, uranium, chromium, zinc, asbestos, mercury, and other toxins polluted soil and groundwater. Operations melted 10.2 acres of glaciers and caused drought by extracting 42 liters of water per second.
- **Philippines:** 200 million tons of mine tailings went directly into Calancan Bay (1975–1991). The Marcopper Mine filled the 26-km Boac River with 3–4 million tons of metal-enriched tailings (1996).

**Mercury Emissions:** According to Miller and Jones, Nevada gold mines released 3,700 lbs of mercury air emissions in 1998; Barrick released 13,629 tons of mercury by-product in 1999.

> **Sources:**
> - [EPA Regulations Document](https://downloads.regulations.gov/EPA-HQ-SFUND-2015-0781-2119/content.pdf)
> - [CorpWatch — Barrick's Dirty Secrets](https://www.corpwatch.org/sites/default/files/Barrick%27s%20Dirty%20Secrets.pdf)
> - [EPA — ASARCO Bankruptcy Settlement](https://www.epa.gov/enforcement/case-summary-asarco-2009-bankruptcy-settlement)

---

#### Rank 5: Freeport McMoRan — 1997–2024

![Freeport McMoRan Waste Trend](Frontend/chart/line_chart/Freeport_McMoRan.png)

A massive spike occurred between 1997–2000. According to Earthworks, Freeport sends more than 76 million metric tons of tailings and waste rock into Indonesian rivers every year (company-reported figure: 50 million tons in 2017).

**Major Incidents:**
- Billions of gallons of sludge escaped, traveling hundreds of kilometers down the Doce River, killing at least 19 people and leaving hundreds homeless.
- Daily toxic waste dumping has escalated from ~10,000 tons to 300,000 tons per day, channeled through the Ajkwa River near Timika.

> **Sources:**
> - [OHCHR — Solidarity for Indigenous Papuans](https://www.ohchr.org/sites/default/files/2022-06/Solidarity%20for%20Indigenous%20Papuans1.pdf)
> - [Mining.com — Giant Mine Spewing Waste](https://www.mining.com/web/giant-mine-spewing-waste-decades-turns-battleground/)

---

### State Rankings

**Question:** What state has the most pounds of waste throughout the years (Ranks 1–5)?

---

**Rank 1: Alaska — ~532 Billion Pounds**

![Alaska Waste Map](Frontend/chart/state_map/Alsaka_Waste.png)

**Top Chemicals:**
- Zinc: 291 Billion lbs
- Lead: 200 Billion lbs

**Disposal Method:** 527 billion pounds land-based. Cominco Alaska Inc (Red Dog Mine) is the primary contributor.

---

**Rank 2: Texas — ~387 Billion Pounds**

![Texas Waste Map](Frontend/chart/state_map/Texas_Waste.png)

**Top Chemicals:**
- Ammonia: 69 Billion lbs
- Nitrate: 27 Billion lbs
- Aluminum: 27 Billion lbs

**Disposal Method:** 201 billion lbs land, 100 billion lbs air. Texas has a lax regulatory environment where polluting facilities can easily dump waste with permits.

---

**Rank 3: Louisiana — ~315 Billion Pounds**

![Louisiana Waste Map](Frontend/chart/state_map/Louisanna_Waste.png)

**Top Chemicals:**
- Ammonia: 48 Billion lbs
- Phosphoric Acid: 35 Billion lbs
- Sulphuric Acid: 30 Billion lbs

**Disposal Method:** 147 billion lbs land, 79 billion lbs air, 74 billion lbs water.

Louisiana contains 25% of U.S. petrochemical products, harming air, water, and soils. The region known as "Cancer Alley" has extreme air pollution causing cancer, reproductive, maternal, newborn, and respiratory health harm.

> **Source:** [Johns Hopkins Public Health — Louisiana's Cancer Alley](https://publichealth.jhu.edu/2025/the-shocking-hazards-of-louisianas-cancer-alley)

---

**Rank 4: Utah — ~250 Billion Pounds**

![Utah Waste Map](Frontend/chart/state_map/Utah_Waste.png)

**Top Chemicals:**
- Copper: 76 Billion lbs
- Lead: 72 Billion lbs
- Chlorine: 39 Billion lbs

**Disposal Method:** 190 billion lbs land, 48 billion lbs air.

> "Sediments produced by the dry playa around Great Salt Lake have been contaminated by a century of mining, waste disposal, oil refining and other human activities." — Utah State University research team

> **Source:** [Utah State University — Great Salt Lake Dust Research](https://www.usu.edu/today/story/new-research-toxins-from-great-salt-lake-dust-absorbed-by-plants-soils-human-bodies)

---

**Rank 5: Ohio — ~222 Billion Pounds**

![Ohio Waste Map](Frontend/chart/state_map/Ohio_Waste.png)

**Top Chemicals:**
- Hydrochloric Acid: 22 Billion lbs
- Zinc: 20 Billion lbs
- Ammonia: 19 Billion lbs

**Disposal Method:** 86 billion lbs air, 72 billion lbs land.

> "EPA estimates 20,000 gallons of hazardous waste is stored in various containers on the site, including chromium, lead, arsenic, various acids, and cyanide salts. Not all containers are labeled, and some containers are missing tops or lids." — EPA on Woodhill Plating Works, Cleveland

> **Source:** [EPA — Woodhill Plating Works Cleanup](https://www.epa.gov/newsreleases/epa-begins-removing-hazardous-waste-woodhill-plating-works-facility-cleveland-ohio)

---

**Key Insight:** Alaska dominates by a significant margin, driven by mining operations. Texas and Louisiana follow with substantial contributions from industrial and petrochemical activities. The data reveals concerning environmental justice issues, particularly in Louisiana's "Cancer Alley" and Utah's Great Salt Lake contamination.
---

### County Rankings

**Question:** What county has the most pounds of waste throughout the years (Ranks 1–5)?

---

**Rank 1: Northwest Arctic, AK — ~478 Billion Pounds**

![Northwest Arctic Map](Frontend/chart/county_map/Northwest_Artic.png)

**Top Chemicals:**
- Zinc: 274 Billion lbs
- Lead: 190 Billion lbs

**Disposal Method:** 476 billion lbs land-based. Red Dog Operations is the primary contributor.

---

**Rank 2: Salt Lake, UT — ~183 Billion Pounds**

![Salt Lake County Map](Frontend/chart/county_map/Salt_Lake_Utah.png)

**Top Chemicals:**
- Copper: 75 Billion lbs
- Lead: 70 Billion lbs

**Disposal Method:** 175 billion lbs land-based. Primary sources: Rio Tinto America and Kennecott Holdings Corp (Rio Tinto subsidiary).

> "The Kennecott South Zone includes the Bingham Mining District in the Oquirrh Mountains... Mining activities began in the 1860s and continue today. Soils, sludge, surface water and groundwater are contaminated." — EPA

> **Source:** [EPA Superfund Site Profile](https://cumulis.epa.gov/supercpad/SiteProfiles/index.cfm?fuseaction=second.cleanup&id=0800601)

---

**Rank 3: Gila, AZ — ~89 Billion Pounds**

![Gila County Map](Frontend/chart/county_map/Gila_AZ.png)

**Top Chemicals:**
- Zinc: 38 Billion lbs
- Additional Zinc compounds: 25 Billion lbs

**Disposal Method:** 87 billion lbs land-based. Primary sources: Freeport-McMoRan Inc and Americas Mining Corp.

---

**Rank 4: San Bernardino, CA — ~81 Billion Pounds**

![San Bernardino Map](Frontend/chart/county_map/San_Bernerdino_CA.png)

**Top Chemicals:**
- Sodium Sulphate: 78 Billion lbs

**Disposal Method:** 55 billion lbs water-based.

---

**Rank 5: Humboldt, NV — ~71 Billion Pounds**

![Humboldt County Map](Frontend/chart/county_map/Humboldt_NV.png)

**Top Chemicals:**
- Arsenic: 48 Billion lbs

**Disposal Method:** 71 billion lbs land-based.

---

**Key Insight:** Mining operations dominate the top counties, with Northwest Arctic, AK leading by a significant margin. Land-based disposal is the overwhelming preference across all top counties except San Bernardino, CA which relies primarily on water-based disposal.

---

### Industry Rankings

#### **Question:** What industries were most involved in dumping waste?

---

**Rank 1: Metal Ore Mining**
Copper, Zinc, Lead, and Nickel — All top 5 facilities belong to this sector

---

**Rank 2: Chemical Manufacturing**
All Other Basic Organic Chemical Manufacturing (NAICS 325199)
Includes American Cyanamid Superfund site: 575-acre facility with VOCs, SVOCs, and metals contamination

---

**Rank 3: Primary Metal Manufacturing**
Iron and Steel Mills & Ferroalloy Manufacturing
U.S. Steel Gary Works: metals, VOCs, SVOCs, and PCBs

---

**Rank 4: Electrical Power Generation**
Fossil Fuel Electric Power Generation
Rio Tinto primary contributor

---

**Rank 5: Paper Manufacturing**
Pulp Mills
Rayonier Mill: 30,000+ tons of contaminated material removed to date

---

**Key Insight:** Metal Ore Mining dominates as the top sector, with all top 5 facilities concentrated in this industry. Chemical Manufacturing follows closely with significant Superfund site contamination.
---

### Top 10 vs Rest

![Top 10 vs Rest Pie Chart](Frontend/chart/pie_chart/top_10_vs_rest.png)

### Waste Distribution Summary

---

**Top 10 Facilities**
- **Waste:** 46.82 Billion lbs
- **Share:** 27.11%

---

**Remaining 36,003 Facilities**
- **Waste:** 125.90 Billion lbs
- **Share:** 72.89%

---

**Total Waste**
- **Combined:** 172.72 Billion lbs
- **Coverage:** 100%

---

**Key Insight:** The top 10 facilities account for over 27% of all waste, despite representing only a tiny fraction of total facilities.
---

## Specific Analysis

### 1. Most Commonly Released Chemicals

**Question:** Which chemicals are the most commonly released (most reported)?

![Most Used Chemicals](Frontend/chart/specific_query_results/most_used_chemical.png)

**Top 5 Chemicals:**
1. Lead
2. Nitrate
3. Hydrochloric Acid
4. Ammonia
5. Zinc

---

### 2. Locations with Most Carcinogenic Chemical Reports

**Question:** Which locations have the most reported carcinogenic chemicals?

![Carcinogens Per Location](Frontend/chart/specific_query_results/total_carcinogen_per_location.png)

**Top 5 Locations:**
1. TX, Harris, Houston
2. TX, Harris, Pasadena
3. TX, Jefferson, Port Arthur
4. KY, Jefferson, Louisville
5. IL, Cook, Chicago

---

### 3. Disposal Domain Comparison

**Question:** Air release vs. water release vs. land release — which domain dominates?

![TRI State Map Dashboard 2020s](Frontend/chart/state_map/TRI_State_Map_Dashboard_2020s.png)

**1. Land Release** — *Dominant by a wide margin*  
The most prevalent disposal method, accounting for the majority of all releases tracked in the TRI database.

**2. Air Release** — *Moderate usage*  
Second most common disposal method, with significant industrial emissions recorded.

**3. Water Release** — *Least used*  
The least utilized disposal method among the three domains.

---

## Interactive Dashboards

---

### Quick Links to Individual Dashboards
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Dashboards</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background: #f8f9fa;
        }
        h1 {
            color: #1a1a1a;
            margin-bottom: 2rem;
        }
        .dashboard-grid {
            display: flex;
            flex-direction: column;
            gap: 2.5rem;
        }
    </style>
</head>
<body>
    <h1>📊 Interactive Dashboards</h1>
    <div class="dashboard-grid">

        <!-- Dashboard 1: Facility Trend Analysis -->
        <div style="margin: 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="padding: 1rem; background: #f5f5f5; border-bottom: 1px solid #e0e0e0; font-weight: bold;">
                📈 Facility Trend Analysis - Top Facilities Throughout Years
            </div>
            <iframe 
                src="https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/line_chart/total_waste_throughout_top_10.html"
                width="100%" 
                height="600px" 
                frameborder="0"
                loading="lazy"
                title="Facility Trend Dashboard"
                style="display: block;">
            </iframe>
        </div>

        <!-- Dashboard 2: State Map - All Time -->
        <div style="margin: 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="padding: 1rem; background: #f5f5f5; border-bottom: 1px solid #e0e0e0; font-weight: bold;">
                🗺️ Geographic Distribution - State Map (All Time: 2003-2025)
            </div>
            <iframe 
                src="https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/state_map/TRI_State_Map_Dashboard_Throughout.html"
                width="100%" 
                height="700px" 
                frameborder="0"
                loading="lazy"
                title="State Map All Time"
                style="display: block;">
            </iframe>
        </div>

        <!-- Dashboard 3: County Map - All Time -->
        <div style="margin: 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="padding: 1rem; background: #f5f5f5; border-bottom: 1px solid #e0e0e0; font-weight: bold;">
                🏛️ Geographic Distribution - County Map (All Time: 2003-2025)
            </div>
            <iframe 
                src="https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/county_map/TRI_County_Map_Dashboard_Throughout.html"
                width="100%" 
                height="700px" 
                frameborder="0"
                loading="lazy"
                title="County Map All Time"
                style="display: block;">
            </iframe>
        </div>

        <!-- Dashboard 4: State Map - 2020s -->
        <div style="margin: 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="padding: 1rem; background: #f5f5f5; border-bottom: 1px solid #e0e0e0; font-weight: bold;">
                🗺️ Geographic Distribution - State Map (Recent: 2020-2025)
            </div>
            <iframe 
                src="https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/state_map/TRI_State_Map_Dashboard_2020s.html"
                width="100%" 
                height="700px" 
                frameborder="0"
                loading="lazy"
                title="State Map 2020s"
                style="display: block;">
            </iframe>
        </div>

        <!-- Dashboard 5: County Map - 2020s -->
        <div style="margin: 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="padding: 1rem; background: #f5f5f5; border-bottom: 1px solid #e0e0e0; font-weight: bold;">
                🏛️ Geographic Distribution - County Map (Recent: 2020-2025)
            </div>
            <iframe 
                src="https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/county_map/TRI_County_Map_Dashboard_2020s.html"
                width="100%" 
                height="700px" 
                frameborder="0"
                loading="lazy"
                title="County Map 2020s"
                style="display: block;">
            </iframe>
        </div>

    </div>
</body>
</html>

## Technical Process

The following technologies and methodologies were used to build the ETL pipeline and database:

### ETL Pipeline Architecture

#### 1. **Schema Design** — SQLAlchemy ORM

- Generated table schemas and column definitions for the TRI database using Object Relational Mapping, ensuring a robust and maintainable data model.

#### 2. **Data Extraction** — Requests Library

- Connected to TRI metadata API endpoints to extract raw data programmatically, handling pagination and rate limiting where necessary.

#### 3. **Data Transformation** — Pandas

- Transformed raw API data into structured DataFrames with only the necessary columns required for the TRI database, optimizing for performance and storage.

#### 4. **Data Standardization** — Data Cleaning

- Cleaned and standardized data within Pandas DataFrames to ensure consistency and readiness for database insertion, including handling missing values and data type conversions.

#### 5. **Database Ingestion** — SQLAlchemy + PostgreSQL Dialects

- Implemented custom Upsert logic (`INSERT ... ON CONFLICT UPDATE`) to avoid duplicate entries and prevent errors during the data insertion process.

#### 6. **Migration Management** — Alembic

- Used autogeneration for automatic database migrations, keeping the schema in sync with the ORM models as the project evolved.

#### 7. **Exploritory Data Analysis(EDA)** - Pandas/JSON

- Created a Dictionary of Queries written by me -> did a string clean up -> then stored them in a JSON file using JSON lib   
-> Loaded the Query from the JSON file -> Used Pandas Read SQL function to output the query from the database
-> Explored, Cleaned, and Transformed data to make it Visualization ready

#### 8. **Data Visualization** - Atlair

- Used the clean dataframe from the previous step to generate various dashboards (Maps, Pie, Line, and Bar)

#### 9. **Data Analysis** - Descriptive & Diagnostic

- Did Descriptive and Diagnostic Analysis above for more info

---

### Process Flow Summary
**API Extraction** *(Requests)*  
↓  
**Data Transformation** *(Pandas)*  
↓  
**Data Cleaning** *(Pandas)*  
↓  
**Database Insertion** *(SQLAlchemy)*  
↓  
**Migrations** *(Alembic)*
↓
**Exploritory Data Analysis(EDA)** *(Pandas/JSON)*
↓
**Data Visualization** *(Altair)*
↓
**Data Analysis** 


### Architecture Overview
