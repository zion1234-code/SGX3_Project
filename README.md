# SGX3 Traffic Incident API

📘 *A project developed for the SGX3 Coding Institute.*

This Flask-based web service provides access to traffic incident data from Austin, Texas. The API allows users to filter incidents by time and location using various query parameters.

---

## 🚦 Dataset

The data is loaded from `atxtraffic.csv`, which contains published traffic incident records including date, time, latitude, and longitude.

---

## 🧰 Requirements

Make sure you have Python 3 installed and install the required packages:

```bash
pip install flask pandas
   #SGX3 Coding Institute Repo
   

# SGX3_Project

This repository contains Python programs developed as part of the SGX3 Coding Institute. The primary focus of these programs is to process and analyze traffic incident data.

## Table of Contents
- [app.py](#apppy)
- [consumer.py](#consumerpy)
- [atxtraffic.csv](#atxtrafficcsv)

## app.py

`app.py` is a Flask application that provides several API endpoints for filtering and querying traffic incident data. It utilizes the Haversine formula to calculate distances for nearby incident queries.

### Features:
- **Data Loading and Preparation**: Loads `atxtraffic.csv`, parses dates, and adds `Year` and `Hour` columns for easier filtering.
- **Haversine Distance Calculation**: Includes a utility function to calculate the distance between two geographical points.
- **API Endpoints**:
    - `/`: A simple home endpoint.
    - `/FilteredIncidents`: Filters incidents based on a specified column name, value, and year.
    - `/IncidentsByHourRange`: Returns incidents that occurred within a specified hour range.
    - `/NearbyIncidents`: Returns incidents within a 1 km radius of a given latitude and longitude.

### Setup and Usage:
1. Ensure you have Python 3 and `pip` installed.
2. Install the required libraries:
   ```bash
   pip install Flask pandas
   ```
3. Make sure `atxtraffic.csv` is in the same directory as `app.py`.
4. Run the application:
   ```bash
   python app.py
   ```
   The application will run on `http://0.0.0.0:8046`.

### API Examples:
- **Filtered Incidents**: `http://localhost:8046/FilteredIncidents?ColumnName=Street&ColumnValue=Main&Year=2023`
- **Incidents by Hour Range**: `http://localhost:8046/IncidentsByHourRange?start=9&end=17`
- **Nearby Incidents**: `http://localhost:8046/NearbyIncidents?latitude=34.0522&longitude=-118.2437`

## consumer.py

`consumer.py` is another Flask application designed to filter traffic incident data based on hour or location. It loads the `atxtraffic.csv` dataset and provides two API endpoints.

### Features:
- **Data Loading**: Loads `atxtraffic.csv` and preprocesses it by converting date columns and ensuring latitude/longitude are float types.
- **API Endpoints**:
    - `/filter_by_hour`: Filters incidents by a specific hour.
    - `/filter_by_location`: Filters incidents within a specified radius of a given latitude and longitude.

### Setup and Usage:
1. Ensure you have Python 3 and `pip` installed.
2. Install the required libraries:
   ```bash
   pip install Flask pandas
   ```
3. Make sure `atxtraffic.csv` is in the same directory as `consumer.py`.
4. Run the application:
   ```bash
   python consumer.py
   ```
   The application will run on `http://0.0.0.0:8046`.

### API Examples:
- **Filter by Hour**: `http://localhost:8046/filter_by_hour?hour=10`
- **Filter by Location**: `http://localhost:8046/filter_by_location?lat=34.0522&lon=-118.2437&radius=0.05`

## atxtraffic.csv

This CSV file contains the raw traffic incident data used by both `app.py` and `consumer.py`. It is expected to have columns such as `Published Date`, `Latitude`, `Longitude`, and other relevant incident details.





