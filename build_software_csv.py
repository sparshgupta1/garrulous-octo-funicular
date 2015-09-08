import os
import sys
import re
import shutil        # For Performing operations on Directories
import subprocess
import time
import random
import client_status


def CreateDrive(Location, StartDriveLetter):

   ReceivedStartDriveLetter = StartDriveLetter

   Error = 0
   VirtualDriveName = ''
   DriveTemp = ''
   VirtualDriveNameFound = 0
   DriveMappingWaitCount = 0
   DriveSuccessfullyMapped = 0
   DriveMappingError = 0
   
   
   if not ('win32' == sys.platform):
      return(Location)
   
   Location = Location.lower()
   
   while(DriveSuccessfullyMapped == 0):

      while(VirtualDriveNameFound == 0):                        # CAUTION !!! Code may hang here, if no drive is available for mapping. Code waits, till a drive is available.

         RandomTimeDelay = random.randint(random.randint(1,10),random.randint(11,20))  # To Increase the Random number's randomability
         time.sleep(RandomTimeDelay/10)
         DriveTemp = str(StartDriveLetter) + ":"
         print ("Waiting for " + str(RandomTimeDelay) + "Sec, for next poll")
         print ("Finding availability of " + DriveTemp)
         if os.path.isdir(DriveTemp):
            DriveMappingWaitCount = 0
            print (DriveTemp + " already exists !\n")
            
            StartDriveLetter = chr(ord(StartDriveLetter) + 1)
            if "Z" == StartDriveLetter:               # If Z Drive is added, Roll back to "H"
               StartDriveLetter = ReceivedStartDriveLetter
               time.sleep(random.randint(1,10))
            
         else:
            VirtualDriveName = str(StartDriveLetter) + ":"
            DriveMappingWaitCount = DriveMappingWaitCount + 1
            if DriveMappingWaitCount >= random.randint(11,20):            # Reasonable Count !, Need to check, if fails drive mismatch occurs !!
               VirtualDriveNameFound = 1

      PathForVirtualDriveCreation = Location
      
      VirtualDriveCreateCommand = ("subst " + VirtualDriveName + " " + '"' + PathForVirtualDriveCreation + '"' + " > Temp_Log.txt")
      
      os.system(VirtualDriveCreateCommand)
      
      TempLogFilePtr = open(os.path.join(os.getcwd(),"Temp_Log.txt"),'r')

      DriveMappingError = 0

      for Line in TempLogFilePtr:
         if re.search("Drive already SUBSTed",Line) or re.search("Invalid parameter",Line):
            DriveMappingError = 1
            VirtualDriveNameFound = 0
            DriveMappingWaitCount = 0

      TempLogFilePtr.close()

      if 0 == DriveMappingError:
         DriveSuccessfullyMapped = 1
         print (DriveTemp + " is found mappable, using this drive for build")

   
   '''
   DriveNameWithFirstDir = re.sub(r"\\",r"\\\\",DriveNameWithFirstDir)

   TempLocation = re.split(DriveNameWithFirstDir,Location)[1]
   TempLocation = TempLocation.strip(r"\\")
   '''
   
   os.remove(os.path.join(os.getcwd(),"Temp_Log.txt"))

   
   return(VirtualDriveName)
   
   
def ModifyToWritePermission(func, path, exc_info):             # Modify the Files and Directories to Write Mode
    import stat
    if not os.access(path, os.W_OK):                           # Is the error an access error ?
      os.chmod(path, 0777)
      func(path)                                               # Recrussive change of mode of all the Files
    else:
      raise
      
def CheckoutEngine(SVNLink,SVNCORevision,ProjectName):
   
   if ('win32' == sys.platform):
      BatchFile = "CO.bat"
   else:
      BatchFile = "CO.sh"
   
   CODirectoryName = os.path.normpath(os.path.join(os.getcwd(),ProjectName))
   
   if os.path.exists(CODirectoryName):
      if ('win32' == sys.platform):
         Cmd = "rmdir /S /Q " + '"' + CODirectoryName + '"'
         os.system('"' + Cmd + '"')         
      else:
         Cmd = "rm -rf " + '"' + CODirectoryName + '"'
         os.system(Cmd)
   
   if ('win32' == sys.platform):   
      Command = "mkdir \"" + CODirectoryName + "\""
   else:
      Command = "mkdir -p \"" + CODirectoryName + "\"" 
   
   os.system(Command)
   
   ChkOutLocation = CreateDrive(CODirectoryName, "M")
   
   Command = ''
   
   if ('win32' == sys.platform):
      Command = ChkOutLocation + " \n"
      
   Command = Command + "cd " + '"' + ChkOutLocation + '"' + "\n"
   
   Command = Command + "svn co " + '"' +  SVNLink + '" \".\" ' + "-r " + SVNCORevision + " --trust-server-cert --non-interactive --username dev_tools_compiler_test --password devsys"
   
   BatchFilePtr = open(BatchFile,"w")
   
   BatchFilePtr.write(Command)
   
   BatchFilePtr.close()
   
   if not ('win32' == sys.platform):
      os.system("chmod +x " + BatchFile)
      os.system('sh ' + BatchFile)
   else:
      os.system('"' + BatchFile + '"')

   #os.system("sh CO.sh")
   os.remove(BatchFile)
   
   return(ChkOutLocation)
