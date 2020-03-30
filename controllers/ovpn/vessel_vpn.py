# -*- coding: utf-8 -*-
import string, time, subprocess
from flask import  request
from datetime import datetime
from library.common import Common

from configparser import ConfigParser
from library.config_parser import configSectionParser

class VesselVPN(Common):

    # INITIALIZE 
    def __init__(self):
        
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.token = configSectionParser(self.config,"TOKEN")['token']

    # GET VESSEL FUNCTION
    def vessel_vpn(self):
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
              id: vessel_vpn
              properties:
                callback_url:
                    type: string
                vessel_number:
                    type: string
                vessel_name:
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
        vessel_number = query_json["vessel_number"]
        vessel_name = query_json["vessel_name"]

        # # CHECK TOKEN
        if not token == self.token:

            data["alert"] = "Invalid Token"
            data['status'] ='Failed'

            # RETURN ALERT
            return self.return_data(data)

        directory = '/home/vvpn/vpn_access'
        process_name = 'script_vpn_real_vessel_auto_creation.py'
        script_file = "%s/%s" % ( directory, process_name)
        print("script_file: ", script_file)
        print("job_id: ", job_id)
        print("callback_url: ", callback_url)
        print("vessel_number: ", vessel_number)
        print("vessel_name: ", vessel_name)
        print("token: ", token)
        print('python3.5', script_file, '-job_id', str(job_id), '-callback_url', str(callback_url), '-vessel_number', str(vessel_number), '-vessel_name', str(vessel_name), '-token', str(token), '-vessel_os', 'LINUX')
        subprocess.Popen(['sudo','python3.5', script_file, '-job_id', str(job_id), '-callback_url', str(callback_url), '-vessel_number', str(vessel_number), '-vessel_name', str(vessel_name), '-token', str(token), '-vessel_os', 'LINUX'])

        # print('python3.5', script_file, '-job_id', str(job_id), '-callback_url', str(callback_url), '-vessel_number', str(vessel_number), '-token', str(token))
        # subprocess.Popen(['sudo','python3.5', script_file, '-job_id', str(job_id), '-callback_url', str(callback_url), '-vessel_number', str(vessel_number), '-token', str(token)])

        data['status'] ='ok'

        return self.return_data(data)


