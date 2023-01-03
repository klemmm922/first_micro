import requests as requests
from flask import Flask,render_template
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

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