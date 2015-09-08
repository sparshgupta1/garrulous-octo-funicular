#####################################################################################
# File : Build_Hudson_MultiConfiguration_Job.py
#
# Author: Shankar R
#
# Date: 21 OCT 2011
#
# File Revision : 2.6 
#
# Revision History
#
# Rev        Change Log                                                Author              Date
#
# 1.0        Initial Draft Varsion, having 2 Files,                    Shankar R           09 FEB 2011
#            P1_Read_Hudson_Parameters.py and P2_Execute_MakeFile.py
#            
# 1.1        Updated Script for proper flow of the execution, Fixed    Shankar R           16 MAR 2011
#            bugs in revision 1.0, Updated Log File Texts and Console
#            output messages to track the failure of the script
#            Added Comments
#
# 1.2        Updated Script for Handling Error, if the Number of       Shankar R           23 MAR 2011
#            parameters, passed are not meeting. 
#           
# 1.3        Updated Script Modifying to write Permissions for         Shankar R           24 MAR 2011
#            the Working directory, project directory and the 
#            files in it
#
# 1.4        Updated Script to Format Log Messages                     Shankar R           28 MAR 2011
#
# 1.5        Updated Script to for compiling PICC18 in STD and         Shankar R           01 APR 2011
#            in PRO Mode, Updated Compiler Path References File also   
#
# 1.6        Removed Support for C18 Compiler                          Shankar R           02 APR 2011
#
# 1.7        Updated Script to display Build URL, wihtout this, the    Shankar R           19 APR 2011
#            E-mail script could not display Link to Compiler Log
#            messages in Consolidated Result, sent via email.
#
# 1.8        Modifued Script to modify make file to build the          Shankar R           04 MAY 2011
#            projects in DEBUG mode, for run-time tests.
#            Also, accommodated the script to build with Simulator 
#            as Debugger
#
# 1.9        Updated script to accommodate the change made in          Shankar R           06 MAY 2011
#            Make File in MPLAB X version Beta 6.0 or later
#
# 2.0        Added Support for Runtime Tests, with HWTool names        Shankar R           27 MAY 2011
#            with Debugger Name at the end. The mdb is used 
#            in Simulator Mode.
#
# 2.1        Added Support for RealICE, ICD3 and SIM. Code has         Shankar R           09 JUN 2011
#            mechanism to test PLIB on tatget.
#
# 2.2        Modularized Script, Splitted into multiple files          Shankar R           10 JUN 2011
#
# 2.3        Included Make Command Exit Status to determine the        Shankar R           28 JUN 2011
#            failure. This avoids the Failure case, accidentally
#            reported as PASS.
#
# 2.4        Updated Script for emailing, even if the Hudson Job       Shankar R           01 JUL 2011
#            configuration is not done properly.
#            The error messages were ported to "error_messages.info"
#            file, with ARBS Error Code. Error Code acts as the 
#            reference to the error_messages.info file.
#
# 2.5        Updated Script to take variable number of parameters,     Shankar R           11 JUL 2011
#            With auto detection of the parameters. The build 
#            operation is performed, if only device or compiler 
#            name is provided.
#
# 2.6        Creating Virtual Drive, only if the Path length of        Shankar R           21 OCT 2011
#            the project in Win is more than 200 characters. 
#            Also, updated the virtual drive existance checking 
#            mechanism for generating 2 level deep random number
#
# Operations performed in this File
# 
# 1. Read the Parameters from Hudson.
# 2. Check for the Mplab X (WS) directory exists and Open 'nbproject' directory
# 3. List out the Make files Open the MakeFile, Check for Compatibility with the given device.
# 4. Replace the Given Device in the Compatible Make Files
# 5. Create a Shell/Batch File for execute the Make File
# 6. Execute the File, which puts the compiler messages into the Log File
# 
# General returns from Subroutenes:
#    0 for no Error
#    1 or more for Error
####################################################################################

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
import virtual_drive
import extract_info

#############################################################
#### Main. Execution Starts from here !  
#############################################################  

