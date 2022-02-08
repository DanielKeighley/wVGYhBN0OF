First of all I just want to walk through some of the files included.

application.py contains all the code for the API
test_application.py contains all of the tests for the API
sensors.json is the database for the API. It contains sensors, their metadata and their metrics
database_backup.json contains the data sensors.json starts off with in case you want to reset the DB for any reason
requirements.txt holds the information the virtual environment will need to set up the necessary dependencies
.gitignore was generated from the tool gitignore.io which can be found at toptal.com/developers/gitignore 

---SETUP---

First of all, you will need the python package installer, pip. If you are running Python3 it should come as standard with your Python install.

Otherwise pip installation information can be found at https://pip.pypa.io/en/stable/installation/

To ensure you have all the dependencies you need to run this code we must create a virtual environment
and install a list of requirements to be installed to it. This ensures that it will run the same on any machine.

First run:
python -m venv venv

In the wVGYhBN0OF directory, you must first active the virtual environment like so:
venv\Scripts\activate   WINDOWS
venv/Scripts/activate   OTHER

When you are done working in the venv, just type:
deactivate

Now that the venv is running, you should see (venv) before your current working directory in the terminal
Now, to install the necessary dependencies you will need to run:
pip install -r requirements.txt

Now everything should be ready to go.

---TESTS---

I would recommend running the tests before anything as due to out-of-scope issues, the database
does not play nice with new data being added and will not execute the database teardown code.
I have commented out the offending tests as well as the teardown code, much about this is explained within test_application.py

Using Coverage.py I have found that my test coverage is 73% as is. Adjusting for the tests that exist but are commented out for reasons explained within the code, the real test coverage is 96%.

Before running tests, the application needs to be up and running. To do this you will either need to open
a seperate terminal and run it from there, or run the application in the background of your current terminal.
Either way, run the application like so:
python application.py

To run tests with coverage, make sure you are in the codingchallenge directory and run:
coverage run -m pytest

To see a report of coverage after running this, run:
coverage report -m

In my tests within test_application.py I have opted for long and verbose naming conventions on all my tests
as I find this is more descriptive and readable. I believe for some codebases readability is more important than
being perfectly efficient, especially with colleagues in mind. In code that does not need to be highly performant
I would err on the side of having readability and collaberation heavily in mind, unless of course instructed otherwise.

---APPLICATION IN BROWSER---

You can visit http://127.0.0.1:5000 in your browser once the application is running. This page will simply say "Home Page"

NOTE: Queries are CASE SENSITIVE :NOTE

To see all sensor data go to http://127.0.0.1:5000/sensor_data
To see all sensor data for a specific sensor go to http://127.0.0.1:5000/sensor_data/<sensor_id>
To see all sensor data for a given country go to http://127.0.0.1:5000/sensor_data/<country_name>
To see all sensor data for a given city go to http://127.0.0.1:5000/sensor_data/<city_name>
To see all metrics for all sensors go to http://127.0.0.1:5000/metrics
To see all metrics for a specific sensor, if any, go to http://127.0.0.1:5000/metrics/<sensor_id>
To see all metrics for a given country, if any, go to http://127.0.0.1:5000/metrics/<country_name> 
To see all metrics for a given country, if any, go to http://127.0.0.1:5000/metrics/<city_name> 

---MAKING CUSTOM REQUESTS---

You can use Postman to make requests
You can get it at:
https://www.postman.com/downloads/

You do not need an account to use Postman, you will see an option towards the bottom left that
will allow you to use the program without one.

