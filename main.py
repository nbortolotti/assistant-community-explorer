import datetime

from flask import Flask, jsonify, request, make_response
from flask_basicauth import BasicAuth
from pycountry_convert import (country_alpha2_to_country_name, COUNTRY_NAME_FORMAT_DEFAULT)

import httplib2
import logging
import json
import googleapiclient.discovery

# meetup integration
import meetup.api

from google.appengine.api import memcache
from oauth2client.contrib.appengine import AppAssertionCredentials
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

urlfetch.set_default_fetch_deadline(180)
app = Flask(__name__, static_url_path="")
basic_auth = BasicAuth(app)

from gdg.models import gdgchapter, gdgchapterurl
from models import Settings

app.config['BASIC_AUTH_USERNAME'] = Settings.get('user_access')
app.config['BASIC_AUTH_PASSWORD'] = Settings.get('pass_access')

@app.route('/api/userconfirmation', methods=['GET'])
def user():
    app.config['BASIC_AUTH_USERNAME'] = Settings.get('user_access')
    app.config['BASIC_AUTH_PASSWORD'] = Settings.get('pass_access')

    if (Settings.get('user_access') == "not set") or (Settings.get('pass_access') == "not set"):
        return 'User Not Confirmed'
    else:
        return 'User Confirmed'

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
@app.route('/api/importschapters', methods=['GET'])
@basic_auth.required
def import_spreadsheet():
    try:
        spreadsheet_id = Settings.get('sheet_id')
        range_name = Settings.get('sheet_range')

        config = config_sheet()
        result = config.service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute(
            http=config.http)

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

@app.route('/api/import_chapter_url', methods=['GET'])
@basic_auth.required
def import_chapter_url():
    try:
        spreadsheet_id = Settings.get('sheet_id')
        range_name = Settings.get('sheet_range')

        config = config_sheet()
        result = config.service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute(
            http=config.http)

        values = result.get('values', [])
        #gdglist = gdgchapterurl.query().fetch()

        for r in values:
            #if r[0] not in gdglist:
            if not gdgchapterurl.query(gdgchapterurl.groupUrlname == r[0]).fetch():
                obj = gdgchapterurl()
                obj.groupUrlname = r[0]
                obj.put()

        return 'importing process completed'
    except:
        logging.error('error into importing process')
        raise


# testing method to explore datastore entity
@app.route('/api/testchapter/<country>', methods=['GET', 'OPTIONS'])
@basic_auth.required
def get_testchapter(country):
    q = gdgchapter.query(gdgchapter.countryMod == country)
    return json.dumps(q.count())


@app.route('/api/assistchapter', methods=['POST'])
@basic_auth.required
def get_chapter():
    req = request.get_json(silent=True, force=True)

    try:
        action = req.get('queryResult').get('intent')
    except AttributeError:
        return 'json error'

    parameters = req['queryResult']['parameters']

    # print(action)
    # print(parameters['country'][0])

    res = 'I can not identify chapters in your country'

    if action['displayName'] == 'chapter.number':
        q = gdgchapter.query(gdgchapter.countryMod == parameters['country'][0])
        chapter_value = q.count()
        print(chapter_value)

        if chapter_value > 0:
            res = 'The number of chapter in your country is ' + str(chapter_value)

    return make_response(jsonify({'fulfillmentText': res}))

@app.route('/api/task_group/<url>', methods=['GET'])
def task_group(url):
    client = meetup.api.Client(Settings.get('meetup_key'))
    group_info = client.GetGroup({'urlname': url})

    check_chapter = gdgchapter.query(gdgchapter.groupUrl == url).fetch()

    cn_name_format = COUNTRY_NAME_FORMAT_DEFAULT

    if not check_chapter:
        obj = gdgchapter()
        obj.groupid = str(group_info.id)
        obj.groupUrl = url
        obj.groupName = group_info.name
        obj.countryMod = country_alpha2_to_country_name(group_info.country, cn_name_format)
        obj.groupStatus = group_info.status
        obj.city = group_info.city
        obj.groupMembers = group_info.members

        obj.put()

        return make_response("task executed")

@app.route('/api/meetup_sync', methods=['POST'])
@basic_auth.required
def test_group():
    try:
        gdg_urls = gdgchapterurl.query().fetch()

        coef = 0
        for gdg_u in gdg_urls:
            coef += 1
            taskqueue.add(method="GET",
                          queue_name='meetup',
                                 url='/api/task_group/' + gdg_u.groupUrlname ,
                                 target='worker_' + gdg_u.groupUrlname + str(datetime.datetime.now()),
                                 eta=datetime.datetime.now() + datetime.timedelta(seconds=(20 + coef)))

        return make_response("importing from Meetup completed")
    except:
        logging.error('error Meetup access process')
        raise