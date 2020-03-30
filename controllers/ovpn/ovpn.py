# -*- coding: utf-8 -*-
import string, time, subprocess
from flask import  request
from datetime import datetime
from library.common import Common

from configparser import ConfigParser
from library.config_parser import configSectionParser

class Ovpn(Common):

    # INITIALIZE 
    def __init__(self):
        
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.token = configSectionParser(self.config,"TOKEN")['token']

    # GET VESSEL FUNCTION
    def ovpn(self):
        """
        This API is for VPN
        ---
        tags:
          - VPN
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
            description: VPN
            required: true
            schema:
              id: ovpn
              properties:
                callback_url:
                    type: string
                data_url:
                    type: string
                job_id:
                    type: integer

        responses:
          500:
            description: Error
          200:
            description: Sending invitaion
        """

        # INIT DATA
        data = {}

        # GET DATA
        token =  request.headers.get('token')

        # GET JSON REQUEST
        query_json = request.get_json(force=True)


        job_id = query_json["job_id"]
        callback_url = query_json["callback_url"]
        data_url = query_json["data_url"]

        # # CHECK TOKEN
        if not token == self.token:

            data["alert"] = "Invalid Token"
            data['status'] ='Failed'

            # RETURN ALERT
            return self.return_data(data)

        directory = '/home/vvpn/vpn_access'
        process_name = 'vpn_access.py'
        script_file = "%s/%s" % ( directory, process_name)
        print("script_file: ", script_file)
        print("job_id: ", job_id)
        print("callback_url: ", callback_url)
        print("data_url: ", data_url)
        print("token: ", token)
        print('python3.5', script_file, '-job_id', str(job_id), '-callback_url', str(callback_url), '-data_url', str(data_url), '-token', str(token))
        subprocess.Popen(['sudo','python3.5', script_file, '-job_id', str(job_id), '-callback_url', str(callback_url), '-data_url', str(data_url), '-token', str(token)])
        # sudo python3.5 vpn_access.py -job_id 2 -callback_url https://www.google.com -data_url https://www.fb.com -token fsdlkfsa349543054305
        # print("callback_url: ", callback_url)
        # print("data_url: ", data_url)
        # print("job_id: ", job_id)

        data['status'] ='ok'

        return self.return_data(data)


