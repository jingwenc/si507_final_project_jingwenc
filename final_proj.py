import requests
import requests.auth
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix
import json
from bs4 import BeautifulSoup
import secrets
import webbrowser
import csv
import math
import cache
import generate_db
import nltk
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.offline as offline

###########################################
#             linkedin profile            #
###########################################
#store personal profile, including first name, last name, and profile link
class Profile():
    def __init__(self,firstName,lastName,url):
        self.firstName=firstName
        self.lastName=lastName
        self.url=url
    def __str__(self):
        return self.firstName+','+self.lastName+','+self.url
#use OAuth2 to get access to user's profile
#if users don't want to authorize the app,
#they can choose to enter their names manually to continue.
def get_linkedin_profile():
    client_id=secrets.Client_ID
    client_secret=secrets.Client_Secret
    redirect_uri='https://www.google.com/'

    base_url='https://www.linkedin.com/jobs/search/'
    authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
    token_url = 'https://www.linkedin.com/uas/oauth2/accessToken'

    linkedin = OAuth2Session(client_id, redirect_uri=redirect_uri)
    linkedin = linkedin_compliance_fix(linkedin)
    authorization_url, state = linkedin.authorization_url(authorization_base_url)
    search_term=input('Can I get the permission to access your acount? Y/N')
    if search_term.upper() == 'Y':
        print('Please go here and authorize,', authorization_url)

        # Get the authorization verifier code from the callback url
        redirect_response = input('Paste the full redirect URL here:')

        # Fetch the access token
        linkedin.fetch_token(token_url, client_secret=client_secret,
                            authorization_response=redirect_response)

        # Fetch a protected resource, i.e. user profile
        r = linkedin.get('https://api.linkedin.com/v1/people/~?format=json')
        profile_dict=json.loads(r.content)
        firstName=profile_dict['firstName']
        lastName=profile_dict['lastName']
        url=profile_dict['siteStandardProfileRequest']['url']
        profile=Profile(firstName,lastName,url)
        return profile
    if search_term.upper() == 'N':
        manual_profile=input('Please enter your name or exit:')
        if manual_profile != 'exit':
            return manual_profile

####################################################
#                  scrape Indeed                   #
####################################################
#store info of a job, including title, company name, location,
#salary, description and part of apply link.
class Jobsum():
    def __init__(self,title,comp,loc,salary,desc,url=None):
        self.title=title
        self.company=comp
        self.location=loc
        self.salary=salary
        self.description=desc
        self.url=url
    def __str__(self):
        state=self.title+'\n'
        state+='  '+self.company+'\n'
        state+='  '+self.location+'\n'
        state+='  '+self.salary+'\n'
        state+='  '+self.description+'\n'
        state+='  '+self.url+'\n'
        return state
#store nearby places of a job
class NearbyPlace():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
#search and scrape job info according to title, location and page in Indeed
def job_search(job,page=0,location='United States'):
    jobsear_base_url='https://www.indeed.com/jobs'
    page=int(page)
    start=page*10
    if start == 0:
        param={'q':job,'l':location}
    else:
        param={'q':job,'l':location,'start':start}
    r=cache.make_request_using_cache(jobsear_base_url,param)
    soup=BeautifulSoup(r,'html.parser')
    results=soup.find_all(class_='result')
    JS_list=[]
    for cell in results:
        detail_url=cell.find('a')['href']
        title=cell.find('a').text.strip()
        company=cell.find('span',class_='company').text.strip()
        comp_location=cell.find('span',class_='location').text.strip()
        try:
            salary=cell.find('span',class_='no-wrap').text.strip()
        except:
            salary='Not available'
        description=cell.find('span',class_='summary').text.strip()
        JS=Jobsum(title,company,comp_location,salary,description,detail_url)
        JS_list.append(JS)
    return JS_list
#get rid of reppeat of some jobs, which is a defect of Indeed
def check_unique_in_list(li):
    check_list=[]
    check_list.append(li[0])
    for i in li:
        num=len(check_list)
        n=0
        for j in check_list:
            if (i.title != j.title) or (i.company != j.company) or (i.location != j.location):
                n+=1
        if n == num:
            check_list.append(i)
    return check_list
