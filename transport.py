# https://www.data.act.gov.au/resource/5x84-xpn7.csv



import streamlit as st
import pandas as pd
import plotly.express as px

def run():
    st.set_page_config(
        page_title="Daily Public Transport Passenger Journeys by Service Type",
        page_icon="🚇",
    )

run()

# Load your time series dataset
# Assuming your dataset is in a CSV file named 'transport_data.csv'
DATA_URL = ('https://www.data.act.gov.au/resource/nkxy-abdj.csv')

st.write("# Daily Public Transport Passenger Journeys by Service Type")
st.markdown(
    """
    This dataset contains daily Public Transport Patronage in types of services. Paper tickets 
    sold by Ticket Vending Machines are excluded except for the ones on light rail platforms. This 
    dataset can be aggregated to provide daily Light Rail and bus patronage number.
    Note: Due to delays in data processing, final number may take up to three days to accurately report on all passenger journeys.

    Different service types:
      * Local route - # of journeys performed by local routes
      * Light rail - # of journeys performed by light rail
      * Peak service - # of journeys performed on weekdays before 9 am and between 4.30 pm and 6 pm
      * Rapid route - # of journeys performed by rapid routes
      * School - # of journeys performed by school service
      * Other - # of journeys performed by other services that are not mentioned above, such as shuttle services.

"""
)

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
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

# Checkbox for the user to view the raw data
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data) 


# Sidebar: User Input
st.sidebar.title('Choose your input')
date_range_option = st.sidebar.radio('Select Date Range', ['All Years', 'Custom Range'])
selected_service = st.sidebar.selectbox('Select Service Type', data.columns)  # Excluding 'date' column

if date_range_option == 'Custom Range':
    selected_year = st.sidebar.selectbox('Select Year', data.index.year.unique())  # Unique years in the index
    filtered_data = data[data.index.year == selected_year]
    filtered_weekly_data = weekly[weekly.index.year == selected_year]
else:
    filtered_data = data  # Show all years
    filtered_weekly_data = weekly  # Show all years



# Main Content: Time Series Graph
st.title('Time Series View')

# Generate tick positions every six months
tick_positions = pd.date_range(start=filtered_data.index.min(), end=filtered_data.index.max(), freq='3M')

# Generate tick labels in the format '%b %Y'
tick_labels = tick_positions.strftime('%b\n%Y')
# Weekly patronage over time view
st.write("### Weekly patronage")
fig1 = px.line(filtered_weekly_data, x=filtered_weekly_data.index, y=selected_service, title=f'{selected_service} Patronage Over Time')

# Customize the x-axis ticks
fig1.update_xaxes(rangeslider_visible=True,
                  tickmode='array',
                  tickvals=tick_positions,
                  ticktext=tick_labels)
st.plotly_chart(fig1)


# Daily patronage over time view
st.write("### Daily patronage")
fig = px.line(filtered_data, x=filtered_data.index, y=selected_service, title=f'{selected_service} Patronage Over Time')

# Customize the x-axis ticks
fig.update_xaxes(rangeslider_visible=True,
                  tickmode='array',
                  tickvals=tick_positions,
                  ticktext=tick_labels)
st.plotly_chart(fig)