if __name__ == "__main__":
   
   ############################
   # Get the Arguments from Command Line
   var = 0
   Error = 0
   PerofrmRunTimeTest = 0
   ErrorCodeCount = 1
   
   P1_ProjectLocation = ''
   P1_INDevice = ''
   P1_INCompiler = ''
   P1_BuildNumber = 0
   P1_BuildURL = ''
   OS = ''
   project_commit_files_extn = ''
   IsDebugEnabled = 1
   
   make_file_for_build = ''
   P1_RT_Test_HW_Tool = "NA"

   P1_BuildNumber = os.getenv('BUILD_NUMBER', "LOCAL_RUN") #os.environ['BUILD_NUMBER']
      
   P1_jobname = os.getenv('JOB_NAME', "LOCAL_RUN") #os.environ['JOB_NAME']    
   
   P1_jobname = re.split("/",P1_jobname)[0]
   
   
   CreateVirtualDrive = 0
   UseDeviceFromMakeFile = 0
   
   if (os.path.split(sys.argv[0])[0]) != '':
      os.chdir(os.path.split(sys.argv[0])[0])
      
   
   LogFile = os.path.join(os.getcwd(),"LogFile.txt")
   if os.path.exists(LogFile):
      os.remove(LogFile)
      
   # Check for essential files
   # check for existance of Error information File
   ErrorInfoFile = os.path.join(os.getcwd(),"error_messages.info")

   if not os.path.exists(ErrorInfoFile):
      arbs_print.LogFile("ARBS_Error_Code: 0101 - Error information file not found.")
      #exit()                                 # If not exists, Exit the code with Error
      misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)
      
   # Check for existance of Compiler Path References File
   
   # CompilerPathRefFile = os.path.join(os.getcwd(),'P2_CompilerPathReferences.mcpr')# the Compiler Path References File
   CompilerPathRefFile = ''
   
   built_in_compiler_path_ref_file = "mcpr_modified.mcpr"
   
   if os.path.exists(built_in_compiler_path_ref_file):
      CompilerPathRefFile = built_in_compiler_path_ref_file
   else:   

      if 'win32' == sys.platform:
         CompilerPathRefFile = "C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr" 
      elif'linux2' == sys.platform:                                 # Linux
         CompilerPathRefFile = "/home/ARBS_SUPPORT/LIN_ToolSuiteLocations.mcpr" 
      elif 'darwin' == sys.platform:                                 # MAC 
         CompilerPathRefFile = "/Users/ARBS_SUPPORT/MAC_ToolSuiteLocations.mcpr"
      
   if not os.path.exists(CompilerPathRefFile):
      output_status.Msg(ErrorCodeCount,2)     # If not exists, Exit the code with Error code 0102
      #exit()   
      misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)

   CompilerDeviceToolsReferenceFile = os.path.join(os.getcwd(),'compiler_dev_tools_reference.info')# the Compiler Path References File
   
   if not os.path.exists(CompilerDeviceToolsReferenceFile):
      output_status.Msg(ErrorCodeCount,3)     # If not exists, Exit the code with Error 0103
      #exit()   
      misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)



   
   ProjectArguments = []
   
   for arg in sys.argv:                                           # Iterate and receive the parameters from command line.
      #var = var+1
      #if 2 == var:
      #   P1_ProjectLocation = arg
      #if var >= 3:
      #   ProjectArguments.append(arg)

      if re.search("-project_location=",arg):
         P1_ProjectLocation = re.split("=",arg)[1]
         print P1_ProjectLocation
      if re.search("-in_device=",arg):
         P1_INDevice = re.split("=",arg)[1]
      if re.search("-in_compiler=",arg):
         P1_INCompiler = re.split("=",arg)[1]         
      if re.search("-build_number=",arg):
         P1_BuildNumber = re.split("=",arg)[1]
      if re.search("-build_url=",arg):
         P1_BuildURL = re.split("=",arg)[1]
      if re.search("-os=",arg):
         OS = re.split("=",arg)[1]
      if re.search("-make_file=",arg):
         make_file_for_build = re.split("=",arg)[1]
      if re.search("-hw_tool=",arg):
         P1_RT_Test_HW_Tool = re.split("=",arg)[1]  
      if re.search("-commit_artifacts=",arg):
         project_commit_files_extn = re.split("=",arg)[1]  
         
         
      temp = re.split(",", project_commit_files_extn)
      for i in range(len(temp)):
         if temp[i].endswith("hex"):
            IsDebugEnabled = 0
            
      '''
      if var == 3:
         P1_INDevice = arg
      if var == 4:
         P1_INCompiler = arg
      if var == 5:
         P1_BuildNumber = arg
      if var == 6:
         P1_BuildURL = arg
      if var == 7:
         P1_RT_Test_HW_Tool = str(arg)
         # Will be received in this order
         # 0 - "$BUILD_NUMBER" 
         # 1 - "$BUILD_URL"
      '''
      
   ############################
   


   #if var != 7:
   #   Error = 1
   #
   #if Error != 0:
   #   output_status.Msg(ErrorCodeCount,Error)     # Error code will be 0101
   #   exit()
   
   #ParametersExtractionError, P1_INDevice, P1_INCompiler, P1_RT_Test_HW_Tool, P1_BuildNumber, P1_BuildURL = extract_info.ExtractParameters(ProjectArguments)
   
   ReceivedProjectLocation = P1_ProjectLocation
   
   '''
   if 'win32' == sys.platform:
      import win32api
      try:
         P1_ProjectLocation = win32api.GetShortPathName(P1_ProjectLocation)
      except:
         print "Error"
   '''
   
   if len(P1_ProjectLocation) > 200:
      CreateVirtualDrive = 1
      
   if "NA" != P1_RT_Test_HW_Tool:      # If run time test, then use only one drive for execution, that is virtual Drive
      CreateVirtualDrive = 1
   
   if 'win32' == sys.platform:
      OS = "Windows XP 32 Bit"
      if 1 == CreateVirtualDrive:
         arbs_print.Console("\nCreating Virtual drive")
         DriveError,VirtualLocation = virtual_drive.Create(P1_ProjectLocation, P1_RT_Test_HW_Tool)
         if 0 == DriveError:
            P1_ProjectLocation = VirtualLocation
   elif 'linux2' == sys.platform:                           # Linux
      OS = "Linux Ubuntu 10.10 32 Bit"
   elif 'darwin' == sys.platform:                           # MAC 
      OS = "MAC 10.6 32 Bit"

     
   arbs_print.LogFile("ARBS_Build_Script_2v6")

   arbs_print.LogFile("\nOperating System : " + OS)
   arbs_print.LogFile("System Time : "+ str(datetime.datetime.now()))

   arbs_print.LogFile("\nListing parameters received from Hudson Job: \n" + ('-' * 44))
   arbs_print.LogFile("Project Location : " + ReceivedProjectLocation)
   
   ##############################
   
   if '' != P1_INDevice:
      arbs_print.LogFile("Device : " + P1_INDevice)
   
   ##############################
   
   if '' != P1_INCompiler:
      arbs_print.LogFile("Compiler : " + P1_INCompiler)
         
   ##############################
   
   if '' != P1_BuildNumber and '0' != P1_BuildNumber:
      arbs_print.LogFile("Build Number : " + str(P1_BuildNumber))
   if '' != P1_BuildURL:
      arbs_print.LogFile("Build URL : " + P1_BuildURL + "\n")                    # Uncommented by Shankar on 19 APR 2011 to keep sync with Email Script, which Expects this info.



   P1_RT_Test_HW_Tool = P1_RT_Test_HW_Tool.upper()

   if "NA" != P1_RT_Test_HW_Tool:
      if sys.platform == 'win32':                                       # Only if the OS is WIN, then, RunTime Test can be performed.
         PerofrmRunTimeTest = 1
         arbs_print.LogFile("Test Type : RunTime Test, using mdb " + P1_RT_Test_HW_Tool)    
      else:
         arbs_print.LogFile("Test Type : Build Test")    
   else:
      arbs_print.LogFile("Test Type : Build Test")    

   #P1_INDevice = re.sub("_RUN|RUN_",'',P1_INDevice)      # Remove Run, if exists

   
   ParametersExtractionError = 0
   if 0 != ParametersExtractionError:
      output_status.Msg(ErrorCodeCount,ParametersExtractionError + 3)     # If not exists, Exit the code with Error 0104 and 0105
      #exit()       
      misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)
   
   # Receive supplied parameters
   ErrorCodeCount = ErrorCodeCount + 1                            # ErrorCodeCount = 2 at this point
   
   
   if '' != P1_INDevice:
   
      Error = misc_operations.ValidateDevice(P1_INDevice)

      if 0 != Error:
         output_status.Msg(ErrorCodeCount,01)     # ErrorCodeCount = 2, Error Code will be 0201
         #exit()
         misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)


   if '' != P1_INCompiler:

      P1_INCompiler = P1_INCompiler.upper()

      Error = misc_operations.ValidateCompiler(P1_INCompiler)

      if 0 != Error:
         output_status.Msg(ErrorCodeCount,02)     # ErrorCodeCount = 2, Error Code will be 0202
         #exit()
         misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)


   if '' != P1_INDevice and '' != P1_INCompiler:
      
      Error = misc_operations.ValidateDeviceVsCompiler(P1_INDevice, P1_INCompiler)
      
      if Error != 0:
         output_status.Msg(ErrorCodeCount,03)     # ErrorCodeCount = 2, Error Code will be 0203 
         #exit()
         misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)
         
   ErrorCodeCount = ErrorCodeCount + 1

   
   ###############################################
   # Find whether the directory "nbroject" exists
   
   if(0 == misc_operations.FindLocation(P1_ProjectLocation)):
      if(0 != misc_operations.FindLocation(os.path.join(P1_ProjectLocation,"nbproject"))):
         Error = 1
      else:
         if 0 != misc_operations.FindLocation(os.path.join(os.path.join(P1_ProjectLocation,"nbproject"),"Makefile-variables.mk")):
            Fptr = open(os.path.join(os.path.join(P1_ProjectLocation,"nbproject"),"Makefile-variables.mk"),"w")
            Fptr.close()
   else:
      Error = 1
   ###############################################
   
   if 0 != Error:
      output_status.Msg(ErrorCodeCount,Error)     # ErrorCodeCount = 3, Error code will be 0301
      #exit()
      misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)
      
   ErrorCodeCount = ErrorCodeCount + 1       
   
   ####################################################
   # Find whether the Make File Exists in the Directory
   # "nbproject". If not, Error
   MakeFileList = []
   
   make_file_for_build = "Makefile-" + make_file_for_build + ".mk"
   MakeFileList = []
   if make_file_for_build == '':
      MakeFileList, MakeFileCount = make_operations.FindMakeFile(os.path.join(P1_ProjectLocation,"nbproject"))
   else:
      MakeFileList, MakeFileCount = [make_file_for_build],[1]
      
      
   
   #MakeFileList, MakeFileCount = make_operations.FindMakeFile( os.path.join(P1_ProjectLocation,"nbproject"))
   if 0 == MakeFileCount:
      Error = 1
   ####################################################
   
   if 0 != Error:
      output_status.Msg(ErrorCodeCount,Error)     # ErrorCodeCount = 4, Error code will be 0401
      #exit()
      misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)
      
   # ErrorCodeCount = ErrorCodeCount + 1
   
   ####################################################
   # Delete the compiler and linker generated files and 
   # directories and list the available make files, zip

   misc_operations.DeleteGeneratedFiles(P1_ProjectLocation)

   #arbs_print.LogFile("-Found: " + str(MakeFileCount))

   CompatibleMakeFileList = []
   CompatibleMakeFileCount = 0
   CompatibleMakeDevice = []
   CompatibleMakeCompiler = []
   CompilerMode = []
   CompilerPathsArray = []
   MakeErrorArray = []
   
  
   CompatibleMakeFileList,CompatibleMakeFileCount,CompatibleMakeDevice,CompatibleMakeCompiler,CompilerMode,CompilerPathsArray,MakeErrorArray, MakeVersion = make_operations.FindCompatibleMakeFile(os.path.join(P1_ProjectLocation,"nbproject"), MakeFileList,P1_INDevice,P1_INCompiler,CompilerPathRefFile)

   if 0 == CompatibleMakeFileCount:
      Error = 2

   if 0 != Error:
      output_status.Msg(ErrorCodeCount,Error)     # ErrorCodeCount = 4, Error Code will be 0402
      #exit()
      misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)
      
   ####################################################   
      
   #ErrorCodeCount = ErrorCodeCount + 1
   
   ####################################################
   # Find the Make Files, compatible to the received 
   # Device from Hudson Update them for the given device
   # and the compiler
   
   arbs_print.LogFile(('-' * 44) + "\n\nMakeFile Information and Execution Result:\n" + ('-' * 44))   
   
   
   CharCount = 1
   

   
   #arbs_print.LogFile("\n-Listing Compatible MakeFiles:")
   for Count in range(CompatibleMakeFileCount):                                                   # Lists the available compatible make files
   
      make_operations.UpdateMakeFile(os.path.join(P1_ProjectLocation,"nbproject"),CompatibleMakeFileList[Count],P1_INDevice,P1_INCompiler,P1_RT_Test_HW_Tool,MakeVersion[Count])
      
      if '' == CompilerMode[Count]:
         arbs_print.LogFile(str(CharCount) + ". " + "Compatible MakeFile - "+ CompatibleMakeFileList[Count])
      else:
         arbs_print.LogFile(str(CharCount) + ". " + "Compatible MakeFile - "+ CompatibleMakeFileList[Count] + " (Build Mode - " + CompilerMode[Count] + ")")
      
      CharCount = CharCount + 1
   
   
   # Create the Executor for the available Make File and execute it.
   arbs_print.LogFile(('-' * 44))
   arbs_print.LogFile("\n\n_ARBS_Build_Started_")

   ErrorCodeCount = ErrorCodeCount + 1       # ErrorCodeCount = 5 here.
   
   for Count in range(CompatibleMakeFileCount):

      arbs_print.MakeFileTag(Count, CompatibleMakeFileList[Count], CompilerMode[Count])

      if 0 == MakeErrorArray[Count]:

         #BatchFile = executor.CreateExecutor(P1_ProjectLocation,CompatibleMakeFileList[Count],CompatibleMakeCompiler[Count],CompilerPathsArray[Count],CompatibleMakeDevice[Count],PerofrmRunTimeTest,CompilerPathRefFile,MakeVersion[Count])
         BatchFile = executor.CreateMkModifyExecutor(P1_ProjectLocation,CompatibleMakeFileList[Count],CompatibleMakeCompiler[Count],CompilerPathsArray[Count],CompatibleMakeDevice[Count],PerofrmRunTimeTest,CompilerPathRefFile,MakeVersion[Count], IsDebugEnabled)
         arbs_print.InsertStartOfExecution()
         Error = executor.ExecuteExecutor(BatchFile,CompatibleMakeFileList[Count])
         ErrorFromZip,DebugFile = zipper.CopyOutputFilesAndZip(P1_ProjectLocation,CompatibleMakeFileList[Count])
         
         if 0 == ErrorFromZip:
            arbs_print.LogFile("Files Info: Output Files Generated Successfully")
         else:
            arbs_print.LogFile("Error: No Output Files Generated")
            
         arbs_print.InsertEndOfExecution()
         misc_operations.DeleteFile(BatchFile)
         
         '''
         if 0 == ErrorFromZip:
            arbs_print.LogFile("Files Info: Output Files Generated Successfully")
         else:
            arbs_print.LogFile("Files Info: No Output Files Generated")

         if 1 == PerofrmRunTimeTest and 0 != ErrorFromZip:
            arbs_print.LogFile("Error: Build_Failure, due to compile time errors\nAborting Run-Time Test for this MakeFile")

         if (1 == PerofrmRunTimeTest and 0 == ErrorFromZip):
            arbs_print.Console(('-' * 30) + "\n----Executing RunTime test----")
            arbs_print.LogFile("\n" + ('-' * 44) + "\n----Executing RunTime test----\nRunTime Test result")
            MDBError = mdb.PerformDebugOperation(CompatibleMakeDevice[Count],DebugFile,P1_RT_Test_HW_Tool,P1_ProjectLocation)
            mdb.DisplayMDBExecutionStatus(11,MDBError)                                        
         '''
         
      else:

         output_status.Msg(ErrorCodeCount,MakeErrorArray[Count])     # ErrorCodeCount = 5,Code will be 0501, 
         arbs_print.LogFile("Files Info: No Output Files Generated")

      
      arbs_print.LogFile("Make File Execution End")
      arbs_print.LogFile(('+-' * 44) + "\n\n\n\n")


   arbs_print.LogFile("\n_ARBS_Build_Ends_Here_")
   
   '''
   # Inserting Expected Build Failures here itself, to avoid executing two commands
      
   BuildTableLocation = os.path.normpath(os.path.split(P1_ProjectLocation)[0] + r"\doc\build_table.csv")

   Command = "python Expected_Build_Failures.py " + '"' + P1_RT_Test_HW_Tool + '"' + " \"" + BuildTableLocation + "\""
   
   if 'win32' == sys.platform:
      BatchFile = "ExpBuildFailure.bat"
   else:
      BatchFile = "ExpBuildFailure.sh"

   BatchFilePtr = open(BatchFile,"w")
   BatchFilePtr.write(Command)
   BatchFilePtr.close()
   if 'win32' == sys.platform:
      os.system('"' + BatchFile + '"')
   else:
      os.system('sh "' + BatchFile + '"')
   os.remove(BatchFile)
   '''
   
   #################################################
   
   misc_operations.ExitARBSDeletingVirtualDrive(P1_ProjectLocation,CreateVirtualDrive)
   
   #if sys.platform == 'win32':
   #   if CreateVirtualDrive == 1:
   #      arbs_print.Console("\nDeleting Virtual drive")
   #      virtual_drive.Delete(P1_ProjectLocation)
   



      
