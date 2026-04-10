# packages
import os
import hyswap
import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from dataretrieval import waterdata
from matplotlib import pyplot as plt
import geopandas as gpd

# importing data from usgs api
url = "https://api.waterdata.usgs.gov/ogcapi/v0/collections/monitoring-locations/items?f=json&state_code=26&limit=50000"

response = requests.get(url)
response.raise_for_status()
api_sites = response.json()

# printing the first 5
for i, item in enumerate(api_sites.get('features', [])):
    if i >= 5:
          break
    print(item)

# converting the json file to a pandas dataframe to get all the site information
mi_sites = pd.json_normalize(api_sites['features'])
# print(mi_sites.shape) # there are 17112 sites in Michigan
# some have the same coordinates, we can combine these later

# renaming columns
mi_sites.rename(columns={
    'properties.id' : 'id_2',
    'properties.agency_code' : 'agency_code',
    'properties.agency_name' : 'agency_name',
    'properties.monitoring_location_number' : 'monitoring_location_number',
    'properties.monitoring_location_name' : 'monitoring_location_name',
    'properties.district_code' : 'district_code',
    'properties.country_code' : 'country_code',
    'properties.country_name' : 'country_name',
    'properties.construction_date' : 'construction_date',
    'properties.aquifer_code' : 'aquifer_code',
    'properties.national_aquifer_code' : 'national_aquifer_code',
    'properties.aquifer_type_code' : 'aquifer_type_code',
    'properties.well_constructed_depth' : 'well_constructed_depth',
    'properties.hole_constructed_depth' : 'hole_constructed_depth',
    'properties.depth_source_code' : 'depth_source_code',
    'geometry.type' : 'geometry_type',
    'geometry.coordinates' : 'geometry_coordinates',
    'properties.state_code' : 'state_code',
    'properties.state_name' : 'state_name',
    'properties.county_code' : 'county_code',
    'properties.county_name' : 'county_name',
    'properties.minor_civil_division_code' : 'minor_civil_division_code',
    'properties.site_type_code' : 'site_type_code',
    'properties.site_type' : 'site_type',
    'properties.hydrologic_unit_code' : 'hydrologic_unit_code',
    'properties.basin_code' : 'basin_code',
    'properties.altitudes' : 'altitudes',
    'properties.altitude_accuracy' : 'altitude_accuracy',
    'properties.altitude' : 'altitude',
    'properties.altitude_method_code' : 'altitude_method_code',
    'properties.altitude_method_name' : 'altitude_method_name',
    'properties.vertical_datum' : 'vertical_datum',
    'properties.vertical_datum_name' : 'vertical_datum_name',
    'properties.horizontal_positional_accuracy_code' : 'horizontal_positional_accuracy_code',
    'properties.horizontal_positional_accuracy' : 'horizontal_positional_accuracy',
    'properties.horizontal_position_method_code' : 'horizontal_position_method_code',
    'properties.horizontal_position_method_name' : 'horizontal_position_method_name',
    'properties.original_horizontal_datum' : 'original_horizontal_datum',
    'properties.original_horizontal_datum_name' : 'original_horizontal_datum_name',
    'properties.drainage_area' : 'drainage_area',
    'properties.contributing_drainage_area' : 'contributing_drainage_area',
    'properties.time_zone_abbreviation' : 'time_zone_abbreviation',
    'properties.uses_daylight_savings' : 'uses_daylight_savings',
}, inplace=True)

# playing with streamlit
st.markdown("""
<style>

/* Make header scroll normally */
header[data-testid="stHeader"] {
    position: relative !important;
}

/* Expand ALL header containers */
header[data-testid="stHeader"],
header[data-testid="stHeader"] > div,
header[data-testid="stHeader"] div[data-testid="stToolbar"] {
    height: auto !important;
    min-height: 6rem !important;
    align-items: center !important;
}

/* Keep your original logo size */
img[alt="Logo"] {
    height: 6rem !important;
    width: auto !important;
}

/* Remove any weird spacing constraints */
header[data-testid="stHeader"] * {
    max-height: none !important;
}

</style>
""", unsafe_allow_html=True)

logo_url = "https://i.imgur.com/p2pULZk.png"

