# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Search by a start date, or start and end date.<br/>"
        f"/api/v1.0/date/<start_date><br/>"
        f"/api/v1.0/date/<start_date>/<end_date><br/>"
        f"NOTE: dates must be entered in (YYYY-MM-DD) form. Date range:(2010-2017)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary"""
    # Gather data
    recent = session.query(Measurement).order_by(Measurement.date.desc()).first()
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= query_date).\
    filter(Measurement.date <= recent.date).all()
    
    session.close()

    # Create a dictionary and display
    precipitation_data = {}
    for date, prcp in year_data:
        precipitation_data[date] = prcp

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    # Gather data
    stations = session.query(Station.station).distinct()
    
    session.close()
    
    # Create list and display
    stations_list = []
    for station in stations:
        stations_list.append(station.station)
    
    return jsonify(stations_list)
    
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Query the dates and temperature observations of the most-active station for the previous year of data"""
    # Gather 
    recent = session.query(Measurement).order_by(Measurement.date.desc()).first()
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    recent_active_temps = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= query_date).\
    filter(Measurement.date <= recent.date).\
    filter(Measurement.station == "USC00519281").all()
    
    session.close()
    
    # Create list and display
    recent_active_temps
    temps_list = []
    for temps in recent_active_temps:
        temps_list.append(temps.tobs)
        
    return jsonify(temps_list)

@app.route("/api/v1.0/date/<start_date>")
@app.route("/api/v1.0/date/<start_date>/<end_date>")
def date(start_date, end_date=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    try:
        # Convert input to datetime objects
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
    
    # Gather temperature data within date range
        if end_date:
            end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
            temperature_data = session.query(
                func.min(Measurement.tobs).label('min_temp'),
                func.avg(Measurement.tobs).label('avg_temp'),
                func.max(Measurement.tobs).label('max_temp')
            ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        else:
            temperature_data = session.query(
                func.min(Measurement.tobs).label('min_temp'),
                func.avg(Measurement.tobs).label('avg_temp'),
                func.max(Measurement.tobs).label('max_temp')
            ).filter(Measurement.date >= start_date).all()
        
        session.close()
        
        # Create a dictionary to store the temperature data
        results = []
        for temp in temperature_data:
            result = {
                'min_temp': temp.min_temp,
                'avg_temp': temp.avg_temp,
                'max_temp': temp.max_temp,
            }
            results.append(result)
            
        return jsonify(results)
    
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use the format: YYYY-MM-DD.'}), 400


if __name__ == '__main__':
    app.run(debug=True)