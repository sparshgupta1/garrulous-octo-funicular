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
import misc_operations
import extract_info
from xml.etree.ElementTree import iterparse,ElementTree
import xml.dom.minidom
###############################################
###############################################
###############################################

def GetValueFromPathsFile(File,String):
   
   if String == "_XC8-C18_PATH_":
      String = "_C18_PATH_"
   ReturnValue = ''
   
   P1_PATH_FILE = open(File,'r')
   
   Error = 1
   
   String = "^" + String
   
   for Line in P1_PATH_FILE:
      
      Line = Line.strip("\n|\r")
      
      if not re.search("^#",Line):
         
         if re.search(String,Line):
            
            ReturnValue = re.split("=",Line)[1]
            
            ReturnValue = ReturnValue.strip(" ")
            
            ReturnValue = re.sub('"','',ReturnValue)
            
            break
   
   if not '' == ReturnValue:
      Error = 0
   
   P1_PATH_FILE.close()
   
   return(Error, ReturnValue)
   
         
def JoinPaths(PathValue1,PathValue2):
   return (PathValue1 + "/" + PathValue2)


########################################################
# Gets Compiler Paths in an array
########################################################

def GetCompilerPaths(Compiler,Mode,CompilerPathRefFile, MakeFileVersion):    # Get the compiler Paths from Paths File

   Compiler = Compiler.upper()
   CompilerPathArray = []
   
   OS_Found_In_Ref_File = 0
   Compiler_Found_In_Ref_File = 0
   
   PathFile = CompilerPathRefFile 
   CompilerPathSearchString = ''
   
   SearchPathsCompiler = Compiler
   SearchPathsBinaries = Compiler
   
   if Compiler == "XC8-C18":
      SearchPathsBinaries = "C18"   
   
   if '' == Mode:
      CompilerPathSearchString = "_" + SearchPathsCompiler + "_PATH_"    # Get the Compiler Installation Path. Example _C30_PATH_ or _PICC18_STD_PATH
   else:
      CompilerPathSearchString = "_" + SearchPathsCompiler + '_' + Mode + "_PATH_"    # Get the Compiler Installation Path. Example _C30_PATH_ or _PICC18_STD_PATH

   
   Error, PathValue = GetValueFromPathsFile(PathFile, CompilerPathSearchString)

   Executables = ["MP_CC", "MP_AS", "MP_LD", "MP_AR", "MP_CPP"]

   if 0 == Error:
      
      for i in range(len(Executables)):
      
         CompilerPathSearchString = "_" + SearchPathsBinaries + '_' + Executables[i] + '_'
         Error, BinPath = GetValueFromPathsFile(PathFile, CompilerPathSearchString)      
                  
         if 0 == Error:
            DirPath = JoinPaths(PathValue,os.path.split(BinPath)[0])
            BinPath = JoinPaths(PathValue,BinPath)
            if MakeFileVersion != 0:
               BinPath = Executables[i] + '=' + '"' + misc_operations.ConvertPathToMPXParameterFormat(BinPath,MakeFileVersion) + '"'
            else:
               BinPath = Executables[i] + '=' + misc_operations.ConvertPathToMPXParameterFormat(BinPath,MakeFileVersion)
               
            CompilerPathArray.append(BinPath)
            if MakeFileVersion != 0:
               DirPath = Executables[i] + '_DIR=' + '"' + misc_operations.ConvertPathToMPXParameterFormat(DirPath,MakeFileVersion) + '"'
            else:
               DirPath = Executables[i] + '_DIR=' + misc_operations.ConvertPathToMPXParameterFormat(DirPath,MakeFileVersion)
               
               
            CompilerPathArray.append(DirPath) 
         else:
            Error = 0
 

   return(CompilerPathArray,Error)
   
   
    
#############################################################
#### Finds the existance of the files in a directory with the 
#### given extension. 
#### Returns the array, containing File names and 
#### the count, that has the number of files, exists
#### This Routene is execlusively written for finding 
#### Make Files in the nbproject directory
#############################################################

def FindMakeFile(Location):                                    # Finds the Existance of Make File in the given Directory and returns the List
   filename = ''                                               # of Files availbale anf the number of Files.
   FileCount = 0
   FileArray = []
   for filename in os.listdir(Location):                       # Lists the Files in the given Location
      if ('Makefile-impl.mk' != filename) and ('Makefile-variables.mk' != filename):   # No need to list the mentioned two Files.
         if not (re.search("Makefile-local-",filename)):
            if filename.endswith(".mk"):                          # If Ends with Make,
               FileArray.append(filename)                         # Append to the return array List
               FileCount = FileCount + 1                          # Track the Count

   return(FileArray,FileCount)                                 # Return the found items and the number.

   

#############################################################
#### This Routine Finds the compatible make file list in the 
#### given directory
#### The Compatibility is checked against the device and the
#### Compiler Commands available in the Make File
####
#### Below table lists the make files to build, for the 
#### combinations of compiler and Device.
####
#### Compiler   Device    Operation
####
#### YES        YES       Find the Compatibility between
####                      the device and the compiler and 
####                      build all the make files, compatible
####                      the device,
#### YES        NO        Build only the make files,
####                      compatible to the compiler
#### NO         YES       Build only the make files,
####                      compatible to the Device
#### NO         NO        Build all the make files, excepr C18
####                      make file.
#############################################################
def GetMakeFileMCU(MakeFile, DevicePrefix, CompilerKeywordList):
   
   Found = 0
   MakeFileMCU = ''
   MakeFileMCUMacroFound = 0
                                                            # This Part identifies the existing device name in the supplied make file
                                                            # This Identified Device's Family will be compared against the Supplied Device's Family
                                                            # If both the families are same, the make file is reported as Compatible
   ################################################################
   # Updated for Version 1.9 by Shankar
   P1_MakeFile = open(MakeFile,"r")
   
   for Line in P1_MakeFile:                                 # Iterate through each line of each make file
      Line = Line.strip("\n|\r")
      if re.search("^MP_PROCESSOR_OPTION=", Line):    
         array = re.split("MP_PROCESSOR_OPTION=",Line)
         MakeFileMCU = array[1].strip("\n|\r")                             # This Array Element will be holding the name of the existing device
         MakeFileMCUMacroFound = 1


   P1_MakeFile.close()                                      # Close it for Reopening purpose

   # In case, if the make file is generated by a older versions of MPLAB X, then there will not be the "MP_PROCESSOR_OPTION" keyword, for detecting the processor.

   
   if MakeFileMCUMacroFound == 0:
      P1_MakeFile = open(MakeFile,"r")
      Found = 0
      for Line in P1_MakeFile:
         Line = Line.upper()
         if re.search("{MP_CC}",Line):
            Count = 0
            for Kwd in CompilerKeywordList:
               Count = Count + 1
               if re.search(Kwd,Line):
                  MakeFileMCU = re.sub('=','',re.split(' ',re.split(Kwd,Line)[1])[0])
                  MakeFileMCU = re.sub(DevicePrefix[Count-1],'',MakeFileMCU)
                  Found = 1
                  break
         if Found == 1:
            MakeFileMCUMacroFound = 1
            break

      P1_MakeFile.close() 
   
   
   return(MakeFileMCU)
   



