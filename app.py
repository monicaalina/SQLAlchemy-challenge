# import depencies

import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify


# engine = create_engine("sqlite:///hawaii.sqlite")

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine,reflect = True)

# We can view all of the classes that automap found

Base.classes.keys()

# Save references to each table

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)


app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"Welcome to the Surfs Up Page!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end><br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    session.close()
    precipitation_data = session.query(Measurement).filter(Measurement.date >= '2016-08-23').filter(Measurement.date <= '2017-08-23')
    precipitation_df = pd.read_sql_query(precipitation_data.statement, session.bind)
    precipitation_df_final = precipitation_df[["date", "prcp"]].set_index("date")
    return jsonify(precipitation_df_final.to_dict())


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [Measurement.station, func.count(Measurement.station), Station.name]
    stations = session.query(*sel).filter(Station.station == Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    session.close()
    return jsonify(stations)



@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    MostActiveStation = 'USC00519281'
    TheStation=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==MostActiveStation).filter(Measurement.date <= '2017-08-23').filter(Measurement.date >= '2016-08-23').all()
    session.close()    
    return jsonify(TheStation)



@app.route("/api/v1.0/<start>")
def Single(start):
    session = Session(engine)
    StartDate = dt.datetime.strptime(start,'%Y-%m-%d')
    SingleData = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= StartDate).all()
    session.close()
    TripData = list(np.ravel(SingleData))
    return jsonify(TripData)



@app.route("/api/v1.0/<start>/<end>")
def Return(start, end):
    session = Session(engine)  
    StartDate = dt.datetime.strptime(start,'%Y-%m-%d')
    EndDate = dt.datetime.strptime(end,'%Y-%m-%d')
    ReturnData = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= StartDate).filter(Measurement.date <= EndDate).all()
    session.close()
    TravelData = list(np.ravel(ReturnData))

    return jsonify(TravelData)



if __name__ == "__main__":
    app.run(debug=True)