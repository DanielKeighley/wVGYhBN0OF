import json
from flask import Flask, request
import datetime
import statistics

app = Flask(__name__)

sensor_data = json.load(open("sensors.json"))

@app.route("/")
def index():
	return "Home Page"

#Returns all data from all sensors
@app.route("/sensor_data", methods = ["GET"])
def get_sensor_all():
	return {"All Sensors" : sensor_data}

#Returns all sensor data of sensor with specified ID
@app.route("/sensor_data/<int:sensor_id>", methods = ["GET"])
def get_sensor(sensor_id):
		for sensor in sensor_data:
			if sensor["sensor_id"] == sensor_id:
				return {"Sensor Data" : sensor_data[sensor_id]}
		return {"Sensor Not Found" : []}

#Returns all sensor data of sensors in specified country	
@app.route("/sensor_data/country/<country_name>", methods = ["GET"])
def get_sensor_country_name(country_name):
	#I would usually use regex to check input, but this was a quick way to rule out at least numbers
	if country_name.isnumeric():
		return {"Invalid Country Name" : []}
	else:
		sensor_list = []
		for sensor in sensor_data:
			if sensor["country_name"] == country_name:
				sensor_list.append(sensor)
		if sensor_list == []:
			return {"No Sensors In This Country / Invalid Country" : []}
		return {"Sensor Data" : sensor_list}	

#Returns all sensor data of sensors in specified city
@app.route("/sensor_data/city/<city_name>", methods = ["GET"])
def get_sensor_city_name(city_name):
	if city_name.isnumeric():
		return {"Invalid City Name" : []}
	else:
		sensor_list = []
		for sensor in sensor_data:
			if sensor["city_name"] == city_name:
				sensor_list.append(sensor)
		if sensor_list == []:
			return {"No Sensors In This City / Invalid City" : []}
		return {"Sensor Data" : sensor_list}

#Returns all metrics for all sensors that have any recorded. Also returns the average value for all non-date metrics.
#The requirements say the application must return the average value of metrics, but I was unsure if it meant JUST the average
#or both the metrics AND the average so I decided to do both to cover all bases.
@app.route("/metrics", methods = ["GET"])
def get_metrics_all():
	metric_list = []
	#I would prefer to dynamically create lists based on the found keys within the metrics
	#but for the sake of brevity I am hard coding these in here
	temperature_list = []
	humidity_list = []
	precipitation_list = []
	wind_list = []
	for sensor in sensor_data:
		if sensor.get("metrics"):
			metric_list.append(sensor["metrics"])
	for sensor_metric in metric_list:
		for metric in sensor_metric:
			for key in metric:
				if key == "temperature":
					temperature_list.append(metric.get(key))
				elif key == "humidity":
					humidity_list.append(metric.get(key))
				elif key == "precipitation":
					precipitation_list.append(metric.get(key))
				elif key == "wind":
					wind_list.append(metric.get(key))
	#I would prefer to break this out into a function that collects the data and calculates the averages.
	#As this is for proof of concept I have decided to only calculate the averages for getting all metrics
	#as without a function for this, the readability of my code would suffer.
	avg_temperature = statistics.mean(temperature_list)
	avg_humidity = statistics.mean(humidity_list)
	avg_precipitation = statistics.mean(precipitation_list)
	avg_wind = statistics.mean(wind_list)
	metric_results = [{"Average Temperature" : avg_temperature, "Average Humidity" : avg_humidity, "Average Precipitation" : avg_precipitation, "Average Wind Speed" : avg_wind,}, {"All Metrics" : metric_list}]
	return {"Average Metrics" : metric_results}

#Returns all metrics for sensor with specified ID, if any metrics exist.
#Will let you know if either the sensor is not found or if that sensor has no metrics recorded.
@app.route("/metrics/<int:sensor_id>", methods = ["GET"])
def get_metrics(sensor_id):
	metric_list = []
	dates = []
	#This calls a function that will, after some input validation, return a list of dates between now
	#and the supplied number of days ago.
	if request.args:
		dates = get_date_range_from_params(request.args)

	for sensor in sensor_data:
		if sensor["sensor_id"] == sensor_id:
			if sensor.get("metrics"):
				for reading in sensor["metrics"]:
					if request.args:
						#This casts the date str to an instance of date
						adate = datetime.datetime.strptime(reading.get("date"), '%Y-%m-%d')
						if adate.date() not in dates:
							continue
					metric_list.append(reading)
			else:
				return {"No Metrics For Sensor" : []}
	if metric_list == []:
		return {"Sensor Not Found" : []}

	#This ensures that if no date range is specified, only the most recent reading is returned
	if not request.args:
		metric_list = find_most_recent_reading(metric_list)
	return {"metrics" : metric_list}
	