############################################################
# Extracts the Device Name, Compiler to be used and the 
# Operating Mode of the Compiler in the Make File
############################################################

def GetMakeFileDetails(MakeFile, CompilerList, DevicePrefix, DeviceList, CompilerKeywordList, Modes, ModeDetectorKwd):
   DeviceInMakeFile = ''
   CompilerInMakeFile = []
   ModeInMakeFile = []
   
   DeviceInMakeFile = GetMakeFileMCU(MakeFile, DevicePrefix, CompilerKeywordList)
   
   P1_MakeFile = open(MakeFile,"r")
   
   Found = 0
   VersionFound = 0
   MakeFileVersion = 0
   
   for Line in P1_MakeFile:
      
      if 0 == VersionFound:

         if re.search("Makefile-local-",Line) and re.search("wildcard",Line):
            MakeFileVersion = 2
            VersionFound = 1
            
         if re.search("^MP_CC=",Line):
            if re.search('"',Line):
               MakeFileVersion = 1

            VersionFound = 1


      Line = Line.strip("\n|\r")
      
      if re.search("{MP_CC}",Line):
         
         for i in range(len(CompilerKeywordList)):
            
            
            Temp = CompilerKeywordList[i] + "$(MP_PROCESSOR_OPTION)"
            
            Temp = re.sub(r"\$", "_ARBS_DOLLAR_",Temp)
            Temp = re.sub(r"\(", "_ARBS_OB_",Temp)
            Temp = re.sub(r"\)", "_ARBS_CB_",Temp)

            Line = re.sub(r"\$", "_ARBS_DOLLAR_",Line)
            Line = re.sub(r"\(", "_ARBS_OB_",Line)
            Line = re.sub(r"\)", "_ARBS_CB_",Line)            
            
            
            for DevList in DeviceList[i]:

               if re.search('^' + DevList, DeviceInMakeFile):

                  if re.search((CompilerKeywordList[i] + DeviceInMakeFile).upper(),Line.upper()) or re.search(Temp.upper(),Line.upper()):
                  
                     CompilerInMakeFile.append(CompilerList[i])

                     DeviceInMakeFile = re.sub("^" + DevicePrefix[i],'',DeviceInMakeFile)

                     Found = 1
                     #break
                  
                  if 1 == Found:
                     # Finding Compiler Mode of operation
                     LMode = ''                                         
                     if not [] == Modes[i]:                         # If there are some modes, scan the line for the existance of the keyword, if exists, then it is in that mode
                        LMode = Modes[i][0]                         # Default is the First Mode
                        LCount = 0
                        for Kwd in ModeDetectorKwd[i]:              # Scan for the Mode determining Keyword.
                           if '' != Kwd:                                # if the Keyword is no "NA", then
                              if re.search(Kwd.upper(), Line.upper()):  # if the line has the kwd, 
                                 LMode = Modes[i][LCount]           # Mode is the matching keyword's array element of MODES.
                                 break
                           LCount = LCount + 1                          # Iterate through all.

                     ModeInMakeFile.append(LMode)                         # Append the Mode.

                     #break # for baeaking for i in range(len(CompilerKeywordList)) loop above
      
      if 1 == Found:
         break
 
   P1_MakeFile.close()
               
   return(DeviceInMakeFile, CompilerInMakeFile, ModeInMakeFile, MakeFileVersion)


############################################################
# Removes the redundant items in a given array and returns the array
############################################################

def RemoveRedundantItems(Items):

   ReturnItems = []
   
   for IItem in Items:
      
      Found = 0
      
      for JItem in ReturnItems:
         
         if IItem == JItem:
            Found = 1
            break
      
      if 0 == Found:
         ReturnItems.append(IItem)
 
   return(ReturnItems)
   
   
   
         
#############################################################
#### This Module returns the List of compilers, that can be 
#### used to executing the given make file.
#############################################################

def GetCompilerListForDevice(Device, CompilerList, DevicePrefix, DeviceList):

   CompilerListForDevice = []
   
   for i in range(len(CompilerList)):
      
      GivenDevice = re.sub(DevicePrefix[i],'',Device)
      
      for DeviceH in DeviceList[i]:
         
         DeviceH = '^' + DeviceH
         
         if re.search(DeviceH, Device):
            
            CompilerListForDevice.append(CompilerList[i])
            
            break

   return(RemoveRedundantItems(CompilerListForDevice))
      


#############################################################
#### This Module returns the List of Compatible Make Files
#### along with the Mode and the Compiler Paths to be used for 
#### executing the Make Files
#############################################################

def FindCompatibleMakeFile(Path, MakeFileList, Device, Compiler, CompilerPathRefFile):        # Returns the List of make files, compatible to the supllied device, from the make file list supplied

   array = []
   CompatibleMakeFileCount = 0
   Count = 0
   Found = 0
   Device = Device.upper()                                     # Make the Device Name Upper, for making it easy for comparison

   MakeFileMCU = ''
   MakeFileMCUMacroFound = 0
   DeviceValid = 0
   CompilerTobeUsed = ''

   CompatibleMakeFileList = []
   ReturnCompiler = []
   ReturnDevice = []
   CompilerMode = []
   
   
   CompilerList = []
   DevicePrefix = []
   DeviceList = []
   CompilerKeywordList = []
   Modes = []
   ModeDetectorKwd = []
   
   MakeVersion = []
   
   CompilerList, DevicePrefix, DeviceList, CompilerKeywordList, Modes, ModeDetectorKwd = extract_info.GetCompilerDeviceInfo()

   #Device = re.sub("PIC",'',Device)
   for MakeFile in MakeFileList:                               # Iterate through the given array of make files
      
      
      DeviceInMakeFile, CompilerInMakeFile, ModeInMakeFile, MakeFileVersion = GetMakeFileDetails(os.path.join(Path,MakeFile), CompilerList, DevicePrefix, DeviceList, CompilerKeywordList, Modes, ModeDetectorKwd)         

      
      
      if not('' == DeviceInMakeFile or [] == CompilerInMakeFile):
         
         if '' == Compiler and '' == Device:     # No Compiler, No Device names specified
            for i in range(len(CompilerInMakeFile)):
               if re.search("^XC", CompilerInMakeFile[i].upper().strip(" ")):
                  ReturnDevice.append(DeviceInMakeFile)
                  ReturnCompiler.append(CompilerInMakeFile[i])
                  CompatibleMakeFileList.append(MakeFile)
                  CompilerMode.append(ModeInMakeFile[i])
                  MakeVersion.append(MakeFileVersion)
                        
         elif '' != Compiler and '' == Device:   # Only Compiler Name Specified
            
            for i in range(len(CompilerInMakeFile)):
               if Compiler == CompilerInMakeFile[i]:
                  ReturnDevice.append(DeviceInMakeFile)
                  ReturnCompiler.append(CompilerInMakeFile[i])
                  CompatibleMakeFileList.append(MakeFile) 
                  CompilerMode.append(ModeInMakeFile[i])
                  MakeVersion.append(MakeFileVersion)
                  
         elif '' == Compiler and '' != Device:   # Only Device Name Specified
            
            '''
            CompilerListForDevice = GetCompilerListForDevice(Device, CompilerList, DevicePrefix, DeviceList)
            
            for Comp in CompilerListForDevice:
               if Comp == CompilerInMakeFile:
                  ReturnDevice.append(Device)
                  ReturnCompiler.append(CompilerInMakeFile)
                  CompatibleMakeFileList.append(MakeFile)
                  CompilerMode.append(ModeInMakeFile)
                  break
            '''
            for i in range(len(CompilerInMakeFile)):

               if Compiler == CompilerInMakeFile[i]:
                  ReturnDevice.append(DeviceInMakeFile)
                  ReturnCompiler.append(CompilerInMakeFile[i])
                  CompatibleMakeFileList.append(MakeFile) 
                  CompilerMode.append(ModeInMakeFile[i])
                  MakeVersion.append(MakeFileVersion)
               
         elif '' != Compiler and '' != Device:   # Both Compiler and Device Names Specified

            for i in range(len(CompilerInMakeFile)):
               if Compiler == CompilerInMakeFile[i]:
                  ReturnDevice.append(DeviceInMakeFile)
                  ReturnCompiler.append(CompilerInMakeFile[i])
                  CompatibleMakeFileList.append(MakeFile) 
                  CompilerMode.append(ModeInMakeFile[i])
                  MakeVersion.append(MakeFileVersion)
         
   for Makefile in CompatibleMakeFileList:
      CompatibleMakeFileCount = CompatibleMakeFileCount + 1 
    
   CompilerPathsArray = []
   LocalCompPthAry = []
   ErrorArray = []
   Error = 0
   
   for i in range(CompatibleMakeFileCount):
      LocalCompPthAry,Error = GetCompilerPaths(ReturnCompiler[i],CompilerMode[i],CompilerPathRefFile, MakeVersion[i])   # Get the Compiler Paths Array and Error, if exists.
      CompilerPathsArray.append(LocalCompPthAry)
      ErrorArray.append(Error)
   return(CompatibleMakeFileList,CompatibleMakeFileCount,ReturnDevice,ReturnCompiler,CompilerMode,CompilerPathsArray,ErrorArray,MakeVersion)
   



      



