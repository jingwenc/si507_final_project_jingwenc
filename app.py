from flask import Flask, render_template, request, redirect
import final_proj
import json
import pandas as pd
import numpy as np
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import os

app = Flask(__name__)
job=''
JS_list=[]
job_list=[]

@app.route('/')
def search_jobs(name='job seeker'):
    try:
        profile=final_proj.get_linkedin_profile()
        name=profile.firstName
    except:
        pass
    return render_template('search.html', name=name)

@app.route('/job',methods=['POST'])
def job_info():
    global job,JS_list,job_list
    job=request.form['job title']
    location=request.form['location']
    num_records=request.form['result_num']
    num_records=int(num_records)
    JS_list=final_proj.init_update_insert_db_for_job(job,num_records,location)
    job_list=final_proj.get_job_list_list(job,JS_list)
    return redirect('/jobs')

@app.route('/jobs',methods=['GET','POST'])
def job_search_result(jobs=job):
    global job_list
    if request.method == 'POST':
        sortby = request.form['sortby']
        sortorder = request.form['sortorder']
        job_list = final_proj.get_all_job_info(sortby, sortorder)
    else:
        job_list= final_proj.get_all_job_info()
    return render_template("job_display.html", job_list=job_list)

@app.route('/jobs/plot')
def plot_option():
    global job_list
    job_list2=[]
    for i in range(len(job_list)):
        job_list2.append([i]+job_list[i])
    return render_template('plot.html',job_list=job_list2)

@app.route('/jobs/plot/jobs')
def plot_jobs():
    global job,JS_list
    final_proj.plot_jobs(job,JS_list)
    return redirect('/jobs/plot')

@app.route('/jobs/plot/nearby',methods=['POST'])
def plot_nearby():
    global job_list,JS_list
    plot_num=request.form['num']
    plot_num=int(plot_num)
    typ=request.form['types']
    true_num=job_list[plot_num][-1]
    jobclass=JS_list[true_num]
    final_proj.plot_nearby_for_job(jobclass,typ)
    return redirect('/jobs/plot')

@app.route('/jobs/plot/quality',methods=['POST'])
def plot_quality():
    global job,JS_list,job_list
    plot_num=request.form['num']
    plot_num=int(plot_num)
    AreaId=job_list[plot_num][-2]
    # jobclass=JS_list[plot_num]
    # AreaId=final_proj.get_area_Id(job,jobclass)
    # print(AreaId)
    food=final_proj.food_expenditure(AreaId)
    transp=final_proj.transportation_fee(AreaId)
    medical=final_proj.medical_expenditure(AreaId)
    edu=final_proj.education_expenditure(AreaId)
    housing=final_proj.housing_expenditure(AreaId)
    values=[food,transp,medical,edu,housing]
    labels=['Food','Transportation','Medical','Education','Housing']
    salary=0.5*(job_list[plot_num][3]+job_list[plot_num][4])
    div=final_proj.offline_plotly(values,labels,salary)
    image_name=job+str(AreaId)+'.html'
    save_path="C:/Users/HUAWEI/Desktop/507FinalProj/templates"
    with open(os.path.join(save_path,image_name),'w') as f:
        f.write(div)
    return render_template(image_name)

if __name__=="__main__":
    final_proj.init()
    app.run(debug=True)