#Returns all metrics for sensors within specified country, if any metrics exist.
#If params are supplied in the form of a number of days ago to go back up to 1 month
#this only returns metrics from that date range. eg. if you pass ?days=31 it will query
#up to one month back
@app.route("/metrics/country/<country_name>", methods = ["GET"])
def get_metrics_country_name(country_name):
	metric_list = []
	dates = []
	if request.args:
		dates = get_date_range_from_params(request.args)

	for sensor in sensor_data:
		if sensor.get("metrics") and sensor["country_name"] == country_name:
			for reading in sensor["metrics"]:
				#This is checking if the reading is within the desired date range
				if request.args:
					#This casts the date str to an instance of date
					adate = datetime.datetime.strptime(reading.get("date"), '%Y-%m-%d')
					if adate.date() not in dates:
						continue
				metric_list.append(reading)
	#This ensures that if no date range is specified, only the most recent reading is returned
	if not request.args:
		metric_list = find_most_recent_reading(metric_list)
	return {"metrics" : metric_list}

#Returns all metrics for sensors within specified city, if any metrics exist.
@app.route("/metrics/city/<city_name>", methods = ["GET"])
def get_metrics_city_name(city_name):
	metric_list = []
	dates = []
	if request.args:
		dates = get_date_range_from_params(request.args)

	for sensor in sensor_data:
		if sensor.get("metrics") and sensor["city_name"] == city_name:
			for reading in sensor["metrics"]:
				#This is checking if the reading is within the desired date range
				if request.args:
					#This casts the date str to an instance of date
					adate = datetime.datetime.strptime(reading.get("date"), '%Y-%m-%d')
					if adate.date() not in dates:
						continue
				metric_list.append(reading)
	#This ensures that if no date range is specified, only the most recent reading is returned
	if metric_list and not request.args:
		metric_list = find_most_recent_reading(metric_list)
	return {"metrics" : metric_list}

#Creates a new sensor either with just and ID or based on the url params associated with the POST request.
#Using just a quick way to get an ID that should always be unique as long as deletion is not supported as this is a proof of concept piece.
@app.route("/sensor_data", methods = ["POST"])
def register_sensor():
	unique_id = len(sensor_data)
	new_sensor = {"sensor_id" : unique_id}
	if request.args:
		params = request.args
		for key in params:
			if key == "country_name" or key == "city_name" or key == "metrics":
				#For brevity I am only doing a single form of input validation, in reality I would be much more thorough
				#And I would ensure that metrics is a list of 0+ dicts
				if params.get(key).isnumeric():
					return {"Values Can Not Be Numeric" : []}
				new_sensor[key] = params.get(key)
			else:
				return {"Invalid Key" : key}		
		sensor_data.append(new_sensor)
		with open("sensors.json", "w") as db:
			json.dump(sensor_data, db, indent=4)
		return {"Registered" : new_sensor}
	#This returns a sensor with just an ID, which is what I assume the requirements mean by
	#not requiring arbitrary metadata and registering by ID
	else:
		return {"Registered" : new_sensor}

#Takes a metric reading in from POST params and adds this reading to the selected sensor's metrics/creates metrics if none existed previously.
@app.route("/metrics/<int:sensor_id>", methods = ["POST"])
def add_metrics(sensor_id):
	reading = {}
	if request.args:
		params = request.args
		for key in params:
			#Accepts only relevent data. If duplicate keys are submitted, only the first is accepted.
			if key == "date" or key == "temperature" or key == "humidity" or key == "precipitation" or key == "wind":
				#Did not have time for input validation here
				reading[key] = params.get(key)
			else:
				return {"Must Only Supply Valid Metric Types" : []}
	else:
		return {"Must Supply Metrics" : reading}

	for sensor in sensor_data:
		if sensor["sensor_id"] == sensor_id:
			if sensor.get("metrics"):
				sensor.get("metrics").append(reading)
			else:
				first_reading = [reading]
				sensor["metrics"] = first_reading
			with open("sensors.json", "w") as db:
				json.dump(sensor_data, db, indent=4)
			return {"New Metrics Added" : reading}
	return {"Sensor Not Found" : []}

def get_date_range_from_params(params):
	today = datetime.date.today()
	dates = []
	for key in params:
		if key != "days":
			return {"Invalid Param" : key}
		else:
			if len(params) > 1:
				return {"Must Only Supply 1 Param With Day" : []}
			day_range = int(params.get(key))
			if day_range > 31:
				return {"Cannot Query Further Than 1 Month Back" : []}
			if day_range < 0:
				return {"Number Must Be Positive" : []}
			if day_range == 0:
				dates.append(today)
			else:
				#We add 1 to day_range because today is at 0 and we're counting in "days ago"
				dates = [today - datetime.timedelta(days=x) for x in range(0, day_range+1)]
	return dates

def find_most_recent_reading(metric_list):
	most_recent_date = None
	most_recent_reading = None
	for reading in metric_list:
		adate = datetime.datetime.strptime(reading.get("date"), '%Y-%m-%d')
		if not most_recent_date:
			most_recent_date = adate
			most_recent_reading = reading
		else:
			if adate > most_recent_date:
				most_recent_date = adate
				most_recent_reading = reading
	if most_recent_reading:
		metric_list = [most_recent_reading]
	return metric_list

if __name__ == "__main__":
	app.run(debug=True)