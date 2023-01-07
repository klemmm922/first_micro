import requests as requests
from flask import Flask,render_template
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd   
from pytrends.request import TrendReq
import datetime
import time
from functools import wraps
from collections import Counter

app = Flask(__name__)

@app.route('/',methods=["GET"])
def home():
    prefix_google = """
    <!-- Google tag (gtag.js) -->
    <script async 
    src="https://www.googletagmanager.com/gtag/js?id=G-XLPQT1T2SC"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XLPQT1T2SC');
    </script>
    """
    return render_template("home.html") + prefix_google

@app.route('/logger', methods=["GET","POST"])
def logger(): 
    
    app.logger.warning("This is a warning")
    app.logger.error("This is an error")
    app.logger.info("This is an info")
    return render_template("logger.html")

@app.route('/cookies')
def cookies():
    req = requests.get("https://analytics.google.com/analytics/web/#/report-home/p344218650")
    #req = requests.get("https://www.google.com/")
    return req.text

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'datasource2-0ebaadeaf61b.json'
VIEW_ID = '344218650'


def initialize_analyticsreporting():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)
  
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics

def get_report(analytics):
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'today'}],
          'metrics': [{'expression': 'ga:pageviews'}],
          'dimensions': []
        }]
      }
  ).execute()


def get_visitors(response):
  visitors = 0 # in case there are no analytics available yet
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for row in report.get('data', {}).get('rows', []):
      dateRangeValues = row.get('metrics', [])

      for i, values in enumerate(dateRangeValues):
        for metricHeader, value in zip(metricHeaders, values.get('values')):
          visitors = value

  return str(visitors)

@app.route('/oauth',methods=["GET"])
def oauth():
    analytics = initialize_analyticsreporting()
    #response = get_report(analytics)
    #visitors = get_visitors(response)
    #return render_template("oauth.html", visitors=str(visitors))
    return render_template("oauth.html")

@app.route('/pytrends',methods=["GET"])
def pytrends():
  pytrend = TrendReq()
  kw_list = ["Facebook","Apple","Google","Microsoft"]
  pytrend.build_payload(kw_list, timeframe='today 3-m')

  regiondf = pytrend.interest_over_time()
  regiondf = regiondf.sort_values(by='Facebook', ascending=False)

  df_facebook = regiondf[['Facebook']]
  df_apple = regiondf[['Apple']]
  df_google = regiondf[['Google']]
  df_microsoft = regiondf[['Microsoft']]

  df_date = regiondf.index.values.tolist()

  ts = [element/1e9 for element in df_date]
  date = [datetime.datetime.fromtimestamp(element) for element in ts]
  days = [element.date() for element in date]
  months = [element.month for element in days]

  params = {
        "type": 'line',
        "data": {
            "labels": months,
            "datasets": [{
                "label": "Facebook",
                "data": df_facebook,
                "borderColor": '#3e95cd',
                "fill": 'false',
            },
                {
                "label": "Apple",
                "data": df_apple,
                "borderColor": '#ffce56',
                    "fill": 'false',
            },
              {
              "label": "Google",
              "data": df_google,
              "borderColor": '#8e5ea2',
                  "fill": 'false',
            },
              {
              "label": "Microsoft",
              "data": df_microsoft,
              "borderColor": '#e8c3b9',
                  "fill": 'false',
            }
            ]
        },
        "options": {
            "title": {
                "display": 'true',
                "text": 'Trend comparison'
            },
            "scales": {
                "yAxes": [{
                    "ticks": {
                          "beginAtZero": 'true'
                          }
                }]
            }
        }
    }


  prefix_chartjs = """
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.min.js"></script>
  <canvas id="myChart" width="1200px" height="700px"></canvas>""" + f"""
  <script>
  var ctx = document.getElementById('myChart');
  var myChart = new Chart(ctx, {params});
  </script>
  """

  #return prefix_chartjs
  
  return regiondf.to_html(classes='table table-striped table-hover table-condensed table-responsive') + prefix_chartjs

  # return regiondf.to_html()
  #return regiondf.to_html(classes='table table-striped table-hover table-condensed table-responsive')


def log_execution_time(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
      start_time = time.time()
      result = func(*args, **kwargs)
      end_time = time.time()
      print(f"Execution time: {end_time - start_time} seconds")
      return result
  return wrapper


@app.route('/shakespear',methods=["GET"])
@log_execution_time
def shakespear():
  with open('shakespeare.txt', 'r') as f:
        text = f.read()

  word_counts = {}
  for word in text.split():
      if word in word_counts:
          word_counts[word] += 1
      else:
          word_counts[word] = 1
  
  return render_template('shakespear.html', word_counts=word_counts)


@app.route('/countShakespear',methods=["GET"])
@log_execution_time
def countShakespear():
  
  with open('shakespeare.txt', 'r') as f:
      text = f.read()

  # Split the text into words
  words = text.split()

  # Use the Counter function to count the number of occurrences of each word
  word_counts = Counter(words)

  return render_template('shakespear.html', word_counts=word_counts)
