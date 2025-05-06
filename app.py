import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_echarts import st_echarts
import pandas as pd
from utils import  generate_distance_matrix, algorithmes, run_algorithmes, convert_to_float, equalize_length



st.set_page_config(page_title="TSP Solver App", layout="wide")


# Inject custom HTML and CSS
st.markdown("""
    <style>
        .location-box {
            border: 1px solid #E0FBFC;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 0px;
            background-color: #98C1D9;
        }
        .location-text {
            font-size: 14px;
            font-family: 'Segoe UI', sans-serif;
            color: #333;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
     
        }
        .stButton>button {
            background-color: #98C1D9;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            padding: 4px 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'locations' not in st.session_state:
    st.session_state.locations = []
if 'results' not in st.session_state:
    st.session_state.results = []



# Helper function to truncate long strings
def truncate_text(text, max_length=50):
    return text if len(text) <= max_length else text[:max_length - 3] + "..."


# Sidebar for location input
with st.sidebar:

    if st.session_state.locations :
        st.header("Locations")
    
    # Display list of selected locations
    #if st.session_state.locations:
        #for idx, loc in enumerate(st.session_state.locations):
            #st.write(truncate_text(f"{loc['name']} (Lat: {loc['Geocordinate'][0] :.6f}, Lon: {loc['Geocordinate'][1]:.6f})"))
    # Display list with delete button

    for idx, loc in enumerate(st.session_state.locations):
        display_text = truncate_text(
            f"<strong>{loc['name']}</strong> (Lat: {loc['Geocordinate'][0]:.6f}, Lon: {loc['Geocordinate'][1]:.6f})"
        )

        with st.container():
            cols = st.columns([0.85, 0.15])
            with cols[0]:
                st.markdown(f"<div class='location-box'><div class='location-text'>{display_text}</div>",  unsafe_allow_html=True)
            with cols[1]:
                if st.button("x", key=f"remove_{idx}"):
                    del st.session_state.locations[idx]
                    st.session_state.results = []
                    st.rerun()
            
            st.markdown(f"</div>", unsafe_allow_html=True)

  
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
    st.write("*CSV should have 'latitude' and 'longitude' columns")
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



    

# Use columns to center
col1, col2, col3 = st.columns([3,3,1])
with col1:
    
    st.image("header_img.png", width=400)

with col2:

    #add top margin top
    st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)

    # Title
    st.title("TSP Solver App")

    st.markdown("""
    <div style="padding-top: 20px;">
        <p style="color: #555; font-size: 18px; max-width: 700px; margin: auto;">
            A study-focused Streamlit web app to visualize and compare different algorithms 
            solving the Traveling Salesman Problem (TSP). Built for learning, experimentation, 
            and educational purposes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    
# Main content area
col_map, col_results = st.columns([2, 1])


# Create a map
with col_map:

    #add top margin top
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

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
        
with col_results : 

    #add top margin top
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    #add sub-header
    st.subheader("TSP algorithms")

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
     
        st.subheader("TSP Solution")

        # find the best solution
        lowest = min(st.session_state.results, key=lambda x: x["distance"])

        # show the minimal distance
        st.metric(
            label="Optimal Distance",
            value=f"{lowest['distance']:.2f} km"
        )

        # show the execution time to find the minimal time
        st.metric(
            label="Execution Time",
            value=f"{lowest['time']:.6f} sec"
        )


# charts place
col_chart, col_df = st.columns([3, 2])

 
if st.session_state.results:

    with col_df:


        # Define ECharts option for the histogram
        hist_option = {
            "backgroundColor": "#293241",
            "title": {
                "text": "Execution Time Histogram ",
                "left": "center",
                "textStyle": {
                    "color": "#e0fbfc",
                    "fontSize": 25,
                    "fontFamily": "Verdana",
                    "fontWeight": "bold"
                }
            },
            "tooltip": {
                "trigger": "axis"
            },
            "xAxis": {
                "type": "category",
                "data": selected_algorithms,
                "axisLabel": {"rotate": 45,
                              "fontSize": 12,
                            "fontFamily": "Verdana",
                            "color": "#f6fff8"
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
                    "fontSize": 12,
                    "fontFamily": "Verdana"
                }
            },
            "series": [{
                "type": "bar",
                "data": [result["time"] for result in st.session_state.results],
                "itemStyle": {
                    "color": "#e0fbfc"
                }
            }]
        }

        # Render the chart
        st_echarts(options=hist_option, height="400px")

    with col_chart:
       
        #Line_1, Line_2, Line_3  = equalize_length()

        # ECharts option for multiple lines
        option = {
            "backgroundColor": "#98C1D9",
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
                    "color": "#293241",
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
                    "itemStyle": {"color": "#ee6c4d"},  # red
                    "emphasis": {
                            "focus": "series",
                            "label": {
                                "show": True,
                                "formatter": "{c}",
                                "fontSize": 14
                            }
                        }
                },
                {
                    "name": st.session_state.results[1]["algorithm"],
                    "type": "line",
                    "data": convert_to_float(st.session_state.results[1]["progress_data"]),
                    "lineStyle": {"width": 2},
                    "itemStyle": {"color": "#e0fbfc"},  # blue
                    "emphasis": {
                            "focus": "series",
                            "label": {
                                "show": True,
                                "formatter": "{c}",
                                "fontSize": 14
                            }
                        }
                },
                {
                    "name": st.session_state.results[2]["algorithm"],
                    "type": "line",
                    "data": convert_to_float(st.session_state.results[2]["progress_data"]),
                    "lineStyle": {"width": 2},
                    "itemStyle": {"color": "#293241"},  # green
                    "showSymbol": True,
                    "emphasis": {
                            "focus": "series",
                            "label": {
                                "show": True,
                                "formatter": "{c}",
                                "fontSize": 14
                            }
                        }
                }
            ]
        }

            # Show chart
        st_echarts(options=option, height="400px")

    




