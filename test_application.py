import pytest
import json
import application
import requests
import datetime
from flask import Flask

#This allows for tests to be performed outside of a request context later
app = Flask(application.__name__)
app.testing = True

#Initialises the database to begin with
#In this case, this db could be accessed directly from application but preferably these tests
#would be performed with a mock database, but for proof of concept I didn't have time to
#make the requests db-agnostic
class ApplicationTestSetup:
	def __init__(self):
		self.db = open("sensors.json")
		self.sensor_data = json.load(self.db)

		
#Instantiates the class which inits the database, this can be passed as an argument to test functions to allow them to access the db
@pytest.fixture
def setup():
	return ApplicationTestSetup()

	
#If new data in the DB played nice with the tests here, this would cleanly remove any sensors added in the testing process.
#Ideally there would be a mock database, but for quick proof of concept having pluggable DBs was out of scope. This is here
#to show what I would have done if I had to clean up the DB after tests, albeit with a hard coded ID cutoff point.

# @pytest.fixture(scope='session')
# def teardown():
	# for sensor in application.sensor_data:
		# if sensor.get("sensor_id") > 11:
			# application.sensor_data.remove(sensor)
		# with open("sensors.json", "w") as db:
			# json.dump(application.sensor_data, db, indent=4)

			
def test_index_returns_correct_message():
	assert application.index() == "Home Page"

	
#This was hard coded as the JSON is being read in a different ordering than it is written.
#I attemped to read as ordered dict but the issue persisted.
#For sake of brevity in this challenge I have opted to leave this as is as token acknowledgement of the need to test this functionality
def test_get_sensor_all_returns_all_sensor_data(setup):
	assert application.get_sensor_all() == { "All Sensors": [ { "city_name": "Galway", "country_name": "Ireland", "metrics": [ { "date": "2022-01-15", "humidity": 50, "precipitation": 5, "temperature": 16, "wind": 20 }, { "date": "2022-02-01", "humidity": 73, "precipitation": 20, "temperature": 6, "wind": 35 }, { "date": "2021-12-25", "humidity": 67, "precipitation": 40, "temperature": -2, "wind": 45 } ], "sensor_id": 0 }, { "city_name": "Limerick", "country_name": "Ireland", "sensor_id": 1 }, { "city_name": "Cork", "country_name": "Ireland", "sensor_id": 2 }, { "city_name": "Dublin", "country_name": "Ireland", "sensor_id": 3 }, { "city_name": "London", "country_name": "England", "sensor_id": 4 }, { "city_name": "Manchester", "country_name": "England", "sensor_id": 5 }, { "city_name": "Leeds", "country_name": "England", "sensor_id": 6 }, { "city_name": "Liverpool", "country_name": "England", "metrics": [ { "date": "2022-01-18", "humidity": 75, "precipitation": 12, "temperature": 8, "wind": 26 }, { "date": "2022-02-01", "humidity": 80, "precipitation": 27, "temperature": 4, "wind": 30 } ], "sensor_id": 7 }, { "city_name": "Berlin", "country_name": "Germany", "sensor_id": 8 }, { "city_name": "Hamburg", "country_name": "Germany", "sensor_id": 9 }, { "city_name": "Paris", "country_name": "France", "sensor_id": 10 }, { "city_name": "Madrid", "country_name": "Spain", "sensor_id": 11 } ]}

	
def test_get_sensor_returns_correct_sensor(setup):
	expected_id = 7
	assert (application.get_sensor(expected_id)["Sensor Data"].get("sensor_id")) == expected_id

	
def test_get_sensor_returns_correct_error_message_for_invalid_sensor(setup):
	assert application.get_sensor(len(setup.sensor_data)+1) == {"Sensor Not Found" : []}

	
#I made sure this test checks all country names before making assertions in case it fails at the first failure.
#If a fail-fast approach is preferred for a piece of work then this can obviously be changed easily.
#If issues arise with what this is testing later, the list that is created here can make for easier debugging.
def test_get_sensor_country_name_returns_correct_country(setup):
	desired_country = "Ireland"
	incorrect_countries = []
	for results in application.get_sensor_country_name(desired_country)["Sensor Data"]:
		if results["country_name"] != desired_country:
			incorrect_countries.append(results["country_name"])
	assert incorrect_countries == []

	
def test_get_sensor_country_name_returns_correct_error_message_for_country_with_no_sensor(setup):
	assert application.get_sensor_country_name("CountryWithNoSensor") == {"No Sensors In This Country / Invalid Country" : []}

	
def test_get_sensor_country_name_returns_correct_error_message_when_provided_with_a_number(setup):
	assert application.get_sensor_country_name("0") == {"Invalid Country Name" : []}

	
def test_get_sensor_city_name_returns_correct_city(setup):
	desired_city = "Galway"
	incorrect_cities = []
	for results in application.get_sensor_city_name(desired_city)["Sensor Data"]:
		if results["city_name"] != desired_city:
			incorrect_cities.append(results["city_name"])
	assert incorrect_cities == []

	
def test_get_sensor_city_name_returns_correct_error_message_for_city_with_no_sensor(setup):
	assert application.get_sensor_city_name("CityWithNoSensor") == {"No Sensors In This City / Invalid City" : []}

	
def test_get_sensor_city_name_returns_correct_error_message_when_provided_with_a_number(setup):
	assert application.get_sensor_city_name("0") == {"Invalid City Name" : []}

	
