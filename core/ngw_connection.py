# -*- coding: utf-8 -*-
"""
/***************************************************************************
    NextGIS WEB API
                              -------------------
        begin                : 2014-11-19
        git sha              : $Format:%H$
        copyright            : (C) 2014 by NextGIS
        email                : info@nextgis.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import json
import requests
from base64 import b64encode
from requests.utils import to_native_string

from ngw_error import NGWError

UPLOAD_FILE_URL = '/api/component/file_upload/upload'


def _basic_auth_str(username, password):
    """Returns a Basic Auth string."""

    authstr = 'Basic ' + to_native_string(
        b64encode(('%s:%s' % (username, password)).encode('utf-8')).strip()
    )

    return authstr


class NGWConnection(object):

    def __init__(self):
        self.__server_url = None
        self.__session = requests.Session()
        self.__auth = ("", "")

    def __init__(self, conn_settings):
        self.__server_url = None
        self.__session = requests.Session()
        self.__auth = ("", "")
        self.set_from_settings(conn_settings)

    def set_from_settings(self, conn_settings):
        self.server_url = conn_settings.server_url
        self.set_auth(conn_settings.username, conn_settings.password)

    @property
    def server_url(self):
        return self.__server_url

    @server_url.setter
    def server_url(self, value):
        if isinstance(value, (str, unicode)):
            self.__server_url = value.strip().rstrip('\\\/')
        else:
            self.__server_url = value

    def set_auth(self, username, password):
        # self.__session.auth = (username, password)
        self.__auth = (username, password)

    def get_auth(self):
        # return self.__session.auth
        return self.__auth

    def __request(self, sub_url, method, params=None, **kwargs):
        payload = None
        if params:
            payload = json.dumps(params)
            
        if 'data' in kwargs:
            payload = kwargs['data']
        
        json_data = None
        if 'json' in kwargs:
            json_data = kwargs['json']

        req = requests.Request(method, self.server_url + sub_url, data=payload, json=json_data)
        req.headers['Authorization'] = _basic_auth_str(self.__auth[0], self.__auth[1])

        prep = self.__session.prepare_request(req)
        
        try:
            resp = self.__session.send(prep)
        except requests.exceptions.RequestException, e:
            raise NGWError(e.message.args[0])

        if resp.status_code / 100 != 2:
            raise NGWError(resp.content)
        
        return resp.json()

    def get(self, sub_url, params=None, **kwargs):
        return self.__request(sub_url, 'GET', params, **kwargs)

    def post(self, sub_url, params=None, **kwargs):
        return self.__request(sub_url, 'POST', params, **kwargs)

    def put(self, sub_url, params=None, **kwargs):
        return self.__request(sub_url, 'PUT', params, **kwargs)
    
    def delete(self, sub_url, params=None, **kwargs):
        return self.__request(sub_url, 'DELETE', params, **kwargs)
    
    def get_upload_file_url(self):
        return UPLOAD_FILE_URL
    
    def upload_file(self, filename):
        with open(filename, 'rb') as fd:
            upload_info = self.put(self.get_upload_file_url(), data=fd) 
            return upload_info
    
    def download_file(self, url):
        req = requests.Request('GET', self.server_url + url)
        prep = self.__session.prepare_request(req)
        
        try:
            resp = self.__session.send(prep, stream=True)
        except requests.exceptions.RequestException, e:
            raise NGWError(e.message.args[0])

        if resp.status_code / 100 != 2:
            raise NGWError(resp.content)
        
        return resp.content