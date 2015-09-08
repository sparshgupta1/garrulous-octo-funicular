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
import xml_operation
import misc_operations
import make_operations

#############################################################
#### This Routine Finds the operating system and creates the  
#### executor, which executes the make file in a 
#### batch/shell scripts, which puts the messages into a log file.
#### This Routene also updates the Make File, resides in the
#### Project directory, to generate the images in Debug Mode 
#### because, by default, compiling Make File generates the
#### images in Release Mode. which cannot be used for Debugging 
#### purposws
#############################################################

def CreateExecutor(P1_ProjectLocation,MakeFile,Compiler,CompilerPathsArray,Device,PerofrmRunTimeTest,CompilerPathRefFile,MakeFileVersion):
   
   MakeFileLocation = os.path.join(P1_ProjectLocation,"nbproject")
   MakeFileLocation = os.path.join(MakeFileLocation,MakeFile)
   
   ExecutorFileName = ''
   
   ###########################################################                # Added For Version 1.8
   # Added by Shankar for Run Time Tests
   
   #Found_TYPE_IMAGEeqDEBUG_RUN = 0
   #ReadEditableMakeFile = os.path.join(P1_ProjectLocation,"Makefile")         # The Make File to be edited will be residing in the Project directory
   #ReadEditableMakeFilePtr = open(ReadEditableMakeFile,'r')                   # opening it in Read Mode
   #for Line in ReadEditableMakeFilePtr:
   #   if re.search("TYPE_IMAGE=DEBUG_RUN", Line):                             # if the Variable TYPE_IMAGE, is equivated to DEBUG_RUN, then the image generated will
   #      Found_TYPE_IMAGEeqDEBUG_RUN = 1                                      # be for Debug Mode.
   #   elif re.search("TYPE_IMAGE = DEBUG_RUN", Line):                         # In the Make File, if the variable is already equivated to the specified value, then 
   #      Found_TYPE_IMAGEeqDEBUG_RUN = 1                                      # no need to edit the existing make File
   #ReadEditableMakeFilePtr.close()
   
   #if Found_TYPE_IMAGEeqDEBUG_RUN == 0:                                       # If the file does not has the variable, equivated already, then edit the file.
   #   ReadEditableMakeFilePtr = open(ReadEditableMakeFile,'r')
   #   WriteEditableMakeFile = os.path.join(P1_ProjectLocation,"Makefile_temp")# Create a Temp file, then copy all Lines from the original File and then 
   #   WriteEditableMakeFilePtr = open(WriteEditableMakeFile,'w')              # add this line also in an appropriate place and save it.
   #   
   #   for Line in ReadEditableMakeFilePtr:
   #      if re.search("^# Environment",Line):
   #         Line = Line + "TYPE_IMAGE = DEBUG_RUN\n"
   #      WriteEditableMakeFilePtr.write(Line)
   #
   #   ReadEditableMakeFilePtr.close()                                         # Once done, close all the files, delete the original File, rename the 
   #   WriteEditableMakeFilePtr.close()                                        # temp file to original File Name.

   #   try:                                         # Remove the original Make File
   #      os.remove(os.path.join(P1_ProjectLocation, "Makefile"))
   #      os.rename(os.path.join(P1_ProjectLocation,"Makefile_temp"),os.path.join(P1_ProjectLocation,"Makefile")) # Rename the Temporary Make File to the name of the original make file.
   #   except OSError, detail:
   #      if detail.errno != 2:
   #         raise 
   
   # End of the Run Time tests adding
   ###########################################################
   # Creation of Batch file/Shell file for creating the Make File and Logging the Compiler Log Messages is here !
   
   MakeCommandPath = "make"
   
   MiscIncludePaths = ''
   
   '''
   CompilerPathRefFilePtr = open(CompilerPathRefFile,"r")

   for Line in CompilerPathRefFilePtr:
      Line = Line.strip("\n|\r")
      SS = "_MAKE_PATH_"+ str(MakeFileVersion) + "_"

      if re.search(SS,Line):
         MakeCommandPath = '"' + re.split("=",Line)[1] + '"'

      if re.search("_MISC_PATH_",Line):
         MiscIncludePaths = re.split("=",Line)[1]
         
   CompilerPathRefFilePtr.close()
   '''
   
   LinkerOption = xml_operation.ExtractLinker(P1_ProjectLocation,MakeFile)
   
   LogFile = os.path.join(os.getcwd(),"LogFile.txt")     # For logging the message into the LogFile.txt.
   
   var = ''
   
   if 'win32' == sys.platform:
      var = P1_ProjectLocation[:2] + "\n"
      
   var =  var + "cd " + '"' + P1_ProjectLocation + '"' 
   var = var + "\n" + MakeCommandPath 
   
   
   if 1 == MakeFileVersion:
      if 'win32' == sys.platform:
         var = var + ' \"MP_MISC_BIN_PATH=' + MiscIncludePaths + '\" \"SHELL=cmd.exe\" \"MKDIR=gnumkdir -p\"'

      else:  
         #var = var + ' \"PATH:=' + MiscIncludePaths + ':$(PATH)\" \"SHELL=''\" \"MKDIR=mkdir -p\"'
         var = var + ' \"MP_MISC_BIN_PATH=' + MiscIncludePaths + ' SHELL=sh \"MKDIR=mkdir -p\"'

   var = var + " -f nbproject/" + MakeFile + " SUBPROJECTS= .clean-conf"
   
   
   var = var + "\n" + MakeCommandPath + " "
   #if 0 == PerofrmRunTimeTest:
   #   var = var + "TYPE_IMAGE=!DEBUG_RUN"
   #else:
   var = var + "TYPE_IMAGE=DEBUG_RUN"
      
   var = var + " MP_PROCESSOR_OPTION=" + Device
   
   if [] == LinkerOption:
      if "C30" == Compiler:                                             #  or Compiler == "C30":
         var = var + " MP_LINKER_FILE_OPTION=\",-T" + "p" + Device + ".gld\""   
      if "C32" == Compiler:                                             #  or Compiler == "C32":
         var = var + " MP_LINKER_FILE_OPTION=\"\""    

   else:
         #LinkerOption[0] = re.sub(r"\\",r"/",LinkerOption[0])
         #LinkerOption[0] = re.sub(" ",r"\\ ",LinkerOption[0])
         var = var + " MP_LINKER_FILE_OPTION=,--script=\"" + misc_operations.ConvertPathToMPXParameterFormat(LinkerOption[0],MakeFileVersion) + '"'
   
   for CompilerPath in CompilerPathsArray:
      CompilerPath = re.sub(r"\n|\r",'',CompilerPath)
      #CompilerPath = re.sub(r"=","=\"",CompilerPath)

      var = var + " \"" + CompilerPath + '"'
   
   if 1 == MakeFileVersion:
      if 'win32' == sys.platform:
         var = var + ' \"MP_MISC_BIN_PATH=' + MiscIncludePaths + '\" \"SHELL=cmd.exe\" \"MKDIR=gnumkdir -p\"'

      else:  
         #var = var + ' \"PATH:=' + MiscIncludePaths + ':$(PATH)\" \"SHELL=''\" \"MKDIR=mkdir -p\"'
         var = var + ' \"MP_MISC_BIN_PATH=' + MiscIncludePaths + ' SHELL=sh \"MKDIR=mkdir -p\"'

   
   
   var = var + " -f nbproject/" + MakeFile + " SUBPROJECTS= .build-conf >> " + '"' + LogFile + '"' + " 2>&1\n"

   # Working var = P1_ProjectLocation[:2] + "\ncd " + '"' + P1_ProjectLocation + '"' + "\nmake clean CONF=" + MakeFile[9: -3] + "\nmake CONF=" + MakeFile[9: -3] + " >> " + '"' + LogFile + '"' + " 2>&1\n"
   # var = P1_ProjectLocation[:2] + "\ncd " + '"' + P1_ProjectLocation + '"' + "\nmake clean CONF=" + MakeFile[9: -3] + "\nmake CONF=" + MakeFile[9: -3] + " >> " + '"' + LogFile + '"' + " 2>&1\n"

   ExecutorFileName = "Build_Conf_" + MakeFile[9: -3]

   
   if 'win32' == sys.platform:                           # In Case of Win 32, create a .bat File
      ###########################################
      # This code determines ans prints the exit status of the make command
      var = var + "\nIF ERRORLEVEL 1 goto failed"
      var = var + "\n@echo Make command exit status: No Errors >> " + '"' + LogFile + '"' + " 2>&1"
      var = var + "\ngoto end"
      var = var + "\n:failed"
      var = var + "\n@echo Make command exit status: Exit with Errors >> " + '"' + LogFile + '"' + " 2>&1"
      var = var + "\ngoto end"
      var = var + "\n:end"
      ###########################################
      
      PrintTemp = os.path.join(P1_ProjectLocation,(ExecutorFileName + ".bat"))
   
   else:                                                 # If Non-Windows OS, (Linux and MAC), create Shell File.
      # var = "\ncd " + '"' + P1_ProjectLocation + '"' + "\nmake clean CONF=" + MakeFile[9: -3] + "\nmake CONF=" + MakeFile[9: -3] + " >> " + '"' + LogFile + '"' + " 2>&1\n"
      
      ###########################################
      # This code determines ans prints the exit status of the make command
      var = var + "\nif test $? -eq 0"
      var = var + "\nthen"
      var = var + "\necho Make command exit status: No Errors >> " + '"' + LogFile + '"' + " 2>&1"
      var = var + "\nelse"
      var = var + "\necho Make command exit status: Exit with Errors >> " + '"' + LogFile + '"' + " 2>&1"
      var = var + "\nfi"
      ###########################################   
      
      PrintTemp = os.path.join(P1_ProjectLocation,(ExecutorFileName + ".sh"))

   
   P1_Temp = open(PrintTemp,'w')
   P1_Temp.write(var)
   P1_Temp.close()
   
   return(PrintTemp)


