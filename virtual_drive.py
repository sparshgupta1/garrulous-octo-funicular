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
import mdb
import zipper
import output_status
import executor
import make_operations
import misc_operations 
import random

########################################

def GetDriveNameWithFirstDir(Location):

   Path = Location

   '''
   if re.search(r"\\isp\\",Location):
      
      return(re.split(r"\\isp\\",Path)[0])
      
   else:
   '''
   
   head = os.path.splitdrive(Path)[1]
   drivename = os.path.splitdrive(Path)[0]
   FinalPath = ''

   PathNames = []

   while not(head == '' or head == "\\"):
      head1 = head
      head = os.path.split(head1)[0]
      if not '' == os.path.split(head1)[1]:
         PathNames.append(os.path.split(head1)[1])

   TempPathNames = PathNames
   PathNames = []

   for i in range(len(TempPathNames)):
      PathNames.append(TempPathNames[(len(TempPathNames) - 1) - i])

   PathForVirtualDriveCreation = drivename + "\\"
   PathResidue = ''

   for i in range(len(PathNames)):
   
      PathForVirtualDriveCreation = os.path.join(PathForVirtualDriveCreation, PathNames[i])
      PathResidue = ''
      for j in range(i+1, (len(PathNames))):
         PathResidue = os.path.join(PathResidue, PathNames[j])
      if (len(PathResidue) + 3) < 200:
         break
               
   return(PathForVirtualDriveCreation, PathResidue)

################################################

def CreateDrive(Location, StartDriveLetter, HWToolName):

   ReceivedStartDriveLetter = StartDriveLetter

   Error = 0
   VirtualDriveName = ''
   DriveTemp = ''
   VirtualDriveNameFound = 0
   DriveMappingWaitCount = 0
   DriveSuccessfullyMapped = 0
   DriveMappingError = 0
   
   
   if not ('win32' == sys.platform):
      return(1,'')
   
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
            
            if "NA" == HWToolName:                             # If it is only build test, roam for the available virtual drive. otherwise, 
                                                               # stick to one drive name
               StartDriveLetter = chr(ord(StartDriveLetter) + 1)
               if "Z" == StartDriveLetter:               # If Z Drive is added, Roll back to "H"
                  StartDriveLetter = ReceivedStartDriveLetter
                  time.sleep(random.randint(1,10))
            
         else:
            VirtualDriveName = str(StartDriveLetter) + ":"
            DriveMappingWaitCount = DriveMappingWaitCount + 1
            if DriveMappingWaitCount >= random.randint(11,20):            # Reasonable Count !, Need to check, if fails drive mismatch occurs !!
               VirtualDriveNameFound = 1

      PathForVirtualDriveCreation, PathResidue = GetDriveNameWithFirstDir(Location)
      
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

   PathForVirtualDriveCreation, PathResidue = GetDriveNameWithFirstDir(Location)
   
   
   '''
   DriveNameWithFirstDir = re.sub(r"\\",r"\\\\",DriveNameWithFirstDir)

   TempLocation = re.split(DriveNameWithFirstDir,Location)[1]
   TempLocation = TempLocation.strip(r"\\")
   '''
   
   Location = os.path.join(VirtualDriveName + "\\",PathResidue)
   Location = os.path.normpath(Location)



   os.remove(os.path.join(os.getcwd(),"Temp_Log.txt"))

   print Location   
   
   return(0,Location)
   

############################################

def Create(Location, HWToolName):
   
   if "NA" == HWToolName:
      StartDriveLetter = "M"
   else:
      StartDriveLetter = "L"
   
   Error,ProjectLocation = CreateDrive(Location,StartDriveLetter,HWToolName)
   
   return(Error,ProjectLocation)
   
############################################

def Delete(Location):
   if os.path.isdir(Location):
      DriveName = os.path.splitdrive(Location)[0]
      SystemCommand = "subst " + DriveName + " /D"
      os.system(SystemCommand)
      