# ask user to input the number of records user requiers,
#but in case that there could exit lots of same results,
#I at first requests one more page of results.
def calculate_page_needed(num):
    num_page=math.ceil(int(num)/16)+1
    return num_page
#gathers all the job info together and returns a list of class object
def gather_pages_results(job,num_records,location='United States'):
    page_list=[]
    current_page=0
    while len(page_list) < num_records:
        num_needed=num_records-len(page_list)
        num_page=calculate_page_needed(num_needed)+current_page
        for i in range(current_page,num_page):
            page_list+=job_search(job,i,location)
            page_list=check_unique_in_list(page_list)
        current_page=num_page
    return  page_list

###################################################
#                 details and apply               #
###################################################
#get summaries and apply links for jobs by scraping and crawling Indeed
def details_for_a_job(jobclass):
    detail_base_url='https://www.indeed.com'
    end_url=jobclass.url
    url=detail_base_url+end_url
    r=cache.make_request_using_cache(url)
    soup=BeautifulSoup(r,'html.parser')
    summary=soup.find('span',id='job_summary').text.strip()
    try:
        apply_link=soup.find('a',class_='view_job_link')['href']
        apply_link=detail_base_url+apply_link
        print('Apply on company website!')
    except:
        print('Apply on Indeed!')
        apply_link=url
    return summary,apply_link
#this function was designed for command line interaction,but not used in the current program
def open_web_to_apply(jobclass):
    summary,apply_link=details_for_a_job(jobclass)
    webbrowser.open(apply_link)

####################################################
#                  generate database               #
####################################################
#initiate database for csv files, which contains living cost at different locations
def init():
    generate_db.init_db_before_job()
#scraping and crawling from indeed and store into db
#and returns the required number of jobs.
def init_update_insert_db_for_job(job,num_records,location='United States'):
    Job=job
    Job=Job.replace(' ','')
    table_name_list=generate_db.get_table_names()
    unique_list=gather_pages_results(job,num_records,location)
    if Job in table_name_list:
        new_job_list=generate_db.check_existance_in_db(unique_list,job)
    else:
        new_job_list=unique_list
        generate_db.init_db_for_job(job)
    generate_db.insert_db(new_job_list,job)
    generate_db.update_salary_in_db(job)    # sort data from db
    generate_db.match_location(job)     #build location relationship in db
    generate_db.get_over_limit_from_json(job)     #due to limit of requests for elements, I change the key to make up the 'OVER_QUERY_LIMIT'
    JS_list=[]
    for i in range(num_records):
        JS_list.append(unique_list[i])
    return JS_list

###############################################
#            select data from db              #
###############################################
#get the area id of a job in database
def get_area_Id(job,jobclass):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    Job=job
    Job=Job.replace(' ','')
    statement=' SELECT NearestLocationId FROM '+ Job
    statement+=''' WHERE JobTitle=? AND Company=?
                AND CompanyLocation=? AND Salary=?
            '''
    values=(jobclass.title,jobclass.company,jobclass.location,jobclass.salary)
    result=cur.execute(statement,values)
    AreaId=result.fetchone()
    return AreaId[0]
#get salaries,if exits, of jobs in the database
def get_salaries_from_db(job):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    Job=job
    Job=Job.replace(' ','')
    statement='SELECT MinSalary,MaxSalary FROM '+Job
    statement+=' WHERE MinSalary > 0 '
    salaries=cur.execute(statement)
    salaries_list=salaries.fetchall()
    conn.close()
    return salaries_list
#the following five functions give the cost in 5 aspects by processing data in db
def food_expenditure(AreaId):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    statement='''
        SELECT S.Value,S.Year,S.Period
        FROM Series AS R
        	JOIN Summary AS S
        	ON R.SeriesId = S.SeriesId
        	JOIN Area AS A
        	ON R.AreaCode = A.AreaCode
        WHERE S.Year=R.EndYear AND S.period=R.EndPeriod
    		AND S.SeriesId= (SELECT SeriesId FROM Series
    		WHERE ItemCode='SAF' AND AreaCode=
            (SELECT AreaCode FROM Area WHERE Id=?))
    '''
    value=(AreaId,)
    food=cur.execute(statement,value)
    food_fee=food.fetchone()[0]
    conn.close()
    return food_fee
