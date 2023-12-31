# weatherdataprocessing.R
# Susan Reefman - Nabu
# Version: 1


### TO DO:
#### Add loading data from python file to R script
#### Implementing altitude in dataset
#### Add check weather column in data
#### Add return to python file function

# Load necessary libraries
library(lubridate)
library(reticulate)

# Set working directory

# Functions

# Load data

# Get the CSV file path from the command line arguments
# args <- commandArgs(trailingOnly = TRUE)
# csv_file <- args[1]

# Read the data from the CSV file
weatherdata <- read.csv('~/Datasets/testdataset.csv')

# Main
## Preprocess data

data <- data.frame(weatherdata$lat, weatherdata$lon, weatherdata$dt, weatherdata$sunrise, weatherdata$sunset, weatherdata$temp, weatherdata$pressure, weatherdata$humidity, weatherdata$dew_point, weatherdata$wind_speed, weatherdata$weather_main)
colnames(data) <- c("lat", "lon", "dt", "sunrise", "sunset", "temp", "pressure", "humidity", "dew_point", "wind_speed", "weather")

data$date_per_hour <- as.POSIXct(data$dt, origin = "1970-01-01", tz = "UTC")
data$date <-  substr(as.character(data$date_per_hour), 1, 10)

# Check if columns are numeric
data$lat <- as.numeric(data$lat)
data$lon <- as.numeric(data$lon)
data$temp <- as.numeric(data$temp)
data$pressure <- as.numeric(data$pressure)
data$humidity <- as.numeric(data$humidity)
data$dew_point <- as.numeric(data$dew_point)
data$wind_speed <- as.numeric(data$wind_speed)

# Remove rows with NA values
data <- data[complete.cases(data), ]

# Check if temp is between -20 and 40 degrees
if (!all(data$temp >= -20) && !all(data$temp <= 40)) {
  data <- data[data$temp >= -20 & data$temp <= 40, ]
}

# Convert pressure from hPa to kPa
data$pressure <- data$pressure / 10

# Check if pressure is between 85 and 110 kPa
if (!all(data$pressure >= 85) && !all(data$pressure <= 110)) {
  data <- data[data$pressure >= 85 & data$pressure <= 110, ]
}

# Check if humidity is between 0 and 100 percent
if (!all(data$humidity >= 0) && !all(data$humidity <= 100)) {
  data <- data[data$humidity >= 0 & data$humidity <= 100, ]
}

# Check if dew_point is between -33 and 35 degrees
if (!all(data$dew_point >= -33) && !all(data$dew_point <= 35)) {
  data <- data[data$dew_point >= -33 & data$dew_point <= 35, ]
}

# Check if wind_speed is between 0 and 115 m/s
if (!all(data$wind_speed >= 0) && !all(data$wind_speed <= 115)) {
  data <- data[data$wind_speed >= 0 & data$wind_speed <= 115, ]
}

# Get direct sunshine hours
data$sunrise <- as.POSIXct(data$sunrise, origin = "1970-01-01", tz = "UTC")
data$sunset <- as.POSIXct(data$sunset, origin = "1970-01-01", tz = "UTC")

## Get unique dates in the dataset
unique_dates <- unique(data$date)

## Iterate through each date and count 'Clear' occurrences between sunrise and sunset
for (date in unique_dates) {
  filtered_data <- data[data$date == date & data$date_per_hour >= data$sunrise & data$date_per_hour <= data$sunset, ]
  clear_count <- sum(filtered_data$weather == "Clear")
  data[data$date == date, "sunshine_hour"] <- clear_count
}

## Prepare data for ET calculation

# Group by date
df <- data.frame(unique(as.Date(data$date)))
colnames(df) <- "date"

df$day_of_year <- yday(df$date)
df$lat <-  tapply(data$lat, data$date, min)
df$lon <-  tapply(data$lon, data$date, min)
df$Tmin <-  tapply(data$temp, data$date, min)
df$Tmax <- tapply(data$temp, data$date, max)
df$Tmean <- tapply(data$temp, data$date, mean)
df$RHmin <- tapply(data$humidity, data$date, min)
df$RHmax <- tapply(data$humidity, data$date, max)
df$uz <- tapply(data$wind_speed, data$date, mean)
df$n <- tapply(data$sunshine_hour, data$date, min)
df$pressure <- tapply(data$pressure, data$date, mean)


## Return the R dataframe as Python object
write.csv(df, file = '~/Datasets/new', row.names = FALSE)