st.logo(logo_url, size="large", link=None, icon_image=None)

# Design front page
st.title("MiWater: Michigan Water Dashboard")

# Create two panels
# Set the page layout to wide mode for more space
st.set_page_config(layout="wide")

# Create two columns with unequal widths
col1, col2 = st.columns([0.3, 0.7])

# Keep only rows where coordinates exist and are lists
mi_sites = mi_sites[mi_sites["geometry_coordinates"].notna()]
mi_sites = mi_sites[mi_sites["geometry_coordinates"].apply(lambda x: isinstance(x, (list, tuple)))]

# Extract lon/lat
mi_sites["lon"] = mi_sites["geometry_coordinates"].apply(lambda x: x[0])
mi_sites["lat"] = mi_sites["geometry_coordinates"].apply(lambda x: x[1])

# making a list of all the monitoring locations that will work by hand because i give up
locations = pd.DataFrame({
    'site_id': ['USGS-04136900','USGS-04137005','USGS-04137680','USGS-04107850',
                'USGS-04108600','USGS-04108660','USGS-04133501','USGS-041275685',
                'USGS-041275689','USGS-04127800','USGS-04138030','USGS-04138536',
                'USGS-04142000','USGS-04143220','USGS-04040500','USGS-04041500',
                'USGS-04043097','USGS-04043150','USGS-04117004','USGS-04117500',
                'USGS-04157060','USGS-04126740','USGS-04096015','USGS-04101500',
                'USGS-04102500','USGS-04096515','USGS-04096590','USGS-040975299',
                'USGS-04096405','USGS-04103490','USGS-04103500','USGS-041035285',
                'USGS-04104945','USGS-04105000','USGS-04105500','USGS-041015313',
                'USGS-04101535','USGS-04101590','USGS-04101800','USGS-04127997',
                'USGS-04127885','USGS-04127917','USGS-04114498','USGS-04115000',
                'USGS-04123500','USGS-04135700','USGS-04135800','USGS-04057510',
                'USGS-04059000','USGS-04059500','USGS-04063522','USGS-04065650',
                'USGS-04065722','USGS-04111000','USGS-04147500','USGS-04148140',
                'USGS-04148295','USGS-04148500','USGS-04152049','USGS-04152238',
                'USGS-04152500','USGS-04031000','USGS-04032150','USGS-04037500',
                'USGS-04126970','USGS-04127200','USGS-04177080','USGS-04043016',
                'USGS-04043050','USGS-04159005','USGS-04159046','USGS-041590774',
                'USGS-04111379','USGS-04112000','USGS-04112500','USGS-04112850',
                'USGS-04113000','USGS-04114000','USGS-04116000','USGS-04137500',
                'USGS-04137716','USGS-041377255','USGS-04060500','USGS-04060993',
                'USGS-04062000','USGS-04062500','USGS-04153725','USGS-04153905',
                'USGS-04154000','USGS-04102786','USGS-04109000','USGS-04105700',
                'USGS-04106000','USGS-04106320','USGS-04106400','USGS-04106500',
                'USGS-04127570','USGS-04118500','USGS-04119000','USGS-04119055',
                'USGS-04119070','USGS-04119160','USGS-04001000','USGS-04146000',
                'USGS-04146063','USGS-04175748','USGS-04176000','USGS-04176063',
                'USGS-041843678','USGS-04172000','USGS-04045500','USGS-04046000',
                'USGS-04161820','USGS-04163400','USGS-04164000','USGS-04164100',
                'USGS-04164151','USGS-04164300','USGS-04164500','USGS-04164800',
                'USGS-04165500','USGS-04124200','USGS-04125550','USGS-04043238',
                'USGS-04043244','USGS-04044003','USGS-04057800','USGS-04057813',
                'USGS-04057814','USGS-04058100','USGS-04058200','USGS-04122500',
                'USGS-04059750','USGS-04066030','USGS-04066800','USGS-04153300',
                'USGS-04153500','USGS-04154512','USGS-04155500','USGS-04156000',
                'USGS-041210041','USGS-04121300','USGS-04176500','USGS-04176617',
                'USGS-04115265','USGS-04154612','USGS-04122100','USGS-04122200',
                'USGS-04121944','USGS-04121970','USGS-04122001','USGS-04122025',
                'USGS-04161000','USGS-04166100','USGS-04166300','USGS-040325155',
                'USGS-04033000','USGS-04036000','USGS-04040000','USGS-04121494',
                'USGS-04121500','USGS-04121507','USGS-04124500','USGS-04136000',
                'USGS-04136500','USGS-04128990','USGS-04108800','USGS-04108862',
                'USGS-04119400','USGS-04145000','USGS-04145785','USGS-04149000',
                'USGS-04151500','USGS-04157005','USGS-04056500','USGS-04144500',
                'USGS-04159130','USGS-04159492','USGS-04159900','USGS-04160600',
                'USGS-040970647','USGS-04097345','USGS-04097500','USGS-04097540',
                'USGS-0409754132','USGS-04098980','USGS-04099000','USGS-04150500',
                'USGS-04102148','USGS-04102700','USGS-04173500','USGS-04174040',
                'USGS-04174500','USGS-04174518','USGS-04176356','USGS-04176400',
                'USGS-04165710','USGS-04166500','USGS-04166700','USGS-04167000',
                'USGS-04167625','USGS-04168400','USGS-04168580','USGS-04168660',
                'USGS-04124000','USGS-04125460']
})

