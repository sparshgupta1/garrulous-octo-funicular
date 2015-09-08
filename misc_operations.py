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
import extract_info
import virtual_drive

#############################################################
#### Finds the Location and returns Error, if not Exists
#############################################################
def FindLocation(InputLocation):                               # Receives the Location, to find its existance
   if os.path.exists(InputLocation):                           # Using Built-in Module
      return(0)                                                # If Existing, Return 0
   else:
      return(1)                                                # Error, if not existing !

#############################################################
#### When removing a Directory Tree, If the Directory has
#### Read only permissions, This Routene can be used to 
#### Modify the Read permissions to Write
#############################################################

def ModifyToWritePermission(func, path, exc_info):             # Modify the Files and Directories to Write Mode
    import stat
    if not os.access(path, os.W_OK):                           # Is the error an access error ?
      os.chmod(path, 0777)
      func(path)                                               # Recrussive change of mode of all the Files
    else:
      raise



###########################################################
#### This Module Deletes the List of generated files,
#### existing in the compiler.
###########################################################

def DeleteGeneratedFiles(P1_ProjectLocation):

   for var in os.listdir(os.getcwd()):
      if var.endswith(".mk"):
         os.remove(var)
      elif var.endswith(".hex"):
         os.remove(var)
      elif var.endswith(".cof"):
         os.remove(var)
      elif var.endswith(".zip"):
         os.remove(var)
      elif var.endswith(".map"):
         os.remove(var)
      elif var.endswith(".elf"):
         os.remove(var)

   var = os.path.join(P1_ProjectLocation,"dist")      # delete the existing Dist Directory, which has older output files, if exists.
   if os.path.exists(var):       
      shutil.rmtree(var,onerror=ModifyToWritePermission)

   var = os.path.join(P1_ProjectLocation,"build")      # delete the existing Dist Directory, which has older output files, if exists.
   if os.path.exists(var):       
      shutil.rmtree(var,onerror=ModifyToWritePermission)
   
   PreviousCWD = os.getcwd()
   
   os.chdir(P1_ProjectLocation)
   
   for var in os.listdir(os.getcwd()):
      if var.endswith(".hex"):
         os.remove(var)
      elif var.endswith(".cof"):
         os.remove(var)
      elif var.endswith(".map"):
         os.remove(var)
      elif var.endswith(".elf"):
         os.remove(var)
      elif var.endswith(".bat"):
         os.remove(var)
      elif var.endswith(".sh"):
         os.remove(var)
   
   os.chdir(PreviousCWD)            
            
#############################################################
#### This Routine Executes the delete Operation on a given , 
#### File Name
#############################################################

def DeleteFile(FileName):
   try:
      os.remove(FileName)
   except OSError, detail:
      if detail.errno != 2:
         raise 
         
         




#############################################################
#### Validates the device, Returns error, in case of 
#### invalid device.
#############################################################
def ValidateDevice(Device):
   
   CompilerList = []
   DevicePrefix = []
   DeviceList = []
   CompilerKeywordList = []
   Modes = []
   ModeDetectorKwd = []
   
   
   CompilerList, DevicePrefixList, DeviceList, CompilerKeywordList, Modes, ModeDetectorKwd = extract_info.GetCompilerDeviceInfo()
   
   Error = 1
   
   for i in range(len(CompilerList)):
      for Dev in DeviceList[i]:
         if re.search(Dev, Device):
            Error = 0
            break
      
      if 0 == Error:
         break
            
      
   return(Error)
   

         
#############################################################
#### Validates the compiler, Returns error, in case of 
#### invalid compiler.
#############################################################
def ValidateCompiler(Compiler):
   
   CompilerList = []
   DevicePrefix = []
   DeviceList = []
   CompilerKeywordList = []
   Modes = []
   ModeDetectorKwd = []
   
   
   CompilerList, DevicePrefixList, DeviceList, CompilerKeywordList, Modes, ModeDetectorKwd = extract_info.GetCompilerDeviceInfo()
   
   Error = 1
   
   for CompilerName in CompilerList:
      if CompilerName == Compiler:
         Error = 0
         break
      
   return(Error)
   
   
#############################################################
#### Validstes compiler against the supplied device
#### Raises error, in case of mismatch.
#############################################################
def ValidateDeviceVsCompiler(Device, Compiler):
   
   CompilerList = []
   DevicePrefix = []
   DeviceList = []
   CompilerKeywordList = []
   Modes = []
   ModeDetectorKwd = []
   
   
   CompilerList, DevicePrefixList, DeviceList, CompilerKeywordList, Modes, ModeDetectorKwd = extract_info.GetCompilerDeviceInfo()
   
   Error = 1
   
   for i in range(len(CompilerList)):
      for Dev in DeviceList[i]:
         if re.search(Dev, Device):
            if CompilerList[i] == Compiler:
               Error = 0
               break
      
      if 0 == Error:
         break

   return(Error)
   
 

#####################################################
#### This module Deletes the Virtual Drive
#### and exits the program
#####################################################


def ExitARBSDeletingVirtualDrive(Location,VirtualDriveCreationFlag):

   if 1 == VirtualDriveCreationFlag:
      if sys.platform == 'win32':
         virtual_drive.Delete(Location)
      exit()
   else:
      exit()



#####################################################
#### This module converts the path format to the 
#### desired make that is being used
#####################################################


def ConvertPathToMPXParameterFormat(Path,Version):

   ReturnValue = ''
   
   if 'win32' == sys.platform:                           # In case of windows, 
   
      if 0 == Version:                                   # For older versions of make filess, convert all the backslash to fwd slash
         ReturnValue = re.sub(r"/",r"\\",Path)
         ReturnValue = re.sub(r"\\",r"\\\\",ReturnValue)           # 
         ReturnValue = re.sub(r" ",r"\\ ",ReturnValue)   # all spaces to backslash slash
      
      else:                                 # For newer versions of MPLAB X Make Files, Use Windows Short path to address 
         ReturnValue = re.sub(r"\\\\",r"\\",Path)
         ReturnValue = re.sub(r"/",r"\\",ReturnValue)

         
         '''
         Array = re.split(r"\\",ReturnValue)

         ReturnValue = ''

         for i in Array:
            if (len(i) > 8) and (i != Array[len(Array)-1]): # if the name of the directory is more than 8 characters, use first 6 chars and 
               ReturnValue = ReturnValue + i[:6] + "~1\\"   # ~<Number> at the last
            else:
               ReturnValue = ReturnValue + i
               if i != Array[len(Array)-1]:
                  ReturnValue = ReturnValue + "\\"
         '''
         #ReturnValue = '"' + ReturnValue + '"'
         
   else:                                                 # in case of linux, no change in paths, between the versions of the make files.
      ReturnValue = re.sub(r"\\\\",r"/",Path)
      ReturnValue = re.sub(r"\\",r"/",ReturnValue)      

   return(ReturnValue)      
   
   


'''
def shortpath(x):

z=''

for y in x.split('\\'):

   if len(y.split('.')[0])>8:

      if ('.' in y):

         z=z+'\\'+y.split('.')[0][:6].upper()+'~1'+'.'+y.split('.')[1]

      else:

         z=z+'\\'+y[:6].upper()+'~1'

   else:

      z=z+'\\'+y

return z[1:]    
'''
