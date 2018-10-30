from flask import Flask, jsonify, request, make_response

import httplib2
import logging
import json
import googleapiclient.discovery

from google.appengine.api import memcache
from oauth2client.contrib.appengine import AppAssertionCredentials
from google.appengine.api import urlfetch

urlfetch.set_default_fetch_deadline(180)
app = Flask(__name__, static_url_path="")

from gdg.models import gdgchapter
from models import Settings

@app.route('/')
def hello():
    return 'Hello Community Assistant Explorer '

@app.errorhandler(404)
def page_not_found(e):
    return 'Sorry, Nothing at this URL.', 404

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class config_sheet(object):
    __metaclass__ = Singleton
    credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/spreadsheets.readonly')
    http = credentials.authorize(httplib2.Http(memcache))
    service = googleapiclient.discovery.build('sheets', 'v4')

# testing method to import information
@app.route('/importschapters', methods=['GET'])
def import_spreadsheet():
    try:
        spreadsheet_id = Settings.get('sheet_id')
        range_name = Settings.get('sheet_range')

        config = config_sheet()
        result = config.service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute(http=config.http)

        values = result.get('values', [])

        for r in values:
            obj = gdgchapter()

            obj.groupName = r[0]
            obj.groupStatus = r[2]
            obj.groupMembers = int(r[3])
            obj.city = r[1]
            obj.countryMod = r[4]

            obj.put()

        return 'importing process completed'
    except:
        logging.error('error into importing process')
        raise

# testing method to explore datastore entity
@app.route('/testchapter/<country>', methods=['GET', 'OPTIONS'])
def get_testchapter(country):
    q = gdgchapter.query(gdgchapter.countryMod == country)
    return json.dumps(q.count())

@app.route('/assistchapter', methods=['POST'])
def get_chapter():
    req = request.get_json(silent=True, force=True)

    try:
        action = req.get('queryResult').get('intent')
    except AttributeError:
        return 'json error'

    parameters = req['queryResult']['parameters']

    #print(action)
    #print(parameters['country'][0])


    res = 'I can not identify chapters in your country'

    if action['displayName'] == 'chapter.number':
        q = gdgchapter.query(gdgchapter.countryMod == parameters['country'][0])
        chapter_value = q.count()
        print(chapter_value)

        if chapter_value > 0:
            res = 'The number of chapter in your country is ' + str(chapter_value)

    return make_response(jsonify({'fulfillmentText': res}))