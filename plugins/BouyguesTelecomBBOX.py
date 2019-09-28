import sys
import socket
import requests
import logging
import __main__ # To access variables from Class invoker


class BouyguesTelecomBBOX(object):
    # Defining URL
    bbox_url = 'mabbox.bytel.fr'
    # Defining the IDs of this plugin
    long_ID = 'Bouygues Telecom BBOX'
    ID = 'BT_BBOX'
    
    # Identifies (or not) the Bouygues Telecom BBOX ADSL router
    def identify(self, session):
        logging.debug(self.long_ID + ':IDENTIFY:Started')
        try:
            socket.gethostbyname(self.bbox_url)
        except:
            logging.debug(self.long_ID + ':IDENTIFY:Not identified')
            return False
        logging.debug(self.long_ID + ':IDENTIFY:Identified !')
        #logging.debug('ID of the router is : ' + self.ID)
        return True

    # Indicates if this router needs parameters to change WiFi state        
    def need_param(self):
        logging.debug(self.long_ID + ':NEED_PARAM: False')
        return False

    # Login function
    def login(self,session):
        # Checking if password was provided
        if __main__.my_password == None:
            logging.error(self.long_ID + ':LOGIN:ERROR:Missing password')
            return False
        try:
            r = session.post('https://' + self.bbox_url + '/api/v1/login', data={'password':__main__.my_password})
        except (requests.ConnectionError):
            # Error on the session.post 
            logging.error(self.long_ID + ':LOGIN:ERROR:During session.post')
            return False
        # POST request went OK (HTTP code 200)
        if r.status_code == 200:
            logging.debug(self.long_ID + ':LOGIN:OK:Status code 200')
            return True
        # Something went wrong. Wrong password most probably
        else:
            logging.error(self.long_ID + ':LOGIN:ERROR:HTTP status code: ' + str(r.status_code))
            # Handling of some types of errors. When multiple wrong passwords for instance
            if r.headers['Content-Length'] != '0':
                json_decoded = r.json()
                logging.error(self.long_ID + ':LOGIN:ERROR:Reason: ' + json_decoded['exception']['errors'][0]['reason'])
            return False

    def logout(self, session):
        try:
            r = session.post('https://' + self.bbox_url + '/api/v1/logout')
        except (requests.ConnectionError) as err:
            logging.error(self.long_ID + ':LOGOUT:ERROR:On session.post')
            return False
        # POST request went OK (HTTP code 200)
        if r.status_code == 200:
            logging.debug(self.long_ID + ':LOGOUT:OK:Status code 200')
            return True
        else:
            # Something went wrong
            logging.error(self.long_ID + ':LOGOUT:ERROR:HTTP status code: ' + str(r.status_code))
            return False

    # Check the status of the WiFi
    def checkwifi(self, session):
        try: 
            r = session.get('https://' + self.bbox_url + '/api/v1/summary')
        except (requests.ConnectionError):
            logging.error(self.long_ID + ':CHECKWIFI:ERROR:On session.get')
            return False
        if r.status_code == 200:
            logging.debug(self.long_ID + ':CHECKWIFI:OK:Status code 200')
            try:
                json_decoded = r.json()
            except (ValueError):
                logging.error(self.long_ID + ':CHECKWIFI:ERROR:While decoding JSON')
                return False
            status_wifi = json_decoded[0]['wireless']['radio']
            if status_wifi == 1:
                logging.debug(self.long_ID + ':CHECKWIFI:WiFi is ON')
                return 'ON'
            elif status_wifi == 0:
                logging.debug(self.long_ID + ':CHECKWIFI:WiFi is OFF')
                return 'OFF'
            else:
                # Should not happen
                return False
        else:
            logging.error(self.long_ID + ':CHECKWIFI:ERROR:HTTP status code: ' + str(r.status_code))
            return False

    # Function to turn ON wifi
    def turnwifion(self,session):
        try:
            r = session.put('https://' + self.bbox_url + '/api/v1/wireless', data={'radio.enable': '1'})
        except (requests.ConnectionError):
            logging.error(self.long_ID + ':TURNWIFION:ERROR:On session.put')
            return False    
        if r.status_code == 200:
            logging.debug(self.long_ID + ':TURNWIFION:OK:HTTP status code 200 OK')
            return True
        else:
            logging.error(self.long_ID + ':TURNWIFION:ERROR:HTTP status code: ' + str(r.status_code))
            return False
        
    # Function to turn OFF wifi
    def turnwifioff(self,session):
        try:
            r = session.put('https://' + self.bbox_url + '/api/v1/wireless', data={'radio.enable': '0'})
        except (requests.ConnectionError):
            logging.error(self.long_ID + ':TURNWIFIOFF:ERROR:On session.put')
            return False
        if r.status_code == 200:
            logging.debug(self.long_ID + ':TURNWIFIOFF:OK:HTTP status code 200 OK')
            return True
        else:
            logging.error(self.long_ID + ':TURNWIFION:ERROR:HTTP status code: ' + str(r.status_code))
            return False
        
    # Get the firmware of the router
    # Working with firmware 17.2.16
    def getfirmware(self, session):
        try:
            r = session.get('https://' + self.bbox_url + '/api/v1/device')
        except (requests.ConnectionError):
            logging.error(self.long_ID + ':GETFIRMWARE:ERROR:On session.get')
            return False
        if r.status_code == 200:
            logging.debug(self.long_ID + ':GETFIRMWARE:OK:Status code 200')
            try:
                json_decoded = r.json()
            except (ValueError):
                logging.error(self.long_ID + ':GETFIRMWARE:ERROR:While decoding JSON')
                return False
            firmware = json_decoded[0]['device']['main']['version']
            logging.debug(self.long_ID + ':GETFIRMWARE:OK:Firmware version is: ' + firmware)
            return firmware
        else:
            logging.error(self.long_ID + ':GETFIRMWARE:ERROR:HTTP status code: ' + str(r.status_code))
            return False