Once in the main screen of Postman, if you click the plus under the center top search bar you can then
- write the URL starting with (http://127.0.0.1:5000)
- choose a method, eg. GET or POST
- add params to the request

An example Postman request to make would be to POST to http://127.0.0.1:5000/sensor_data
This URL is where you can see all sensor data with a GET request, or add a new sensor with a POST request
You can then enter country_name and city_name into two different keys
Then you can choose a country and city of your choice to add to the value
If you have the application running, when you click send, you will see a response at the bottom of Postman
It will say "Registered" and contains the new sensor data
If you do a GET request for http://127.0.0.1:5000/sensor_date or check the file sensors.json, you will see that it has been updated with the new data.

Another important request you can make is getting metrics with a "days" key.
If you GET http://127.0.0.1:5000/metrics/0 in Postman you will get the most recent metric.
If you GET http://127.0.0.1:5000/metrics/0 with the key days and the value 31 you will see all readings within a month of the day you are making the query.
This also works for http://127.0.0.1:5000/metrics/<country_name> and http://127.0.0.1:5000/metrics/<city_name>

NOTE: Due to test_application.py not being compatible with adding data, make sure to either run tests     :NOTE
NOTE: before trying to POST, OR replace the data in sensors.json with the data inside of data_backup.json :NOTE

---REQUIREMENTS---

In review I will be looking at the requirements set down and how they were met

"The application must allow you to register sensors by id. When registering a sensor,
metadata about the sensor (country name and city name) may be stored with the
sensor. The application does not have to support arbitrary sensor metadata."

-My assumption was that by not having to support arbitrary sensor metadata, it meant that sensors could be made without a country or city name (or neither) and that by registering by ID it was meant that each needs a unique ID.
If the former meant that no OTHER data was necessary then I could have made the params in register_sensor() require these fields. If the latter meant that the user would manually register a specified ID to be the sensor's ID then I would have made that a requirement in register_sensor() and I would have made a check to see if that ID exists already and if it is numeric.

-This requirement was met with the register_sensor() function at line 175 in application.py
With a POST request, you can supply metadata (or no metadata) about the sensor and it will be created and added to the json database, along with a unique ID.
--------------------------------------------------------------------------------------------------------------------

"Once a sensor has been registered, the application can receive new metric values as
the weather changes around the sensor via an API call."

-This requirement was met with the add_metrics() function at line 200 in application.py
With a POST request, you can supply metric values to be written to an existing sensor.
--------------------------------------------------------------------------------------------------------------------

"The application must allow querying sensor data. A query should define:
• One or more (or all sensors) to include in results.
• The metrics (e.g. temperature and humidity); the application should return
the average value for these metrics.
• A date range (between one day and a month, if not specified, the latest data
should be queried).
• Example query: Give me the average temperature and humidity for sensor 1
in the last week."

-Querying is possible through various functions throughout application.py through GET requests.
You may query one sensor by ID, you may query many sensors by country or city and you can query all sensors.

-When querying sensors, you receive ALL information about a sensor, including metrics
To receive only metrics, you query metrics specifically.

-In this proof of concept application, the average metrics are only shown when querying ALL metrics.
This is explained within the comments in application.py, but in essence I have already shown I can get the application to return averages of data and because I did not have time to implement average calculation how I would like it, extending average calculation to all queries would make the code less readable.

-When querying metrics by ID, country or city the API will only return the most recent data by default. You may pass params with your GET request to define a number of days you want to go back (up to 1 month) and the API will only return metrics from that date range.

-In relation to the example query, you can indeed get the metrics for sensor 1 in the past 7 days, but my reasoning for not having average calculation for specific metric reading queries was explained previously and I did not have time to add querying for 1 or more specific metrics.
If I were to add querying 1 or more specific pieces of data from metrics I could have made a check for a param that would be a list of desired metrics and only return those. It would also be easy to implement averages as the required metrics are already supplied. I don't believe it would take long to implement this but I did not want to spend too many hours on this, as requested.
--------------------------------------------------------------------------------------------------------------------


---ENHANCEMENTS---

I have discussed several enhancements I would like to make already, but appart from those I have listed a few things that I wish I had time to do

1:

I would have liked to have had time to write a script that programmatically made requests so that something like Postman would not be required to demonstrate the full functionality of my code.

You can see a little bit of what that might have looked like in the tests with things such as
requests.post("http://127.0.0.1:5000/sensor_data?country_name=Scotland&city_name=Glasgow")

I could have also have created this:
params = {"country_name" : "Scotland", "city_name" : "Glasgow"}

and passed that into the request, allowing me to both simply make queries, but also
to simply paramaterise tests- as I make mention of in test_application.py

2:

Better input validation. I showed in my code that input validation was not forgotten about and various sanity checks are made throughout the code, but ideally I would have had things like regular expressions in place to properly validate exactly what was being provided. 

3:

More tests. For the sake of this challenge I mostly focused on test coverage, rather than checking every edge case etc. Usually I would like to parametrise tests and test them for various datasets and cases, such as querying metrics from sensor 1 0 days ago, 10 days ago, "string" days ago, None days ago, etc

Feel free to ask me about it in the next interview and I could definitely pick out additional tests that I would
liked to have added.

4:

Pluggable databases and mock database. In hindsight I wish I abstracted the code in application.py from a specific database and made it all work with anything in json format. This would have allowed me to make mock databases and test much more effectively. The reason there is a horribly hard coded test in test_application.py is because of this issue and is only kept there as token acknowledgement of need for what it is testing.
In an ideal situation my tests could have added to and deleted from these mock databases so that the application and the tests could never affect each other. This unfortunate occurance has been probably the biggest pain point of what I have written for me and I would not write code like this in other circumstances.


I am sure I have much more to say and talk about in relation to this challenge and the work I've done here,
but I will be speaking with you soon about it.

Thank you for your time,
Daniel Keighley