'''

def InsertEmailAddresses(Owner,ResultFileName):
   
   TempResultFileName = ResultFileName + "temp"
   Fptr = open(ResultFileName,'r')
   TempFptr = open(TempResultFileName,'w')
   Owner = "nagesh.prasad; vinayak.bhagwat; ravichandra.giriyappa; manjunath.muniraju; shankar.ramasamy"
   for Line in Fptr:
      if re.search("Test Summary:",Line):
         Line = "EMAIL_OWNERS=" + Owner + "\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n" + "Test Summary:" + "\n"

      TempFptr.write(Line)
  
   TempFptr.close()
   Fptr.close()
   
   os.remove(ResultFileName)
   os.rename(TempResultFileName,ResultFileName)
   
'''
def InsertEmailAddresses(ProjectName,Owner,CompilerTobeUsed):

   Owner = "nagesh.prasad;manjunath.muniraju;shankar.ramasamy"
   
   EmailFileName = ProjectName + "_" + CompilerTobeUsed + ".email"
   
   EmailFilePtr = open(EmailFileName,"w")
   
   EmailFilePtr.write("EMAIL_OWNERS=" + Owner)
   
   EmailFilePtr.close()



def RenameResultFile(ResultFileName, ProjectName):

   if os.path.exists(ResultFileName):
      TargetFileName = ProjectName + '_' + ResultFileName
      if os.path.exists(TargetFileName):
         os.remove(TargetFileName)

      InsertEmailAddresses(Owner[i],ResultFileName)

      os.rename(ResultFileName, TargetFileName)
         
         
