# Irrigation_system
The objective of this project is the data analysis and control of irrigation systems in agriculture by using meteorological data and satellite images. This involves employing evapotranspiration calculation methods in combination with vegetation index analysis.

## Introduction

Understanding evapotranspiration rates is crucial for effective irrigation management throughout the crop growth cycle. Evapotranspiration, the combined process of water evaporation from soil and plant transpiration, provides insights into the water requirements of crops.

This project focuses on calculating the crop evapotranspiration rate (ETc) through calculating the reference evapotranspiration rate (ET0) using meteorological data and a specific crop coefficient (Kc) curve using the Normalized Difference Vegetation Index acquired from satellite images. The Penman-Monteith method, recommended by the Food and Agriculture Organization (FAO), is employed for its accuracy and reliability in estimating the rates. The [FAO](https://www.fao.org/3/x0490e/x0490e00.htm) guidelines, detailed in 'Crop Evapotranspiration - Guidelines for computing crop water requirements - FAO Irrigation and Drainage Paper 56' , provide comprehensive definitions and information about all the parameters used in the calculation.

By combining meteorological data, satellite images and the recommended method, this project aims to enhance the accuracy of water outflow predictions, particularly tailored for the specific crop corn. The calculated ETc values serve as a valuable tool for farmers and stakeholders in optimizing irrigation practices throughout the agricultural cycle.

## Project Overview
The project is organized the following:

- `ET0Calculation.py`: Implements the Penman-Monteith method to calculate reference evapotranspiration (ET0).
- `ETcCalculation.py`: Utilizes the calculated ET0 and crop coefficients to estimate crop evapotranspiration (ETc).
- `main.py`: Serves as the entry point for running the project.
- `model.py`: Defines the machine learning model to predict crop evapotranspiration when NDVI data is not available.
- `sample.csv`: A sample CSV file for testing and demonstration purposes.

- **Get_Weather_Data:**
  - `get_weather_data.py`: Retrieves meteorological data from Open Weather API.
  - `weather_data_processing.py`: Processes and prepares weather data for analysis.

- **NDVI_Data:**
  - `Kc_curve.py`: Generates a crop coefficient (Kc) curve based on NDVI values.
  - `ndvi_processing.py`: Processes and analyzes Normalized Difference Vegetation Index (NDVI) data.

## Installation
To use this script, please follow the steps stated below.

**Step 1: Acquiring Files**

Either [clone](https://github.com/Susanreefman/Irrigation_system/blob/main/sample.csv) or acquire API keys from OpenWeather [One Call API 3.0](https://openweathermap.org/api/one-call-3)
and [Google Elevation API](https://developers.google.com/maps/documentation/elevation/overview). Download NDVI values from [Copernicus](https://www.copernicus.eu/en/access-data) or [Planet](https://developers.planet.com/docs/basemaps/).

**Step 2: Installing Python**

The script was developed in the language Python (version 3.7.9). Please follow the instructions on how to install Python [here](https://docs.python.org/3/index.html).

### Installing Necessary Packages

In addition, a necessary external package needs to be installed; [pwlf](https://jekel.me/piecewise_linear_fit_py/index.html) (version 2.2.1) is used to predict breakpoints in the Kc curve. After that, execute the following command on the command line:

```bash
python3 -m pip install pwlf
```
Now, you are set to use this program.

## Usage
Use the following steps to run the program. 

### Using the sample file

If you are using the provided sample file, execute the following commands:

To run the main program with the sample file
```bash
$ python3 main.py -f sample.csv -r [name of result file]
```
To run the model script with the sample file
```bash
$ python3 model.py -t [result file] -p [file with data to predict] -r [name of result file]
```

### Using your own data
**Step 1: Add an Environment file**
- Create an `.env` file in the working directory
- Add the following lines to the `.env` file, replacing `[apikey]` with your own API keys. 

```bash
api_key_w=[apikey]  # Your OpenWeather One Call API 3.0 key
api_key_a=[apikey]  # Your Google Elevation API key
```

**Step 2: Get weather data**
- Run the script to retrieve weather data
```bash
$ python3 Get_Weather_Data/get_weather_data.py -d [date] -l [latitude] -o [longitude] -r [result file]
```
- Process the weather data
```bash
$ python3 Get_Weather_Data/weather_data_processing.py -f [resulting file] -r [new result file]
```

**Step 3: Acquire NDVI values**
- Obtain NDVI values from [Copernicus](https://www.copernicus.eu/en/access-data) or [Planet](https://developers.planet.com/docs/basemaps/)
- Add these values to the corresponding dates in the resulting weather file.
(Optional: Run the NDVI processing script to format NDVI values correctly)
```bash
$ python3 NDVI_Data/ndvi_processing.py -f [file] -r [result file]
```

**Step 4: Run the main program**

- To run the main program with your data
```bash
$ python3 main.py -f [your data file] -r [name of result file]
```

- To run the model script with your data
```bash
$ python3 model.py -t [file with training data] -p [file with predicting data] -r [result file]
```

## Contact
If you have any questions, suggestions, or encounter issues, feel free to reach out:
 [email](mailto:h.s.reefman@st.hanze.nl)
