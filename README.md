# Toxic Release Inventory(TRI) ELT/Analysis:

## A fully functional project written in Python that creates a TRI  Database Model and a Data Extraction Pipeline to insert clean data into the TRI database for further Analysis.

### This goal of this project is answer questions such as:

1. What facility was involved in dumping the most throughout the years?
    1. **1987 Kree Mcgee Corp**
        * After analysis the total_waste_throughout_top_10.html chart. We see a massive gap between **Kree Mcgee Corp** and other facilities during the 1987 approximately 5.2 billons of pounds worth of waste gap. While I can't seem to find the articles for the specific year, I did find articles about Kerr Mcgee prior to 1987. 
        
            According to the DARRP(Damage Assement Remedition, and Restoration Program) between 1979-1980 Kerr Mcgee dismantled one of its creosote wood-treating facilities located at "250-acre parcel of land adjacent to the Cape Fear River, Brunswick River and Sturgeon Creek in Navassa, North Carolina."(DARRP), which then released Creosote and sludge, which then led to the release of SVOC (Semi Volatile Organic Compound) spefcically the PAH(Polycyclic Aromatic Hydrocarbon) which is released to soils, groundwater, and surronding marsh sediments sites. According to my database (which I got the data from EPA.gov) PAH is a Cancer Causing PBT chemical.
            
            https://darrp.noaa.gov/hazardous-waste/kerr-mcgee-chemical-corp-tronox

            
            According to the NRC(Nuclear Regulatory Commission) Kerr Mcgee dropped '...fabricate enriched uranium and mixed oxide fuels for nuclear reactors from 1965–1975.'(NRC) between 1965-1975 at Cimarron site located at Cimarron City, Oklahoma. Where '... On site, there were several buildings, collection ponds, sanitary lagoons, storage areas, and burial areas.'(NRC).
            
            https://www.nrc.gov/info-finder/decommissioning/complex/kerr-mcgee-cimarron-corporation-former-fuel-fabrication-facility
            
            According to the EPA(Enviromental Protection Agency) between 1940s-1980s Kerr Mcgee mined over 7 million tons of uranium at northeastern Arizon, Navajo Nation, Chapter Cove which consists of 50 AUMs(Abandoned Uranium Mines). Which affected the air and water, future land use, health, and workforce development of the community living near Lukachukai, and Carrizo Mountains on the Navajo Nation. Through 2000s - 2020 action have been taken by many entites such as EPA, AML(Abandoned Mine Lands) programs, and ASPECT(irborne Spectral Photometric Environmental Collection Technology) to recover the Cove from damages. 
            
            https://www.epa.gov/navajo-nation-uranium-cleanup/cove-area-mines
            
        The Activites of Kerr Mcgee stops at 2001 according to my analysis(go to in [Top 30 Facility visualization](#visualization)), due to all the legal pushback and brought by Anadrako Petroleum at 2006
    
        https://www.sec.gov/Archives/edgar/data/773910/000095012906007908/h38749exv99w1.htm
    2. **1998 Neveda Gold Mines LLC (Joint venture between Barrick and Newmon)**
        * We see a small spike **Neveda Gold Mines LLC** (Joint venture between Barrick and Newmont as of 2019), primary toxic chemical being released is mercury. According to Greg Jones and Glenn Miller. Amount of mercury released into the atomospehere from gold mines has not been systematically measured and reported, and reliable estimates were not available, they were esitmate based on the EPA's series of emisson factor requirements. but during 1997 metal mining companies were required to report to the EPA as the beginning of 1998, thus we see according to our graph([Top 30 Facility visualization](#visualization)) that Neveda Gold Mines LLC waste data begins at 1998. 
        
        * According to Miller and Jones Neveda Gold Mines released 3700 lbs of mercury air emission in 1998, Barrick released 13,629 tons of Mercury by-product in 1999, Newmont released 16,264 lbs of mercury by product in 1989. 
        
        * We can speculate that Majority of the pollution at the State of Utah and Neveda came from these Gold Mines([By State 2003 - 2025](#visualization)). Accoriding to my State Waste map 2003 - 2025 and 2020s most of the pollution occured in Lands with metal related chemicals such as mercury or mercury related compounds. 
        
        https://downloads.regulations.gov/EPA-HQ-SFUND-2015-0781-2119/content.pdf

    3. **1999 (Rio Tinto America Inc)**:

        * 
        
### Visualization:
1. Line chart depicting the trends of waste dumped by Top 10 facility(with the most toxic waste dumped) throughout the years.

    1. Top 30 Facility: 
        ![alt text](Frontend/chart/total_waste_throughout_top_10.png)[https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/total_waste_throughout_top_10.html]

    * Click the HTML for Interactive Mode. 

2. Dashboard of the Total Waste Released in the US states and counties. 
        
    1. From(2003 - 2025) 
        * By County 2003-2025:
            ![alt text](Frontend/chart/county_waste_dashboard_all_time.png)[https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/county_waste_dashboard_all_time.html]
            
        * By State 2003 - 2025: 
            ![alt text](Frontend/chart/waste_dashboard_all_time.png)[https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/waste_dashboard_all_time.html]
        
    2. From(2020 - 2025) 
        * By County
            ![alt text](Frontend/chart/county_waste_dashboard_2020s.png)[https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/county_waste_dashboard_2020s.html]
            
        * By State:
            ![alt text](Frontend/chart/waste_dashboard_2020s.png)[https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/waste_dashboard_2020s.html]

            
    * Click the HTML for Interactive Mode. 


Process used:
* Used SQLAlchemy ORM(Object Relational Mapping) to generate Tables and Column for the TRI Database. 
* Used requests to connect to the TRI metadata API endpoints and extracted raw data from it 
* Used the raw data and transformed them into Pandas DataFrame with
necessary columns needed for the TRI Database.
* Cleaned up the data in the Pandas DataFrame to make it ready for DataBase insertion. 
* Then finally used the SQLAlchemy Postgresql Dialects to create an Upsert logic to avoid duplicate entries or errors during the insertion process. 
* Extra: Used Alembic autogeneration for automatic Database Migrations. 