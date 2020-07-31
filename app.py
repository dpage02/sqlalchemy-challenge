import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite")



# reflect an existing database into a new model
# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect = True)

# Save references to each table
measurement = Base.classes.measurement
station= Base.classes.station

from flask import Flask, jsonify


app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the Home Page <br> Available Routes <br>"
        f"/api/v1.precipitaion <br>"
        f"/api/vq.0/stations <br>"
        f"/api/v1.0/tobs <br>"
        f"/api/v1.0/YYYY-MM-DD<br>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )

@app.route("/api/v1.precipitaion")
def precipitation():
    session = Session(engine)

    # Design a query to retrieve the last 12 months of precipitation data and plot the results

    query = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()

    stat_id = query[0][0]
    
    stat_query = session.query(measurement.date, measurement.prcp).filter(measurement.station == stat_id).all()

    # Perform a query to retrieve the data and precipitation scores
    
    stat_id = query[0][0]

    session.close()

    # create a dictionary data 
    all_precip = []
    for date, prcp in stat_query:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_precip.append(prcp_dict)
    return jsonify(all_precip)

@app.route("/api/vq.0/stations")
def stations():

    session = Session(engine)

    station_name_count = session.query(station.name, func.count(measurement.station)).filter(measurement.station == station.station)\
        .group_by(measurement.station).all()

    station_list = list(np.ravel(station_name_count))
    session.close()

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

    stat_query = session.query(measurement.tobs).filter(measurement.date >= query_date).\
        filter(measurement.station == "USC00519281").all()

    session.close()

    tobs1 = list(np.ravel(stat_query))

    return jsonify(tobs1)

@app.route("/api/v1.0/<start_date>")
def start(start_date):

    session = Session(engine)

    return_temp = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()
    
    session.close()

    return jsonify(return_temp)
    
@app.route("/api/v1.0/<start_date>/<end_date>")
def range(start_date,end_date):

    session = Session(engine)

    return_temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    session.close()

    return jsonify(return_temps)


if __name__ == "__main__":
    app.run(debug = True )