# Citi Bikes ride predictor

The Citi Bikes ride predictor aims to predict the number of rentals at 30 stations in Lower Manhattan.

[Citi Bike stations](src/map.png "Citi Bike stations")

## Requirements
To run the notebooks you should have jupyter lab or jupyter notebook installed

Create an environment and run `pip install -r requirements.txt`

## Data

### Bike data
The data used in this project is from [Citi Bike NYC](https://citibikenyc.com/system-data).

The data spans from July 2021 to June 2023.

### Weather data
Weather data was obtained from [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api) with the following settings:
- Location coordinate for NYC
- Date July 1, 2021 and June 30, 2023
- Temperature, Precipitation, Windspeed(10m) boxs checked
- Units of measurement: Fahrenheit, in, Mph

Run the notebooks as follows:
1. Download the files from Citi Bike (link above) into the folder `data/raw`
2. Run `notebooks/cleaning_data.ipynb`