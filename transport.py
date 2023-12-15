# Copyright (c) johnsons-ds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Load packages
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.colored_header import colored_header
import requests

# Set page configuration
st.set_page_config(
    page_title="ACT Public Transport Data",
    page_icon="🚆",
    layout="centered",
    initial_sidebar_state="auto"
)


# Define the URLs for data sources
urls = {
    'Passenger data of daily boardings': 'https://www.data.act.gov.au/resource/4f52-nub8.csv?$query=SELECT%20date%2C%20local_route%2C%20light_rail%2C%20peak_service%2C%20rapid_route%2C%20school%2C%20other%20ORDER%20BY%20%3Aid%20ASC',
    'Passenger data of daily journey': 'https://www.data.act.gov.au/resource/nkxy-abdj.csv',
    'Daily boarding by passenger group': 'https://www.data.act.gov.au/resource/4d78-rcjw.csv?$query=SELECT%20date%2C%20other%2C%20adult%2C%20concession%2C%20tertiary%2C%20school_student%20ORDER%20BY%20date%20DESC'
}


# Sidebar: User Input
st.sidebar.markdown(""" ### Choose your input """) 
selected_url = st.sidebar.selectbox('Select Data Source', options=list(urls.keys()))# Create a selectbox for URL selection
date_range_option = st.sidebar.radio('Select date range', ['All Years', 'Custom Year'])


# Displaying a colored header with specified parameters
colored_header(
    label="ACT Public Transport 🚇 Data 📈",
    description="~ Developed by johnsons-ds",
    color_name="violet-70",
)

st.markdown(
    """
    This dataset contains daily Public Transport Patronage in types of services and passenger group. Paper tickets 
    sold by Ticket Vending Machines are excluded except for the ones on light rail platforms. This 
    dataset can be aggregated to provide daily Light Rail and bus patronage number.
    
    **Note: Due to delays in data processing, final number may take up to three days to accurately report on all passenger journeys.**

    ***Data source: https://www.data.act.gov.au/browse?q=transport&sortBy=relevance***

    Different service types:
    * Local route - # of boardings performed by local routes
    * Light rail - # of boardings performed by light rail
    * Peak service - # of boardings performed on weekdays before 9 am and between 4.30 pm and 6 pm
    * Rapid route - # of boardings performed by rapid routes
    * School - # of boardings performed by school service
    * Other - # of boardings performed by other services that are not mentioned above, such as shuttle services.

    Different passenger groups:
    * Other - # of baordings performed by other group of passengers such as employee and welfare.
    * Adult - # of boardings performed by adult
    * Concession - # of boardings performed by concession
    * Tertiary - # of boardings performed by tertiary
    * Student - # of boardings performed by school students

"""
)

# Load data
def load_data():
    data = pd.read_csv(urls[selected_url])
    #data.dtypes
    #lowercase = lambda x: str(x).lower()
    #data.rename(lowercase, axis='columns', inplace=True)
    # Convert the 'date' column to datetime format   
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y/%m/%d')
    # Sorting the data frame by datetime variable in ascending order (i.e., oldest to newest)
    data = data.sort_values(by='date', ascending=True, ignore_index=True)
    # Set index of data frame to the date
    data = data.set_index('date')
    data.index = pd.to_datetime(data.index)
    return data


data = load_data() # all data
weekly=data.resample('W').sum() # data summed by weekly
monthly=data.resample('M').sum() # data summed by month

st.write("---")
# Checkbox for the user to view the raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data) 

# Sidebar: User Input
selected_service = st.sidebar.multiselect('Select service type/group', data.columns, default=data.columns[3])  # Excluding 'date' column

if date_range_option == 'Custom Year':
    #selected_year = st.sidebar.date_input('Select Date Range', [data.index.min(), data.index.max()])
    start_year = st.sidebar.date_input('Start date', data.index.min())
    end_year = st.sidebar.date_input('End date', data.index.max())
    # Validate date range
    if pd.Timestamp(start_year) < pd.Timestamp(data.index.min()) or pd.Timestamp(end_year) > pd.Timestamp(data.index.max()) or pd.Timestamp(start_year) >= pd.Timestamp(end_year):
        st.sidebar.error(f"Invalid date range. Please select a valid date range within the dataset's available range - {pd.Timestamp(data.index.min()).strftime('%Y/%m/%d')} to {pd.Timestamp(data.index.max()).strftime('%Y/%m/%d')}.")
        st.stop()

    filtered_data = data.loc[start_year:end_year]
    filtered_weekly_data = weekly.loc[start_year:end_year]
    filtered_monthly_data = monthly.loc[start_year:end_year]
