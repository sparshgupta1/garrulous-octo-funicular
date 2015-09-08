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
import output_status

###########################################################################################
#####           Implemented for RunTime Test along with Hudson Parameters             #####
###########################################################################################

##############################################################
# This Module receives the mdb Location, and the batch file  #
# name, which calls the mdb,                                 #
# This Calls the mdb and waits for the specified timeout,    #
# and if the mdb still runs, it will be forced to terminate  #
# At the end of the termination, the mdb generated messages  #
# were analyzed to report the Proper error status and        #
# returned with the status code accordingly                  #
# Added for Ver 2.0                                          #
##############################################################

def ExecuteMDB(MDBLocation,MDBExecuteBatchFile,MDBReportLogFile,MDBHangingExitTimeOut,ProjectLocation):   # Receives the following parameters
                                                                                          # 1. Location of mdb
                                                                                          # 2. Batch File, which has the commands to execute the mdb and log the message
                                                                                          # 3. A File name, Logs the mdb generated Messages
                                                                                          # 4. mdb exit Timeout in seconds
   MDBHangError = 0
   LocationBeforeMDBRun = os.getcwd()                          # While running mdb, the CWD should be the place, where the mdb.bat is placed.
   
   os.chdir(MDBLocation)                                       # Change the Working Directory to the dir, where the mdb is.
  
   try:                                                        # try executing the mdb Batch File
      Process1 = subprocess.Popen(MDBExecuteBatchFile, shell=True, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   except:                                                     # If the mdb is used by another process, then this exception will be raised.
      os.chdir(LocationBeforeMDBRun)                           # Change the CWD to original and return with Error code
      arbs_print.Console("mdb is used by another process, so Exiting here\nError: Unable to perform RunTime test")
      arbs_print.LogFile("\nMDB is used by another process, so Exiting here\nError: Unable to perform RunTime test\nRunTest: FAIL\n" + ('-' * 44) +"\n\n")
      return(2)                                                # Error code corresponding to mdb Hang, before opening
      
   ExitTimeout = 0
   DisplayTimeout = 0
   MDBLogFileLineCount = 0
   PrevMDBLogFileLineCount = 0
   time.sleep(2)
   while(Process1.poll() == None):                             # If the mdb is Opened and started execution successfully, poll for the process's existance
                                                               # if the process (mdb) is still running, Enter here.
      ExitTimeout = ExitTimeout + 1                            # Usually the mdb will exit before Timeout of 20 seconds
      DisplayTimeout = DisplayTimeout + 1
                                                               # If the mdb is updating the mdbLogFile, then mdb is alive, so, reset the Timeout counter
      CopyMDBLogFile = MDBReportLogFile + "Copy"               # Copy the Log file as MDBlogfile.txtCopy
      shutil.copyfile(MDBReportLogFile,CopyMDBLogFile)         # Copy it in the same folder,
      CopyMDBLogFilePtr = open(CopyMDBLogFile,"r")             # Open it in Read Mode, to read the number of Line
      MDBLogFileLineCount = 0
      for Line in CopyMDBLogFilePtr:
         MDBLogFileLineCount = MDBLogFileLineCount + 1         # Count the number of Lines in the log file
      CopyMDBLogFilePtr.close()
      time.sleep(0.1)
      os.remove(CopyMDBLogFile)
      
      if PrevMDBLogFileLineCount < MDBLogFileLineCount:        # If the Log file is updated than previous one, then reset exit timeout counter
         PrevMDBLogFileLineCount = MDBLogFileLineCount
         ExitTimeout = 0
      
      if (ExitTimeout >= MDBHangingExitTimeOut):               # Check for the timeout. if time is expired, then report Error
         arbs_print.Console("mdb Hang detected\n")                   
         arbs_print.Console("Executing Force Quit on mdb")           # Print Debug Messages !
         MDBHangError = 1
         os.popen("taskkill /PID " + str(Process1.pid) + " /F /T")   # Execute Force Quit on mdb ! :) No other way to Quit. Even subprocess.kill Fails, subprocess.terminate too ! :)
                                                                     # Need to Fight with mdb Developers ! :)
      time.sleep(1)                                                  # Thats why the command Task Kill is used ! 
   
   os.chdir(LocationBeforeMDBRun)                              # Before the sub routine exits, change the working directory and return the values, based on 
                                                               # Comes out, only if the mdb is exited Successfuly. So, this loop will continue till the mdb exists.
                                                               # This is for Safety Measure !
   if 1 == MDBHangError:                                       # This Flag tells, whether the mdb is exited normally or is it Quited 
      arbs_print.LogFile("mdb Hang detected, Exiting Runtime Test\n" + ('-' * 44))
      arbs_print.Console("mdb Hang detected, Exiting Runtime Test\nRunTest: FAIL\n" + ('-' * 44))
      
   arbs_print.Console("\n\nMDB exited in " + str(DisplayTimeout) + " Seconds\n")  # Tell user that mdb exited in how many Seconds
                                                                     # This will tell even though, the Force Quit is executed on mdb
   MDBLogFilePtr = open(MDBReportLogFile,"r")                        # Open the File, contains the mdb Messages 
   
   ProgrammingFailed = 1                                       # Flags to decide the status of the Execution
   TestCasePass = 0
   PrintNextLine = 0
   
   SymbolNotFound = 0
   ErrorCountValue = 0
   
   for Line in MDBLogFilePtr:                                  # Iterate through Lines and decide what could have happened
      if 1 == PrintNextLine:                                   # If the Line has "Symbol not found in scope", then print the Next Line, 
         arbs_print.Console(Line)                                    # which will have some information about the simbol monitored. Look at the mdb Error Log
         PrintNextLine = 0
      if re.search("^Program sucessed",Line):                  # If this Keyword is found, then the programming is successful. otherwise , programming failed 
         ProgrammingFailed = 0
      elif (re.search("^ErrorCount=0x00\n",Line) or re.search("^ErrorCount=0x0000\n",Line) or re.search("^ErrorCount=0x00000000\n",Line)) and ProgrammingFailed == 0:  # If the Programming is success and the Error Count reads 0x00, then the Test Case is Pass
         TestCasePass = 1                                                  # Print the Line.
      elif re.search("Symbol not found in scope",Line):        # If the error Count Variable is not there in the Code, then Error.
         PrintNextLine = 1 
         SymbolNotFound = 1
         TestCasePass = 0
      if re.search("^ErrorCount=0x",Line):
         arbs_print.Console(Line)
         arbs_print.LogFile(Line)         
   MDBLogFilePtr.close()

   #############################################
   #############################################
   # Added to display the Failed Test case
   # in the log File
   MDBRefFile = "MDB_Reference_"
   MDBRefFileFound = 0
   ErrorIndex = ''
   

   MDBLogFilePtr = open(MDBReportLogFile,"r")
   for Line in MDBLogFilePtr:
      Line = Line.strip("\n|\r")
      if re.search("ErrorIndex=",Line):
         ErrorIndex = re.split("=",Line)[1]
         
      if re.search("MDBReferenceFileIndex=",Line):
         Val = re.split("=",Line)[1]
         Val = hex(eval(Val))
         Val = re.sub("0x",'',Val)
         MDBRefFile = MDBRefFile + Val + ".txt"
         break
         
   MDBLogFilePtr.close()
   
   MDBRefFilePath = os.path.split(ProjectLocation)[0]
   MDBRefFilePath = os.path.join(MDBRefFilePath, "MDB_Ref")
   MDBRefFile = os.path.join(MDBRefFilePath, MDBRefFile)
   
   if os.path.exists(MDBRefFile):
      if not ErrorIndex == '':
         ErrorIndex = re.sub(r"\\u",'',ErrorIndex)
         ErrorIndex = re.sub("0x",'',ErrorIndex)
         ErrorIndex = re.sub("\"",'',ErrorIndex)
         arbs_print.LogFile("\n") 
         for i in range(len(ErrorIndex)):
            if ErrorIndex[i] == "1":
               MDBRefFilePtr = open(MDBRefFile,"r")
               
               for Line in MDBRefFilePtr:
                  Line = Line.strip("\n|\r")
                  SearchString = "ErrorIndex: " + str(i)
                  if re.search(SearchString, Line):
                     Msg = "Failed" + ((re.split(",",Line)[1]).strip(" "))
                     arbs_print.LogFile(Msg) 
                     arbs_print.Console(Msg)
               
               MDBRefFilePtr.close()
               
         arbs_print.LogFile("\n")           
      
   #############################################
   #############################################
   
                                                               # test execution Status !
   if 1 == ProgrammingFailed:
      return(5)                                                # Programming Failed had Return code of 5
   if 1 == SymbolNotFound:
      return(3)                                                # Error_Count Not found has error code of 3
   if 1 == MDBHangError:
      return(4)                                                # mdb Hang returns 4
   if 1 == TestCasePass:
      return(0)                                                # Error_Count = 0, Pass returns 0.
   else:
      return(6)                                                # Error_Count != 0, then Test Case Failed, so, return with 6.

   '''if TestCasePass == 1:
      arbs_print.Console("RunTest: PASS")
      arbs_print.LogFile("RunTest: PASS\n--------------------------------------------\n\n")
   else:
      arbs_print.Console("RunTest: FAIL")
      arbs_print.LogFile("RunTest: FAIL\n--------------------------------------------\n\n")
   '''
   
   return(0xFF)                                                   # Dummy Line, the code will reach here never.





###########################################################
#### Module for creating Command.txt file for mdb execution
#### This validates the supplied Hardware tool and creates
#### the appropriate tool name in the command.txt file.
#### In V2.0, support for PLIB tests only is implemented
#### While running mdb, the mdb looks for a variable 
#### "ErrorCount" and prints the value.
###########################################################

def CreateMDBCommandFile(MDBCommandFile, Device, CofFile, InTool):
   
   MDBCommandFilePtr = open(MDBCommandFile,"w")
   
   if "SIM" == InTool:                                            # validates Tool here
      InTool = "SIM"                                              # As of release date of V2.0 of this script, 
   elif "REALICE" == InTool:                                      # mdb supports only three tools, SIM, RealICE and ICD3. 
      InTool = "RealICE"                                          # This validation of tool name will be updated, upon successive releases of mdb.
   elif "ICD3" == InTool:
      InTool = "ICD3"
   else:
      return(1)                                                   # Invalid Tool, return with Error.
   
   InCofFile = CofFile                                            # Get the COF file and the device Name
   InDevice = Device
   
   InCofFile = re.sub(r"/",r"\\\\",InCofFile)                     # Edit the path format of the Cof File which is accepted by mdb. 
   #InCofFile = re.sub(r" ",r"\\ ",InCofFile)                     # Remember this is only for Win XP, for other OS, No support for mdb is available.
   InCofFile = re.sub(r"(?<=[a-zA-Z0-9:])\\(?=[a-zA-Z0-9])",r"\\\\",InCofFile)

   MDBCommandFilePtr.write("# Commands File for PLIB Run Time test for ARBS\n# Warning: This file is generated by Script, editing this file may cause mdb non-functional !!!\n\n")
   MDBCommandFilePtr.write("Device " + InDevice + "\n")
   MDBCommandFilePtr.write("Hwtool " + InTool + "\n")
   MDBCommandFilePtr.write("Set programoptions.eraseb4program true\n\n")
   MDBCommandFilePtr.write("Program " + '"' + InCofFile + '"' + "\n\n")
   MDBCommandFilePtr.write("run\n")
   MDBCommandFilePtr.write("sleep 5000\n")
   MDBCommandFilePtr.write("halt\n\n")
   MDBCommandFilePtr.write("print /x ErrorCount\n")
   MDBCommandFilePtr.write("print /a ErrorCount\n\n")
   MDBCommandFilePtr.write("print /x ErrorIndex\n")
   MDBCommandFilePtr.write("print /a ErrorIndex\n\n")
   MDBCommandFilePtr.write("print /x MDBReferenceFileIndex\n")
   MDBCommandFilePtr.write("sleep 500\n")
   MDBCommandFilePtr.write("quit")

   MDBCommandFilePtr.close()
   
   return(0)                                                      # After updating the Commands.txt file, return with no error.
   
   
   
   
   
   
###########################################################
#### This Module creates the command.txt file and it invokes
#### the mdb and logs the mdb messages and analyzes it and 
#### reports the appropriate execution status to the main
#### Routene.
#### Here has the Path of mdb core and the Time out
#### for mdb to exit.
###########################################################   

def PerformDebugOperation(InDevice,DebugFile,DebugTool,ProjectLocation):

   
   MDBLocation = "E:/MDB_ARBS"                                    # Path, where the mdb is located in Windows Slave Computer
   
   MDBError = 0
 
   MDBHangingExitTimeOut = 25                                     # Timeout for the mdb execution is 25 Seconds. Need to update this.

   InCofFile = DebugFile
   
   if not os.path.isfile(InCofFile):                              # In case, if the Cof file is not found in the specified directory, then
      MDBError = 1                                                # return with appropriate error
      arbs_print.Console("Error ! unable to find debug File")
      arbs_print.LogFile("Error ! unable to find debug File")
      return(1)
      
   if 0 == MDBError:                                              # If coff file is found and no error, proceed further
      InDevice = InDevice.upper()                                 # keep the appropriate device name, which mdb can take.
      if re.search("^[PIC|DSPIC]", InDevice):
         InDevice = re.sub(r"DSPIC","dsPIC",InDevice)
      else:
         if re.search("^30|33",InDevice):
            InDevice = InDevice.upper()
            InDevice = "dsPIC" + InDevice
         else:
            InDevice = InDevice.upper()
            InDevice = "PIC" + InDevice

      MDBExecuteBatchFile = os.path.join(MDBLocation,"Exec_MDB.bat") # Create a batch file for executing mdb and logging messages

      MDBReportLogFile = os.path.join(MDBLocation,"MDBLog.txt")   # Name of the file, where mdb logs its Output messages
   
      MDBCommandFile = os.path.join(MDBLocation,"command.txt")    # mdb commands File

      FileCreationError = CreateMDBCommandFile(MDBCommandFile, InDevice, InCofFile, DebugTool)  # This module creates the Commands File. This module also validates the supplied tool name.
      if 1 == FileCreationError:                                  # If the supplied tool is erronious, then return with tool name error
         return(7)
      elif 0 != FileCreationError:
         return(2)                                                # else, if some other error, report it to main as unknown file creation error !
      
      MDBExecuteBatchFilePtr = open(MDBExecuteBatchFile,"w")      # Create the Batch File with appropriate commands to execute the mdb and log the mdb messages.

      MDBExecuteBatchFilePtr.write("echo mdb report as follows > " + '"' + re.sub(r'/',r'\\',MDBReportLogFile) + '"' + "\n" + '"' + os.path.join(re.sub(r'/',r'\\',MDBLocation),"mdb.bat") + '"' + " >> " + '"' + re.sub(r'/',r'\\',MDBReportLogFile) + '"' + "2>&1\n")

      MDBExecuteBatchFilePtr.close()

      try:                                         # Remove the existing Report File
         os.remove(MDBReportLogFile)
      except OSError, detail:
         if 2 != detail.errno:
            raise

      return(ExecuteMDB(MDBLocation,MDBExecuteBatchFile,MDBReportLogFile,MDBHangingExitTimeOut,ProjectLocation))   # Execute mdb and return the state of execution



###########################################################
#### This Module Prints the mdb Status, based on the ,
#### Error Code, returned by the mdb Executor.
###########################################################

def DisplayMDBExecutionStatus(ErrorCode,MDBError):    # Error Code will be 11 for mdb based Errors

   output_status.Msg(ErrorCode, MDBError)
      
###########################################################################################
###########################################################################################
####End of Implementation for RunTime Test along with Hudson#####
###########################################################################################
###########################################################################################