def GetNumberOfLines(File):
   
   LineCount = 0
   
   if os.path.exists(File):   
   
      FileTempCopy = File + "Temp"
      shutil.copyfile(File,FileTempCopy)
      FileTempCopyPtr = open(FileTempCopy,"r")

      for Line in FileTempCopyPtr:
         LineCount = LineCount + 1

      FileTempCopyPtr.close()
      time.sleep(0.1)
      os.remove(FileTempCopy)
   
   return(LineCount)
   


#############################################################
#### This Routine Executes the given batch/shell file, 
#### depending upon the OS 
#############################################################

def ExecuteExecutor(File,MakeFile):
   
   HangDetected = 0
   
   '''
   #########################################################
   MkFullPath = os.path.join("nbproject",MakeFile)
   MkFullPath = os.path.join(os.path.split(File)[0],MkFullPath)
   
   MkFilePtr = open(MkFullPath,"r")
   
   NoOfSrcFiles = 0
   
   for Line in MkFilePtr:
      if re.search("\$\{MP_CC\}",Line):
         NoOfSrcFiles = NoOfSrcFiles + 1
   
   MkFilePtr.close()
   NoOfSrcFiles = NoOfSrcFiles / 2

   TimeOutValue = NoOfSrcFiles * 60 # Providing 1 Min for each file
   #########################################################
   '''
   
   LogFile = os.path.join(os.getcwd(),MakeFile + ".log")  # Log file to log the compiler messages
   
   time_for_build = 0
   
   if 'win32' == sys.platform:                        # IOnly in case of Win 32, use subprocess.
      TempCWD = os.getcwd()
      os.chdir(os.path.split(File)[0])
      File = re.sub(r"/",r"\\",File)
      var = '"' + File + '"'
      Process1 = subprocess.Popen(var)
      
      
      
      TimeOut = 0
      OldLineCount = 0
      NewLineCount = 0
      
      while(None == Process1.poll()):                 # Check for the existance of the process
         time.sleep(1)
         
         time_for_build = time_for_build + 1
         
         NewLineCount = GetNumberOfLines(LogFile)
         
         if NewLineCount != OldLineCount:
            
            OldLineCount = NewLineCount
            TimeOut = 0

         TimeOut = TimeOut + 1
         
         if TimeOut >= 600:
            os.system("taskkill /PID " + str(Process1.pid) + " /F /T")   # Kill the process, in case of timeout.
            HangDetected = 1
            arbs_print.Console("\n\nError !! Hang Detected\n\n")

      os.chdir(TempCWD)

      
   else:
   
      var = ["sh", File]
      Process1 = subprocess.Popen(var)
      
      TimeOut = 0
      OldLineCount = 0
      NewLineCount = 0
      
      while(None == Process1.poll()):                 # Check for the existance of the process
         time.sleep(1)
         
         time_for_build = time_for_build + 1
         
         NewLineCount = GetNumberOfLines(LogFile)
         
         if NewLineCount != OldLineCount:
            
            OldLineCount = NewLineCount
            TimeOut = 0

         TimeOut = TimeOut + 1
         
         
   
   time.sleep(2)
   
   Message = ''
   
   if os.path.exists(LogFile):
      try:
         LogFilePtr = open(LogFile,'r')

         for Line in LogFilePtr:
            Message = Message + Line

         LogFilePtr.close()
         
      except:
         Message = Message + "\n***Error: Unable to access Compiler Message Log File. Hang Detected and the compiler still holds the log file. \n***This ERROR Message is reported by ARBS\nMake command exit status: Exit with Errors"
   else:
      Message = Message + "\n***Error: Compiler Message Log File not found\n***This ERROR Message is reported by ARBS\nMake command exit status: Exit with Errors"
   
   
   if HangDetected == 0:
      if os.path.exists(LogFile):
         try:
            os.remove(LogFile)
         except:
            arbs_print.Console("\nError: Unable to delete the Compiler Messages log file. Compiler still holds the file")
   else:
      Message = Message + "\n***Error: Hang Detected while executing above command, ARBS killed the process and exited. \n***Error: Above command was not responsive for more than 600 Seconds. \n***This ERROR Message is reported by ARBS\nMake command exit status: Exit with Errors"

   arbs_print.LogFile(Message)  
   arbs_print.LogFile("BUILD_DURATION: " + str(time_for_build) + " Seconds") 
