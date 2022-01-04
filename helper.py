#!/bin/python3

# ------- Imports
from flask import request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import json, sqlite3, sys, os, pathlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime
import pandas as pd

# ----- Environment

this_year = datetime.now().strftime("%Y")

def twilio_setup():
      """
      Returns everything you need to connect to Twilio API

      NOTE: This is stored locally, you can obtain yours from Twilio
      """

      with open("./twilio.json") as incoming:
            temp = json.load(incoming)
            return temp['sid'], temp['auth'], temp['my_number']


def environment_setup():
      """
      Sets up routing for plot and CSV output
      """

      temp_path = os.path.join(f'./static/{this_year}/plots')

      if not os.path.exists(temp_path):
            pathlib.Path(temp_path).mkdir(parents=True, exist_ok=True)


TWIL_account, TWIL_auth, TWIL_number = twilio_setup()                   # SID and authoriziation from Twilio
environment_setup()
API = Client(TWIL_account, TWIL_auth)                                   # Instantiate Twilio API

# ----- App Functions

def fetch_sms():
      return API.messages.stream()                                      # Returns all texts to/from my_number


def response_sms(INCOMING):
      """
      Decision tree for incoming SMS texts
      
      * If a raw float is input, it's added to miles run
      * If 'Miles' is input, end user receives a text
      """
      
      body = INCOMING

      # Determine if text is able to be cast to float
      def checkForCast(X):
            try:
                  float(body)
                  return True

            except ValueError:
                  return False

      if checkForCast(body):
            resp = MessagingResponse()
            val = milesRun()

            if (round(val) % 100) < 10:
                  confetti_cake = (round(val) / 100) * 100
                  resp.message(f"{confetti_cake} miles already? That's {val} miles on the year dude, you're crushing it!")
            else:
                  resp.message(f"That's what's up! You've run {val} miles this year big homie")
            return str(resp)
      
      elif body.upper() == "MILES":
            resp = MessagingResponse()
            resp.message("Respond to this text with your miles run today\n\nKeep up the good work dude!")
            return str(resp)

      else:
            return "Ok"

            
