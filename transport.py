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
import requests

# Define the URLs
urls = {
    'Passenger data of daily boardings': 'https://www.data.act.gov.au/resource/4f52-nub8.csv',
    'Passenger data of daily journey': 'https://www.data.act.gov.au/resource/nkxy-abdj.csv',
    'Daily boarding by passenger group': 'https://www.data.act.gov.au/resource/4d78-rcjw.csv'
}


# Sidebar: User Input
st.sidebar.markdown(""" ### Choose your input """) 
selected_url = st.sidebar.selectbox('Select Data Source', options=list(urls.keys()))# Create a selectbox for URL selection
date_range_option = st.sidebar.radio('Select date range', ['All Years', 'Custom Year'])


st.write("# ACT Public Transport Data")
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

#@st.cache_data
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


data = load_data()
weekly=data.resample('W').sum()
monthly=data.resample('M').sum()


# Checkbox for the user to view the raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data) 

# Sidebar: User Input
selected_service = st.sidebar.selectbox('Select service type/group', data.columns)  # Excluding 'date' column


if date_range_option == 'Custom Year':
    selected_year = st.sidebar.selectbox('Select Year', data.index.year.unique())  # Unique years in the index
    filtered_data = data[data.index.year == selected_year]
    filtered_weekly_data = weekly[weekly.index.year == selected_year]
    filtered_monthly_data = monthly[monthly.index.year == selected_year]
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
st.header('Composition of Selected Dataset')

# Get column names excluding the first column (date column)
composition_columns = filtered_data.columns[1:]

# Calculate the sum of each column in the filtered dataset
composition_data = filtered_data[composition_columns].sum()

# Create a pie chart using Plotly Express
pie_fig = px.pie(
    names=composition_data.index,
    values=composition_data.values,
    title=f'Composition of {selected_url}'
)

st.plotly_chart(pie_fig)

# Main Content: Time Series Graph
st.title('Time Series View')

# Generate tick positions every six months
tick_positions = pd.date_range(start=filtered_data.index.min(), end=filtered_data.index.max(), freq='3M')

# Generate tick labels in the format '%b %Y'
tick_labels = tick_positions.strftime('%b\n%Y')

# Calculate moving average
moving_avg_window = 6  # Choose the window size for the moving average
moving_avg = filtered_data[selected_service].rolling(window=moving_avg_window).mean()


# Monthly view
st.write("### Monthly view")
fig2 = px.line(filtered_monthly_data, x=filtered_monthly_data.index, y=selected_service, title=f'Count of {selected_service} Over Time')

# Customize the x-axis ticks
fig2.update_xaxes(rangeslider_visible=True,
                  tickmode='array',
                  tickvals=tick_positions,
                  ticktext=tick_labels)
st.plotly_chart(fig2)

# Weekly view
st.write("### Weekly view")
fig1 = px.line(filtered_weekly_data, x=filtered_weekly_data.index, y=selected_service, title=f'Count of {selected_service} Over Time')

# Customize the x-axis ticks
fig1.update_xaxes(rangeslider_visible=True,
                  tickmode='array',
                  tickvals=tick_positions,
                  ticktext=tick_labels)
st.plotly_chart(fig1)


# Daily view
st.write("### Daily view")
fig = px.line(filtered_data, x=filtered_data.index, y=selected_service, title=f'Count of {selected_service} Over Time')

# Customize the x-axis ticks
fig.update_xaxes(rangeslider_visible=True,
                  tickmode='array',
                  tickvals=tick_positions,
                  ticktext=tick_labels)

# Add moving average line trace
fig.add_scatter(x=filtered_data.index, y=moving_avg, mode='lines', name=f'Moving Average ({moving_avg_window} months)', line_color='orange')
st.plotly_chart(fig)