# picking the sites
mi_sites = mi_sites[mi_sites['id'].isin(locations['site_id'])]

# Start designing dashboard
with col1:
    st.write("Select a Michigan Monitoring Site:")
    layer = pdk.Layer(
        "ScatterplotLayer",
        mi_sites,
        id="id",
        get_position="[lon, lat]",
        get_color="[0, 0, 255, 160]",
        get_radius=4000,
        pickable=True,
        auto_highlight=True,
    )
    event = st.pydeck_chart(
        pdk.Deck(
            map_style = 'light',
            layers=[layer],
            initial_view_state=pdk.ViewState(
                latitude=44.3,
                longitude=-85.6,
                zoom=6
            ),
            tooltip={"text": "Site ID: {id}"}
        ),
        on_select="rerun",  # This makes it interactive!
        selection_mode="single-object",  # Allows clicking multiple points
    )
    # Check if anything is selected
    if event and "selection" in event:
        # Access the selected objects
        selected_objects = event["selection"]["objects"].get("id", [])

        st.info("Click a point on the map to see specific site data.")

with col2:
    tab1, tab2, tab3 = st.tabs(["Hydrograph", "Percentile", "Other"])

    selected_objects = []
    if event and "selection" in event:
        selected_objects = event["selection"]["objects"].get("id", [])

    if selected_objects:
        selected_df = pd.DataFrame(selected_objects)
        selected_sitename = selected_df.iat[0, 32]
        selected_id = selected_df.iat[0, 28]

        os.environ["API_USGS_PAT"] = "MIOx3md6PQUlTLSHUWa3V51GLGRXFtp6I81fmjec"

        # Streamflow (only once!)
        streamflow, metadata = waterdata.get_daily(
            monitoring_location_id=selected_id,
            parameter_code='00060',
            time='2010-01-01/..'
        )
        streamflow['time'] = pd.to_datetime(streamflow['time'])
        streamflow.set_index('time', inplace=True)

        # Temperature
        temperature = None
        try:
            temperature, metadata2 = waterdata.get_daily(
                monitoring_location_id=selected_id,
                parameter_code='00010',
                time='2010-01-01/..'
            )
            temperature['time'] = pd.to_datetime(temperature['time'])
            temperature.set_index('time', inplace=True)
        except Exception:
            temperature = None

        # Precipitation
        precipitation = None
        try:
            precipitation, metadata3 = waterdata.get_daily(
                monitoring_location_id=selected_id,
                parameter_code='00045',
                time='2010-01-01/..'
            )
            precipitation['time'] = pd.to_datetime(precipitation['time'])
            precipitation.set_index('time', inplace=True)
        except Exception:
            precipitation = None

        # Specific Conductance
        speccond = None
        try:
            speccond, metadata4 = waterdata.get_daily(
                monitoring_location_id=selected_id,
                parameter_code='00300',
                time='2010-01-01/..'
            )
            speccond['time'] = pd.to_datetime(speccond['time'])
            speccond.set_index('time', inplace=True)
        except Exception:
            speccond = None

        # Store everything
        st.session_state["streamflow"] = streamflow
        st.session_state["temperature"] = temperature
        st.session_state["precipitation"] = precipitation
        st.session_state["speccond"] = speccond
        st.session_state["selected_site"] = selected_sitename

