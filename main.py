#!/bin/python3

"""
About this App

* This is a programmatic way to keep track of how far I run in 2021
* Incoming texts are funneled to SQLite Database
* Miles run are plotted and displayed on landing page of app

IRF
"""

# --------- Imports
from flask import Flask, render_template, redirect, url_for, request
from helper import *

app = Flask(__name__)
load_dotenv()
sql_init()
plotYeah()


# --------- App Setup

"""
Index (root) => Renders plots of miiles run, derived from 
SMS => Text I/O, produces handles incoming and triggers outgoing SMS
"""

@app.route('/', methods=['GET', 'POST'])
def index():
      sms = fetch_sms()                                      
      return render_template('index.html', sms=sms)


@app.route('/sms', methods=['GET', 'POST'])
def sms():
      return response_sms(request.values.get('Body'))
      

# ---------- Run App
if __name__ == "__main__":
      app.run(debug=True)