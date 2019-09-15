# CLI for Universal WiFi Switch
#
#
# For input : Have a look at the Arguments construction
#
# For output :
#   ERROR : Something went wrong (use -d to troubleshoot)
#   NOK_ERROR : Error that should not happen. Please report. (use -d to troubleshoot)
#   OK : All went well
#   ON : Wifi is ON
#   OFF : Wifi is OFF
#
# 
#

import sys
import requests # to start the session from here. Has to be installed in addition to Python
import logging
import time
import argparse # To handle the command line. No installation required
import os
import importlib


# All functions are in this section

def cli_identify():
    global wifirouter
    class_path = 'plugins'
    my_path = os.path.abspath(__file__)
    my_path = my_path[0:my_path.find(__file__)]
    my_path += class_path + '/'
    for module in os.listdir(my_path):
        if module == '__init__.py' or module[-3:] != '.py':
            # Skipping
            continue
        new_module = importlib.import_module(class_path + '.' + module[:-3])
        my_method = getattr(new_module, module[:-3])
        wifirouter = my_method()
        if wifirouter.identify(my_session):
            return wifirouter.ID
    return False
# Get the IP and return it
def get_my_ip():
    import socket
    return socket.gethostbyname(socket.gethostname())

# Get the IP of the Gateway with NETIFACES and return it
def get_my_gw_ip():
    import netifaces # Has to be installed in addition to Python
    gws = netifaces.gateways()
    return gws['default'][netifaces.AF_INET][0]


# Construct the argument parser
ap = argparse.ArgumentParser()

# Defining all the parser logic
# Login is not required for 2 reasons : 1)Some routeur/ADSL box does not require a login. 2)User can execute identify action without providing login/password 
ap.add_argument('-l', '--login', required=False, help='Routeur login')
# Password is not required to allow user to execute identify action without providing login/password
ap.add_argument('-p', '--password', required=False, help='Routeur password')
ap.add_argument('-a', '--action', required=True, help='Possible values are : identify, checkwifi, turnwifion, turnwifioff, getfirmware')
ap.add_argument('-id', '--id', required=False, help='Routeur ID, needed for all actions except identify')
ap.add_argument('-d', '--debug', required=False, help='Activates DEBUG logging', action='store_true')
args = vars(ap.parse_args())

# First let's check if the debug logging has been requested
if args['debug'] :
    # Setting logging to DEBUG level
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    logging.debug('DEBUG logging level activated')
else:
    # Disable logging
    logging.disable(sys.maxsize)

# Initializing & Defining global variables 
# Some of them will be accessed from the router/box Class
my_session = requests.Session()
wifirouter = None

# Checking if login was provided
if args['login'] != None:
    my_login = args['login']
    logging.debug('My Login is : ' + my_login)
else:
    my_login = None
    logging.debug('No login provided')

# Checking if password was provided
if args['password'] != None:
    my_password = args['password']
    logging.debug('My Password is : ' + my_password)
else:
    my_password = None
    logging.debug('No password provided')

my_ip = get_my_ip()
logging.debug('My IP is : ' + my_ip)

my_gw_ip = get_my_gw_ip()
logging.debug('My Gateway IP is : ' + my_gw_ip)


# Check if provided action is allowed
if args['action'] in ['identify','checkwifi', 'turnwifion', 'turnwifioff', 'getfirmware']:
    logging.debug('Provided action : ' + str(args['action']))
else:
    logging.debug('Provided action is not recognized : ' + str(args['action']))
    print('ERROR')
    exit()

if (args['action']) == 'identify':
    logging.debug('Executing identify action')
    result = cli_identify()
    # Could not find a match
    if result == False:
        print('ERROR')
    # Found something
    elif result != '':
        print(result)
    else:
        # Should not happen
        print('NOK_ERROR')
    exit()

# Is the ID of the router provided ?
if args['id'] == None:
    # If not, let's notify and exit
    logging.debug('No Router ID provided, please use -id ID parameter')
    print('ERROR')
    exit()

# Execute identify() allows to :
#   instantiate wifirouter
#   get the ID of the active router
result = cli_identify()
# Checking the ID 
if result != args['id']:
    # The ID provided is not the same as the provided one
    logging.debug('Provided router ID is not matching detected router ID, please use -a identify first')
    print('ERROR')
    exit()

# Execute the login() because it is common to all actions handled below
result = wifirouter.login(my_session)
# Check result
if result != True:
    print('ERROR')
    exit()

# Handling the checkwifi actions
if (args['action']) == 'checkwifi':
    result = wifirouter.checkwifi(my_session)
    if result == False:
        print('ERROR')
        exit()
    if wifirouter.logout(my_session):
        print(result)
    else:
        print('ERROR')

# Handling the getfirmware actions
if (args['action']) == 'getfirmware':
    result = wifirouter.getfirmware(my_session)
    if result == False:
        print('ERROR')
        exit()
    if wifirouter.logout(my_session):
        print(result)
    else:
        print('ERROR')

# Handling the turnwifiON actions
if (args['action']) == 'turnwifion':
    result = wifirouter.turnwifion(my_session)
    if result == False:
        print('ERROR')
        exit()
    if wifirouter.logout(my_session):
        print('OK')
    else:
        print('ERROR')

# Handling the turnwifiOFF actions
if (args['action']) == 'turnwifioff':
    result = wifirouter.turnwifioff(my_session)
    if result == False:
        print('ERROR')
        exit()
    if wifirouter.logout(my_session):
        print('OK')
    else:
        print('ERROR')