with tab1:
    try:
        formatted = hyswap.rasterhydrograph.format_data(streamflow, data_column_name="value")
            # Create a new figure and axes for each plot
        hydrograph, ax = plt.subplots()
        ax = hyswap.plots.plot_raster_hydrograph(
            formatted,
            ax = ax,
            title = f"Raster Hydrograph for {selected_sitename}"
            )
        st.pyplot(hydrograph)
    except:
        st.write("Select a site.")

with tab2:
    try:
        # Define percentile thresholds to use
        percentile_thresholds = [5, 10, 25, 50, 75, 90, 95]
        # calculate fixed percentiles for entire dataset
        fixed_percentile_values = hyswap.percentiles.calculate_fixed_percentile_thresholds(
            streamflow['value'], percentile_thresholds)
        # calculate variable percentiles for each day of the year
        variable_percentile_values = hyswap.percentiles.calculate_variable_percentile_thresholds_by_day(
            streamflow, 'value', percentile_thresholds
        )
        # plotting
        # getting year/doy info
        streamflow_year = hyswap.utils.define_year_doy_columns(streamflow,
                                                               year_type='water',
                                                               clip_leap_day=True)
        streamflow_2025 = streamflow_year[streamflow_year['index_year'] == 2025]
        #plotting percentiles
        percentileplot, ax = plt.subplots()
        ax = hyswap.plots.plot_duration_hydrograph(
            variable_percentile_values,
            streamflow_2025,
            'value',
            ax = ax,
            data_label = 'Water Year 2025',
            title = f"Percentiles of Streamflow by Day of Year \n at {selected_sitename}",
            xlab = 'Month'
        )
        ax.set_xticklabels(['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'])
        st.pyplot(percentileplot)
    except:
        st.write("Select a site")

with tab3:
    st.subheader("Annual Averages by Site")
    site = st.session_state.get("selected_site", "")

    # Retrieve datasets from session_state
    datasets = {
        "Streamflow": ("streamflow", "Flow"),
        "Precipitation": ("precipitation", "Precip"),
        "Temperature": ("temperature", "°C"),
        "Specific Conductance": ("speccond", "µS/cm")
    }

    # Colors for each variable
    colors = {
        "Streamflow": "blue",
        "Precipitation": "green",
        "Temperature": "red",
        "Specific Conductance": "orange"
    }

    # Create 2x2 columns
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    cols = [col1, col2, col3, col4]

    # Reusable plotting function
    def plot_yearly_avg(df, title, ylabel, color='blue'):
        """
        Computes yearly average and plots a simple line chart.
        Returns the figure if data exists, else None.
        """
        if df is not None and not df.empty:
            try:
                yearly_avg = (
                    df
                    .assign(year=df.index.year)
                    .groupby("year")["value"]
                    .mean()
                )
                fig, ax = plt.subplots(figsize=(4,3))
                ax.plot(yearly_avg.index, yearly_avg.values, marker='o', color=color)
                ax.set_title(title)
                ax.set_xlabel("Year")
                ax.set_ylabel(ylabel)
                return fig
            except Exception as e:
                return None
        else:
            return None

    # Loop through datasets and display in 2x2 grid
    for i, (name, (key, ylabel)) in enumerate(datasets.items()):
        df = st.session_state.get(key)
        color = colors.get(name, 'blue')  # default to blue if missing
        fig = plot_yearly_avg(df, f"{name}\n{site}", ylabel, color=color)

        with cols[i]:
            if fig:
                st.pyplot(fig)
            else:
                st.markdown(
                    f"<p style='color:gray;text-align:center;'>No {name.lower()} data available</p>",
                    unsafe_allow_html=True
                )

st.write("Site Information Table")
mi_sites

st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col3:
    logo_url = "/Users/ramyasolai/Desktop/usgs.png"
    st.image(logo_url, width=200)
    st.write("Acknowledgments: Data from USGS")
