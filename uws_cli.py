# CLI for Universal WiFi Switch
#
#
# For input : Have a look at the Arguments construction
#
# For output :
#   ID : The ID of the router found
#   ID PARAMS : ID of the routeur + Indication that this specfic router will need parameters handling
#   ERROR : Something went wrong (use -d to troubleshoot)
#   NOK_ERROR : Error that should not happen. Please report. (use -d to troubleshoot)
#   OK : All went well
#   ON : Wifi is ON
#   OFF : Wifi is OFF
#   x.x.x : Firmware version
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

# Get the Gateway HTML Page and return it.
# Get Headers and HTTP status code
def get_gw_http_page():
    # They are going to be modified
    global my_gw_page_headers
    global my_gw_page_status
    global my_gw_protocol
    logging.debug('Starting get_gw_http_page...')
    # First let's try in HTTP
    try:
        r = my_session.get('http://' + my_gw_ip)
    except (requests.ConnectionError) as err:
        logging.error(err)
        logging.error('Problem getting gateway webpage in HTTP.')
        return ''
    logging.debug('Gateway web page in HTTP OK')
    my_gw_page_headers = r.headers
    my_gw_page_status = r.status_code
    my_gw_protocol = 'http://'
    logging.debug('Protocol set to HTTP')
    return r.text


# Get the Gateway HTML Page and return it.
# Get Headers and HTTP status code
def get_gw_https_page():
    # They are going to be modified if page is found in HTTPS
    global my_gw_page_headers
    global my_gw_page_status
    global my_gw_protocol
    logging.debug('Starting get_gw_https_page...')
    # Since it did not worked, let's try in HTTPS
    # In order to work, we are going to :
    # 1) Disable Warnings when connecting to a site with unverified HTTPS request            
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    #2) Add support for all cipher suites
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS='ALL'
    try:
        # 3) Not verify the certificate
        r = my_session.get('https://' + my_gw_ip, verify=False)
    except (requests.ConnectionError) as err:
        logging.error(err)
        logging.error('Problem getting gateway webpage in HTTPS.')
        return ''
    logging.debug('Gateway web page in HTTPS OK')
    my_gw_page_headers = r.headers
    my_gw_page_status = r.status_code
    my_gw_protocol = 'https://'
    logging.debug('Protocol set to HTTPS')
    return r.text


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
ap.add_argument('-pf', '--param_file', required=False, help='Specify filename to save/use Wifi parameters')
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
# Most of them will be accessed from the router/box Class
my_session = requests.Session()
wifirouter = None
my_gw_page_headers = None
my_gw_page_status = None
my_gw_protocol = None # HTTP or HTTPS ?
my_param_filename = None

# Perform different checks that do not need connection to the router
# Check if provided action is allowed
if args['action'] in ['identify','checkwifi', 'turnwifion', 'turnwifioff', 'getfirmware', 'dump_params']:
    logging.debug('Provided action : ' + str(args['action']))
else:
    logging.debug('Provided action is not recognized : ' + str(args['action']))
    print('ERROR')
    exit()

# Is the ID of the router provided for actions <> identify ?
if (args['action'] != 'identify') and (args['id'] == None):
    # If not, let's notify and exit
    logging.debug('No Router ID provided, please use -id ID parameter')
    print('ERROR')
    exit()

# Check that a filename is specified for action dump_params
if (args['action'] == 'dump_params') and (args['param_file'] == None):
    logging.debug('No params filename provided, please specify -pf filename')
    print('ERROR')
    exit()


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

# Checking if parameters filename was provided
if args['param_file'] != None:
    my_param_filename = args['param_file']
    logging.debug('Parameters filename : ' + my_param_filename)
else:
    my_param_filename = None
    logging.debug('Parameters filename provided')

# Getting the IP
my_ip = get_my_ip()
logging.debug('My IP is : ' + my_ip)

#Getting the IP of the gateway
#my_gw_ip = get_my_gw_ip()
my_gw_ip = '192.168.1.1'
logging.debug('My Gateway IP is : ' + my_gw_ip)


# Fetch the HTML page in HTTPS first
my_gw_page = get_gw_https_page()
if my_gw_page == '':
    # If nothing found, let's try in HTTP
    my_gw_page = get_gw_http_page()
    if my_gw_page == '':
        # If nothing found, there is a problem
        logging.debug('Could not fetch web page from gateway')
        exit()


# Execute identify() allows to :
#   instantiate wifirouter
#   get the ID of the active router
result = cli_identify()

# For actions : turnwifion and turnwifioff check if params file is needed ?
if (args['action'] in ['turnwifion','turnwifioff']) and (wifirouter.need_param() == True) and (my_param_filename == None):
    # If not, let's notify and exit
    logging.debug('For this router, Turn Wifi ON or Turn Wifi OFF need a parameters file. Please use -pf filename')
    print('ERROR')
    exit()

if (args['action']) == 'identify':
    # result = cli_identify()
    # Could not find a match
    if result == False:
        print('ERROR')
    # Found something
    elif result != '':
        if wifirouter.need_param():
            print(result + ' PARAMS')
        else:
            print(result)
    else:
        # Should not happen
        print('NOK_ERROR')
    # No other action to perform when doing identify, exiting
    exit()

# Checking the ID 
if result != args['id']:
    # The ID provided is not the same as the provided one
    logging.debug('Provided router ID is not matching detected router ID, please first use -a identify')
    print('ERROR')
    exit()

# Execute the login() because it is common to all actions handled below
result = wifirouter.login(my_session)
# Check result
if result != True:
    print('ERROR')
    exit()

# Handling dump_params actions
if (args['action']) == 'dump_params':
    # Dump parameters only when wifi is on
    if (wifirouter.checkwifi(my_session) == 'ON'): #and wifirouter.need_param():
        # Dumping parameters ok ?
        if wifirouter.dump_params(my_session):
            print('OK')
        else:
            print('ERROR')
    else:
        logging.debug('Wifi is OFF, please turn ON before dumping parameters')
        print('ERROR')
    # All done, exiting
    exit()

# Handling the checkwifi actions
if (args['action']) == 'checkwifi':
    result = wifirouter.checkwifi(my_session)
    if result == False:
        print('ERROR')
    if wifirouter.logout(my_session):
        print(result)
    else:
        print('ERROR')
    exit()

# Handling the getfirmware actions
if (args['action']) == 'getfirmware':
    result = wifirouter.getfirmware(my_session)
    if result == False:
        print('ERROR')
    if wifirouter.logout(my_session):
        print(result)
    else:
        print('ERROR')
    exit()

# Handling the turnwifiON actions
if (args['action']) == 'turnwifion':
    result = wifirouter.turnwifion(my_session)
    if result == False:
        print('ERROR')
    if wifirouter.logout(my_session):
        print('OK')
    else:
        print('ERROR')
    exit()

# Handling the turnwifiOFF actions
if (args['action']) == 'turnwifioff':
    result = wifirouter.turnwifioff(my_session)
    if result == False:
        print('ERROR')
    if wifirouter.logout(my_session):
        print('OK')
    else:
        print('ERROR')
    exit()