def transportation_fee(AreaId):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    statement='''
        SELECT S.Value,S.Year,S.Period
        FROM Series AS R
        	JOIN Summary AS S
        	ON R.SeriesId = S.SeriesId
        	JOIN Area AS A
        	ON R.AreaCode = A.AreaCode
        WHERE S.Year=R.EndYear AND S.period=R.EndPeriod
    		AND S.SeriesId= (SELECT SeriesId FROM Series
    		WHERE ItemCode='SAT' AND AreaCode=
            (SELECT AreaCode FROM Area WHERE Id=?))
    '''
    value=(AreaId,)
    transp=cur.execute(statement,value)
    transp_fee=transp.fetchone()[0]
    conn.close()
    return transp_fee
def housing_expenditure(AreaId):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    statement='''
        SELECT S.Value,S.Year,S.Period
        FROM Series AS R
        	JOIN Summary AS S
        	ON R.SeriesId = S.SeriesId
        	JOIN Area AS A
        	ON R.AreaCode = A.AreaCode
        WHERE S.Year=R.EndYear AND S.period=R.EndPeriod
    		AND S.SeriesId= (SELECT SeriesId FROM Series
    		WHERE ItemCode='SAH' AND AreaCode=
            (SELECT AreaCode FROM Area WHERE Id=?))
    '''
    value=(AreaId,)
    housing=cur.execute(statement,value)
    housing_fee=housing.fetchone()[0]
    conn.close()
    return housing_fee
def medical_expenditure(AreaId):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    statement='''
        SELECT S.Value,S.Year,S.Period
        FROM Series AS R
        	JOIN Summary AS S
        	ON R.SeriesId = S.SeriesId
        	JOIN Area AS A
        	ON R.AreaCode = A.AreaCode
        WHERE S.Year=R.EndYear AND S.period=R.EndPeriod
    		AND S.SeriesId= (SELECT SeriesId FROM Series
    		WHERE ItemCode='SAM' AND AreaCode=
            (SELECT AreaCode FROM Area WHERE Id=?))
    '''
    value=(AreaId,)
    medical=cur.execute(statement,value)
    medical_fee=medical.fetchone()[0]
    conn.close()
    return medical_fee
def education_expenditure(AreaId):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    statement='''
        SELECT S.Value,S.Year,S.Period
        FROM Series AS R
        	JOIN Summary AS S
        	ON R.SeriesId = S.SeriesId
        	JOIN Area AS A
        	ON R.AreaCode = A.AreaCode
        WHERE S.Year=R.EndYear AND S.period=R.EndPeriod
    		AND S.SeriesId= (SELECT SeriesId FROM Series
    		WHERE ItemCode='SAE' AND AreaCode=
            (SELECT AreaCode FROM Area WHERE Id=?))
    '''
    value=(AreaId,)
    education=cur.execute(statement,value)
    education_fee=education.fetchone()[0]
    conn.close()
    return education_fee
#get min and max salary, if exits, in the db
def get_max_min_salary(job,title,company,location,salary):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    Job=job
    Job=Job.replace(' ','')
    statement=' SELECT MinSalary,MaxSalary FROM '+Job
    statement+=' WHERE JobTitle =? AND Company=? AND CompanyLocation=? AND Salary=?'
    statement+=' AND MinSalary > 0'
    values=(title,company,location,salary)
    salary_range=cur.execute(statement,values)
    salary_range_tuple=salary_range.fetchone()
    min_salary=salary_range_tuple[0]
    max_salary=salary_range_tuple[1]
    conn.close()
    return min_salary,max_salary

#sort the salary by descending and acsending
job_list=[]
def get_job_list_list(job,JS_list):
    global job_list
    job_list=[]
    original_in_JS=0
    for i in JS_list:
        summary,apply_link=details_for_a_job(i)
        try:
            id=get_area_Id(job,i)
        except:
            id='No matched AreaId'
        try:
            min_salary,max_salary=get_max_min_salary(job,i.title,i.company,i.location,i.salary)
        except:
            min_salary=0.0
            max_salary=0.0
        job_list.append([i.title,i.company,i.location,min_salary,max_salary,i.description,apply_link,summary,id,original_in_JS])
        original_in_JS+=1
    return job_list
