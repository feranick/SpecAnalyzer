'''
dataManagement.py
-----------------
Class for providing access to data-management database

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import sys, math, json, os.path, time
global MongoDBhost

#************************************
''' Class Database '''
#************************************
class DataManagement:
    def __init__(self, info):
        #self.info = info
        self.dbHostname = info[0]
        self.dbPortNum = info[1]
        self.dbName = info[2]
        self.dbUsername = info[3]
        self.dbPassword = info[4]

    # Connect to Data Management database via pyMongo
    def connectDB(self):
        from pymongo import MongoClient
        client = MongoClient(self.dbHostname, int(self.dbPortNum),
                             serverSelectionTimeoutMS=1000)
        if self.dbUsername != "" and self.dbPassword !="":
            client[self.dbName].authenticate(self.dbUsername, self.dbPassword)
        else:
            client[self.dbName]
        try:
            client.admin.command('ismaster')
            #print(" Server Available!")
            flag = True
        except:
            #print(" Server not available")
            flag = False
        return client, flag
