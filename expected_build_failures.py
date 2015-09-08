# from xlrd import open_workbook                              # Import xlrd module
import os
import re
import sys
import random
import time
import csv_reader

# Path of the excel sheet in svn as parameter 
XLSFileFound = 1
XLSheetLocation = ''
VerifiedByARBS = 0

var = 0   
LogFile = os.path.join(os.getcwd(),"LogFile.txt")           # Name of the Log File
TempLogFile = os.path.join(os.getcwd(),"TempLogFile.txt")   # Name of the temp Log File, Later this File will be remaned to LogFile.txt
HWTool = ''
for arg in sys.argv:                                        # receive the Parameters from Hudson
   var = var+1
   if 3 == var:
      XLSheetLocation = arg                                 # This is Excel Sheet Location
   if 2 == var:
      HWTool = arg                                          # Tool Name, in case of Run Time Test. "NA", in case of Build Test.

HWTool = HWTool.upper()
not_supp_apis = []                                          # array to store non supported api's
SupportedAPIList = []
UnSupportedAPIList = []
ExpectedErrorFromFile = []
ExpectedWarningFromFile = []

ErrorInfoFileExistingError = 0

if "NA" == HWTool:                                          # If HW tool supplied is NA, the proceed with Reading Non-Supported APIs from Excel Sheet.

   XLSFileFound = 0
   if XLSheetLocation.endswith(".csv"):
      if os.path.isfile(XLSheetLocation):                      # If Xls file is not found, print Error. Note that this is only, if the Supplied Tool Name is NA.
         XLSFileFound = 1
   #  Get the device from the log file

   LogFilePtr = open(LogFile,"r")
   DeviceInLogFile = ''



   if 1 == XLSFileFound:                                    # if xls file is found,

      for Line in LogFilePtr:
         if re.search("^Device : ",Line):                   # read the Device in the Log File.
            DeviceInLogFile = re.split("Device : ",Line)[1]
            DeviceInLogFile = DeviceInLogFile.rstrip("\n|\r")
            DeviceInLogFile = DeviceInLogFile.upper()
            DeviceInLogFile = re.sub(r"^DSPIC",'',DeviceInLogFile)  # Device Name Extracted.
            DeviceInLogFile = re.sub(r"^PIC",'',DeviceInLogFile)  # Device Name Extracted.
      LogFilePtr.close()

      # Device in log file will have the name of the device  

      SupportedAPIList,UnSupportedAPIList,ExpectedErrorFromFile,ExpectedWarningFromFile,ErrorInfoFileExistingError = csv_reader.GetAPIList(XLSheetLocation,DeviceInLogFile)
      not_supp_apis = UnSupportedAPIList
      
      '''
      book = open_workbook(XLSheetLocation) # Open the excel sheet
      sheet = book.sheet_by_index(0)                              # Open the first sheet

      no_of_devices = sheet.nrows                                 # no of devices (Rows in the first sheet)
      first_column = sheet.col_values(0)                          # Retrive the devices - in the first column of the excel sheet
      ColCount = 0
      RowCount = 0

      for device in first_column:                           # The First column of the xls file will be having Device names,
         ColCount = ColCount + 1
         device = device.lstrip("u")   
         device = device.upper()
         device = re.sub(r"^DSPIC",'',device)                 # Remove the dsPIC in the device names.
         device = re.sub(r"^PIC",'',device)                 # Remove the PIC in the device names.

         if device == DeviceInLogFile:                      # if the Device in xls column and the device in the log file is same, 
            RowValues = sheet.row_values(ColCount-1)        # extract the non supported API in the xls sheet.
            RowCount = 0
            for Value in RowValues:                         # Iterate through each row, in that column
               RowCount = RowCount + 1
               if re.search("n|N",Value):                   # If the row value is N, then append it in an array, leaving the leading and trailing spaces.
                  not_supp_apis.append(sheet.col_values(RowCount-1)[0].strip(" "))

      '''
   LogFilePtr.close()
   
   #print "\nUnsupported API List : \n"
   #for not_supp_api in not_supp_apis:
   #   print not_supp_api

