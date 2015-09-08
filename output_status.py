import os            # For Operating System related operations
import re            # For Regular Expressions and String Management Operations
import sys           # For Calling System Variables and call system commands and passed arguments
import datetime      # For Getting Date and Time information from OS
import shutil        # For Performing operations on Directories
import stat          # For Reading/Changing Permissions for Directories.
import errno
import zipfile       # For Zip Engine
import subprocess    # For mdb, to run as a parallel process
import time          # Timer for waiting
import arbs_print


def PrintErr(ErrorCode,Text):
   arbs_print.Console(ErrorCode)
   # arbs_print.LogFile("No Make Files Found Compatible \n--------------------------------------------\n")
   # arbs_print.LogFile("\nExecuting for Makefile: <NONE>\n")
   ErrLogFilePtr = open(os.path.join(os.getcwd(),"error_messages.info"),'r')
   
   for Line in ErrLogFilePtr:
      if re.search('^' + ErrorCode,Line):
         j = ''
         for i in Line:
            if '`' == i:                        # if a newline needs to be printed, give a "`"
               arbs_print.LogFile(Text + j)
               Text = ''
               j = ''
            else:
               j = j + i
            
         arbs_print.LogFile(Text + j)
         break
   
   ErrLogFilePtr.close()
   
   #arbs_print.LogFile("\nMake File Execution End")   

#################################################################
#### Prints the Message either in the Console or in the  
#### LogFile.
#### The Messages depend upon the the 'Error' and the (Stages of
#### execution) - 'ErrorCodeCount'
#################################################################  
   
def Msg(ErrorCodeCount,Error):
   
   Text = ''
   
   if 11 == ErrorCodeCount:
      Text = "mdb"
   else:
      Text = "ARBS"
      
      
   if 0 == Error:
      Text = Text + "_Exit_Code "   
   else:
      Text = Text + "_Error_Code: "
   
   ErrorCode = (ErrorCodeCount * 100) + Error

   #if ErrorCodeCount >= 5:

   # arbs_print.LogFile("\n")

   if ErrorCode <= 999:
      PrintErr('0' + str((ErrorCodeCount * 100) + Error),Text)
   else:
      PrintErr(str((ErrorCodeCount * 100) + Error),Text)
         
         
   #if Error != 0:
   #   PrintErr(str((ErrorCodeCount * 100) + Error))
   
   '''
   if ErrorCodeCount == 1:
      
      if Error == 0:
         arbs_print.Console("Passed Level 01, Received Parameters from Hudson")
      elif Error == 1:                                                                         # Updated in Version 1.2
         #arbs_print.Console("ARBS_INFO: Build_Failure, ARBS Error: Code 01.01: Invalid number of parameters received to execute the job !")
         #arbs_print.LogFile("Not Enough parameters to execute the job ")
         PrintEnd(0101)
      elif Error == 2:
         #arbs_print.Console("ARBS_INFO: Build_Failure, ARBS Error: Code 01.02: Invalid Compiler Name Supplied")
         #arbs_print.LogFile("ARBS Error Code 01.02: Invalid Compiler Name Supplied")   
         PrintEnd(0102)
         
      elif Error == 3:
         #arbs_print.Console("ARBS_INFO: Build_Failure, ARBS Error: Code 01.03: No Support for C18 Compiler")
         #arbs_print.LogFile("ARBS Error Code 01.03: No Support for C18 Compiler")           
         PrintEnd(0103)
         
   if ErrorCodeCount == 2:
      if Error == 0:
         arbs_print.Console("Passed Level 02, Found Project Directory")
      else:
         #arbs_print.Console("ARBS_INFO: Build_Failure, ARBS Error: Code 02: MPLAB X Project Location not Found !")
         PrintEnd(0201)

   if ErrorCodeCount == 3:
      if Error == 0:
         #arbs_print.LogFile("Finding Make Files")
         arbs_print.Console("Passed Level 03, Finding Make Files")
      else:
         #arbs_print.LogFile("Make Files not Found ")
         #arbs_print.Console("ARBS_INFO: Build_Failure, ARBS Error: Code 03: Make Files not Found !")
         PrintEnd(0301)
   if ErrorCodeCount == 4:
      if Error == 0:
         #arbs_print.LogFile("Finding Compatible Make Files")
         arbs_print.Console("Passed Level 04, Finding Compatible Make Files")
      else:
         #arbs_print.LogFile("No Make Files Found Compatible \n--------------------------------------------\n")
         #arbs_print.LogFile("\nExecuting for Makefile: <NONE>\n")
         #arbs_print.LogFile("ARBS_INFO: Build_Failure, \nARBS Error: Code 04: No Make Files Found Compatible !")
         #arbs_print.LogFile("\nMake File Execution End")
         PrintEnd(0401)

   if ErrorCodeCount == 5:

      if Error == 0:
         arbs_print.Console("Passed Level 05, Replacing Device in the Make File")
         arbs_print.Console("Passed Level 06, Make File Execution Success")
      elif Error == 1:
         PrintEnd(0501)
         #arbs_print.Console("ARBS_INFO: Build_Failure, ARBS Error Code 05: Unable to find MakeFiles for Execution")
         #arbs_print.LogFile("\nARBS Error: Code 05.01: Unable to find MakeFiles for Execution ")
      elif Error == 2:
         PrintEnd(0502)
         #arbs_print.Console("ARBS_INFO: Build_Failure, ARBS Error Code 05.02: Unable to find Compiler Path References File !")
         #arbs_print.LogFile("\nARBS Error: Code 05.02: Unable to find Compiler Path References File ")
      elif Error == 3:
         PrintEnd(0503)
         #arbs_print.Console("ARBS_INFO: Build_Failure, ARBS Error Code 05.03: Unable to find compiler paths in the Compiler path references file !")
         #arbs_print.LogFile("\nARBS Error: Code 05.03: Unable to find compiler paths in the Compiler path references file ")
      elif Error == 4:
         PrintEnd(0504)
         #arbs_print.Console("ARBS_INFO: Build_Failure, ARBS Error Code 05.04: Incompatible Compiler for compiling the device")
         #arbs_print.LogFile("\nARBS Error: Code 05.04: Incompatible Compiler for compiling the device")


   '''
   