#############################################################
#### This Module updates the Name of the HW Tool in the Make
#### File Commands. The Module replaces the tool name in the 
#### Line and returns the Line
#### Added this as a different routine in V2.0
#############################################################

def UpdateDebuggerNameInMakeFile(Line,HW_Tool,Compiler):

   ##########################################################                 # Added in Version 1.8 and Updated in Ver 2.0
   # Added for PLIB Run Time Test using Smiulator, by Shankar R
   # For C30, C32
                                                         # Replace the Debugger Name with "-D__DEBUG"
                                                         # for both HTC and Microchip C Compilers
   if re.search("-D__DEBUG -D__MPLAB_DEBUGGER",Line):
      Line = Line.replace("-D__DEBUG -D__MPLAB_DEBUGGER_REAL_ICE=1","-D__DEBUG_NON_PICC_TYPE ")
      Line = Line.replace("-D__DEBUG -D__MPLAB_DEBUGGER_ICD3=1","-D__DEBUG_NON_PICC_TYPE ")
      Line = Line.replace("-D__DEBUG -D__MPLAB_DEBUGGER_PK3=1","-D__DEBUG_NON_PICC_TYPE ")
      Line = Line.replace("-D__DEBUG -D__MPLAB_DEBUGGER_PICKIT2=1","-D__DEBUG_NON_PICC_TYPE ")
      Line = Line.replace("-D__DEBUG -D__MPLAB_DEBUGGER_ICD2=1","-D__DEBUG_NON_PICC_TYPE ")

   elif re.search("-D__DEBUG --debugger",Line):
      Line = Line.replace("-D__DEBUG --debugger=realice","-D__DEBUG_PICC_TYPE ")
      Line = Line.replace("-D__DEBUG --debugger=pickit3","-D__DEBUG_PICC_TYPE ")
      Line = Line.replace("-D__DEBUG --debugger=pickit2","-D__DEBUG_PICC_TYPE ")
      Line = Line.replace("-D__DEBUG --debugger=pickit3","-D__DEBUG_PICC_TYPE ")
      Line = Line.replace("-D__DEBUG --debugger=icd2","-D__DEBUG_PICC_TYPE ")      

   elif re.search("-D__DEBUG",Line):
      if (Compiler == "PICC" or Compiler == "PICC18"):
         Line = Line.replace("-D__DEBUG","-D__DEBUG_PICC_TYPE ")
      else:
         Line = Line.replace("-D__DEBUG","-D__DEBUG_NON_PICC_TYPE ")

   if re.search("-mdebugger -D__MPLAB_DEBUGGER",Line):
      Line = Line.replace("-mdebugger -D__MPLAB_DEBUGGER_REAL_ICE=1","-D__DEBUG_NON_PICC_TYPE_LKR ")
      Line = Line.replace("-mdebugger -D__MPLAB_DEBUGGER_ICD3=1","-D__DEBUG_NON_PICC_TYPE_LKR ")
      Line = Line.replace("-mdebugger -D__MPLAB_DEBUGGER_PK3=1","-D__DEBUG_NON_PICC_TYPE_LKR ")
      Line = Line.replace("-mdebugger -D__MPLAB_DEBUGGER_PICKIT2=1","-D__DEBUG_NON_PICC_TYPE_LKR ")
      Line = Line.replace("-mdebugger -D__MPLAB_DEBUGGER_ICD2=1","-D__DEBUG_NON_PICC_TYPE_LKR ")
   elif re.search("-mdebugger ",Line):
      Line = Line.replace("-mdebugger","-D__DEBUG_NON_PICC_TYPE_LKR ")
                                                         # Based on the Supplied tool, update the Debugger Tool nane 
                                                         # along with the Keyword -D__DEBUG
   if "REALICE" == HW_Tool:                                                   

      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE ","-D__DEBUG -D__MPLAB_DEBUGGER_REAL_ICE=1")
      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE_LKR ","-mdebugger -D__MPLAB_DEBUGGER_REAL_ICE=1")
      Line = Line.replace("-D__DEBUG_PICC_TYPE ","-D__DEBUG --debugger=realice")

   elif "ICD3" == HW_Tool:

      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE ","-D__DEBUG -D__MPLAB_DEBUGGER_ICD3=1")
      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE_LKR ","-mdebugger -D__MPLAB_DEBUGGER_ICD3=1")
      Line = Line.replace("-D__DEBUG_PICC_TYPE ","-D__DEBUG --debugger=pickit3")

   elif "ICD2" == HW_Tool:

      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE ","-D__DEBUG -D__MPLAB_DEBUGGER_ICD2=1")
      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE_LKR ","-mdebugger -D__MPLAB_DEBUGGER_ICD2=1")
      Line = Line.replace("-D__DEBUG_PICC_TYPE ","-D__DEBUG --debugger=icd2")

   elif "PICKIT3" == HW_Tool:

      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE ","-D__DEBUG -D__MPLAB_DEBUGGER_PK3=1")
      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE_LKR ","-mdebugger -D__MPLAB_DEBUGGER_PK3=1")
      Line = Line.replace("-D__DEBUG_PICC_TYPE ","-D__DEBUG --debugger=pickit3")

   elif "PICKIT2" == HW_Tool:

      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE ","-D__DEBUG -D__MPLAB_DEBUGGER_PICKIT2=1")
      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE_LKR ","-mdebugger -D__MPLAB_DEBUGGER_PICKIT2=1")
      Line = Line.replace("-D__DEBUG_PICC_TYPE ","-D__DEBUG --debugger=pickit2")

   else: # The else cases are : HW_Tool == "NA" or HW_Tool == "SIM" or HW_Tool == is some invalid tool name.

      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE ","-D__DEBUG")                # if that is the case, use the Simulator thing.
      Line = Line.replace("-D__DEBUG_NON_PICC_TYPE_LKR ","-mdebugger")
      Line = Line.replace("-D__DEBUG_PICC_TYPE ","-D__DEBUG")      # This is the case for Build Test also !       
   ########################################################## 


   return(Line)




#############################################################
#### This Routine Updates the required modifications in the existing Make File 
#### The Mechanism is creates a temp make file, copies
#### all the lines from the original make file, replaces/updates
#### the required items and pastes it in the temp make file.
#### Once all the lines are updated/modified, 
#### Deletes the oroginal Make File and renames the 
#### Temp make File to original make file.
#############################################################

def UpdateMakeFile(Path,MakeFile,INDevice,IN_Compiler,HW_Tool,MakeVersion):
   
   time.sleep(1)
   
   P1_MAKEFILE = open(os.path.join(Path,MakeFile),'r')               # Now, with the existing device in the make file and the Compiler paths, 
   P1_MAKEFILE_TEMP = open(os.path.join(Path,"Temp-"+MakeFile),'w')  # Re-open the orogonal Make File and create an another temporary make file,
                                                                     # Copy all the lines from the original make file to the temp make file
   for Line in P1_MAKEFILE:                                          # by replacing the device and the compiler paths.
      
      Line = UpdateDebuggerNameInMakeFile(Line,HW_Tool,IN_Compiler)
      
      #Line = re.sub(r"\\","/",Line)
      
      #if 'win32' == sys.platform:
      #   Line = re.sub("/ ",r"\\ ",Line)
      
      Line = re.sub(r"\\\"",'"',Line)
      
      if MakeVersion >= 1:
      
         if re.search("%[a|c|f|l|n|s]",Line):
            if 'win32' == sys.platform:
               if not re.search("%%",Line):
                  Line = re.sub("%","%%",Line)
            else:
               if re.search("%%",Line):
                  Line = re.sub("%%","%",Line)  
                  
      if MakeVersion == 0:
         if re.search("\$\{MP_CPP\}",Line):
            Line = "#" + Line
                  
                  
         
      if "PICC" == IN_Compiler or "PICC18" == IN_Compiler or "XC8" == IN_Compiler:        # Add option to Generate Map File, while building. This is for PICC and PICC18
         Line = re.sub(r"-map",r"+map",Line)    # Generate Map File
      
      
      elif "C30" == IN_Compiler or "C32" == IN_Compiler or "XC16" == IN_Compiler or "XC32" == IN_Compiler:      # This is for C30 and C32
         if re.search(r"\${MP_CC}",Line):
            Line = re.sub(",--report-mem",'',Line)    # Added for removing memory report in Compiler Message Log
            
            Line = re.sub("-Wl,","-Wl,--report-mem,",Line) # Enabling report memory option for memory usage analysis.
            
            #if re.search(r"OBJECTFILES",Line):
            if not re.search(r"-Map=",Line):
               Line = re.sub("-Wl,","-Wl,-Map=\"MapFile.map\",",Line)
            else:
               Line = re.sub(r"\$\(BINDIR_\)\$\(TARGETBASE\).map","MapFile.map",Line)
                  
                  
      P1_MAKEFILE_TEMP.write(Line)              # Print the line in the temp make file, after all the modifications were done !
   
   time.sleep(0.5)   
   P1_MAKEFILE.close()
   P1_MAKEFILE_TEMP.close()
   
   time.sleep(1)
   
   try:                                         # Remove the original Make File
      os.remove(os.path.join(Path,MakeFile))
   except OSError, detail:
      if 2 != detail.errno:
         raise
   
   time.sleep(0.5)
   os.rename(os.path.join(Path,"Temp-"+MakeFile),os.path.join(Path,MakeFile)) # Rename the Temporary Make File to the name of the original make file.

   return(0)


##########################################################
# Misc Operations
##########################################################
# This Code updates the make file with the given parameters
# But, this is not used, since the concept of parameterization is used.

def UpdateMakeFileProcessor(MakeFile, ProcessorName):
   time.sleep(1)
   P1_MAKEFILE = open(MakeFile,'r')               # Now, with the existing device in the make file and the Compiler paths, 
   P1_MAKEFILE_TEMP = open(MakeFile + "temp",'w')  # Re-open the orogonal Make File and create an another temporary make file,
                                                                     # Copy all the lines from the original make file to the temp make file
   for Line in P1_MAKEFILE:                                          # by replacing the device and the compiler paths.
      if re.search("^MP_PROCESSOR_OPTION=",Line):
         Line = ProcessorName + "\n"
      P1_MAKEFILE_TEMP.write(Line)              # Print the line in the temp make file, after all the modifications were done !
   
   time.sleep(1)
   P1_MAKEFILE.close()
   P1_MAKEFILE_TEMP.close()
   
   try:                                         # Remove the original Make File
      os.remove(MakeFile)
   except OSError, detail:
      if 2 != detail.errno:
         raise
   
   time.sleep(0.1)
   os.rename(MakeFile + "temp",MakeFile) # Rename the Temporary Make File to the name of the original make file.





def UpdateMakeFileCompilerPaths(MakeFile, CompilerPathsArray):
   time.sleep(1)
   P1_MAKEFILE = open(MakeFile,'r')               # Now, with the existing device in the make file and the Compiler paths, 
   P1_MAKEFILE_TEMP = open(MakeFile + "temp",'w')  # Re-open the orogonal Make File and create an another temporary make file,
                                                                     # Copy all the lines from the original make file to the temp make file
   for Line in P1_MAKEFILE:                                          # by replacing the device and the compiler paths.
      for Compiler in CompilerPathsArray:
         Keyword = '^' + re.split("=",Compiler)[0] + "="
         if re.search(Keyword,Line):
            Line = Compiler + "\n"
      P1_MAKEFILE_TEMP.write(Line)              # Print the line in the temp make file, after all the modifications were done !
   time.sleep(1)
   P1_MAKEFILE.close()
   P1_MAKEFILE_TEMP.close()
   time.sleep(1)
   try:                                         # Remove the original Make File
      os.remove(MakeFile)
   except OSError, detail:
      if 2 != detail.errno:
         raise
   time.sleep(0.5)
   os.rename(MakeFile + "temp",MakeFile) # Rename the Temporary Make File to the name of the original make file.
   

