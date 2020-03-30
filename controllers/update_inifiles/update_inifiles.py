# -*- coding: utf-8 -*-
import time
import json
import string
import subprocess
import requests
from flask import  request
from datetime import datetime
from library.common import Common

from configparser import ConfigParser
from library.config_parser import configSectionParser
import paramiko

class UpdateINIFiles(Common):

    # INITIALIZE 
    def __init__(self):
        
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.token = configSectionParser(self.config,"TOKEN")['token']

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.load_system_host_keys()

    # GET VESSEL FUNCTION
    def update_inifiles(self):
        """
        This API is for VPN
        ---
        tags:
          - INI Files
        produces:
          - application/json
        parameters:
          - name: token
            in: header
            description: Token
            required: true
            type: string
          - name: query
            in: body
            description: INI Files
            required: true
            schema:
              id: update ini files
              properties:
                host:
                    type: string
                port:
                    type: string
                ini_data:
                    type: json
                    example: {}

        responses:
          500:
            description: Error
          200:
            description: Sending command
        """

        # INIT DATA
        data = {}

        # GET DATA
        token =  request.headers.get('token')
        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        host = query_json["host"]
        port = query_json["port"]
        ini_data = query_json["ini_data"]

        # # CHECK TOKEN
        if not token == self.token:

            data["alert"] = "Invalid Token"
            data['status'] ='Failed'

            # RETURN ALERT
            return self.return_data(data)

        try:

            params = {}
            params['datas'] = ini_data
            api_endpoint = "http://" + str(host) + ":" + str(port) + "/vessel/ini/files"

            print("++"*100)
            print("api_endpoint: ", api_endpoint)
            print("++"*100)

            headers = {'content-type': 'application/json', 'token': token}
            req = requests.put(api_endpoint, data=json.dumps(params), headers=headers)
            res = req.json()

            data['status'] = 'Failed'
            if res['status'] == 'ok':

                data['status'] ='ok'

        except:

            data['status'] ='Failed'

        return self.return_data(data)
