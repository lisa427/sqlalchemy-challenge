import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import datetime as dt

from flask import Flask, jsonify

# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask setup
app = Flask(__name__)

# Flask routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<strong>Welcome to the Honolulu weather API</strong><br/></br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD <em>--Enter the start date you want</em><br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD <em>--Enter the start and end dates you want</em>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data as json"""
    session = Session(engine)
    last_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    last_date_dt = dt.datetime.strptime(last_date, "('%Y-%m-%d',)")
    year_ago = last_date_dt - dt.timedelta(days=365)
    precip_results = session.query(Measurement.date, Measurement.prcp).\
        filter(func.DATE(Measurement.date) > year_ago).all()
    session.close()

    date = [result[0] for result in precip_results]
    precip = [result[1] for result in precip_results]
    precip_dict = dict(zip(date, precip))

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return the station data as json"""
    session = Session(engine)
    station_results = session.query(Station.station).all()
    session.close()

    station_list = [result[0] for result in station_results]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the tobs data as json"""
    session = Session(engine)
    last_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    last_date_dt = dt.datetime.strptime(last_date, "('%Y-%m-%d',)")
    year_ago = last_date_dt - dt.timedelta(days=365)
    station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(desc(func.count(Measurement.station))).all()
    active_station = station_activity[0][0]
    temp_results = session.query(Measurement.tobs).\
        filter(func.DATE(Measurement.date) > year_ago).filter(Measurement.station == active_station).all()
    session.close()

    temp_list = [result[0] for result in temp_results]

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def temps_by_start(start):
    """Return temp data as json for dates greater than and equal to start date"""
    try:
        start_dt = dt.datetime.strptime(start, "%Y-%m-%d")
        session = Session(engine)
        temp_min = session.query(func.min(Measurement.tobs)).\
            filter(func.DATE(Measurement.date) >= start_dt).all()
        temp_avg = session.query(func.avg(Measurement.tobs)).\
            filter(func.DATE(Measurement.date) >= start_dt).all()
        temp_max = session.query(func.max(Measurement.tobs)).\
            filter(func.DATE(Measurement.date) >= start_dt).all()
        session.close()

        temp_dict = {}
        temp_dict["minimum_temperature"] = temp_min[0][0]
        temp_dict["average_temperature"] = temp_avg[0][0]
        temp_dict["maximum_temperature"] = temp_max[0][0]

        return jsonify(temp_dict)

    except ValueError:
        return jsonify({"error": "Date in wrong format"}), 404

@app.route("/api/v1.0/<start>/<end>")
def temps_by_start_end(start, end):
    """Return temp data as json for dates between start and end dates"""
    try:
        start_dt = dt.datetime.strptime(start, "%Y-%m-%d")
        end_dt = dt.datetime.strptime(end, "%Y-%m-%d")
        session = Session(engine)
        temp_min = session.query(func.min(Measurement.tobs)).\
            filter(func.DATE(Measurement.date) >= start_dt).\
            filter(func.DATE(Measurement.date) <= end_dt).all()
        temp_avg = session.query(func.avg(Measurement.tobs)).\
            filter(func.DATE(Measurement.date) >= start_dt).\
            filter(func.DATE(Measurement.date) <= end_dt).all()
        temp_max = session.query(func.max(Measurement.tobs)).\
            filter(func.DATE(Measurement.date) >= start_dt).\
            filter(func.DATE(Measurement.date) <= end_dt).all()
        session.close()

        temp_dict = {}
        temp_dict["minimum_temperature"] = temp_min[0][0]
        temp_dict["average_temperature"] = temp_avg[0][0]
        temp_dict["maximum_temperature"] = temp_max[0][0]

        return jsonify(temp_dict)

    except ValueError:
        return jsonify({"error": "Date in wrong format"}), 404

if __name__ == '__main__':
    app.run(debug=True)