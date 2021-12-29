#!/bin/python3

"""
About this App

* This is a programmatic way to keep track of how far I run every year
* Incoming texts are funneled to SQLite Database
* Miles run are plotted and displayed on landing page of app

IRF
"""

# ----- Imports
from flask import Flask, render_template, redirect, url_for, request
from helper import *

app = Flask(__name__)
sql_init()
plotYeah()


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
      return render_template('miles_2021.html', sms=sms)


@app.route('/2022', methods=['GET', 'POST'])
def miles_2022():
      sms = fetch_sms()
      return render_template('miles_2022.html', sms=sms)


if __name__ == "__main__":
      app.run(debug=True)