else:
    filtered_data = data  # Show all years
    filtered_weekly_data = weekly  # Show all years
    filtered_monthly_data = monthly # Show all years


# Data download button
if selected_url:
    response = requests.get(urls[selected_url])
    if response.status_code == 200:
        file_name = selected_url.split('/')[-1]  # Extract filename from URL

        st.sidebar.download_button(label='Download Data', data=response.content, file_name=file_name)
    else:
        st.error(f"Error fetching data from {urls[selected_url]}")

st.sidebar.markdown(
    """
    
"""
)
st.sidebar.markdown(
    """
    
"""
)
st.sidebar.markdown(
    """
    
"""
)
st.sidebar.markdown(
    """
    Developed by johnsons-ds [![GitHub](https://img.shields.io/badge/GitHub-Profile-blue?style=social&logo=github)](https://github.com/johnsons-ds)

"""
)




# Chart Section

# Pie Chart Section
st.header(f'Charts of {selected_url.lower()}')

# Get column names excluding the first column (date column)
composition_columns = filtered_data.columns[0:]

# Calculate the sum of each column in the filtered dataset
composition_data = filtered_data[composition_columns].sum()

# Create a pie chart using Plotly Express
pie_fig = px.pie(
    names=composition_data.index,
    values=composition_data.values,
    title=f'Pie chart of {selected_url.lower()}'
)
pie_fig.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(pie_fig)



# Main Content: Time Series Graph
st.title(f'Line charts of {selected_url.lower()}')

# Generate tick positions every six months
tick_positions = pd.date_range(start=filtered_data.index.min(), end=filtered_data.index.max(), freq='3M')

# Generate tick labels in the format '%b %Y'
tick_labels = tick_positions.strftime('%b\n%Y')

# Calculate moving average - SWITCHED OFF 7 December 2023
#moving_avg_window = 6  # Choose the window size for the moving average
#moving_avg = filtered_data[selected_service].rolling(window=moving_avg_window).mean()



# Monthly view
st.write("### Monthly view")
fig2 = px.line(filtered_monthly_data, x=filtered_monthly_data.index, y=selected_service)

# Customize the x-axis ticks
fig2.update_xaxes(rangeslider_visible=True,
                  tickmode='array',
                  tickvals=tick_positions,
                  ticktext=tick_labels,
                  rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    ))

# Move the legend to the top of the chart
fig2.update_traces(mode="lines", hovertemplate=None)
fig2.update_layout(legend=dict(orientation="h", y=1.0, x=0.1),
                  hovermode="x unified")
st.plotly_chart(fig2, height=1000, width=1200)



# Weekly view
st.write("### Weekly view")
fig1 = px.line(filtered_weekly_data, x=filtered_weekly_data.index, y=selected_service)

# Customize the x-axis ticks
fig1.update_xaxes(rangeslider_visible=True,
                  tickmode='array',
                  tickvals=tick_positions,
                  ticktext=tick_labels,
                  rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    ))

# Move the legend to the top of the chart
fig1.update_traces(mode="lines", hovertemplate=None)
fig1.update_layout(legend=dict(orientation="h", y=1.0, x=0.1),
                  hovermode="x unified")
st.plotly_chart(fig1, use_container_width=False, height=1000, width=1200)


# Daily view
st.write("### Daily view")
fig = px.line(filtered_data, x=filtered_data.index, y=selected_service)

# Customize the x-axis ticks
fig.update_xaxes(rangeslider_visible=True,
                  tickmode='array',
                  tickvals=tick_positions,
                  ticktext=tick_labels,
                  rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    ))

# Move the legend to the top of the chart
fig.update_traces(mode="lines", hovertemplate=None)
fig.update_layout(legend=dict(orientation="h", y=1.0, x=0.1),
                  hovermode="x unified")
st.plotly_chart(fig, use_container_width=False, height=1000, width=1200)




