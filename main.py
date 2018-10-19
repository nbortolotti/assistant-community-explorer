from datetime import timedelta
from functools import update_wrapper

from flask import Flask, jsonify, abort, request, make_response, url_for

import httplib2
import logging
import json

from google.appengine.api import memcache

import googleapiclient.discovery
from oauth2client.appengine import AppAssertionCredentials

credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/spreadsheets.readonly')
http = credentials.authorize(httplib2.Http(memcache))

service = googleapiclient.discovery.build('sheets', 'v4')


from google.appengine.api import urlfetch

urlfetch.set_default_fetch_deadline(180)

app = Flask(__name__, static_url_path="")

from gdg.models import gdgchapter

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            # logging.info('atencion')
            # logging.info(request.url_root)

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator

@app.route('/')
def hello():
    return 'Hello Community Assistant Explorer '

@app.errorhandler(404)
def page_not_found(e):
    return 'Sorry, Nothing at this URL.', 404

# testing method to import information
@app.route('/importschapters', methods=['GET'])
def import_spreadsheet():
    try:
        spreadsheet_id = '16FE0UN9nSup8T2LXaFoW0LKbrjN2BOmcrn3Q8VvMTTE'
        range_name = 'Hoja1!A2:E100'

        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute(http=http)

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
        logging.error('Error')
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