#   try:
#      os.remove(File)
#   except OSError, detail:
#      if detail.errno != 2:
#         raise  
   return(0)



#########################################################
#########################################################
#########################################################
def detectCPUs():
   """
   Detects the number of CPUs on a system. Cribbed from pp.
   """
   # Linux, Unix and MacOS:
   if hasattr(os, "sysconf"):
      if os.sysconf_names.has_key("SC_NPROCESSORS_ONLN"):
         # Linux & Unix:
         ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
         if isinstance(ncpus, int) and ncpus > 0:
            return ncpus
      else: # OSX:
         return int(os.popen2("sysctl -n hw.ncpu")[1].read())
   # Windows:
   if os.environ.has_key("NUMBER_OF_PROCESSORS"):
      ncpus = int(os.environ["NUMBER_OF_PROCESSORS"]);
      if ncpus > 0:
         return ncpus
         
   return 2 # Default

#############################################################
#############################################################
#############################################################
def CreateMkModifyExecutor(P1_ProjectLocation,MakeFile,Compiler,CompilerPathsArray,Device,PerofrmRunTimeTest,CompilerPathRefFile,MakeFileVersion,IsDebugEnabled=1):
   
   MakeFileLocation = os.path.join(P1_ProjectLocation,"nbproject")
   MakeFileLocation = os.path.join(MakeFileLocation,MakeFile)
   
   ExecutorFileName = ''
   

   try:
      import multiprocessing
      num_cores = multiprocessing.cpu_count()
   except:   
      num_cores = detectCPUs()   
   
   j_number = num_cores * 2
   
   additional_options_for_make_file = "-j " + str(j_number) + " -k"
   
   # if the -mpa option is available for XC16 compiler, disable the parallel make feature
   if Compiler == "XC16":
   
      disable_parallel_make = 0

      fptr = open(MakeFileLocation, "r")

      for line in fptr:
         if re.search("-mpa ", line):
            disable_parallel_make = 1

      fptr.close()


      if disable_parallel_make == 1:   
         additional_options_for_make_file = ""

   '''
   # Adding Make Command to System Path
   mplabx_path = ''
   if os.path.exists(CompilerPathRefFile):

      mcpr_file_pointer = open(CompilerPathRefFile,"r")

      for line in mcpr_file_pointer:
         line = line.strip("\n|\r")
         line = line.strip(" ")
         if line != '':

            if not re.search("^#",line):
               if re.search("^_MPLAB_X_INSTALLATION_PATH_", line):
                  mplabx_path = re.split("=", line)[1]
                  mplabx_path = mplabx_path.strip(" ")
                  mplabx_path = mplabx_path.rstrip("/")
                  mplabx_path = mplabx_path.rstrip(r"\\")
                  if 'win32' == sys.platform:
                     mplabx_path = os.path.join(mplabx_path, "gnuBins/GnuWin32/bin")
                     mplabx_path = os.path.normpath(mplabx_path)
                  elif 'linux2' == sys.platform:  
                     mplabx_path = os.path.join(mplabx_path, "mplab_ide/bin")
                     mplabx_path = os.path.normpath(mplabx_path)
                  elif 'darwin' == sys.platform:
                     # /Applications/microchip/mplabx215/mplab_ide.app/Contents/Resources/mplab_ide/bin
                     mplabx_path = os.path.join(mplabx_path, "mplab_ide.app/Contents/Resources/mplab_ide/bin")
                     mplabx_path = os.path.normpath(mplabx_path)
                  
                  break    

      mcpr_file_pointer.close()

   
   if mplabx_path != "":
      if os.path.exists(mplabx_path):
         if 'win32' == sys.platform:
            os.environ["PATH"] = mplabx_path + ";" + os.environ["PATH"]
         else:
            os.environ["PATH"] = mplabx_path + ":" + os.environ["PATH"]  
   '''
   
   # framing Make comamnd
   
   MakeCommandPath = "make " + additional_options_for_make_file + " "
   
   MiscIncludePaths = ''
   '''
   CompilerPathRefFilePtr = open(CompilerPathRefFile,"r")

   for Line in CompilerPathRefFilePtr:
      Line = Line.strip("\n|\r")
      
      if MakeFileVersion == 0:
         SS = "_MAKE_PATH_"+ str(0) + "_"
      else:
         SS = "_MAKE_PATH_"+ str(1) + "_"

      if re.search(SS,Line):
         MakeCommandPath = '"' + re.split("=",Line)[1] + '"'

      if re.search("_MISC_PATH_",Line):
         MiscIncludePaths = re.split("=",Line)[1]
         
   CompilerPathRefFilePtr.close()
   '''
   
   
   LinkerOption = xml_operation.ExtractLinker(P1_ProjectLocation,MakeFile)
   
   #LogFile = os.path.join(os.getcwd(),"LogFile.txt")     # For logging the message into the LogFile.txt.
   
   LogFile = os.path.join(os.getcwd(),MakeFile + ".log")     # For logging the message into the LogFile.txt.
   
   var = ''
   
   if 'win32' == sys.platform:
      var = P1_ProjectLocation[:2] + "\n"
      
   var =  var + "cd " + '"' + P1_ProjectLocation + '"' 
   var = var + "\n" + MakeCommandPath
   
   
   if 0 != MakeFileVersion:
      if 'win32' == sys.platform:
         var = var + ' \"SHELL=cmd.exe\" \"MKDIR=gnumkdir -p\"'
      else:  
         var = var + ' SHELL=sh \"MKDIR=mkdir -p\"'

   var = var + " -f nbproject/" + MakeFile + " SUBPROJECTS= .clean-conf"
   
   
   var = var + "\n" + MakeCommandPath
   #if 0 == PerofrmRunTimeTest:
   #   var = var + "TYPE_IMAGE=!DEBUG_RUN"
   #else:
   if IsDebugEnabled == 1:
      var = var + "TYPE_IMAGE=DEBUG_RUN"
   
   make_operations.UpdateMakeFileProcessor(MakeFileLocation, "MP_PROCESSOR_OPTION=" + Device)
   
   if [] == LinkerOption:
      if "C30" == Compiler:                                             #  or Compiler == "C30":
         LinkerOption = "MP_LINKER_FILE_OPTION=\",-T" + "p" + Device + ".gld\""   
      if "C32" == Compiler:                                             #  or Compiler == "C32":
         LinkerOption = "MP_LINKER_FILE_OPTION=\"\""    

   else:
         if MakeFileVersion != 0:
            LinkerOption = "MP_LINKER_FILE_OPTION=,--script=\"" + misc_operations.ConvertPathToMPXParameterFormat(LinkerOption[0],MakeFileVersion) + '"'
         else:
            LinkerOption = "MP_LINKER_FILE_OPTION=,--script=" + misc_operations.ConvertPathToMPXParameterFormat(LinkerOption[0],MakeFileVersion)
   
   #if not LinkerOption == '':
   #   make_operations.UpdateMakeFileLinkerPath(MakeFileLocation, LinkerOption)
   if MakeFileVersion != 2:
      make_operations.UpdateMakeFileCompilerPaths(MakeFileLocation, CompilerPathsArray)

      make_operations.UpdateMakeFileDependencies(MakeFileLocation, MiscIncludePaths)
   else:
      make_operations.CreateVer2LocalMakeFile(MakeFileLocation, CompilerPathsArray, MiscIncludePaths)
   
   
   if 0 != MakeFileVersion:
      if 'win32' == sys.platform:
         var = var + ' \"SHELL=cmd.exe\" \"MKDIR=gnumkdir -p\"'

      else:  
         var = var + ' SHELL=sh \"MKDIR=mkdir -p\"'

   
   
   var = var + " -f nbproject/" + MakeFile + " SUBPROJECTS= .build-conf > " + '"' + LogFile + '"' + " 2>&1\n"

   # Working var = P1_ProjectLocation[:2] + "\ncd " + '"' + P1_ProjectLocation + '"' + "\nmake clean CONF=" + MakeFile[9: -3] + "\nmake CONF=" + MakeFile[9: -3] + " >> " + '"' + LogFile + '"' + " 2>&1\n"
   # var = P1_ProjectLocation[:2] + "\ncd " + '"' + P1_ProjectLocation + '"' + "\nmake clean CONF=" + MakeFile[9: -3] + "\nmake CONF=" + MakeFile[9: -3] + " >> " + '"' + LogFile + '"' + " 2>&1\n"
   
   print "*" * 30
   print var
   print "*" * 30
   
   ExecutorFileName = "Build_Conf_" + MakeFile[9: -3]

   
   if 'win32' == sys.platform:                           # In Case of Win 32, create a .bat File
      ###########################################
      # This code determines ans prints the exit status of the make command
      var = var + "\nIF ERRORLEVEL 1 goto failed"
      var = var + "\n@echo Make command exit status: No Errors >> " + '"' + LogFile + '"' + " 2>&1"
      var = var + "\ngoto end"
      var = var + "\n:failed"
      var = var + "\n@echo Make command exit status: Exit with Errors >> " + '"' + LogFile + '"' + " 2>&1"
      var = var + "\ngoto end"
      var = var + "\n:end"
      ###########################################
      
      PrintTemp = os.path.join(P1_ProjectLocation,(ExecutorFileName + ".bat"))
   
   else:                                                 # If Non-Windows OS, (Linux and MAC), create Shell File.
      # var = "\ncd " + '"' + P1_ProjectLocation + '"' + "\nmake clean CONF=" + MakeFile[9: -3] + "\nmake CONF=" + MakeFile[9: -3] + " >> " + '"' + LogFile + '"' + " 2>&1\n"
      
      ###########################################
      # This code determines ans prints the exit status of the make command
      var = var + "\nif test $? -eq 0"
      var = var + "\nthen"
      var = var + "\necho Make command exit status: No Errors >> " + '"' + LogFile + '"' + " 2>&1"
      var = var + "\nelse"
      var = var + "\necho Make command exit status: Exit with Errors >> " + '"' + LogFile + '"' + " 2>&1"
      var = var + "\nfi"
      ###########################################   
      
      PrintTemp = os.path.join(P1_ProjectLocation,(ExecutorFileName + ".sh"))

   
   P1_Temp = open(PrintTemp,'w')
   P1_Temp.write(var)
   P1_Temp.close()
   
   return(PrintTemp)