if __name__ == "__main__":

   ProjectName = []
   Owner = []
   SVNAddress = []
   SVNChkOutRev = []
                  
   EmailErrorFileName = "MPLAB.errinfo"
   ClientSetupStatus, ErrorMessage = client_status.Get()
   
   ErrorFileName = "ClientSetupError.html"
   
   if ClientSetupStatus != 0:
      Fptr = open(ErrorFileName,"w")
      Fptr.write(ErrorMessage)
      Fptr.close()

      Fptr = open(EmailErrorFileName,"w")
      Fptr.write(ErrorMessage)
      Fptr.close()
      
      exit()
      
   if len(sys.argv) != 3:
      print "ERROR ! \nInvalid Number of parameters"
      exit()
      
   CsvFileName = sys.argv[1]
   CompilerTobeUsed = sys.argv[2].upper()
   
   if not os.path.exists(CsvFileName):
      print "ERROR !\nThe specified CSV file is not found"
      exit()
   
   if not (CompilerTobeUsed == "C18" or CompilerTobeUsed == "C30" or CompilerTobeUsed == "C32" or CompilerTobeUsed == "ALL" or CompilerTobeUsed == "XC8" or CompilerTobeUsed == "XC16" or CompilerTobeUsed == "XC32" or CompilerTobeUsed == "XC8-C18"):
      print "ERROR !\nThe specified Compiler Name is Invalid"
      exit()      
   
   CSVFile = CsvFileName

   CSVFilePtr = open(CSVFile,'r')

   LineCount = 0
   CSVLineInformation = []
   for Line in CSVFilePtr:
      LineCount = LineCount + 1
      if LineCount == 1:
         Header = Line
      elif LineCount >= 6:
         CSVLineInformation.append(re.split(',',Line))

   for RowIndex in range(len(CSVLineInformation)):
      
      for ColumnIndex in range(len(CSVLineInformation[RowIndex])):
         
         if ColumnIndex <= 1:
            CSVLineInformation[RowIndex][ColumnIndex] = CSVLineInformation[RowIndex][ColumnIndex].strip("\n|\n| ")
            CSVLineInformation[RowIndex][ColumnIndex] = re.sub("\.",'_',CSVLineInformation[RowIndex][ColumnIndex])
            CSVLineInformation[RowIndex][ColumnIndex] = re.sub("/",'',CSVLineInformation[RowIndex][ColumnIndex])
            CSVLineInformation[RowIndex][ColumnIndex] = re.sub(" ",'_',CSVLineInformation[RowIndex][ColumnIndex])
            if ColumnIndex == 1:
               CSVJobName = CSVLineInformation[RowIndex][0] + '_' + CSVLineInformation[RowIndex][ColumnIndex]
         else:
            if re.search("yes",CSVLineInformation[RowIndex][4],re.IGNORECASE):
               ProjectName.append(CSVJobName)
               Owner.append(CSVLineInformation[RowIndex][2])
               SVNAddress.append(CSVLineInformation[RowIndex][6])
               SVNChkOutRev.append(CSVLineInformation[RowIndex][7])
               break

   


   for i in range(len(ProjectName)):
      
      CheckedoutDirectoryName = CheckoutEngine(SVNAddress[i],SVNChkOutRev[i],ProjectName[i])
      
      MP8ExecutionBatchFileName = ""
      MPXExecutionBatchFileName = ""
      Temp = ' '
      if ('win32' == sys.platform):
         MP8ExecutionBatchFileName = "BatFileMP8.bat"
         MPXExecutionBatchFileName = "BatFileMPX.bat"
         Temp = "\\"
         
      else:
         MP8ExecutionBatchFileName = "BatFileMP8.sh"
         MPXExecutionBatchFileName = "BatFileMPX.sh" 
              
      
      Command = "python build_mplab_8.py " + os.path.normpath(CheckedoutDirectoryName) + Temp + " -cor=" + SVNChkOutRev[i] + " -com=" + CompilerTobeUsed + " -link=" + '"' + SVNAddress[i] + '"' + " -pro=" + '"' + ProjectName[i] + '"'

      BatFile = open(MP8ExecutionBatchFileName,'w')
      BatFile.write(Command)
      BatFile.close()
      
      Command = "python build_mplab_x.py " + os.path.normpath(CheckedoutDirectoryName) + Temp + " -cor=" + SVNChkOutRev[i] + " -com=" + CompilerTobeUsed + " -link=" + '"' + SVNAddress[i] + '"' + " -pro=" + '"' + ProjectName[i] + '"'
      
      BatFile = open(MPXExecutionBatchFileName,'w')
      BatFile.write(Command)
      BatFile.close()

      if ('win32' == sys.platform):
         
         Process1 = subprocess.Popen('"' + MP8ExecutionBatchFileName + '"')
      
         Process2 = subprocess.Popen('"' + MPXExecutionBatchFileName + '"')
         
      else:
         os.system("chmod +x " + MPXExecutionBatchFileName)
         os.system('sh ' + MPXExecutionBatchFileName)

      TimeoutCounter = 0

      ForceExitDetected = 0

      if ('win32' == sys.platform):      
         while(Process1.poll() == None): 
            time.sleep(1)
         while(Process2.poll() == None): 
            time.sleep(1)      
      
      InsertEmailAddresses(ProjectName[i],Owner[i],CompilerTobeUsed)
      
      if ('win32' == sys.platform):
      
         Command = "subst " + CheckedoutDirectoryName + " /D"
      
         os.system('"' + Command + '"')
      
      '''
      ## Renaming MPLAB 8 Results
      
      ResultFileNameMP8 = CompilerTobeUsed + "_ResultSummary.txt"
      
      RenameResultFile(ResultFileNameMP8, "MPLAB8_" + ProjectName[i])
      
      ResultFileNameMP8 = CompilerTobeUsed + "_ResultSummary.PASS"
            
      RenameResultFile(ResultFileNameMP8, "MPLAB8_" + ProjectName[i])
      
      ResultFileNameMP8 = CompilerTobeUsed + "_ResultSummary.FAIL"
            
      RenameResultFile(ResultFileNameMP8, "MPLAB8_" + ProjectName[i]) 
      
      
      
      
      ResultFileNameMP8 = CompilerTobeUsed + "_ResultSummary.html"
            
      RenameResultFile(ResultFileNameMP8, "MPLABX_" + ProjectName[i])

      #ResultFileNameMP8 = CompilerTobeUsed + "_ResultSummary.PASS"
            
      #RenameResultFile(ResultFileNameMP8, "MPLABX_" + ProjectName[i])
      
      #ResultFileNameMP8 = CompilerTobeUsed + "_ResultSummary.FAIL"
            
      #RenameResultFile(ResultFileNameMP8, "MPLABX_" + ProjectName[i])      
   
      '''


      
