
##Data sources:
 1. Create a LinkedIn developer app since client ID and client secret are needed. Store keys and secrets into secrets.py file as 'Client_ID' and 'Client_Secret'. Then set the 'Authorized Redirect URLs' for OAuth2.0(https url is recommended, no other limitations.Choose whatever url you like!), make sure the 'redirect_uri' in final_proj.py is set corresponding to the one you set in your app.
 - Go to [here](https://www.linkedin.com/developer/apps) to create an app and get the client ID and client key
 - For instructions of OAuth2 for LinkedIn click [here](https://developer.linkedin.com/docs/oauth2)

 2. Google maps distance matrix API keys needed. This API is used to match the job location with the location area in the 'Area' table in the database and assign the Area Id to each job title in the job table. For example, 'DataAnalyst' have the 'NearestLocationId' collumn to store the Id of matched area in the table 'Area'.
 Note that 2500 elements querry limit is applied per day. So make sure you have alternative API keys to override the 'OVER_QUERY_LIMIT' Error (this overriding process will be automatically run with get_over_limit_from_json() function), if you wanna request a large amount of data.
 - Go to [here](https://developers.google.com/maps/documentation/distance-matrix/get-api-key) to get the keys and store them into secrets.py file as 'Map_api_key2' 'Map_api_key3'.
 - For instructions, click [here](https://developers.google.com/maps/documentation/distance-matrix/start)

 3. Google places API key needed. Get the key by the following link and store them into secrets.py file as 'Place_api_key'.
 - To get keys, click [here](https://developers.google.com/places/web-service/get-api-key)
 - For instructions,click [here](https://developers.google.com/places/web-service/search)

 4. Job information scraped from Indeed (since LinkedIn does not allow any scraping of any of their websites), including job title, company, job location, brief description, apply link and detailed summary.

 5. Living cost data collected from DATA.GOV, the name of dataset is "Consumer Price Index - All Urban Consumers (Current Series)". The files I need, such as Area.csv, Summary.csv, Series.csv, USHousing.csv and so on has been included in the repository.
 - If you're interested in other cost data, go [here](https://catalog.data.gov/dataset/consumer-price-index-all-urban-consumers-current-series)


##Other info:
 1. Getting started with Plotly for python:https://plot.ly/python/getting-started/
 2. Offline plots in Plotly in python:https://plot.ly/python/offline/


##Brief description of code:
 **Main function:**
 1. init(): initiates database for csv files, which contains living cost at different locations
 2. init_update_insert_db_for_job(): scraping and crawling from Indeed and store into db and returns the required number of jobs.
 3. offline_plotly():uses plotly offline module to store the plot into local directory.
 **Class definitions:**
 1. class Profile(): contains personal profile, including first name, last name, and profile link.
 2. class Jobsum(): contains info of a job, including title, company name, location,salary, description and part of apply link.
 3. class NearbyPlace: contains names of nearby places of a job.


##User guide:
 1. Run the app.py in terminal window and go to http://127.0.0.1:5000/. Don't close the page tab when working on the step2.
 2. Back to terminal window to authorize the app get access to your linkedin account. You still can continue the program if you refuse. If you agree, you need to go on by following the instruction in the command line, including copy the link and open it in your browser (new tag), press 'enter' button and then copy and paste the full link back to the command line.(Sometimes you will be asked twice for authorization)
 3. Go to the page you opened at step1. Now you can search job based on location and the number of results you want to view. (The database contains the results of 'Data Analyst' in the 'United States' with over 100 records. I recommend using the existing records in case of the limit of querries from google maps API and places API)
 4. View all result info and order by salary (descending or ascending). You can access to apply website within one click in the 'apply' collumn.
 5. Go to plot page: you can plot all the job locations with Plotly, search the nearby place based on the type and plot, and plot the living quality of a job with available salary with offline plotly!
 6. Now start job search and find your ideal job!
