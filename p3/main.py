#!/usr/bin/env python
# coding: utf-8

# In[1]:


# project: p3
# submitter: tjones25
# partner: none


# In[9]:


import pandas as pd
from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)
df = pd.read_csv("main.csv")
counter = 0
counterA = 0
counterB = 0

@app.route('/')
def home():
    global counter
    
    if counter < 10 and (counter % 2) == 0:
        counter += 1
        with open("index1.html") as f:
            html = f.read()

        return html
        
    if counter < 10 and (counter % 2) != 0:
        counter += 1
        with open("index2.html") as f:
            html = f.read()

        return html
    
    if counter == 10 and counterA >= counterB:
        with open("index1.html") as f:
            html = f.read()
        return html
    
    if counter == 10 and counterA < counterB:
        with open("index2.html") as f:
            html = f.read()
        return html
    
@app.route('/browse.html')
def browse():
    with open(os.path.join("main.csv")) as f:
    #with open("main.csv") as f:
        df = pd.read_csv(f)
    df_html = df.to_html()
    
    html = "<html><body><h1>Browse</h1></body></html>" + df_html
    return html

@app.route('/donate.html', methods=["GET"])
def donations():
    global counterA
    global counterB
    page = request.args.get("from")
    plea = "Thanks for visiting our donations page! Our mission is to provide you with the most efficient and most relevant data available to us. If you appriciate what we're doing, please continue and donate any amount you can!"
    html = "<html><body><h1>Donations</h1><p>" + plea + "</p></body></html>"
    if str(page) == 'A':
        counterA += 1
        return html
    
    if str(page) == 'B':
        counterB += 1
        return html
    
    else:
        return html

@app.route('/api.html')
def api():
    l1 = "<p>To get data on a specific launch number, do this:<pre>  /spacex.json?launch=1</pre>"
    l2 = "<p>To get all data in a .json file, do this:<pre>  /spacex.json</pre>"
    l3 = "<p>To get launched with specific orbits, do this:<pre>  /spacex.json?orbit=LEO"
    html = "<html><body><h1>API</h1>" + l1 + l2 + l3 + "</body></html>"
    
    return html

@app.route('/spacex.json', methods=["GET"])
def json():
    launch = request.args.get("launch")
    orbit = request.args.get("orbit")
    
    if orbit != None:
        df1 = df.loc[df['Orbit'] == str(orbit)]
        return jsonify(df1.to_dict(orient='records'))
    elif launch != None:
        df2 = df.loc[df['Flight Number'] == str(launch)]
        return jsonify(df2.to_dict(orient='records'))
    else:
        return jsonify(df.to_dict(orient='records'))


@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    #regex taken from https://www.regular-expressions.info/email.html
    if re.match(r"\b[\w._%+-]+@[\w.-]+\.[\w]{2,}\b", email):
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n")
        return jsonify("thanks")
    return jsonify("WHAT ARE YOU DOING?! THAT'S NOT AN EMAIL ADDRESS!")

if __name__ == '__main__':
    app.run(host="0.0.0.0") # don't change this line!


# In[ ]:




