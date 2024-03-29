# UWS-cli
Universal WiFi Switch - CLI

This small project is to check and control WiFi on ADSL/router boxes via a Command Line Interface.  
It is an implemantation of my other project [MOPPA](https://github.com/nogegon/moppa) in terms of software design.  

## Installation 
You need a working Python3 environment.  
In addition to standard libraries provided with your default Python3 installation, you need to install :
  - __Netifaces__ available [here](https://pypi.org/project/netifaces/) 
  - __Requests__ available [here](https://2.python-requests.org/en/master/) 
  
A computer (or a device able to execute Python3) connected to the same LAN as the Wifi Box you wish to control.  

## Usage
First, you need to identify the active routeur by typing the followig command:  
__python3 uws_cli.py -a identify__  

This will give you the ID of the dectected router. If nothing is detected, you'll get : __ERROR__  
You can add the __-d__ parameter to activate debug mode.  

Once you have the ID, you can perform different kind of operations :
  - Turn Wifi Off (__-a turnwifioff__)
  - Turn Wifi On (__-a turnwifion__)
  - Get the firmware version (__-a getfirmware__)
  - Check WiFi status (__-a checkwifi__)
 
Please note that you have to provide the ID of the router (__-ID ID__)  

Expected, but optional depending on your router model/configuration:  
  - The login (__-l login__) 
  - The password (__-p password__)


The final command will look like this:  
__python3 uws_cli.py -a checkwifi -l login -p password -id ID__

Finally, you can get information about the command line parameters by using :  
__python3 uws_cli.py -h__

## Plugins
Bouygues Telecom BBOX  
Function : ADSL router (French market)  
Firmware version : 17.2.16  
HTTP/HTTPS : HTTPS only  
ID : BT_BBOX  
SDK : [https://api.bbox.fr/doc/](https://api.bbox.fr/doc/)

## Disclaimer
I'm not a professionnal developper, doing all this just for fun.
