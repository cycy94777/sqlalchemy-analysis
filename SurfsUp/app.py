# import dependenices
from flask import Flask, jsonify
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import sqlalchemy as sql
import datetime as dt

# using Flask to create python app
app = Flask(__name__)
# generate the engine to the sqlite file
engine =create_engine('sqlite:///Resources/hawaii.sqlite')
# reflect the database schema
Base = automap_base()
Base.prepare(autoload_with=engine)
# save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station
# create and binds the session between the python app and database
session = Session(engine)

# query the most recent date and one year before the date
recent = session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1).all()
session.close()
recent = list(np.ravel(recent))
recent_y = recent[0]
oneyear = dt.datetime.strptime(recent_y,"%Y-%m-%d")-dt.timedelta(days=366)

## Flask API
# homepage: list all available routes
@app.route('/')
def homepage():
    link = """
        Available Routes:  <br>
            /api/v1.0/precipitation <br>
            /api/v1.0/stations <br>
            /api/v1.0/tobs <br>
            /api/v1.0/<start> <br>
            /api/v1.0/<start>/<end> <br>
        """
    return link

# precipitation analysis: retrieve and convert datas to 
# a dictionary using date as keys and prcp as values for the most recent year.
@app.route('/api/v1.0/precipitation')
def prcp_date():
   
    data = session.query(Measurement.date, Measurement.prcp).\
           filter(Measurement.date >=oneyear).filter(Measurement.date <= recent_y).all()
    
    session.close()
    date_prcp = {}
    for result in data:
        date, prcp = result
        date_prcp[date]=prcp
           
    return jsonify(date_prcp)


# each station datas : return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def station():
    sel = [Station.id,Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    station_data = session.query(*sel).all()
    session.close()
    stations=[]
    for row in station_data:
        id, station, name, lat, lon, elev = row
        station_dict = {}
        station_dict['id']= id
        station_dict['station']= station
        station_dict['name']= name
        station_dict['latitide']= lat
        station_dict['longitude']= lon
        station_dict['elevation']= elev
        stations.append(station_dict)
    
    return jsonify(stations)

# returns jsonified data of dates and temperature observations
# for the most active station (USC00519281) the last year
@app.route('/api/v1.0/tobs')
def tob():
   
    active_data = session.query(Measurement.date,
                                Measurement.tobs).\
                                filter(Station.station==Measurement.station).\
                                filter(Station.id==7).\
                                filter(Measurement.date >=oneyear).\
                                filter(Measurement.date <= recent_y).\
                                all()
    session.close()
    
    date_tob=[]
    for row in active_data:
        date_temp = {}
        date, temp = row
        date_temp['date']=date
        date_temp['temperature']=temp
        date_tob.append(date_temp)

    return jsonify(date_tob)

# design the route that return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range.
@app.route('/api/v1.0/<start>')
def start_date(start):
    a = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),
                      func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    tob_list = []
    for min_tob, max_tob, avg_tob in a:
        tob_dict = {}
        tob_dict['TMIN']=min_tob
        tob_dict['TMAX']=max_tob
        tob_dict['TAVG']=avg_tob
        tob_list.append(tob_dict)
    
    return jsonify(tob_list)


# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a start-end range.
@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    a = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),
                      func.avg(Measurement.tobs)).filter(Measurement.date >= start).\
                      filter(Measurement.date <= end).all()
    session.close()
    tob_list = []
    for min_tob, max_tob, avg_tob in a:
        tob_dict = {}
        tob_dict['TMIN']=min_tob
        tob_dict['TMAX']=max_tob
        tob_dict['TAVG']=avg_tob
        tob_list.append(tob_dict)
    
    return jsonify(tob_list)
        

if __name__ == "__main__":
    app.run(debug=True)