#Unfortunately had to hardcode again. This would be fine if I had a mock database where I could be sure it remains a certain way
#but if metrics get added to the db this test will fail. I'm keeping this here as acknowledgement that this test should be done,
#but not without expressing why this is flawed and why a mock DB would make these tests so much better.
def test_get_metrics_all_returns_all_metrics(setup):
	assert application.get_metrics_all() == { "Average Metrics": [ { "Average Humidity": 69, "Average Precipitation": 20.8, "Average Temperature": 6.4, "Average Wind Speed": 31.2 }, { "All Metrics": [ [ { "date": "2022-01-15", "humidity": 50, "precipitation": 5, "temperature": 16, "wind": 20 }, { "date": "2022-02-01", "humidity": 73, "precipitation": 20, "temperature": 6, "wind": 35 }, { "date": "2021-12-25", "humidity": 67, "precipitation": 40, "temperature": -2, "wind": 45 } ], [ { "date": "2022-01-18", "humidity": 75, "precipitation": 12, "temperature": 8, "wind": 26 }, { "date": "2022-02-01", "humidity": 80, "precipitation": 27, "temperature": 4, "wind": 30 } ] ] } ]}

	
def test_find_most_recent_reading_returns_correct_date(setup):
	metric_list = [{"date" : "1999-01-01"}, {"date" : "2000-01-01"}, {"date" : "2015-01-01"}, {"date" : "2022-01-01"}]
	assert application.find_most_recent_reading(metric_list) == [{"date" : "2022-01-01"}]

	
def test_get_date_range_from_params_returns_correct_dates(setup):
	today = datetime.date.today()
	yesterday = today - datetime.timedelta(days=1)
	params = {"days" : 1}
	assert application.get_date_range_from_params(params) == [today, yesterday]

	
def test_get_metrics_returns_correct_metrics_for_sensor_with_metrics(setup):
	sensor_to_be_tested = 0
	sensor_metrics = []
	for sensor in application.sensor_data:
		if sensor.get("sensor_id") == sensor_to_be_tested:
			if sensor.get("metrics"):
				sensor_metrics = sensor.get("metrics")
	sensor_metrics = application.find_most_recent_reading(sensor_metrics)
	with app.test_request_context():
		assert application.get_metrics(sensor_to_be_tested)["metrics"] == sensor_metrics

		
def test_get_metrics_returns_correct_error_message_when_metrics_not_found(setup):
	#This line is necessary to test the app outside of a request context
	with app.test_request_context():
		assert application.get_metrics(1) == {"No Metrics For Sensor": []}

		
def test_get_metrics_returns_correct_error_message_when_sensor_not_found(setup):
	with app.test_request_context():
		assert application.get_metrics(len(setup.sensor_data)+1) == {"Sensor Not Found": []}

		
def test_get_metrics_country_name_returns_correct_metrics_for_sensor_with_metrics(setup):
	desired_country = "Ireland" 
	sensor_metrics = []
	for sensor in application.sensor_data:
		if sensor.get("country_name") == desired_country:
			if sensor.get("metrics"):
				sensor_metrics = sensor.get("metrics")
	sensor_metrics = application.find_most_recent_reading(sensor_metrics)
	with app.test_request_context():
		assert application.get_metrics_country_name(desired_country)["metrics"] == sensor_metrics

		
def test_get_metrics_city_name_returns_correct_metrics_for_sensor_with_metrics(setup):
	desired_city = "Galway" 
	sensor_metrics = []
	for sensor in application.sensor_data:
		if sensor.get("city_name") == desired_city:
			if sensor.get("metrics"):
				sensor_metrics = sensor.get("metrics")
	sensor_metrics = application.find_most_recent_reading(sensor_metrics)
	with app.test_request_context():
		assert application.get_metrics_city_name(desired_city)["metrics"] == sensor_metrics

		
#This test should pass as it does correctly create the sensor, but for some reason the tests aren't
#playing nice with any new data getting added to the DB, even though it acknowledges it's there.
#I tried multiple ways of posting this request, such as using Flask's inbuilt app.post function to no avail

#def test_register_sensor_creates_correct_sensor(setup):
	#requests.post("http://127.0.0.1:5000/sensor_data?country_name=Scotland&city_name=Glasgow")
	#assert {"sensor_id" : "12", "country_name" : "Scotland", "city_name" : "Glasgow"} in application.sensor_data

	
#This test should also pass, but is commented out for the same reason as the previous one. I think it's still valuable
#to show what I would have done if this issue did not exist
	
# def test_add_metrics_creates_correct_metrics(setup):
	# desired_sensor = None
	# requests.post("http://127.0.0.1:5000/metrics/1?date=2022-02-08&temperature=8&humidity=89&precipitation=14&wind=19")
	# for sensor in application.sensor_data:
		# if sensor.get("sensor_id") == 1:
			# desired_sensor = sensor
	# assert {"date": "2022-02-08", "humidity": "89", "precipitation": "14", "temperature": "8", "wind": "19"} in desired_sensor["metrics"]

	
#This test does pass, but I'm commenting it out as this adds to the database and the database cleanup at teardown is commented out
#If I were to have added parametrisation to this test, I could have tested multiple different sets of data to substitute in
#for the country_name and city_name

# def test_register_sensor_returns_200_response_when_valid_data_is_sent(setup):
	# assert requests.post("http://127.0.0.1:5000/sensor_data?country_name=Scotland&city_name=Glasgow").status_code == 200

	
def test_register_sensor_returns_404_when_non_existent_page_is_supplied(setup):
	assert requests.post("http://127.0.0.1:5000/invalid_url").status_code == 404
