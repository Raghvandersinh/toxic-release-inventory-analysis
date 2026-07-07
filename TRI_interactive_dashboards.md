## Interactive Dashboards

**JUST FOLLOW THIS LINK (To Go Back To Home Page)** : https://raghvandersinh.github.io/toxic-release-inventory-analysis/

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
            max-width: 1650px;
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
    <h1>Interactive Dashboards</h1>
    <div class="dashboard-grid">

        <!-- Dashboard 1: Facility Trend Analysis -->
        <div style="margin: 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="padding: 1rem; background: #f5f5f5; border-bottom: 1px solid #e0e0e0; font-weight: bold;">
                Facility Trend Analysis - Top Facilities Throughout Years
            </div>
            <iframe 
                src="https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/line_chart/total_waste_throughout_top_10.html"
                width="57.5%" 
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
                Geographic Distribution - State Map (All Time: 2003-2025)
            </div>
            <iframe 
                src="https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/state_map/TRI_State_Map_Dashboard_Throughout.html"
                width="97%" 
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
                Geographic Distribution - County Map (All Time: 2003-2025)
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
                Geographic Distribution - State Map (Recent: 2020-2025)
            </div>
            <iframe 
                src="https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/state_map/TRI_State_Map_Dashboard_2020s.html"
                width="97%" 
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
                Geographic Distribution - County Map (Recent: 2020-2025)
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

        <div style="margin: 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="padding: 1rem; background: #f5f5f5; border-bottom: 1px solid #e0e0e0; font-weight: bold;">
                NAICS Industries Wastes - Tree Map (Recent: 2020-2025)
            </div>
            <iframe 
                src="https://raghvandersinh.github.io/toxic-release-inventory-analysis/Frontend/chart/tree_map/hierarchical_industries_tree_map.html"
                width="70%" 
                height="700px" 
                frameborder="0"
                loading="lazy"
                title="State Map 2020s"
                style="display: block;">
            </iframe>
        </div>

    </div>
</body>
</html>

