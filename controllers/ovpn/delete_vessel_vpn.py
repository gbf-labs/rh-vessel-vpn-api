# -*- coding: utf-8 -*-
import os
import json
import requests
import subprocess
import string, time, subprocess
from flask import  request
from datetime import datetime
from library.common import Common

from configparser import ConfigParser
from library.postgresql_queries import PostgreSQL
from library.config_parser import configSectionParser

class DeleteVesselVPN(Common):

    # INITIALIZE 
    def __init__(self):
        
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.token = configSectionParser(self.config,"TOKEN")['token']

        self.postgres = PostgreSQL()

    # GET VESSEL FUNCTION
    def delete_vessel_vpn(self):
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
              id: delete_vessel_vpn
              properties:
                vessel_number:
                    type: string

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

        vessel_number = query_json["vessel_number"]

        # # CHECK TOKEN
        if not token == self.token:

            data["alert"] = "Invalid Token"
            data['status'] ='Failed'

            # RETURN ALERT
            return self.return_data(data)

        vpn_name = "VESSEL_" + str(vessel_number)
        vpn_dir = "/etc/openvpn/ccd/" + vpn_name
        vpn_easy_rsa = "/home/all_vpn/" + vpn_name + ".zip"

        try:
            # cmd = "source /etc/openvpn/easy-rsa/vars ; "
            # cmd += "/etc/openvpn/easy-rsa/revoke-full " + vpn_name
            # cmd = "/etc/openvpn/easy-rsa;"
            # cmd += "source ./vars;"
            # cmd += "./revoke-full {0}".format(vpn_name)
            
            os.chdir("/etc/openvpn/easy-rsa")

            cmd = '. ./vars  &&  ./revoke-full {} && service openvpn restart'.format(vpn_name)

            print("Command: ", cmd)

            os.system(cmd)

            # result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            # print(result)

            subprocess.run(["rm", "-rf", vpn_dir])
            subprocess.run(["rm", "-rf", vpn_easy_rsa])
            subprocess.run(["sudo", "service", "openvpn", "restart"]) 

            conditions = []

            conditions.append({
                "col": "account_id",
                "con": "=",
                "val": vessel_number
                })

            conditions.append({
                "col": "vpn_type",
                "con": "=",
                "val": "VESSEL"
                })

            query_json = {}
            query_json['is_active'] = 0

            self.postgres.update('account_vpn_access', query_json, conditions)

            data['status'] ='ok'

        except Exception as e:
            
            print(e)

            data['status'] = 'Failed'

        return self.return_data(data)