def UpdateMakeFileLinkerPath(MakeFile, LinkerPath):
   time.sleep(1)
   P1_MAKEFILE = open(MakeFile,'r')               # Now, with the existing device in the make file and the Compiler paths, 
   P1_MAKEFILE_TEMP = open(MakeFile + "temp",'w')  # Re-open the orogonal Make File and create an another temporary make file,
                                                                     # Copy all the lines from the original make file to the temp make file
   for Line in P1_MAKEFILE:                                          # by replacing the device and the compiler paths.
      if re.search("^MP_LINKER_FILE_OPTION=",Line):
         Line = LinkerPath + "\n"
      P1_MAKEFILE_TEMP.write(Line)              # Print the line in the temp make file, after all the modifications were done !
   time.sleep(0.5)
   P1_MAKEFILE.close()
   P1_MAKEFILE_TEMP.close()
   time.sleep(0.5)
   try:                                         # Remove the original Make File
      os.remove(MakeFile)
   except OSError, detail:
      if 2 != detail.errno:
         raise
   time.sleep(0.5)
   os.rename(MakeFile + "temp",MakeFile) # Rename the Temporary Make File to the name of the original make file.





def UpdateMakeFileIncludeDirs(MakeFile, include_dir):
   time.sleep(1)
   P1_MAKEFILE = open(MakeFile,'r')               # Now, with the existing device in the make file and the Compiler paths, 
   P1_MAKEFILE_TEMP = open(MakeFile + "temp",'w')  # Re-open the orogonal Make File and create an another temporary make file,
                                                                     # Copy all the lines from the original make file to the temp make file
   
   for Line in P1_MAKEFILE:                                          # by replacing the device and the compiler paths.
      if re.search("{MP_CC}",Line):
         ary = re.split(" ", Line)
         dirs_updated = 0
         temp1 = ''
         for items in ary:
            temp = items
            if re.search("-I", temp):
               if dirs_updated == 0:
                  dirs_updated = 1
                  temp = "-I" + "\"" + include_dir + "\""
               else:
                  temp = ''
            temp1 = temp1 + temp + " "
         
         Line = temp1.strip(" ")
         
      P1_MAKEFILE_TEMP.write(Line)              # Print the line in the temp make file, after all the modifications were done !
   time.sleep(0.5)
   P1_MAKEFILE.close()
   P1_MAKEFILE_TEMP.close()
   time.sleep(0.5)
   try:                                         # Remove the original Make File
      os.remove(MakeFile)
   except OSError, detail:
      if 2 != detail.errno:
         raise
   time.sleep(0.5)
   os.rename(MakeFile + "temp",MakeFile) # Rename the Temporary Make File to the name of the original make file.





def UpdateMakeFileDependencies(MakeFile, DepLocation):
   P1_MAKEFILE = open(MakeFile,'r')               # Now, with the existing device in the make file and the Compiler paths, 
   P1_MAKEFILE_TEMP = open(MakeFile + "temp",'w')  # Re-open the orogonal Make File and create an another temporary make file,
                                                                     # Copy all the lines from the original make file to the temp make file
   for Line in P1_MAKEFILE:                                          # by replacing the device and the compiler paths.
      
      if re.search("^MP_JAVA_PATH=",Line):
         Line = ""
     
      if re.search("^DEP_GEN=",Line):
      
         Line = "DEP_GEN=java -jar \"" + os.path.join(DepLocation, "extractobjectdependencies.jar") + "\n"
      
      if re.search("^PATH:=",Line) and re.search(":\$\(PATH\)",Line):
         Line = "PATH:=" + DepLocation + ":$(PATH)\n"
      P1_MAKEFILE_TEMP.write(Line)              # Print the line in the temp make file, after all the modifications were done !
   time.sleep(1)
   P1_MAKEFILE.close()
   P1_MAKEFILE_TEMP.close()
   time.sleep(0.5)
   try:                                         # Remove the original Make File
      os.remove(MakeFile)
   except OSError, detail:
      if 2 != detail.errno:
         raise
   time.sleep(0.5)
   os.rename(MakeFile + "temp",MakeFile) # Rename the Temporary Make File to the name of the original make file.




def CreateVer2LocalMakeFile(MakeFileLocation, CompilerPathsArray, MiscIncludePaths):
   time.sleep(1)
   NewMakeFileName = os.path.split(MakeFileLocation)[1]
   NewMakeFileName = os.path.splitext(NewMakeFileName)[0]
   
   NewMakeFileName = "Makefile-local-" + re.sub("Makefile-",'',NewMakeFileName) + ".mk"
   
   NewMakeFileName = os.path.join(os.path.split(MakeFileLocation)[0], NewMakeFileName)
   
   TextTobePrinted = ''
   
   TextTobePrinted = TextTobePrinted + "SHELL=cmd.exe\n"
   
   TextTobePrinted = TextTobePrinted + "PATH_TO_IDE_BIN=" + MiscIncludePaths + "\n"
   
   TextTobePrinted = TextTobePrinted + "PATH:=" + MiscIncludePaths + ":$(PATH)\n" 
   
   #TextTobePrinted = TextTobePrinted + "MP_JAVA_PATH=\"C:\Program Files\Java\jre6/bin/\"\n"
   
   TextTobePrinted = TextTobePrinted + "OS_CURRENT=\"$(shell uname -s)\"\n"
   
   TextTobePrinted = TextTobePrinted + "DEP_GEN=java -jar \"" + os.path.join(MiscIncludePaths, "extractobjectdependencies.jar") + "\"\n" 
   
   kw = []
   
   
   for CompilerPaths in CompilerPathsArray:
      kw.append(re.split("=",CompilerPaths)[0])
      
      #TextTobePrinted = TextTobePrinted + CompilerPaths + "\n"
   
   fptr = open(NewMakeFileName,"r")
   
   TextTobePrinted = ''
   
   for line in fptr:
      if re.search("=",line):
         for i in range(len(kw)):
            if re.split("=",line)[0] == kw[i]:
               line = CompilerPathsArray[i] + "\n"
      
      TextTobePrinted = TextTobePrinted + line
   time.sleep(1)
   fptr.close()
   
   time.sleep(0.5)
   
   NewMakeFileNamePtr = open(NewMakeFileName,"w")
   NewMakeFileNamePtr.write(TextTobePrinted)
   NewMakeFileNamePtr.close()

escape_dict={'\a':r'\a',
           '\b':r'\b',
           '\c':r'\c',
           '\f':r'\f',
           '\n':r'\n',
           '\r':r'\r',
           '\t':r'\t',
           '\v':r'\v',
           '\'':r'\'',
           '\"':r'\"',
           '\0':r'\0',
           '\1':r'\1',
           '\2':r'\2',
           '\3':r'\3',
           '\4':r'\4',
           '\5':r'\5',
           '\6':r'\6',
           '\7':r'\7',
           '\8':r'\8',
           '\9':r'\9'}

def raw(text):
    """Returns a raw string representation of text"""
    new_string=''
    for char in text:
        try: new_string+=escape_dict[char]
        except KeyError: new_string+=char
    return new_string

