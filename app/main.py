import streamlit as st
import pandas as pd
import folium
import yaml
import os.path
from streamlit_folium import folium_static
import requests
from datetime import date




try:
    with open("/Users/deborahhaar/Desktop/ironhack-work/citi_bikes/config.yaml", 'r') as file:
        config = yaml.safe_load(file)
except Exception as e:
    print('Error reading config file')


def create_citi_map(df):
    
    m = folium.Map(location=[40.70868217336032, -74.0110311319653], zoom_start=15)
    
    for index, row in df.iterrows():
        
        folium.Marker(
            [row['start_lat'], row['start_lng']],
            tooltip=row['start_station_name'],
            popup="Station ID: " + str(row['start_station_id']),
            icon=folium.Icon(prefix='fa', icon = 'bicycle')
        ).add_to(m)

    return m



st.title('Citi Bike rides predictor')
st.markdown("This app predicts the number of rides per hour from these stations given the weather forecast")

station_info_path = "/Users/deborahhaar/Desktop/ironhack-work/citi_bikes/data/cleaned/station_info.csv"
data=pd.read_csv(station_info_path)

bike_map = create_citi_map(data)

#display map in streamlit
folium_static(bike_map)

#get weather

path = '/Users/deborahhaar/Desktop/ironhack-work/citi_bikes/app/date.txt'

check_file = os.path.isfile(path)

if check_file == True:
	with open("/Users/deborahhaar/Desktop/ironhack-work/citi_bikes/app/date.txt", "r") as file:
    		file_date = file.read()
	
	if file_date < str(date.today()):
		api_call="https://api.open-meteo.com/v1/forecast?latitude=40.7143&longitude=-74.006&hourly=temperature_2m,precipitation,windspeed_10m&temperature_unit=fahrenheit&windspeed_unit=mph&precipitation_unit=inch&timezone=America%2FNew_York&forecast_days=1"
		try:
			response = requests.get(api_call)
			st.write('getting latest weather')
		
		except:
			st.write("Could not get weather forecast")

		
		results = response.json()
		forecast = pd.DataFrame(results['hourly'])
		forecast.to_csv("/Users/deborahhaar/Desktop/ironhack-work/citi_bikes/data/cleaned/forecast.csv", index=False)


		today = str(date.today())
		with open("/Users/deborahhaar/Desktop/ironhack-work/citi_bikes/app/date.txt", "w") as file:
			file.write(today)

	else:
	    st.write('Weather forecast is up to date')

else:
	st.write('no date file')


forecast = pd.read_csv("/Users/deborahhaar/Desktop/ironhack-work/citi_bikes/data/cleaned/forecast.csv")
forecast_1day = forecast.copy()

forecast_1day['time']=pd.to_datetime(forecast_1day['time'], format="%Y-%m-%dT%H:%M").dt.strftime('%Y-%m-%d %H:%M:%S')
forecast_1day.columns = ['started_at_rounded', 'temperature_f', 'precipitation_in', 'windspeed_mph']

st.dataframe(forecast_1day, hide_index=True)

#cross join with station info

station_info = data.copy()

forecast_1day['key'] = 1
station_info['key'] = 1

merged_df = pd.merge(forecast_1day,station_info, on='key').drop('key', axis=1)

st.dataframe(merged_df)






