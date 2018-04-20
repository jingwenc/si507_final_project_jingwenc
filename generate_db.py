##generate_db.py##
import sqlite3
import csv
import nltk
import secrets
import cache
import json

####################################################
#                  generate database               #
####################################################
AREA='area.csv'
SERIES='series.csv'
HOUSING='USHousing.csv'
TRANS='Transportation.csv'
FOOD='FoodBeverage.csv'
SUMMARY='summary.csv'
def init_db():
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()

    statement='''
        DROP TABLE IF EXISTS 'Area' ;
    '''
    cur.execute(statement)
    statement='''
        DROP TABLE IF EXISTS 'Series' ;
    '''
    cur.execute(statement)
    statement='''
        DROP TABLE IF EXISTS 'Housing' ;
    '''
    cur.execute(statement)
    statement='''
        DROP TABLE IF EXISTS 'Transportation' ;
    '''
    cur.execute(statement)
    statement='''
        DROP TABLE IF EXISTS 'FoodBeverage' ;
    '''
    cur.execute(statement)
    statement='''
        DROP TABLE IF EXISTS 'Summary' ;
    '''
    cur.execute(statement)
    conn.commit()

    statement='''
        CREATE TABLE 'Area' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'AreaCode' TEXT,
            'AreaName' TEXT
        );
    '''
    cur.execute(statement)
    statement='''
        CREATE TABLE 'Series' (
            'SeriesId' TEXT,
            'AreaCode' TEXT,
            'ItemCode' TEXT,
            'SeriesTitle' TEXT,
            'BeginYear' INT,
            'BeginPeriod' TEXT,
            'EndYear' INT,
            'EndPeriod' TEXT
        );
    '''
    cur.execute(statement)
    statement='''
        CREATE TABLE 'Housing' (
            'SeriesId' TEXT,
            'Year' INT,
            'Period' TEXT,
            'Value' REAL
        );
    '''
    cur.execute(statement)
    statement='''
        CREATE TABLE 'Transportation' (
            'SeriesId' TEXT,
            'Year' INT,
            'Period' TEXT,
            'Value' REAL
        );
    '''
    cur.execute(statement)
    statement='''
        CREATE TABLE 'FoodBeverage' (
            'SeriesId' TEXT,
            'Year' INT,
            'Period' TEXT,
            'Value' REAL
        );
    '''
    cur.execute(statement)
    statement='''
        CREATE TABLE 'Summary' (
            'SeriesId' TEXT,
            'Year' INT,
            'Period' TEXT,
            'Value' REAL
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()
#add period table
def init_db1():
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    statement='''
        DROP TABLE IF EXISTS 'Period' ;
    '''
    cur.execute(statement)
    statement='''
        CREATE TABLE 'Period' (
            'period' TEXT,
            'period_abbr' TEXT,
            'period_name' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()
def insert_db3():
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    with open('period.csv','r') as f:
        data=csv.reader(f)
        for i in data:
            if i[0] != 'period':
                statement=' INSERT INTO "Period" '
                statement+='''
                    (period,period_abbr,period_name)
                    VALUES (?,?,?)
                '''
                insertion=(i[0],i[1],i[2])
                cur.execute(statement,insertion)
    conn.commit()
    conn.close()
def insert_db1():
    global AREA,SERIES
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    with open(AREA,'r') as f:
        area_data=csv.reader(f)
        for i in area_data:
            if i[0] != 'area_code':
                statement='''
                    INSERT INTO 'Area' (AreaCode,AreaName)
                    VALUES (?,?)
                '''
                insertion=(i[0],i[1])
                cur.execute(statement,insertion)
    with open(SERIES,'r') as f:
        series_data=csv.reader(f)
        for i in series_data:
            if i[0] != 'series_id':
                statement='''
                    INSERT INTO 'Series' (SeriesId,AreaCode,ItemCode,SeriesTitle,
                                        BeginYear,BeginPeriod,EndYear,EndPeriod)
                    VALUES (?,?,?,?,?,?,?,?)
                '''
                insertion=(i[0],i[1],i[2],i[7],i[9],i[10],i[11],i[12])
                cur.execute(statement,insertion)
    conn.commit()
    conn.close()
def insert_db2(filename,tablename):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    with open(filename,'r') as f:
        data=csv.reader(f)
        for i in data:
            if i[0] != 'series_id':
                statement=' INSERT INTO ' + tablename
                statement+='''
                    (SeriesId,Year,Period,Value)
                    VALUES (?,?,?,?)
                '''
                insertion=(i[0],i[1],i[2],i[3])
                cur.execute(statement,insertion)
    conn.commit()
    conn.close()

def init_db_before_job():
    init_db()
    init_db1()
    insert_db1()
    insert_db3()
    insert_db2(HOUSING,'Housing')
    insert_db2(TRANS,'Transportation')
    insert_db2(FOOD,'FoodBeverage')
    insert_db2(SUMMARY,'Summary')

def get_table_names():
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    statemnt='''
        SELECT name FROM sqlite_master WHERE type='table'
    '''
    table=cur.execute(statemnt)
    table_list=table.fetchall()
    table_name_list=[]
    for i in table_list:
        table_name_list.append(i[0])
    return table_name_list
def init_db_for_job(job):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    Job=job
    Job=Job.replace(' ','')
    statement=' DROP TABLE IF EXISTS '
    statement= statement+ Job +' ; '
    cur.execute(statement)
    conn.commit()
    statement=' CREATE TABLE '+Job
    statement+=''' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'JobTitle' TEXT,
            'Company' TEXT,
            'CompanyLocation' TEXT,
            'Salary' INT,
            'Description' TEXT,
            'MinSalary' REAL,
            'MaxSalary' REAL,
            'NearestLocationId' INT

        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()
def check_existance_in_db(unique_list,job):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    Job=job
    Job=Job.replace(' ','')
    new_job_list=[]
    statement=' SELECT JobTitle,Company,CompanyLocation,Salary,Description '
    statement+=' FROM ' +Job
    existed_jobs=cur.execute(statement)
    existed_jobs_list=existed_jobs.fetchall()
    for i in unique_list:
        num=len(existed_jobs_list)
        n=0
        for j in existed_jobs_list:
            if (i.title != j[0]) or (i.company != j[1]) or (i.location != j[2]) or (i.salary != j[3]) or (i.description != j[4]):
                n+=1
        if n == num:
            new_job_list.append(i)
    return new_job_list
def insert_db(unique_list,job):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    Job=job
    Job=Job.replace(' ','')
    for i in unique_list:
        statement=' INSERT INTO ' + Job
        statement+='''
            (JobTitle,Company,CompanyLocation,Salary,Description)
            VALUES (?,?,?,?,?)
        '''
        insertion=(i.title,i.company,i.location,i.salary,i.description)
        cur.execute(statement,insertion)
    conn.commit()
    conn.close()


##################################################
#              sort data from db                 #
##################################################
def update_salary_in_db(job):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    Job=job
    Job=Job.replace(' ','')
    statement=' SELECT Id, Salary FROM '+Job
    results=cur.execute(statement)
    results_list=results.fetchall()
    salary_list = []
    for i in results_list:
        if i[1] != 'Not available':
            num_str = nltk.word_tokenize(i[1])
            new_list1 = []
            new_list2 = []
            for j in num_str:
                try:
                    j=j.replace(',','')
                    j=float(j)
                    new_list1.append(j)
                except:
                    pass
                if j == 'hour':
                    for k in new_list1: #transform all salaries to year-based
                        k=k*2080#working hours: 40 h/week, 52 week/year, 2080 h/year
                        new_list2.append(k)
                if j == 'week':
                    for k in new_list1:
                        k=k*52  #working hours:52 week/year
                        new_list2.append(k)
                if j == 'month':
                    for k in new_list1:
                        k=k*12 #working hours: 12 month/year
                        new_list2.append(k)
                if j == 'year':
                    new_list2=new_list1
            if len(new_list2)==1:
                new_list2.append(new_list2[0])
            new_list2.sort()
            statement=' UPDATE '+Job
            statement+=' SET MinSalary='+ str(new_list2[0])
            statement+=' , MaxSalary='+ str(new_list2[1])
            statement+=' WHERE Id='+str(i[0])
            cur.execute(statement)
            salary_list.append(new_list2)
    conn.commit()
    conn.close()
    return salary_list
##################################################
#        build location relationship in db       #
##################################################
distance_url='https://maps.googleapis.com/maps/api/distancematrix/json'
map_key=secrets.Map_api_key
map_key2=secrets.Map_api_key2
map_key3=secrets.Map_api_key3

def get_info_from_db(job):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    Job=job
    Job=Job.replace(' ','')
    statement='''
                SELECT Id, AreaName FROM Area
                WHERE (Id BETWEEN 15 AND 22) OR (Id BETWEEN 33 AND 35) OR
                (Id BETWEEN 37 AND 40) OR (Id BETWEEN 42 AND 48) OR (Id >49)
            '''
    area_results=cur.execute(statement)
    area_list=area_results.fetchall()
    statement='SELECT Id, CompanyLocation FROM '+Job
    comp_results=cur.execute(statement)
    comp_list=comp_results.fetchall()
    conn.close()
    return area_list,comp_list

def get_destinations(job):
    area_list,comp_list=get_info_from_db(job)
    des_list=[]
    for i in area_list:
        area_id=i[0]
        area=i[1]
        des_list.append(area)
    destinations="|".join(des_list)
    return destinations,des_list

def make_request(origins,destinations,key):
    global distance_url,map_key,map_key2
    param={"origins":origins,"destinations":destinations,"key":key}
    resp=cache.make_request_using_cache(distance_url,param)
    data=json.loads(resp)
    return data

def update_nearest_db(job,data,des_list,id):
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    Job=job
    Job=Job.replace(' ','')
    dist_list=[]
    try:
        total_list=data['rows'][0]['elements']
        for i in range(len(total_list)):
            if total_list[i]['status'] == 'OK':
                dist_list.append([total_list[i]['distance']['value'],i])
        rank_dist_list=sorted(dist_list)
        # print(rank_dist_list)
        min_dist_value=rank_dist_list[0][0]
        min_dist_id=rank_dist_list[0][1]
        min_dist_name=des_list[min_dist_id]
        print(id)
        statement=' UPDATE '+Job
        statement+=' SET NearestLocationId = ( SELECT Id FROM Area WHERE AreaName= ?)'
        statement+=' WHERE Id = ?'
        values=(min_dist_name,id)
        cur.execute(statement,values)
        conn.commit()
    except:
        statement=' UPDATE '+Job
        statement+=' SET NearestLocationId = ? '
        statement+=' WHERE Id = ?'
        values=(data['status'],id)
        cur.execute(statement,values)
        conn.commit()
    conn.close()

def match_location(job):
    global distance_url,map_key,map_key2
    area_list,comp_list=get_info_from_db(job)
    destinations,des_list=get_destinations(job)
    for j in comp_list:
        comp_id=j[0]
        comp_l=j[1]
        if comp_l != 'Remote' and comp_l != 'Work at Home':
            origins=comp_l
            data=make_request(origins,destinations,map_key2)
            update_nearest_db(job,data,des_list,comp_id)

def get_over_limit_from_json(job):
    global distance_url,map_key3
    conn=sqlite3.connect('jobs.db')
    cur=conn.cursor()
    Job=job
    Job=Job.replace(' ','')
    statement=' SELECT Id, CompanyLocation FROM '+Job
    statement+=' WHERE NearestLocationId="OVER_QUERY_LIMIT"'
    over_results=cur.execute(statement)
    over_list=over_results.fetchall()
    conn.close()
    destinations,des_list=get_destinations(job)
    # print(over_list)
    for i in over_list:
        over_comp_id=i[0]
        over_comp_l=i[1]
        over_data=make_request(over_comp_l,destinations,map_key3)
        update_nearest_db(job,over_data,des_list,over_comp_id)
