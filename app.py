import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_echarts import st_echarts
import pandas as pd
import time
import matplotlib.pyplot as plt
import io
from utils import  generate_distance_matrix, algorithmes, run_algorithmes, convert_to_float


# Set page configuration
st.set_page_config(page_title="TSP Solver App", layout="wide")

# Inject custom CSS
st.markdown("""
    <style>
            
    button[kind="primary"] > div:has-text("x"),
    div.stButton > button {
        background-color: transparent !important;
        color: #ee6c4d !important;
        font-size: 20px !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px 8px !important;
    }

    div.stButton > button:hover {
        color: darkred !important;
        background-color: #ee6c4d !important;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)    


# Initialize session state variables
if 'locations' not in st.session_state:
    st.session_state.locations = []
if 'results' not in st.session_state:
    st.session_state.results = []

# Title
st.title("TSP Solver App")

# Helper function to truncate long strings
def truncate_text(text, max_length=30):
    return text if len(text) <= max_length else text[:max_length - 3] + "..."

# Sidebar for location input
with st.sidebar:
    st.header("Locations")
    
    # Display list of selected locations
    #if st.session_state.locations:
        #for idx, loc in enumerate(st.session_state.locations):
            #st.write(truncate_text(f"{loc['name']} (Lat: {loc['Geocordinate'][0] :.6f}, Lon: {loc['Geocordinate'][1]:.6f})"))
    # Display list with delete button

    for idx, loc in enumerate(st.session_state.locations):
        col1, col2 = st.sidebar.columns([0.85, 0.15])  # Text and delete button
        st.markdown('<div class="remove-button-container">', unsafe_allow_html=True)
        with col1:
            display_text = truncate_text(f"{loc['name']} (Lat: {loc['Geocordinate'][0] :.6f}, Lon: {loc['Geocordinate'][1]:.6f})")
            st.write(display_text)
        with col2:
            
            
            if st.button("x", key=f"remove_{idx}"):
                del st.session_state.locations[idx]
                st.session_state.results = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
  
    # Manual location inputs
    st.subheader("Add Location Manually")
    name = st.text_input("location name")
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, step=0.00001, format="%.5f")
    with col2:
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, step=0.00001, format="%.5f")
    
    if st.button("Add Location"):
        idx = len(st.session_state.locations)
        if not name : 
            name = f"location {len(st.session_state.locations)+1}"
        location = {"name" : name , "Geocordinate" : (lat, lon)}
        st.session_state.locations.append(location)
        st.rerun()

    # CSV Upload
    st.subheader("Upload Locations CSV")
    st.write("CSV should have 'latitude' and 'longitude' columns")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if 'latitude' in df.columns and 'longitude' in df.columns and name in df.columns:

                new_locations = list(zip(df['latitude'], df['longitude']))
                st.session_state.locations.extend(new_locations)
                st.success(f"Added {len(new_locations)} locations from CSV file")
                st.rerun()
            else:
                st.error("CSV must contain 'latitude' and 'longitude' columns")
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
    
    # Clear all locations
    if st.button("Clear All Locations"):
        st.session_state.locations = []
        st.session_state.results = []
        st.rerun()

    st.markdown("### 👤 Contact Me")
    st.markdown("""
    **Belaouali Anas**

    [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/anas-bellaouali/)
    [![GitHub](https://img.shields.io/badge/GitHub-000?logo=github&logoColor=white)](https://github.com/Bellaouali-anas)
    [bellaoualai.anas@gmail.com](mailto:bellaoualai.anas@gmail.com)
    """, unsafe_allow_html=True)
    st.markdown("Feel free to reach out or check out my work!")

# Main content area
col_map, col_controls = st.columns([3, 1])

# Create a map
with col_map:
    # Default location (center of the map) - adjust as needed
    default_location = [0, 0]
    if st.session_state.locations:
        # Center the map on the average of locations
        lats = [loc["Geocordinate"][0] for loc in st.session_state.locations]
        lons = [loc["Geocordinate"][1] for loc in st.session_state.locations]
        default_location = [sum(lats) / len(lats), sum(lons) / len(lons)]
    
    # Create the map
    m = folium.Map(location=default_location, zoom_start=3)
    
    # Add markers for each location
    for idx, loc in enumerate(st.session_state.locations):
        lat = loc["Geocordinate"][0]
        lon = loc["Geocordinate"][1]
        popup = f"Location {idx +1}: ({lat:.6f}, {lon:.6f})"
        folium.Marker(
            [lat, lon],
            popup=popup,
            icon=folium.Icon(color="blue", icon="map-pin")
        ).add_to(m)
    
    # Add the optimized route polyline if available
    if st.session_state.results:

        # Get coordinates of the optimized route
        lowest = min(st.session_state.results, key=lambda x: x["distance"])
        route_coords = [st.session_state.locations[i]["Geocordinate"] for i in lowest['optimized_route']]
        # Add the first location again to complete the circuit
        route_coords.append(route_coords[0])
        
        # Create the polyline
        folium.PolyLine(
            locations=[(lat, lon) for lat, lon in route_coords],
            color="red",
            weight=4,
            opacity=0.8
        ).add_to(m)
    
    # Display the map
    map_data = st_folium(m, width="100%", height=500)
    
    # Handle map clicks to add new locations
    if map_data["last_clicked"]:
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]
        idx = len(st.session_state.locations)
        new_location = location = {"name" : f"location {idx +1}" , "Geocordinate" : (clicked_lat, clicked_lon)}
        
        # Check if the location already exists to avoid duplicates
        if new_location not in st.session_state.locations:
            st.session_state.locations.append(new_location)
            st.rerun()

# TSP algorithm selection and execution
with col_controls:

    st.subheader("TSP Algorithms")
    # Multiselect input
    algorithms =  [algorithm for algorithm, _ in algorithmes]
    
    selected_algorithms = st.multiselect("Select 3 algorithms:",options=algorithms)

    # Execute TSP algorithm
    if st.button("Solve TSP"):

        if len(selected_algorithms) == 3: 
            if len(st.session_state.locations) < 3:
                st.error("Please add at least 3 locations to solve TSP")
            else:
                # Create distance matrix
                distance_matrix = generate_distance_matrix(st.session_state.locations)
            
                # Run algorithmes
                results = run_algorithmes(selected_algorithms, distance_matrix)
                st.session_state.results = results

                # Trigger rerun to update the map
                st.rerun()
         
        else : 
            st.error("Please select 3 algorithms to solve TSP")
    
    # calculate and display lowest distance
    if st.session_state.results:
     
        lowest = min(st.session_state.results, key=lambda x: x["distance"])

        st.metric(
            label="Optimal Distance",
            value=f"{lowest['distance']:.2f} km"
        )
    
        st.metric(
            label="Execution Time",
            value=f"{lowest['time']:.6f} sec"
        )

# Main content area
col_chart, col_df = st.columns([2, 1])

 
if st.session_state.results:

    with col_df:

        st.subheader("TSP Solution Results")

        results_df = pd.DataFrame({ 
            "Algorithem" : selected_algorithms,
            "Distance" : [result["distance"] for result in st.session_state.results],
            "time" : [result["time"] for result in st.session_state.results]
        })
        # Style the dataframe
        styled_df = results_df.style\
            .set_table_styles([
                {'selector': 'th', 'props': [('font-size', '16px'), ('background-color', '#f0f0f0'), ('color', '#333')]},
                {'selector': 'td', 'props': [('font-size', '14px'), ('color', '#444')]}
            ])\
            .format({
                "Distance (km)": "{:.2f}",
                "Time (s)": "{:.2f}"
            })

        # Display styled DataFrame without the index
        st.dataframe(styled_df.hide(axis="index"), use_container_width=True)

    with col_chart:
       
        # ECharts option for multiple lines
        option = {
            "backgroundColor": "#293241",
            "title": {
                "text": "Solution Progress",
                "left": "center",
                "textStyle": {
                    "color": "#e0fbfc",
                    "fontSize": 25,
                    "fontFamily": "Verdana",
                    "fontWeight": "bold"
                }
            },
            "tooltip": {
                "trigger": "axis",
                "backgroundColor": "#3d5a80",
                "borderColor": "#98c1d9",
                "borderWidth": 1,
                "textStyle": {
                    "color": "#e0fbfc",
                    "fontSize": 16
                }
            },
            "legend": {
                "data": selected_algorithms,
                "top": "10%",
                "textStyle": {
                    "color": "#98c1d9",
                    "fontSize": 16
                }
            },
            "xAxis": {
                "type": "category",
                "axisLine": {
                    "lineStyle": {
                        "color": "#f6fff8",
                    }
                },
                "axisLabel": {
                    "fontSize": 15,
                    "fontFamily": "Verdana",
                }
            },
            "yAxis": {
                "type": "value",
                "axisLine": {
                    "lineStyle": {
                        "color": "#f6fff8",
                    }
                },
                "axisLabel": {
                    "fontSize":  16,
                    "fontFamily": "Verdana"
                }
            },
            "grid": {
                "left": "10%",
                "right": "10%",
                "top": "20%",
                "bottom": "10%",
                "borderColor": "#f6fff8",
                "borderWidth": 2,
                "containLabel": True
            },
            "series": [
                {
                    "name": st.session_state.results[0]["algorithm"],
                    "type": "line",
                    "data": convert_to_float(st.session_state.results[0]["progress_data"]),
                    "lineStyle": {"width": 2},
                    "itemStyle": {"color": "#ee6c4d"}  # red
                },
                {
                    "name": st.session_state.results[1]["algorithm"],
                    "type": "line",
                    "data": convert_to_float(st.session_state.results[1]["progress_data"]),
                    "lineStyle": {"width": 2},
                    "itemStyle": {"color": "#e0fbfc"}  # blue
                },
                {
                    "name": st.session_state.results[2]["algorithm"],
                    "type": "line",
                    "data": convert_to_float(st.session_state.results[2]["progress_data"]),
                    "lineStyle": {"width": 2},
                    "itemStyle": {"color": "#98c1d9"}  # green
                }
            ]
        }

            # Show chart
        st_echarts(options=option, height="400px")

    