def find_compilerVersion(xc_path):
   if 'win32' == sys.platform :
      regex = os.sep + os.sep
   else:
      regex = os.sep
   if re.search('xc8',re.sub(regex,' ',repr(xc_path.lower()))):
      if 'win32' == sys.platform :
         try :
            xc8_compiler_version = subprocess.check_output([os.path.join(os.path.sep,repr(raw(xc_path)).strip("''"),'bin','xc8.exe'),'--ver'])
            xc8_compiler_version = xc8_compiler_version.split('\n')[0]
            xc8_compiler_version = re.sub('.+v','',xc8_compiler_version.lower())
            xc8_compiler_version = xc8_compiler_version.strip()
            try:
               float(xc8_compiler_version)                     
            except:
               print '--ver execution of the compiler did'/'nt yield a float result.String Val = %s' %(xc8_compiler_version) 
               xc8_compiler_version = None
         except subprocess.CalledProcessError as Cpe:
            print 'Problems obtaining XC8 Version, Ignore this error if XC8 not relevant for job:', Cpe
            xc8_compiler_version = None
         except OSError as Ose:
            print >> sys.stderr, "Problems obtaining XC8 Version, Ignore this error if XC8 not relevant for job: ", Ose
            xc8_compiler_version = None
      else :
         try:
            xc8_compiler_version = subprocess.check_output([os.path.join(os.path.sep,xc_path,'bin','xc8'),'--ver'])
            xc8_compiler_version = xc8_compiler_version.split('\n')[0]
            xc8_compiler_version = re.sub('.+v','',xc8_compiler_version.lower())
            xc8_compiler_version = xc8_compiler_version.strip()
            try:
               float(xc8_compiler_version)                     
            except:
               print '--ver execution of the compiler did'/'nt yield a float result.String Val = %s' %(xc8_compiler_version)
               xc8_compiler_version = None
         except subprocess.CalledProcessError as Cpe:
            print 'Problems obtaining XC8 Version, Ignore this error if XC8 not relevant for job:', Cpe
            xc8_compiler_version = None
         except OSError as Ose:
            print >> sys.stderr, "Problems obtaining XC8 Version, Ignore this error if XC8 not relevant for job: ", Ose
            xc8_compiler_version = None
      return xc8_compiler_version
   elif re.search('xc16',re.sub(regex,' ',repr(xc_path.lower()))):
      if 'win32' == sys.platform:
         try:            
            xc16_compiler_version = subprocess.check_output([os.path.join(os.path.sep,repr(raw(xc_path)).strip("''"),'bin','xc16-gcc.exe'),'--version'])
            xc16_compiler_version = xc16_compiler_version.split('\n')[1]
            xc16_compiler_version = re.sub('part support version: ','',xc16_compiler_version.lower())
            xc16_compiler_version = re.sub('[(].[)]','',xc16_compiler_version)
            xc16_compiler_version = xc16_compiler_version.strip()
            try:
               float(xc16_compiler_version)
            except:
               print '--version execution of the compiler did'/'nt yield a float result.String Val = %s' %(xc16_compiler_version)
               xc16_compiler_version = None
         except subprocess.CalledProcessError as Cpe:
            print 'Problems obtaining XC16 Version, Ignore this error if XC16 not relevant for job:', Cpe
            xc16_compiler_version = None
         except OSError as Ose:
            print >> sys.stderr, "Problems obtaining XC16 Version, Ignore this error if XC16 not relevant for job: ", Ose
            xc16_compiler_version = None
      else:
         try:
            xc16_compiler_version = subprocess.check_output([os.path.join(os.path.sep,xc_path,'bin','xc16-gcc'),'--version'])
            xc16_compiler_version = xc16_compiler_version.split('\n')[1]
            xc16_compiler_version = re.sub('part support version: ','',xc16_compiler_version.lower())
            xc16_compiler_version = re.sub('[(].[)]','',xc16_compiler_version)
            xc16_compiler_version = xc16_compiler_version.strip()
            try:
               float(xc16_compiler_version)
            except:
               print '--version execution of the compiler did'/'nt yield a float result.String Val = %s' %(xc16_compiler_version)
               xc16_compiler_version = None
         except subprocess.CalledProcessError as Cpe:
            print 'Problems obtaining XC16 Version, Ignore this error if XC16 not relevant for job:', Cpe
            xc16_compiler_version = None
         except OSError as Ose:
            print >> sys.stderr, "Problems obtaining XC16 Version, Ignore this error if XC16 not relevant for job: ", Ose
            xc16_compiler_version = None
      return xc16_compiler_version
   elif re.search('xc32',re.sub(regex,' ',repr(xc_path.lower()))):
      if 'win32' == sys.platform:
         try:
            xc32_compiler_version = subprocess.check_output([os.path.join(os.path.sep,repr(raw(xc_path)).strip("''"),'bin','xc32-gcc.exe'),'--version'])
            xc32_compiler_version = xc32_compiler_version.split('\n')[1]
            xc32_compiler_version = re.sub('part support version: ','',xc32_compiler_version.lower())
            xc32_compiler_version = re.sub('[(].[)]','',xc32_compiler_version)
            xc32_compiler_version = xc32_compiler_version.strip()
            try:
               float(xc32_compiler_version)
            except:
               print '--version execution of the compiler did'/'nt yield a float result.String Val = %s' %(xc32_compiler_version)
               xc32_compiler_version = None
         except subprocess.CalledProcessError as Cpe:
            print 'Problems obtaining XC32 Version, Ignore this error if XC32 not relevant for job:', Cpe
            xc32_compiler_version = None
         except OSError as Ose:
            print >> sys.stderr, "Problems obtaining XC32 Version, Ignore this error if XC32 not relevant for job: ", Ose
            xc32_compiler_version = None
      else:
         try:
            xc32_compiler_version = subprocess.check_output([os.path.join(os.path.sep,xc_path,'bin','xc32-gcc'),'--version'])
            xc32_compiler_version = xc32_compiler_version.split('\n')[1]
            xc32_compiler_version = re.sub('part support version: ','',xc32_compiler_version.lower())
            xc32_compiler_version = re.sub('[(].[)]','',xc32_compiler_version)
            xc32_compiler_version = xc32_compiler_version.strip()
            try:
               float(xc32_compiler_version)
            except:
               print '--version execution of the compiler did'/'nt yield a float result.String Val = %s' %(xc32_compiler_version)
               xc32_compiler_version = None
         except subprocess.CalledProcessError as Cpe:
            print 'Problems obtaining XC32 Version, Ignore this error if XC32 not relevant for job:', Cpe
            xc32_compiler_version = None
         except OSError as Ose:
            print >> sys.stderr, "Problems obtaining XC32 Version, Ignore this error if XC32 not relevant for job: ", Ose
            xc32_compiler_version = None
      return xc32_compiler_version
   else:
      return None

def peruse_configurations_in_project_xml(project_configuration_xml):   
   if (os.path.exists(project_configuration_xml)):
      print 'Scanning the configurations in file %s' %(project_configuration_xml)
      try:
         configuration_list = []         
         for (event, node) in iterparse(project_configuration_xml, ['start', 'end', 'start-ns', 'end-ns']):
            if node.tag !=  'conf':
               continue   
            if (node.tag == 'conf' and event == 'start'):
               configuration_list.append(node.attrib['name'])
         return configuration_list
      except:
         e = sys.exc_info()[0]
         print 'Unable to peruse the the project configuration with error : %s' %(e)
         return None
   else:
      raise OSError(errno.ENOENT, 'File: ' + project_configuration_xml + ' is not present.')

