import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title and header using Markdown
st.markdown("# WALS Linguistic Features Explorer", unsafe_allow_html=True)

# Load the data
df = pd.read_csv('app/features_table.tsv', sep='\t')

# Initialize session state for search and selected area if not already set
if 'search_query' not in st.session_state:
    st.session_state.search_query = ''
if 'selected_area' not in st.session_state:
    st.session_state.selected_area = 'All Areas'  # Set default to "All Areas"

# Sidebar with navigation between pages
page = st.sidebar.radio("Choose a page:", ["Intro Page", "Main Page", "Statistics"])

# Intro Page
if page == "Intro Page":
    # Introductory section describing the page structure and what you can do on each
    st.markdown("""
        <h3>Welcome to the WALS Linguistic Features Explorer!</h3>
        <p>This tool allows you to explore linguistic features from the World Atlas of Language Structures (<a href="https://wals.info" target="_blank">WALS</a>), a comprehensive resource on cross-linguistic variation.</p>
        <p>The tool is structured into three main pages:</p>
        <ul>
            <li><strong>Intro Page:</strong> This is where you are currently. It provides an overview of the tool and explains the structure of the pages.</li>
            <li><strong>Main Page:</strong> On this page, you can filter linguistic features based on the <strong>Area</strong> and search for specific <strong>Linguistic Features</strong> or features by <strong>ID</strong>. You can view the filtered results in a table and download the data in CSV format for further analysis.</li>
            <li><strong>Statistics Page:</strong> This page displays basic statistics about the data, including the number of features in each area, represented through bar and pie charts. It also provides the total number of features in the dataset.</li>
        </ul>
        <p>Each page is designed to provide a different aspect of the data, from an overview and filtering options to statistical analysis, helping you explore the WALS linguistic features effectively.</p>
    """, unsafe_allow_html=True)

# Main Page for filtering by area and searching features
elif page == "Main Page":
    # Instructions for using the tool
    st.markdown("""
        <h3>To use the tool:</h3>
        <ul>
            <li>Use the sidebar to select a specific <strong>Area</strong> to filter the data.</li>
            <li>Use the search bar to find specific <strong>Linguistic Features</strong> or features related to an <strong>ID</strong>.</li>
            <li>Once you filter the data, you can view the results in a table format.</li>
            <li>You can also <strong>download the filtered data</strong> in CSV format for further analysis.</li>
        </ul>
    """, unsafe_allow_html=True)

    # Streamlit Sidebar for Area selection, including "All Areas"
    areas = ['All Areas'] + list(df['Area'].unique())
    selected_area = st.sidebar.selectbox('Choose an area:', areas, index=areas.index(st.session_state.selected_area))

    # Filter the dataframe based on the selected area
    if selected_area == 'All Areas':
        filtered_df = df
    else:
        filtered_df = df[df['Area'] == selected_area]

    # Add a text input field for searching linguistic features
    search_query = st.text_input('Search for a linguistic feature:', value=st.session_state.search_query)

    # Filter the dataframe based on the search query, including the 'Id' column
    if search_query:
        # Ensure case-insensitive search, and handle empty results gracefully
        filtered_search = filtered_df[
            filtered_df['Name'].str.contains(search_query, case=False, na=False) |
            filtered_df['Id'].astype(str).str.contains(search_query, case=False, na=False) |  # Search in 'Id' column
            filtered_df['Name'].str.contains(f'{search_query}', na=False)  # Number search
        ]
    else:
        filtered_search = filtered_df

    # Rename the 'Id' column to 'WALS feature ID'
    filtered_search = filtered_search.rename(columns={'Id': 'WALS feature ID'})

    # Display the filtered data (search results)
    st.markdown(f'Showing features for: <span style="color: #ff6347;">{selected_area}</span>', unsafe_allow_html=True)

    if filtered_search.empty:
        st.write("No features found matching your search.")
    else:
        # Reorder the columns to include "WALS feature ID" at the beginning
        filtered_search = filtered_search[['WALS feature ID', 'Name', 'Linguistic question', 'Possible values']]

        # Display the filtered dataframe as a table with the desired column order
        st.write(filtered_search)

    # Add a download button for the filtered data
    def convert_df(df):
        """Converts the DataFrame to CSV for downloading with UTF-8 encoding."""
        return df.to_csv(index=False, encoding='utf-8').encode('utf-8')

    # Convert the filtered dataframe to CSV
    csv = convert_df(filtered_search)

    # Add a button to download the filtered data
    st.download_button("Download filtered data", csv, "filtered_data.csv", "text/csv")

# Statistics Page
elif page == "Statistics":
    # Basic statistics
    st.subheader("Basic Statistics")

    # Count number of features in each area
    area_counts = df.groupby('Area').size()

    # Display statistics as bar chart
    st.markdown("### Number of features in each area (Bar Chart):")
    fig, ax = plt.subplots()
    area_counts.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_xlabel('Area')
    ax.set_ylabel('Number of Features')
    ax.set_title('Number of Features by Area')
    st.pyplot(fig)

    # Display statistics as pie chart
    st.markdown("### Distribution of Features by Area (Pie Chart):")
    fig, ax = plt.subplots()
    area_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax.set_ylabel('')  # Remove ylabel for better display
    ax.set_title('Feature Distribution by Area')
    st.pyplot(fig)

    # Display the total number of features in the dataset
    total_features = df.shape[0]
    st.write(f"Total number of features: {total_features}")

# Footer with HTML
st.markdown("<br><hr><p style='text-align: center;'>Powered by Streamlit</p>", unsafe_allow_html=True)
