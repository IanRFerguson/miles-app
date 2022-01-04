#!/bin/python3

"""
About this App

* This is a programmatic way to keep track of how far I run every year
* Incoming texts are funneled to SQLite Database
* Miles run are plotted and displayed on landing page of app

IRF
"""

"""
Running to-do

* Miles to date under hyperlink header ... consider h3 size
* More customized text responses (every 100 miles or so)
"""

# ----- Imports
from flask import Flask, render_template, redirect, url_for, request
from helper import *

app = Flask(__name__)
sql_init()

try:
      plotYeah()
except:
      print("Still compiling miles to plot...")


# ----- App Setup

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


# ---- Year by Year

@app.route('/2021', methods=['GET', 'POST'])
def miles_2021():
      sms = fetch_sms()
      mtd = milesRun(YEARVALUE=2021)
      return render_template('miles_2021.html', sms=sms, mtd=mtd)


@app.route('/2022', methods=['GET', 'POST'])
def miles_2022():
      sms = fetch_sms()
      mtd = milesRun(YEARVALUE=2022)
      return render_template('miles_2022.html', sms=sms, mtd=mtd)


if __name__ == "__main__":
      app.run(debug=True)