ARBS_Build_Started_Tag = 0

ExitNow = 0

LogFilePtr = open(LogFile,"r")

for Line in LogFilePtr:

   if re.search("_VERIFIED_BY_ARBS_",Line):           # if the tag is already present, then stop doing again !!
      VerifiedByARBS = 1
      #exit()
   #if re.search("ARBS_INFO: ",Line):                        # The Key word: ARBS_INFO will be filled only by this script. 
   #   exit()                                         # If the Log file, already has the ARBS_INFO keyword, It might be filled by Run time Script, 
   if re.search("_ARBS_Build_Started_",Line):
      ARBS_Build_Started_Tag = 1
      
LogFilePtr.close()                                          # then Exit, without doing any operation on the Log file.

#############################################
#############################################
#############################################
if 0 == VerifiedByARBS:

   LogFilePtr = open(LogFile,"r")
   TempLogFilePtr = open(TempLogFile,"w")

   ErrorFromLogFile = ''

   LookForErrors = 0
   UnSupportedAPIFound = 0
   OtherFailure = 0
   PrintErrorMsg = 0
   OutPutFilesFound = 0
   MakeFileError = 0
   UndefinedAPIinPICCStyleFound = 0
   IgnoreThisLine = 0
   MakeFileExitStatus = 0
   ExpectedErrorFlag = 0
   UnExpectedErrorFlag = 0
   ExpectedWarningFlag = 0
   UnExpectedWarningFlag = 0
   RunTestError = 0
   APIFailureFlag = 0


   MakeFileName = []
   MakeFileExecutionStatus = []

   for Line in LogFilePtr:                                  # Iterate through each line in the log File, 

      if 1 == PrintErrorMsg: #If "Make File Execution End" is found in mae file, its time to print the ARBS_INFO: message.
         PrintErrorMsg = 0

         if 1 == OtherFailure:                            # If the Compiler messages are having errors, except only unsupported APIs
            Line = "ARBS_INFO: Build_Failure, Failed to invoke build\n" + Line
            MakeFileExecutionStatus.append("FAIL, Ubable to invoke build")

         elif 1 == MakeFileError:                             # If the Make File is having Errors
            Line = "ARBS_INFO: Build_Failure, Errors encountered in MakeFile\n" + Line
            MakeFileExecutionStatus.append("FAIL, Errors encountered in MakeFile")

         elif 1 == ErrorInfoFileExistingError:
            Line = "ARBS_INFO: Build_Failure, Arbitrary Error Information File not found\n" + Line
            MakeFileExecutionStatus.append("FAIL, Arbitrary Error Information File not found")

         elif 1 == UnExpectedErrorFlag:                            # Other errors occured to build, such as unknown compiler, no make files for the device, etc.,
            Line = "ARBS_INFO: Build_Failure, Unexpected Errors Found \n" + Line
            MakeFileExecutionStatus.append("FAIL, Unexpected Errors Found")

         elif 1 == APIFailureFlag:                            # Other errors occured to build, such as unknown compiler, no make files for the device, etc.,
            Line = "ARBS_INFO: Build_Failure, Failure due to Errors in API \n" + Line
            MakeFileExecutionStatus.append("FAIL, API Errors")

         elif 1 == UnExpectedWarningFlag and "NA" == HWTool:                            # Other errors occured to build, such as unknown compiler, no make files for the device, etc.,
            Line = "ARBS_INFO: Build_Failure, Unexpected Warnings Found \n" + Line      # Check for this warning, only in build test
            MakeFileExecutionStatus.append("FAIL, Unexpected Warnings Found")

         elif 1 == RunTestError:                            # RunTime Test Errors
            Line = "ARBS_INFO: Build_Failure, Failure Encountered while peforming Run time test, "+ ErrorFromLogFile.strip("\n") + "Test Failed\n" + Line
            MakeFileExecutionStatus.append("Build PASS, Run_Test FAIL")

         elif 1 == ExpectedErrorFlag:                            # UnExpected Errors
            Line = "ARBS_INFO: Build_Success, Failure is due to Specified, Expected Errors \n" + Line
            MakeFileExecutionStatus.append("PASS, with Specified Expected Errors")

         elif 1 == UnSupportedAPIFound:                     # Failure is due to un-supported API
            Line = "ARBS_INFO: Build_Success, Failure is due to Specified, Expected unsupported API\n" + Line
            MakeFileExecutionStatus.append("PASS, with Specified Unsupported API Errors")

         elif 1 == MakeFileExitStatus:                      # Any case will not come here. All the possible errors will be falling in any of the above catogories.
            Line = "ARBS_INFO: Build_Failure, Makefile execution exited with Errors\n" + Line
            MakeFileExecutionStatus.append("FAIL")

         elif 1 == ExpectedWarningFlag and "NA" == HWTool:                            # UnExpected Warnings, check for this, only in build test
            Line = "ARBS_INFO: Build_Success, Failure is due to Specified, Expected Warnings \n" + Line
            MakeFileExecutionStatus.append("PASS, with Specified Expected Warnings")

         elif 1 == OutPutFilesFound:                        # Success !
            Line = "ARBS_INFO: Build_Success\n" + Line 
            MakeFileExecutionStatus.append("PASS")

         else:                                              # Unknown reasons, but no output files found !!
            Line = "ARBS_INFO: Build_Failure\n" + Line

            MakeFileExecutionStatus.append("FAIL")


         #if XLSFileFound == 0 and ErrorFound == 1:

         #   Line = "Warning: Unable to find the Excel Sheet with list of un-supported APIs\nSkipping testing for Expected Build Failures\n" + Line

      if re.search("Files Info: Output Files Generated Successfully",Line):
         OutPutFilesFound = 1


      ########
      # Print
      ########
      if re.search("Make File Execution End",Line):
         PrintErrorMsg = 1

      ########
      # Stop
      ########
      if re.search("-End of Make File Messages-",Line):
         LookForErrors = 0

      # Make File Exit Status
      if re.search("Make command exit status: No Errors",Line):
         MakeFileExitStatus = 0

      if 1 == LookForErrors:# and HWTool == "NA":                         # if the HW tool is none, it means only build test happened. No need to check unsupported API while performing RT Test.

         ########
         # Case 1
         ########
         if re.search("no rule to make",Line,re.IGNORECASE) or re.search("missing separator",Line,re.IGNORECASE):
            MakeFileError = 1;

         ########
         # Case 2
         ########
         if re.search("undefined reference",Line,re.IGNORECASE):
            IgnoreThisLine = 1
            if [] == not_supp_apis:                                  # If unsupported API is none, then the error is other build error.
               APIFailureFlag = 1
            else:
               UnSupportedAPIFound = 0

               APIInLine = ''                                        # Extracting only the API name

               TempLine = Line
               TempLine = re.sub(r"\`|\'","ARBS_PLUS_CHAR",TempLine)
               APIInLine = re.sub("ARBS_PLUS_CHAR",'',re.findall("ARBS_PLUS_CHAR.*?ARBS_PLUS_CHAR",TempLine)[0])
               APIInLine = re.sub("^_",'',APIInLine)
               print "From Err Log " + APIInLine                     # For Debug purpose
               for UnSupportedAPI in not_supp_apis:                  # Iterate through the non-supported APIS, from CSV File
                  print "From xl Log " + "_IMP_" + UnSupportedAPI              # For Debug purpose
                  if ("_IMP_" + UnSupportedAPI == APIInLine) or ("IMP_" + UnSupportedAPI == APIInLine):                 # If any of the APIs found in the line, then mark and break the local loop
                     UnSupportedAPIFound = 1
                     print "Success"                                 # For Debug purpose
                     break

               if 0 == UnSupportedAPIFound:                          # If un supported API is not found, then, the error is something else.
                  APIFailureFlag = 1
                  print "Failure"                                    # For Debug purpose

         ###########
         # Case 2.1
         ###########
         # For PICC style Projects 
         if 1 == UndefinedAPIinPICCStyleFound:
            UndefinedAPIinPICCStyleFound = 0
            IgnoreThisLine = 1
            # Split the APIs into an array of other texts
            PICCStyleUnsupportedAPI = []
            TempArray = []

            TempArray = re.split("\t| ",re.sub("\(.*?\)",'',Line))
            for i in TempArray:
               if not '' == i:
                  print "Extracted APIs from Error Log " + i
                  PICCStyleUnsupportedAPI.append(i)

            if [] == not_supp_apis:
               APIFailureFlag = 1

            else:
               UnSupportedAPIFound = 0
               for UnSupportedAPI in not_supp_apis:                  # Iterate through the non-supported APIS from Excel Sheet, 
                  print "From Xl Log " + "_IMP_" + UnSupportedAPI 
                  for i in PICCStyleUnsupportedAPI:     
                     print "From Err Log " + i 
                     i = re.sub("^_",'',i)                           # Remove the underscore, if exists. This will make easy for comparison
                     if ("_IMP_" + UnSupportedAPI == i) or ("IMP_" + UnSupportedAPI == i):                 # If any of the APIs found in the line, then mark and break the local loop
                        UnSupportedAPIFound = 1                      # Break Inner Loop
                        print "Success"
                        break

                  if 1 == UnSupportedAPIFound:                       # This is for the outer loop !!
                     break 

               if 0 == UnSupportedAPIFound:                          # If un supported API is not found, then, the error is something else.
                  APIFailureFlag = 1
                  print "Failure"

         if re.search("error: undefined symbol:",Line,re.IGNORECASE):
            UndefinedAPIinPICCStyleFound = 1
            IgnoreThisLine = 1
         ########
         # Case 3
         ########

   # ExpectedErrorFromFile
   # ExpectedWarningFromFile

         if 0 == IgnoreThisLine:
            if re.search(r"error:|error \[",Line,re.IGNORECASE) and (not re.search("error: %",Line,re.IGNORECASE)):          

               if [] == ExpectedErrorFromFile:
                  UnExpectedErrorFlag = 1

               #elif not_supp_apis == []:                                  # If there is no un supported API for this device, then concider the Make Errors also.
               #   OtherFailure = 1

               else:                                                    # If there are un supported APIs, then ignore, errors returned by Make
                  if not re.search(r"make\[3\]:|make\[2\]:|make\[1\]:|make:",Line):      # Ignore the errors reported by MAKE !!, Added after taking advice from Manjunath:

                     ErrorExpected = 0

                     for ExpectedError in ExpectedErrorFromFile:
                        if re.search(ExpectedError,Line):
                           ErrorExpected = 1
                           break

                     if 1 == ErrorExpected:
                        ExpectedErrorFlag = 1           # Expected Error
                     else:
                        UnExpectedErrorFlag = 1              # Unexpected Error

            if re.search(r"warning:|warning \[",Line,re.IGNORECASE) and (not re.search("This make file contains OS dependent code.",Line)) and(not re.search("--chip=",Line)):

               if not re.search("ISP-IGNORE",Line.upper()):      # Added for suggession from Nidhi, Ref email - RE: ADC_Data_Logger Job Execution Status, dated 29 Sep 2011

                  if [] == ExpectedWarningFromFile:
                     UnExpectedWarningFlag = 1
                  else:

                     WarningExpected = 0

                     for ExpectedWarning in ExpectedWarningFromFile:
                        if re.search(ExpectedWarning,Line):
                           WarningExpected = 1

                     if 1 == WarningExpected:
                        ExpectedWarningFlag = 1              # Expected Warning
                     else:
                        UnExpectedWarningFlag = 1                 # Unexpected Warning

         else:
            IgnoreThisLine = 0


      #########
      # start
      ########
      if re.search("-Make File Messages-",Line):                           # This is the End Keyword, for starting scanning for errors.
         UnSupportedAPIFound = 0
         OtherFailure = 0
         PrintErrorMsg = 0
         OutPutFilesFound = 0
         MakeFileError = 0
         LookForErrors = 1
         IgnoreThisLine = 0
         UndefinedAPIinPICCStyleFound = 0
         MakeFileExitStatus = 1
         APIFailureFlag = 0
         ExpectedErrorFlag = 0
         UnExpectedErrorFlag = 0
         ExpectedWarningFlag = 0
         UnExpectedWarningFlag = 0
         RunTestError = 0

      #if re.search("Executing for Makefile: <NONE>",Line):                 # If the Log File has this keyword, then no build happened, then print Build Failure.   
      #   OtherFailure = 2

      # if error code is encountered, without the make file execution information, 

      if re.search("MDB_Error_Code: ",Line):
         RunTestError = 1
         ErrorFromLogFile = Line   

      if re.search("ARBS_Error_Code: ",Line):
         OtherFailure = 1
         ErrorFromLogFile = Line
         if re.search("ARBS_Error_Code: 00|ARBS_Error_Code: 01|ARBS_Error_Code: 02|ARBS_Error_Code: 03|ARBS_Error_Code: 04",Line):
            PrintErrorMsg = 1

      if re.search("Executing for Makefile: ",Line):
         i = re.split("Executing for Makefile: ",Line.strip("\n|\r"))[1]
         MakeFileName.append(i)

      TempLogFilePtr.write(Line)   


   LogFilePtr.close()
   TempLogFilePtr.close()

   try:                                         # Remove the original Make File
      os.remove(LogFile)
   except OSError, detail:
      if 2 != detail.errno:
         raise

   os.rename(TempLogFile,LogFile) # Rename the Temporary Make File to the name of the original make file.







   ### Added for displaying result in the make file name itself. 

   MaxLen = 0
   LogFilePtr = open(LogFile,"r")
   for Line in LogFilePtr:
      if re.search("Compatible MakeFile - ",Line):
         if (len(Line) > MaxLen):
            MaxLen = len(Line)
   LogFilePtr.close()

   InsertDash = ''

   MaxLen = MaxLen + 7

   LogFilePtr = open(LogFile,"r")
   TempLogFilePtr = open(TempLogFile,"w")

   for Line in LogFilePtr:

      MakeFileExecutionCount = 0                   # Reset Count for every Line !

      if re.search("Compatible MakeFile - ",Line):

         #################
         # Added for inserting number of dashes, so that, the result shall look aligned

         InsertDash = ('-' * (MaxLen - len(Line)))

         #################

         for MakeName in MakeFileName:
            if re.search(re.sub("\(|\)",'_',MakeName),re.sub("\(|\)",'_',Line)):
               Line = Line.strip("\n") + " " + InsertDash + " [" + MakeFileExecutionStatus[MakeFileExecutionCount] + "]\n"
            MakeFileExecutionCount = MakeFileExecutionCount + 1

      TempLogFilePtr.write(Line) 

   TempLogFilePtr.write("\n\n_VERIFIED_BY_ARBS_\n\n")

   LogFilePtr.close()
   TempLogFilePtr.close()

   try:                                         # Remove the original Make File
      os.remove(LogFile)
   except OSError, detail:
      if 2 != detail.errno:
         raise

   os.rename(TempLogFile,LogFile) # Rename the Temporary Make File to the name of the original make file.







            


   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   


   
