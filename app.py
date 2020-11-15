import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
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
        f"Welcome to the Honolulu weather API"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date>"
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

    #precipitation_data = list(np.ravel(precip_results))
    date = [result[0] for result in  precip_results]
    precip = [result[1] for result in precip_results]
    precip_dict = dict(zip(date, precip))

    return jsonify(precip_dict)



if __name__ == '__main__':
    app.run(debug=True)