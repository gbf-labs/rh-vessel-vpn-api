import time
from library.postgresql_queries import PostgreSQL
from flask import jsonify, request, json
from library.config_parser import configSectionParser
from configparser import ConfigParser

class Common():

    # INITIALIZE
    def __init__(self):

        # INIT CONFIG
        self.config = ConfigParser()
        # CONFIG FILE
        self.config.read("config/config.cfg")

        # SET CONFIG VALUES
        self.token = configSectionParser(self.config,"TOKEN")['token']

    # RETURN DATA
    def return_data(self, data):

        # RETURN
        return jsonify(
            data
        )

    # VALIDATE TOKEN
    def validate_token(self, token):

        # CHECK IF COLUMN EXIST,RETURN 0 IF NOT
        if not token: return 0
        
        if token == self.token:
            
            return 1

        else: return 0