def create_mod_proj_xml_and_get_all_configs(compilertypeversion_dict,project_configuration_xml):
   if os.path.isfile(project_configuration_xml):         
      try:
         configuration_list = []         
         for (event, node) in iterparse(project_configuration_xml, ['start', 'end', 'start-ns', 'end-ns']):
            if node.tag !=  'conf':
               continue   
            if (node.tag == 'conf' and event == 'start'):
               configuration_list.append(node.attrib['name'])
            project_config_contains_xc = False
            index = -1
            if (event == 'start'):
               for i in node.iter('languageToolchain'):
                  if (i.text.lower() in compilertypeversion_dict.keys()):
                     project_config_contains_xc = True
                     index = compilertypeversion_dict.keys().index(i.text.lower())
               if (project_config_contains_xc == True):
                  for i in node.iter('languageToolchainVersion'):
                     if (i.text == None) :
                        org_ver = 'No Value'
                     else:
                        org_ver = str(i.text)
                     print 'Changing %s Originalversion: %s to NewVersion: %s' %(compilertypeversion_dict.keys()[index],org_ver,str(compilertypeversion_dict[compilertypeversion_dict.keys()[index]]))
                     i.clear()
                     i.text = compilertypeversion_dict[compilertypeversion_dict.keys()[index]]            
         modifiedXML_file_Name = os.path.join(os.path.sep,os.path.dirname(project_configuration_xml),'configurations_modified.xml')
         print 'Writing modified configuration file %s' %(modifiedXML_file_Name)
         ElementTree(node).write(modifiedXML_file_Name)
         if os.path.exists(modifiedXML_file_Name):
            try:
               if os.path.isfile(project_configuration_xml):
                  print 'Removing orignal config file at %s.' %(project_configuration_xml)
                  os.remove(project_configuration_xml)
                  print 'Renaming modified config file at %s to original config file at %s' %(modifiedXML_file_Name,project_configuration_xml)
                  os.rename(modifiedXML_file_Name,project_configuration_xml)
            except:
               e = sys.exc_info()[0]
               print 'Unable to replace the modified configuration file with the original project config with error : %s' %(e)
               return None
         return configuration_list         
      except:
         e = sys.exc_info()[0]
         print 'Unable to modify the the project configuration with error : %s' %(e)
   else:
      print 'configuration file is not preset at %s' %(project_configuration_xml)
      return None  

def del_modified_config_files_restore_org(project_configuration_xml):
   if (os.path.isfile(project_configuration_xml) and os.path.isfile(project_configuration_xml + '.tmp')):
      print 'Removing modified configuration file %s' %(project_configuration_xml)
      os.remove(project_configuration_xml)
      print 'Renaming old config file to %s' %(project_configuration_xml)
      shutil.copyfile(project_configuration_xml + '.tmp',project_configuration_xml)
      print 'Removing tmp configuration file at %s' %(project_configuration_xml + '.tmp')
      os.remove(project_configuration_xml + '.tmp')
   else:
      return
   
