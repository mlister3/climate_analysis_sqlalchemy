from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Part 2: Design Your Climate App
# Now that you’ve completed your initial analysis, you’ll design a Flask API based on the queries that you just developed. 
#To do so, use Flask to create your routes as follows:

# 1. /
# Start at the homepage.
# List all the available routes.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
app = Flask(__name__)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

Station = Base.classes.station
Measurement = Base.classes.measurement

@app.route("/")
def home():
    return (
        f"Welcome to Thew's Climate App API!<br/><br/>"
        
        f"Available Routes:<br/><br/>"
        
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# 2. /api/v1.0/precipitation
# Convert the query results from your precipitation analysis 
# (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(bind=engine)
    
    # Calculate the date one year from the last date in the dataset
    recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query the precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {}
    for date, prcp in results:
        precipitation_data[date] = prcp
    
    return jsonify(precipitation_data)

# 3. /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(bind=engine)
    
    # Query the list of stations
    stations = session.query(Station.station, Station.name).all()
    
    session.close()
    
    # Convert the query results to a list of dictionaries
    station_list = []
    for station, name in stations:
        station_dict = {
            "station": station,
            "name": name
        }
        station_list.append(station_dict)
    
    return jsonify(station_list)

# 4. /api/v1.0/tobs
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(bind=engine)
    
    # Calculate the date one year from the last date in the dataset
    recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Find the most active station
    busiest_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()
    
    # Query the temperature observations for the most active station in the last 12 months
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == busiest_station[0]).\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()
    
    # Convert the query results to a list of dictionaries
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {
            "date": date,
            "tobs": tobs
        }
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

# 5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end=None):
    session = Session(bind=engine)
    
    # Query the temperature data based on start and end dates
    if end:
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).all()
    
    session.close()
    
    # Convert the query results to a list of dictionaries
    temp_stats_list = []
    for min_temp, avg_temp, max_temp in results:
        temp_stats_dict = {
            "min_temp": min_temp,
            "avg_temp": avg_temp,
            "max_temp": max_temp
        }
        temp_stats_list.append(temp_stats_dict)
    
    return jsonify(temp_stats_list)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)