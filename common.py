import os
import re
import sys



def get_non_production_report_email_addresses():

   email_addresses = "shankar.ramasamy"   # arbs.developers
   return(email_addresses)
   
   
def get_database_name():
   database_address = "some_db"  # feed the develpment server's database access name.
   
   if get_jenkins_type() == "PRODUCTION":
      jenkins_cli_jar_file_name = "idc-ws-isparbs.mchp-main.com" 
   
   return(jenkins_cli_jar_file_name)
   
   
def get_jenkins_type():
   server_type = os.getenv('JENKINS_SERVER_TYPE', "PRODUCTION")
   return(server_type)
   
def get_cli_jar_file_name():
   jenkins_cli_jar_file_name = "some_file.jar"  # feed the develpment server's CLI file name.
   
   if get_jenkins_type() == "PRODUCTION":
      jenkins_cli_jar_file_name = "idc_ws_isparbs_hudson-cli.jar" 
   
   return(jenkins_cli_jar_file_name)

def get_jenkins_url():
   default_jenkins_url = "http://idc-lt-i14304.mchp-main.com:8080/"
   url = os.getenv('JENKINS_URL', default_jenkins_url)
   return(url)