def re_create_make_files(path_of_mcpr_file, project_path, include_dirs):
   time.sleep(1)
   enable_make_file_creation = 0   
   mplab_x_installation_directory = ''
   make_file_creator_bin_path = ''
   xc8_compiler_version = None
   xc16_compiler_version = None
   xc32_compiler_version = None

   # Getting the make file creator utility path from mcpr file
   #####################################
   if os.path.exists(path_of_mcpr_file):
      mcpr_f_ptr = open(path_of_mcpr_file,"r")
      for line in mcpr_f_ptr:
         line = line.strip("\n")
         line = line.strip("\r")
         line = line.strip(" ")
         if re.search("^_MPLAB_X_INSTALLATION_PATH_",line):
            mplab_x_installation_directory = re.split("=",line)[1]

         if re.search("^_XC8_PATH_",line):
            xc8_installation_directory = re.split("=",line)[1]
            if (os.path.exists(xc8_installation_directory)):
               xc8_compiler_version = find_compilerVersion(xc8_installation_directory)
            else:
               print 'Searched line = %s' %(line)
               print 'XC8 Installation directory does not exist, Ignore this error if XC8 not relevant for job.'
               xc8_compiler_version = None
         if re.search("^_XC16_PATH_",line):
           xc16_installation_directory = re.split("=",line)[1]
           if (os.path.exists(xc16_installation_directory)):
              xc16_compiler_version = find_compilerVersion(xc16_installation_directory)
           else:
              print 'Searched line = %s' %(line)
              print 'XC16 Installation directory does not exist, Ignore this error if XC16 not relevant for job.'
              xc16_compiler_version = None
         if re.search("^_XC32_PATH_",line):
           xc32_installation_directory = re.split("=",line)[1]
           if (os.path.exists(xc32_installation_directory)):
              xc32_compiler_version = find_compilerVersion(xc32_installation_directory)
           else:
              print 'Searched line = %s' %(line)
              print 'XC32 Installation directory does not exist, Ignore this error if XC32 not relevant for job.'
              xc32_compiler_version = None

         if 'darwin' == sys.platform:
            # /Applications/microchip/mplabx215/mplab_ide.app/Contents/Resources/mplab_ide/bin
            make_file_creator_bin_path = "mplab_ide.app/Contents/Resources/mplab_ide/bin"
         else:
            make_file_creator_bin_path = "mplab_ide/bin"
         
         #if re.search("^_MAKE_FILE_UTIL_PATH_",line):
         #   make_file_creator_bin_path = re.split("=",line)[1]         
      mcpr_f_ptr.close()
   #####################################
   
   make_file_creator_bin = ''
   make_file_creator_batch_file = ''
   
   # Determining the make file creator utility binary, depending upon the OS
   #####################################
   if 'win32' == sys.platform:
      make_file_creator_bin = "prjMakefilesGenerator.bat"
      make_file_creator_batch_file = "make_file_creation.bat"
   elif'linux2' == sys.platform:                                 # Linux
      make_file_creator_bin = "prjMakefilesGenerator.sh"
      make_file_creator_batch_file = "make_file_creation.sh"
   elif 'darwin' == sys.platform:                                 # MAC 
      make_file_creator_bin = "prjMakefilesGenerator.sh"
      make_file_creator_batch_file = "make_file_creation.sh"
   #####################################
   
   make_file_creator_full_path = os.path.join(mplab_x_installation_directory, make_file_creator_bin_path)
   
   make_file_creator_bin_full_path = os.path.join(make_file_creator_full_path, make_file_creator_bin)
   
   make_file_creator_bin_full_path = os.path.normpath(make_file_creator_bin_full_path)
   
   if make_file_creator_full_path != '' and os.path.exists(make_file_creator_bin_full_path):
      
      enable_make_file_creation = 1
   if enable_make_file_creation == 1:
   
      batch_file_string = ''
      projConfigXMLPath = os.path.join(os.path.sep,project_path,'nbproject','configurations.xml')
      print 'Creating a tmp copy of orignal config file at %s .' %(projConfigXMLPath)
      shutil.copyfile(projConfigXMLPath,projConfigXMLPath + '.tmp')
      
      if (xc8_compiler_version != None or xc16_compiler_version !=None or xc32_compiler_version != None):
         dict_MCPR_compilers = {}
         if (xc8_compiler_version != None):
            print 'MCPR XC8Version: ' + str(xc8_compiler_version)
            dict_MCPR_compilers['xc8'] = xc8_compiler_version
         if (xc16_compiler_version != None):
            print 'MCPR XC16Version: ' + str(xc16_compiler_version)
            dict_MCPR_compilers['xc16'] = xc16_compiler_version
         if (xc32_compiler_version != None):
            print 'MCPR XC32Version: ' + str(xc32_compiler_version)
            dict_MCPR_compilers['xc32'] = xc32_compiler_version
         create_mod_proj_xml_and_get_all_configs(dict_MCPR_compilers,projConfigXMLPath)

      
      if 'win32' == sys.platform:
         batch_file_string = batch_file_string + os.path.splitdrive(make_file_creator_full_path)[0] + "\n"

      batch_file_string = batch_file_string + "cd " + '"' + os.path.normpath(make_file_creator_full_path) + '"' + "\n"

      batch_file_string = batch_file_string + '"' + make_file_creator_bin_full_path + '"' + " " + '"' + project_path + '"' + "\n"   

      batch_file_ptr = open(make_file_creator_batch_file,"w")
      batch_file_ptr.write(batch_file_string)
      batch_file_ptr.close()

      if (xc8_installation_directory!= None):
         print 'Adding %s to Environment variable PATH' %(os.path.join(xc8_installation_directory,'bin')) 
         os.environ['PATH'] = os.path.join(xc8_installation_directory,'bin') + os.pathsep + os.environ['PATH']
         if ('linux2' == sys.platform):
            os.system('export PATH='+os.path.join(xc8_installation_directory,'bin')+':$PATH')
      if (xc16_installation_directory!= None):
         print 'Adding %s to Environment variable PATH' %(os.path.join(xc16_installation_directory,'bin')) 
         os.environ['PATH'] = os.path.join(xc16_installation_directory,'bin') + os.pathsep + os.environ['PATH']
         if ('linux2' == sys.platform):
            os.system('export PATH='+os.path.join(xc16_installation_directory,'bin')+':$PATH')
      if (xc32_installation_directory!= None):
         print 'Adding %s to Environment variable PATH' %(os.path.join(xc32_installation_directory,'bin')) 
         os.environ['PATH'] = os.path.join(xc32_installation_directory,'bin') + os.pathsep + os.environ['PATH']
         if ('linux2' == sys.platform):
            os.system('export PATH='+os.path.join(xc32_installation_directory,'bin')+':$PATH')
      if ('linux2' == sys.platform):
         if (os.path.exists('~/.bashrc')):
            os.system('. ~/.bashrc')

      projectConfigurations = peruse_configurations_in_project_xml(projConfigXMLPath)
      expectedMakeFilePaths = sorted(map(lambda x:os.path.join(os.path.dirname(projConfigXMLPath),'Makefile-'+x+'.mk'),projectConfigurations))

      exit_loop = 0
      exit_count = 0
      while exit_loop == 0:
      
         exit_status = 1
         
         if 'win32' == sys.platform:
            exit_status = os.system('"' + make_file_creator_batch_file + '"')
         else:
            exit_status = os.system('sh "' + make_file_creator_batch_file + '"')   


         if exit_status != 0:
            time.sleep(10)
            exit_count = exit_count + 1
            if exit_count >= 20:
               exit_loop = 1
         else:
            exit_loop = 1
            exit_with_error = 0
      
      if (xc8_installation_directory!= None):
         path_list = os.environ['PATH'].split(os.pathsep)
         print 'Removing %s from Environment variable PATH' %(os.path.join(xc8_installation_directory,'bin')) 
         if os.path.join(xc8_installation_directory,'bin') in path_list:
            path_list.remove(os.path.join(xc8_installation_directory,'bin'))         
         os.environ['PATH'] = os.pathsep.join(path_list)
      if (xc16_installation_directory!= None):
         path_list = os.environ['PATH'].split(os.pathsep)
         print 'Removing %s from Environment variable PATH' %(os.path.join(xc16_installation_directory,'bin'))
         if os.path.join(xc16_installation_directory,'bin') in path_list: 
            path_list.remove(os.path.join(xc16_installation_directory,'bin'))         
         os.environ['PATH'] = os.pathsep.join(path_list)
      if (xc32_installation_directory!= None):
         path_list = os.environ['PATH'].split(os.pathsep)
         print 'Removing %s from Environment variable PATH' %(os.path.join(xc32_installation_directory,'bin'))
         if os.path.join(xc32_installation_directory,'bin') in path_list: 
            path_list.remove(os.path.join(xc32_installation_directory,'bin'))         
         os.environ['PATH'] = os.pathsep.join(path_list)

      makeFilesInProject = [f for f in os.listdir(repr(os.path.dirname(projConfigXMLPath)).strip("'")) if (f.endswith('.mk') and f != 'Makefile-impl.mk' and f!='Makefile-variables.mk' and not('Makefile-local-' in f))]
      makeFilesInProjectPaths = sorted(map(lambda x:os.path.join(os.path.dirname(projConfigXMLPath),x),makeFilesInProject))
      if (len(expectedMakeFilePaths) != len(makeFilesInProjectPaths)):
         print 'Make file creation yielded less files than expected.'
         del_modified_config_files_restore_org(os.path.join(os.path.sep,project_path,'nbproject','configurations.xml'))
         #sys.exit(403)

      del_modified_config_files_restore_org(os.path.join(os.path.sep,project_path,'nbproject','configurations.xml'))

      if include_dirs != '':
         _project_make_files, _count = FindMakeFile(os.path.join(project_path, "nbproject"))
         for mk_file in _project_make_files:
            make_file_full_path = os.path.join(project_path, "nbproject")
            make_file_full_path = os.path.join(make_file_full_path, mk_file)
            UpdateMakeFileIncludeDirs(make_file_full_path, include_dirs)
         
         
   '''
   _project_make_files, _count = FindMakeFile(os.path.join(project_path, "nbproject"))
   
   for i in range(len(_project_make_files)):
      pp = []
      pp.append(_project_make_files[i])
      _CompatibleMakeFileList,_CompatibleMakeFileCount,_CompatibleMakeDevice,_CompatibleMakeCompiler,_CompilerMode,_CompilerPathsArray,_MakeErrorArray, _MakeVersion = FindCompatibleMakeFile(os.path.join(project_path,"nbproject"), pp,"","",path_of_mcpr_file)
      p = os.path.join(project_path,"nbproject")
      p = os.path.join(p,_project_make_files[i])
      CreateVer2LocalMakeFile(p, _CompilerPathsArray[0], "A")
   '''

def re_create_misc_make_files(project_path):
   time.sleep(1)
   var_path = os.path.join(project_path,"nbproject")
   impl_path = os.path.join(project_path,"nbproject")
   
   if os.path.exists(var_path):
   
      var_path = os.path.join(var_path,"Makefile-variables.mk")
      impl_path = os.path.join(impl_path,"Makefile-impl.mk")
      
      if not os.path.exists(var_path):
         fptr = open(var_path,"w")
         time.sleep(0.1)
         fptr.close()
      
      if not os.path.exists(impl_path):
         fptr = open(impl_path,"w")
         time.sleep(0.1)
         fptr.close()     