def get_all_job_info(sortby='MinSalary', sortorder='desc'):
    global job_list

    if sortby == 'MinSalary':
        sortcol = 3
    elif sortby == 'MaxSalary':
        sortcol = 4
    else:
        sortcol = 0

    rev = (sortorder == 'desc')
    sorted_list = sorted(job_list, key=lambda row: row[sortcol], reverse=rev)
    return sorted_list

#################################################
#         Plot Company location with Plotly     #
#################################################
text_search_url='https://maps.googleapis.com/maps/api/place/textsearch/json'
nearby_url='https://maps.googleapis.com/maps/api/place/nearbysearch/json'
place_key=secrets.Place_api_key
#get longitude and latitude of working location
#and nearby places according to different types required
def get_long_lat_of_company(jobclass):
    global text_search_url,place_key
    address=jobclass.location
    title=jobclass.title
    param={'query':address,'key':place_key}
    resp=cache.make_request_using_cache(text_search_url,param)
    resp_dict=json.loads(resp)
    try:
        geo=resp_dict['results'][0]['geometry']['location']
        lat=geo['lat']
        lng=geo['lng']
    except:
        lat='unavailable latitude'
        lng='unavailable longitude'
    return title,lat,lng
def get_info_for_nearby_places(jobclass,types):
    global nearby_url,place_key
    title,lat,lng=get_long_lat_of_company(jobclass)
    if type(lat) != str:
        location=str(lat)+','+str(lng)
        params_n={'location':location,'radius':10000,'types':types,'key':place_key}
        output_n=cache.make_request_using_cache(nearby_url,param=params_n)
        output_nn_dict=json.loads(output_n)
        results=output_nn_dict['results']
        nearby_list=[]
        for i in results:
            i_list=[]
            geo=i['geometry']['location']
            i_list.append(i['name'])
            i_list.append(geo['lat'])
            i_list.append(geo['lng'])
            nearby_list.append(i_list)
        return nearby_list
    else:
        message='error:'+lat+' and '+lng
        print(message)
        return message
def get_nearby_places_for_job(jobclass,types):
    name_list=[]
    nearby_list=get_info_for_nearby_places(jobclass,types)
    if type(nearby_list) == list:
        for i in nearby_list:
            n_name=i[0]
            nb_name=NearbyPlace(n_name)
            name_list.append(nb_name)
        return name_list
    else:
        return nearby_list
#plot all the jobs in a results list
def plot_jobs(job,JS_list):
    min_lat = 10000
    max_lat = -10000
    min_lng = 10000
    max_lng = -10000

    lat_vals=[]
    lng_vals=[]
    text_vals=[]
    for i in JS_list:
        title_i,lat_i,lng_i=get_long_lat_of_company(i)
        if type(lat_i) != str:
            lat_vals.append(lat_i)
            lng_vals.append(lng_i)
            text_vals.append(title_i)

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lng_vals:
        v = float(str_v)
        if v < min_lng:
            min_lng = v
        if v > max_lng:
            max_lng = v

    max_range = max(abs(max_lat - min_lat), abs(max_lng - min_lng))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lng_axis = [min_lng - padding, max_lng + padding]

    data = [ dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lng_vals,
            lat = lat_vals,
            text = text_vals,
            mode = 'markers',
            marker = dict(
                size = 8,
                symbol = 'star',
            ))]
    center_lat = (max_lat+min_lat) / 2
    center_lng = (max_lng+min_lng) / 2

    layout = dict(
            title = 'jobs for '+str(job),
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(100, 217, 217)",
                countrycolor = "rgb(217, 100, 217)",
                lataxis = {'range': lat_axis},
                lonaxis = {'range': lng_axis},
                center= {'lat': center_lat, 'lon': center_lng },
                countrywidth = 3,
                subunitwidth = 3
            ),
        )

    fig=dict(data=data, layout=layout )
    py.plot( fig, validate=False, filename='jobs for '+str(job))
