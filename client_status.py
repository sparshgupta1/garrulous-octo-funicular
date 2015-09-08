import os
import re
import sys


def GetMakeCommandStatus():
   
   ReturnCode = 1
   Message = ''
   if os.system("make -v") == 0:
      ReturnCode = 0
   else:
      Message = Message + "Error: unable to find &quot;make&quot; command in System Environment Path\n[*FAIL*]"
      ReturnCode = 1
   
   return(ReturnCode, Message)




def GetARBSSupportDir():
   
   ReturnCode = 1
   Message = ''
   
   if 'win32' == sys.platform:
      ARBSSupportsDir = "C:/ARBS_SUPPORT" 
   elif'linux2' == sys.platform:                                 # Linux
      ARBSSupportsDir = "/home/ARBS_SUPPORT" 
   elif 'darwin' == sys.platform:                                 # MAC 
      ARBSSupportsDir = "/Users/ARBS_SUPPORT"
      
   if os.path.exists(ARBSSupportsDir):
      ReturnCode = 0
   else:
      Message = Message + "Error: "+ ARBSSupportsDir +" Path Not Found\n[*FAIL*]"
      ReturnCode = 1
   
   if ReturnCode == 0:
      if (os.stat(ARBSSupportsDir).st_mode & 0555) != 0555:
         Message = Message + "<br>Error: Missing Execute and/or Read Permissions for some files in ARBS_SUPPORT Directory\n[*FAIL*]"
         ReturnCode = 1
      
   return(ReturnCode, Message)
      



def Get():
   ReturnStatus = 1
   Message = ''
   ReturnStatus1, Message1 = GetMakeCommandStatus()
   
   ReturnStatus2, Message2 = GetARBSSupportDir()
   
   if ReturnStatus1 == 0 and ReturnStatus2 == 0:
      ReturnStatus = 0
   else:
      ReturnStatus = 1
   
   Message = "<html>\n<head>\n<title>Setup Error Summary</title>\n</head>\n<body>\n\n"

   Message = Message + "<b>Build was NOT performed due to <i>Setup Issues</i> with ARBS Client Computer</b><br><br>\n"
   Message = Message + "<b><font face=Courier >Issues found:</b><br>\n"
   Message = Message + Message1 + "\n<br>" + Message2 + "\n</font>"
   Message = Message + "<br><br>Please refer the <i><a href=http://mchpweb-2010/tools/division/Quality/ISP%20Test%20Group/Shared%20Documents/Forms/AllItems.aspx>ARBS Quick Start Guide Document</a></i> for information about setting up the ARBS Client Computer<br>\n"
   Message = Message + "</html>\n"
   return (ReturnStatus, Message)
    