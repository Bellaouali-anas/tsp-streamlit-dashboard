import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from utils import  generate_distance_matrix, algorithmes, run_algorithmes, assemble_progress, to_excel_bytes
from plots import plot_execution_time, plot_memory_usage, get_algorithm_progress_fig, plot_cpu_usage

from Styles.SidebarStyle import sidebar_style
from Styles.BaseStyle import base_style
from Styles.BodyStyle import body_style



st.set_page_config(page_title="TSP Solver App", layout="wide")




st.markdown(base_style, unsafe_allow_html=True)
# Initialize session state variables
if 'locations' not in st.session_state:
    st.session_state.locations = []
if 'results' not in st.session_state:
    st.session_state.results = []
if 'csv_uploaded' not in st.session_state:
    st.session_state.csv_uploaded = False



# Helper function to truncate long strings
def truncate_text(text, max_length=50):
    return text if len(text) <= max_length else text[:max_length - 3] + "..."


# Sidebar for location input
with st.sidebar:
  
    # Inject custom HTML and CSS
    st.markdown(sidebar_style, unsafe_allow_html=True)


    # Manual location inputs
    st.subheader("Add Location Manually")
    name = st.text_input("location name")
    Location_input = st.columns(2)
    with Location_input[0]:
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, step=0.00001, format="%.5f")
    with Location_input[1]:
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, step=0.00001, format="%.5f")
    
    if st.button("Add Location"):
        idx = len(st.session_state.locations)
        if not name : 
            name = f"location {len(st.session_state.locations)+1}"
        location = {"name" : name , "geo_coordinates" : (lat, lon)}
        st.session_state.locations.append(location)
        st.rerun()

    if st.session_state.locations :
        st.header("Locations")

        if len(st.session_state.locations) <= 7:
            locations_container =  st.container(border=True)
        else :
            locations_container =  st.container(height= 280)

        with locations_container:
           
            for idx, loc in enumerate(st.session_state.locations):
                display_text = truncate_text(
                    f"<strong>{loc['name']}</strong> (Lat: {loc['geo_coordinates'][0]:.6f}, Lon: {loc['geo_coordinates'][1]:.6f})"
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

        # Clear all locations
        if st.button("Clear All Locations"):
            st.session_state.locations = []
            st.session_state.results = []
            st.session_state.csv_uploaded =False
            uploaded_file = None
            df_preview = None
            st.rerun()

        excel_data = to_excel_bytes(st.session_state.locations)

        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name="locations.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    # CSV Upload Section
    st.subheader("Upload Locations CSV")
    st.write("*CSV should have 'name', 'latitude' and 'longitude' columns")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv", "xlsx"])


    # Show only if a file is selected and not already uploaded
    if uploaded_file is not None :
        try:
            if uploaded_file.name.endswith('.csv'):
                df_preview = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df_preview = pd.read_excel(uploaded_file)
                #print("file uplaoded")
            else:
                st.error("Unsupported file format.")
                df_preview = None

            if df_preview is not None and not st.session_state.csv_uploaded:
                st.write("📄 Preview of uploaded file:")
                df_no_index = df_preview[['name', 'latitude', 'longitude']].head().reset_index(drop=True)
                st.dataframe(df_no_index)

                # Confirm upload
                if st.button("✅ Upload File"):
                    if all(col in df_preview.columns for col in ['name', 'latitude', 'longitude']):
                        new_locations = [
                            {"name": row['name'], "geo_coordinates": (row['latitude'], row['longitude'])}
                            for _, row in df_preview.iterrows()
                        ]

                        st.session_state.locations.extend(new_locations)
                        st.success(f"✅ Successfully added {len(new_locations)} locations.")
                        st.session_state.csv_uploaded = True
                        df_preview = None
                        st.rerun()
                    else:
                        st.error("❌ File must contain 'name', 'latitude' and 'longitude' columns.")

        except Exception as e:
            st.error(f"⚠️ Error reading file: {e}")

        

    st.markdown("### 👤 Contact Me")
    st.markdown("""
    **Belaouali Anas**

    [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/anas-bellaouali/)
    [![GitHub](https://img.shields.io/badge/GitHub-000?logo=github&logoColor=white)](https://github.com/Bellaouali-anas)
    [bellaoualai.anas@gmail.com](mailto:bellaoualai.anas@gmail.com)
    """, unsafe_allow_html=True)
    st.markdown("Feel free to reach out or check out my work!")


st.markdown(body_style, unsafe_allow_html=True)

# Use columns to center
col1, col2, _ = st.columns([3, 4, 1])

with col1: 
    st.image("Images/header_img.png", width=400)

with col2:


    #add top margin top
    st.markdown("""<div class="top-margin"></div>""", unsafe_allow_html=True)
    
    # Title
    st.markdown(
    """
    <div class="centered-title">TSP Algorithms simulation</div>
    """,
    unsafe_allow_html=True
    )

    # Description
    st.markdown(
    """
    <div class="custom-text">
        This web app helps compare the performance of different optimization algorithms in solving the Traveling Salesman Problem (TSP) using real-world locations. Built for educational purposes, the app is free to use and still in development. More algorithms will be added soon. Anyone with feedback or who wishes to contribute or test their algorithm is welcome to contact me via email or LinkedIn (links in the sidebar). The source code is available on GitHub.
    </div>
    <div class="custom-text">   
         
    </div>
    """,
    unsafe_allow_html=True
    )

    
# Main content area
col_map, col_results = st.columns([2, 1])


# Create a map
with col_map:

    #add top margin top
    st.markdown("""<div class="top-margin"></div>""", unsafe_allow_html=True)

    # Default location (center of the map) - adjust as needed
    default_location = [0, 0]
    if st.session_state.locations:
        # Center the map on the average of locations
        lats = [loc["geo_coordinates"][0] for loc in st.session_state.locations]
        lons = [loc["geo_coordinates"][1] for loc in st.session_state.locations]
        default_location = [sum(lats) / len(lats), sum(lons) / len(lons)]
    
    # Create the map
    m = folium.Map(location=default_location, zoom_start=3)
    
    # Add markers for each location
    for idx, loc in enumerate(st.session_state.locations):
        lat = loc["geo_coordinates"][0]
        lon = loc["geo_coordinates"][1]
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
        route_coords = [st.session_state.locations[i]["geo_coordinates"] for i in lowest['optimized_route']]

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
        new_location = location = {"name" : f"location {idx +1}" , "geo_coordinates" : (clicked_lat, clicked_lon)}
        
        # Check if the location already exists to avoid duplicates
        if new_location not in st.session_state.locations:
            st.session_state.locations.append(new_location)
            st.rerun()
 
        
with col_results : 

    #add top margin top
    st.markdown("""<div class="top-margin"></div>""", unsafe_allow_html=True)

    #add sub-header
    st.subheader("TSP algorithms")

    # Multiselect input
    algorithms =  [algorithm for algorithm, _ in algorithmes]
    selected_algorithms = st.multiselect("Select 3 algorithms:",options=algorithms)

    # Execute TSP algorithm
    if st.button("Solve TSP"):

        if selected_algorithms: 
            if len(st.session_state.locations) < 3:
                st.error("Please add at least 3 locations to solve TSP")
            else:
                # Create distance matrix
                distance_matrix = generate_distance_matrix(st.session_state.locations)

                print('selected algo : ',selected_algorithms)
                # Run algorithmes
                results = run_algorithmes(selected_algorithms, distance_matrix)
                #print('results before : ' , results)
                st.session_state.results = results

                # Trigger rerun to update the map
                st.rerun()
         
        else : 
            st.error("Please select 3 algorithms to solve TSP")
    
    # calculate and display lowest distance
    if st.session_state.results:
     
        st.subheader("Solution")

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



if st.session_state.results:

    # Display progress over time
    algos_progress = assemble_progress(st.session_state.results)
    fig = get_algorithm_progress_fig(algos_progress, selected_algorithms)
    st.plotly_chart(fig, use_container_width=True) 

    # charts place
    col_time, col_memory, col_cpu = st.columns([1, 1, 1])

    with col_time : 
        # Display execution time
        fig = plot_execution_time(st.session_state.results)
        st.plotly_chart(fig, use_container_width=True)

    with col_memory :
        # Display memory used
        fig = plot_memory_usage(st.session_state.results)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_cpu :
        # Display memory used
        fig = plot_cpu_usage(st.session_state.results)
        st.plotly_chart(fig, use_container_width=True)