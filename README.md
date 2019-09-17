# uws-cli
Universal WiFi Switch - CLI


This small project is to check and control wifi on ADSL/router boxes via a Command Line Interface.
It is an implemantation of my other project (MOPPA) in terms of software design.

Installation 
You need a working Python3 environment.
In addition to standard libraries, you need to install :
  Netifaces
  Requests
  
A computer connected to the same LAN as the Wifi Box you wish to control.  

Usage
First, you need to identify the active routeur.
python3 uws_cli.py -a identify

This will give you the ID of the dectected router. If nothing is detected, you'll get : ERROR
You can add the -d parameter to activate debug mode.

Once you have the ID, you can perform different kind of operations :
  Turn Wifi Off (-a turnwifioff)
  Turn Wifi On (-a turnwifion)
  Get the firmware version (-a getfirmware)
  Check WiFi status (-a checkwifi)
  
Please note that you have to provide also : 
  The ID of the router (-ID ID) 
  The login (-l login) [But not alwaysn, the Bouygues Telecom BBOX doesn't need it]
  The password (-p password)

The final command will be something like : 
python3 uws_cli.py -a checkwifi -l login -p password -id ID

Finally, you can get information about the command line parameters by using :
python3 uws_cli.py -h

Plugins
Bouygues Telecom BBOX
Firmware version : 17.2.16
HTTP/HTTPS : HTTPS only
ID : BT_BBOX
SDK : 

Disclaimer
I'm not a professionnal developper, doing all this for fun.