# ------- Tables
def sql_init():
      """
      * Creates DB table if it doesn't exist
      * Pushes unique texts to table
      """

      with sqlite3.connect('twilio-database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS texts
            (created DATE PRIMARY KEY,
            sent_to TEXT,
            sent_from TEXT,
            body TEXT)
            ''')

      try:
            # Connect to DB
            conn = sqlite3.connect('twilio-database.db')

      except Exception as e:
            print('\nIssue connecting to database:\t\t{}'.format(e))
            sys.exit(1)

      cur = conn.cursor()                                                     # Define cursor for DB executions
     
      for text in fetch_sms():

            if text.from_ == '+17038190646':
                  temp = [text.date_created, text.to,                         # Values derived from text class
                        text.from_, text.body] 

                  cur.execute('''
                  INSERT OR IGNORE INTO texts
                  VALUES (?, ?, ?, ?)''', temp)

      conn.commit()
      conn.close()


def compile_miles(YEARVALUE=this_year):
      """
      * Merges SQLite databse with local CSV (miles logged before app)
      * Could this be written more effectively? For sure!
      """

      # Query to excute on SQLite table
      query = '''
      SELECT *
      FROM texts
      WHERE sent_from = '+17038190646';
      '''

      # Determine if value can be cast to numeric type or not
      def numericCheck(x):
            try:
                  float(x)
                  return True
            except:
                  return False


      with sqlite3.connect('./twilio-database.db') as connect:
            # Read in query as a Pandas DataFrame object
            data = pd.read_sql(query, connect)

      # Boolean column isolates numeric entries
      data['numeric'] = data['body'].apply(lambda x: numericCheck(x))
      data = data[data['numeric'] == True].reset_index(drop=True)

      # Convert created column to datetime format
      data['created'] = pd.to_datetime(data['created'])
      data['created'] = data['created'].apply(lambda x: datetime.strftime(x, '%Y-%m-%d'))

      data['year_value'] = data['created'].apply(lambda x: int(x.split('-')[0]))
      data = data[data['year_value'] == int(YEARVALUE)]

      # Align DB table with local CSV for continuity
      data.rename(columns={'created': 'dates', 'body': 'miles'}, inplace=True)
      data = data.loc[:, ['dates', 'miles']]

      # Isolate day of week and month
      data['DOW'] = data['dates'].apply(lambda x: datetime.strftime(pd.to_datetime(x), '%A'))
      data['month'] = data['dates'].apply(lambda x: datetime.strftime(pd.to_datetime(x), '%B'))


      try:
            # Read in local CSV and perform similar operations
            miles = pd.read_csv(f'./static/{YEARVALUE}/Raw.csv')
            miles['dates'] = miles['dates'].apply(lambda x: datetime.strptime(x, '%A %B %d'))
            miles['dates'] = miles['dates'].apply(lambda x: x.replace(2021))

            # Concatenate the two dataframes
            output = pd.concat([miles, data])
      
      except Exception as e:
            print(f"{e} ... moving on anyway")
            output = data
            
      output['dates'] = pd.to_datetime(output['dates'])
      output = output.sort_values(by='dates').reset_index(drop=True)
      return output


# ------- Plots!
def frames(YEARVALUE):
      """
      Returns a DataFrame object wtih *all* dates so far this year
      Dates where I didn't run will show 0
      """

      # Instantiate miles run and cast miles to numeric
      MTD = compile_miles(YEARVALUE=YEARVALUE)
      MTD['miles'] = pd.to_numeric(MTD['miles'])

      # Determines if run was the longest of the year
      def maxMiles(x):
            if x == max(MTD['miles']):
                 return True
            else:
                 return False

      # Every date for the year  
      def xAsDates(X):
           return list(pd.date_range(start=min(X['dates']), end=max(X['dates']), freq='D'))

      # Create dataframe of NA's for every date of the year
      def generateNonsense(X):
            nonsense = pd.DataFrame(columns=['dates', 'miles'])
            nonsense['dates'] = xAsDates(X)
            return nonsense

      # Merge nonsene DF with real DF + only keep values that are not NA
      def AllDates(X):
            Y = generateNonsense(X)
            temp = X.merge(Y, on='dates', how='right')
            temp = temp.drop(columns=['miles_y']).rename(
                  columns={'miles_x': 'miles'})
            temp['miles'] = pd.to_numeric(temp['miles'])
            temp['max_miles'] = temp['miles'].apply(lambda x: maxMiles(x))
            temp['miles'] = temp['miles'].fillna(0)
            return temp

      return AllDates(MTD)


def milesRun(YEARVALUE=this_year):
      """
      Returns total # of miles run this year
      """

      output = frames(YEARVALUE=YEARVALUE)
      return round(sum(output['miles']), 2)


def plotYeah(YEARVALUE=this_year):
      """
      Generates plots of miles run and saves them locally
      These are displayed on landing page
      """

      output = frames(YEARVALUE=YEARVALUE)

      def generateSubtitle(X):
          total_run = round(sum(X['miles']), 2)
          today = datetime.now().strftime('%B %d, %Y')
          return "Updated {}".format(today)

      dateForm = mdates.DateFormatter('%m-%d')

      # ALL MILES
      plt.figure(figsize=(15, 6))
      g = sns.barplot(data=output, x='dates', y='miles', hue='max_miles')
      ticks = g.get_xticks()
      labels = g.get_xticklabels()

      try:
            n = len(ticks) // 20
      except:
            n = len(ticks)

      g.set_xticks(ticks[::n])
      g.set_xticklabels(labels[::n])
      plt.title(generateSubtitle(output), fontsize=18)
      g.xaxis.set_major_formatter(dateForm)
      plt.xlabel('')
      plt.ylabel('Miles Run', fontsize=12)
      plt.legend('')
      plt.savefig(f'./static/{YEARVALUE}/plots/MILES.png')

      # BY MONTH
      plt.figure(figsize=(15, 6))
      sns.violinplot(data=output, x="month", y="miles", palette='Spectral')
      plt.xlabel('')
      plt.ylabel('Miles Run')
      plt.savefig(f'./static/{YEARVALUE}/plots/MONTHS.png')

      # BY DOW
      plt.figure(figsize=(15,6))
      sns.violinplot(data=output, x='DOW', y='miles', palette='Spectral')
      plt.xlabel('')
      plt.ylabel('Miles Run')
      plt.savefig(f'./static/{YEARVALUE}/plots/DOW.png')