#plot nearby places for a chosen job according to types
def plot_nearby_for_job(jobclass,types):
    min_lat = 10000
    max_lat = -10000
    min_lng = 10000
    max_lng = -10000

    job_t,job_la,job_lg=get_long_lat_of_company(jobclass)
    if type(job_la) != str:
        title=jobclass.title
        job_lat=[]
        job_lng=[]
        job_text=[]
        job_lat.append(job_la)
        job_lng.append(job_lg)
        job_text.append(job_t)
        lat_vals=[]
        lng_vals=[]
        text_vals=[]
        nearby_list=get_info_for_nearby_places(jobclass,types)
        for i in nearby_list:
            name_i=i[0]
            lat_i=i[1]
            lng_i=i[2]
            lat_vals.append(lat_i)
            lng_vals.append(lng_i)
            text_vals.append(name_i)

        total_lat_vals=lat_vals+job_lat
        total_lng_vals=lng_vals+job_lng
        for str_v in total_lat_vals:
            v = float(str_v)
            if v < min_lat:
                min_lat = v
            if v > max_lat:
                max_lat = v
        for str_v in total_lng_vals:
            v = float(str_v)
            if v < min_lng:
                min_lng = v
            if v > max_lng:
                max_lng = v

        max_range = max(abs(max_lat - min_lat), abs(max_lng - min_lng))
        padding = max_range * .10
        lat_axis = [min_lat - padding, max_lat + padding]
        lng_axis = [min_lng - padding, max_lng + padding]

        trace1 =  dict(
                type = 'scattergeo',
                locationmode = 'USA-states',
                lon = job_lng,
                lat = job_lat,
                text = job_text,
                mode = 'markers',
                marker = dict(
                    size = 8,
                    symbol = 'star',
                ))
        trace2 =  dict(
                type = 'scattergeo',
                locationmode = 'USA-states',
                lon = lng_vals,
                lat = lat_vals,
                text = text_vals,
                mode = 'markers',
                marker = dict(
                    size = 8,
                    symbol = 'circle',
                    opacity = 0.5
                ))
        center_lat = (max_lat+min_lat) / 2
        center_lng = (max_lng+min_lng) / 2

        layout = dict(
                title = 'jobs for '+str(title),
                geo = dict(
                    scope='usa',
                    projection=dict( type='albers usa' ),
                    showland = True,
                    landcolor = "rgb(250, 250, 250)",
                    subunitcolor = "rgb(100, 217, 217)",
                    countrycolor = "rgb(217, 100, 217)",
                    lataxis = {'range': lat_axis},
                    lonaxis = {'range': lng_axis},
                    center= {'lat': center_lat, 'lon': center_lng },
                    countrywidth = 3,
                    subunitwidth = 3
                ),
            )
        data=[trace1,trace2]
        fig=dict(data=data, layout=layout )
        try:
            title=title.replace('/','')
            title=title.replace(',','')
        except:
            pass
        py.plot( fig, validate=False, filename='nearby places for '+str(title))
#use offline plotly to plot the pie charts of job salaries and living cost
def offline_plotly(values,labels,salary):
    total_cost=0
    for i in values:
        total_cost+=i
    rest_money=salary/12-total_cost
    fig = {
      "data": [
        {
          "values": values,
          "labels": labels,
          "domain": {"x": [0, .48]},
          "text": "Cost",
          "name": "Life Quality",
          "hoverinfo":"label+percent+name",
          "hole": .4,
          "type": "pie"
        },
        {
          "values": [total_cost,rest_money],
          "labels": [
            "living cost",
            "salary less cost"
          ],
          "text":"Cost/Earning",
          "textposition":"inside",
          "domain": {"x": [.52, 1]},
          "name": "Cost/Earning ratio",
          "hoverinfo":"label+percent+name",
          "hole": .4,
          "type": "pie"
        }],
        "layout": {
        "title":"Living Quality Pies",
        "annotations": [
            {
                "font": {
                    "size": 20
                },
                "showarrow": False,
                "text": "Cost",
                "x": 0.20,
                "y": 0.5
            },
            {
                "font": {
                    "size": 20
                },
                "showarrow": False,
                "text": "Cost/Earning",
                "x": 0.84,
                "y": 0.5
            }]
            }
        }

    div=offline.plot(fig,show_link=False, output_type="div", include_plotlyjs=True)
    return div
