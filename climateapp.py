# Import values
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta 

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    #List all available api routes.
    return (
        f"Available Routes Below:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/start date<br/>"
        f"Enter the start date in 'YYYY-MM-DD' format<br/>"
        f"<br/>"
        f"/api/v1.0/start date/end date<br/>"   
        f"Enter the dates in 'YYYY-MM-DD/YYYY-MM-DD' format<br/>"
    )
#Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()
    
    # Create a dictionary from the data and append to a list
    precipitation_values = []
    for row in results:
        prcp_dict = {row.date:row.prcp}
        precipitation_values.append(prcp_dict)

    return jsonify(precipitation_values)

# Return a json list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    #Return a list of all station names
    # Query all stations
    session = Session(engine)
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)

# Return a json list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
#    * Query for the dates and temperature observations from the last year.
#    * Return a JSON list of Temperature Observations (tobs) for the previous year..
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= last_year).\
        order_by(Measurement.date).all()

# Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for temp in temperature:
        dict = {"date": temp[0], "tobs": temp[1]}
        temperature_totals.append(dict)

    return jsonify(temperature_totals)

# Return a json list of the minimum temperature, the average temperature, and the max 
# temperature for a given start or start-end range.
@app.route("/api/v1.0/<start>")
def temperatures_start(start):
    #Given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than 
    #    and equal to the start date. 
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    
    # Convert list of tuples into normal list
    temperatures_start = list(np.ravel(results))

    return jsonify(temperatures_start)

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates 
# between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def temperatures_start_end(start, end):
    #When given the start and the end date, calculate the TMIN, TAVG, 
    #    and TMAX for dates between the start and end date inclusive.
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    
    # Convert list of tuples into normal list
    temperatures_start_end = list(np.ravel(results))

    return jsonify(temperatures_start_end)


if __name__ == "__main__":
    app.run(debug=True)