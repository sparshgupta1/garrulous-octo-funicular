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



#############################################################
#### Lists the Directories for Zip Operation, Recrussive 
#### listing of the files and directory
#############################################################   
def dirEntries(dir_name, subdir, *args):
    fileList = []
    for file in os.listdir(dir_name):
        dirfile = os.path.join(dir_name, file)
        if os.path.isfile(dirfile):
            if not args:
                fileList.append(dirfile)
            else:
                if os.path.splitext(dirfile)[1][1:] in args:
                    fileList.append(dirfile)
                                                               # recursively access file names in subdirectories
        elif os.path.isdir(dirfile) and subdir:
            fileList.extend(dirEntries(dirfile, subdir, *args))
    return fileList
    
#############################################################
#### Copies the files with extension given 
#### from Src Directory to Dst directory
#############################################################      

'''
def CopyFiles(Src,Dst,Extn):
   for i in os.listdir(Src):                                            # Copy the Build Batch File and Shell File for further analysis
      if i.endswith(Extn):
         DashboardFileSrc = os.path.join(Src,i)                           # If exists, then copy to Dashboard (workspace)
         DashboardFileDst = os.path.join(Dst,i)
         #shutil.copyfile(DashboardFileSrc,DashboardFileDst) 
'''


#################################################################
#### Copies the Output Files - *.mk, *.cof, *.hex, *.map  
#### and Zip them into the name of the make File.
#### The Dashboard displays the file Extn, from the Workspace 
#### Directory, So, if a file needs to be displayed in the DB,
#### Copy it to the Workspace Directory, which is os.getcwd()
#### If the build is success, then, put all the generated files 
#### into the zip and put it in Dashboard.
#### Else, if the build is failure, then copy only the make file
#### into the workspace.
#### The Build Success/Failure is determined by the existance of 
#### Output files and the directory.
################################################################# 


def CopyOutputFilesAndZip(P1_ProjectLocation,INMakeFile):
   
   DebugCofFileLocation = ''
   DebugHexFileLocation = ''
   Error = 0
   BuildMode = 0
   var = os.path.join(P1_ProjectLocation,"nbproject")                         # Make File needs to be copied to Dashboard or to the ZIP file displayed in DB.
   INMakeFileLocation = os.path.join(var,INMakeFile)
   
   var = os.path.join(P1_ProjectLocation,"dist")                              # If the directory "dist" exists, then the make file is executed in Release Mode.
   var = os.path.join(var,INMakeFile[9: -3])
   
   if os.path.exists(os.path.join(var,"production")):                         
      var = os.path.join(var,"production")                                    
      arbs_print.LogFile("Build_Mode: RELEASE")  
      BuildMode = 1
   else: #if os.path.exists(os.path.join(var,"debug")):
      var = os.path.join(var,"debug")                                         # Else, if the "debug" directory is exists, then the build is in Debug Mode.
      arbs_print.LogFile("Build_Mode: DEBUG")                                         # In our case, this only will happen ! :)
      BuildMode = 2
                                                                              # Check "CreateExecutor" routene.
   OutputHexFileFound = 0
   OutputHexFileName = ''
   OutputDbgFileFound = 0
   OutputDbgFileName = ''
   OutputMapFileFound = 0
   OutputMapFileName = ''


   if os.path.exists(var):                                                    # List the Files in the debug or dist directory
                                                                              # as the files needs to be zipped and copied to Workspace.
      for i in os.listdir(var):
         if i.endswith(".hex"):                                               # If the build is successful, then .hex would have been generated.     
            OutputHexFileName = i                                             # no harm, if it does not exists also.
            OutputHexFileFound = 1                                            # If exists, just copy it to the dashboard.

         elif i.endswith(".a"):                                               # If the build is successful, then .hex would have been generated.     
            OutputDbgFileName = i                                             # no harm, if it does not exists also.
            OutputDbgFileFound = 1                                            # If exists, just copy it to the dashboard.
                         
         elif i.endswith(".cof"):                                             # similarly .Cof,.elf and.map files also.
            OutputDbgFileName = i
            OutputDbgFileFound = 1
            
         elif i.endswith(".elf"):
            OutputDbgFileName = i
            OutputDbgFileFound = 1
         
         elif i.endswith(".map"):
            OutputMapFileName = i
            OutputMapFileFound = 1

      if 1 == OutputHexFileFound or 1 == OutputDbgFileFound or 1 == OutputMapFileFound:      # if any of the output files are found, then copy all into a directory, it means that the build is success
                                                                                             # named INMakeFile[9: -3], and zip it.
         ########################################################
         ############Create a directory and copy make file#######
         #var = INMakeFile[: -3] + '_' + INDevice + ".mk"
         DashboardFileSrc = INMakeFileLocation
         j = os.path.join(os.getcwd(),INMakeFile[9: -3])                                     # Create a directory, in the name of the make file.                            
         if os.path.exists(j):                                                               # if already exists, remove it.
            shutil.rmtree(j,onerror=misc_operations.ModifyToWritePermission)                                 # if error with permission, change it.
         #os.mkdir(j)
         DashboardFileDst = os.path.join(j,INMakeFile)
         #shutil.copyfile(DashboardFileSrc,DashboardFileDst)                                  # Copy the make file to the newly created directory        
         
         #CopyFiles(P1_ProjectLocation,j,".bat")
         #CopyFiles(P1_ProjectLocation,j,".sh")
         
         ########################################################
         #############Copy the output files to the created directory
         if 1 == OutputHexFileFound:                                                         # This Flag indicates the availability of Hex File
            DashboardFileSrc = os.path.join(var,OutputHexFileName)                           # If exists, then copy to Dashboard (workspace)
            DashboardFileDst = os.path.join(j,OutputHexFileName)
            #shutil.copyfile(DashboardFileSrc,DashboardFileDst)       
            
            DebugHexFileLocation = DashboardFileSrc
            
         if 1 == OutputDbgFileFound:                                                         # This is for Debug file (.cof/elf) file
            DashboardFileSrc = os.path.join(var,OutputDbgFileName)
            DashboardFileDst = os.path.join(j,OutputDbgFileName)
            #shutil.copyfile(DashboardFileSrc,DashboardFileDst)   
            
            DebugCofFileLocation = DashboardFileSrc
         
         if 1 == OutputMapFileFound:                                                         # This copies the Map file into the Workspace.
            DashboardFileSrc = os.path.join(var,OutputMapFileName)
            DashboardFileDst = os.path.join(j,OutputMapFileName)
            #shutil.copyfile(DashboardFileSrc,DashboardFileDst) 
         else:
            var = P1_ProjectLocation
            for i in os.listdir(var):
               if i.endswith(".map"):
                  OutputMapFileName = i
                  OutputMapFileFound = 1
                  
                  DashboardFileSrc = os.path.join(var,OutputMapFileName)
                  DashboardFileDst = os.path.join(j,OutputMapFileName)
                  #shutil.copyfile(DashboardFileSrc,DashboardFileDst) 
         ########################################################
         ############# zipper####################################
         '''
         directory = INMakeFile[9: -3]                                                       # Create the zipper in the name of Make File
         archive = "Build_Output_File_For_" + directory + ".zip"                             # Build_Output_File_For_<MakeFile>.zip will be file name.

         fileList = dirEntries(directory, True)    
         
         ZipFilePtr = zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED)                    # Zipping Engine !
         for IndividualFile in fileList:                                                     # Considers zip folder also as a file.
            ZipFilePtr.write(IndividualFile)                                                 # Copies the individual files into the zipped folder.
         ZipFilePtr.close()

         var = os.path.join(os.getcwd(),INMakeFile[9: -3])
         time.sleep(1)                                                                       # Before deleting the directory, give 1 sec delay, for OS to release the controls on this dir.
         if os.path.exists(var):       
            shutil.rmtree(var,onerror=misc_operations.ModifyToWritePermission)  
         '''
         ########################################################
      
      if not (1 == OutputHexFileFound or 1 == OutputDbgFileFound or 1 == OutputMapFileFound):   # if none of the output files is not found, Build is failure, copy only the make file.
         
         DashboardFileSrc = INMakeFileLocation
         j = "Failed-" + INMakeFile
         DashboardFileDst = os.path.join(os.getcwd(),j)
         #shutil.copyfile(DashboardFileSrc,DashboardFileDst)

         #CopyFiles(P1_ProjectLocation,os.getcwd(),".bat")
         #CopyFiles(P1_ProjectLocation,os.getcwd(),".sh")
                                                                                             # Removed Attention message, as it generates mauch misunderstanding !
   else:                                                                                     # if the output directory doesnot exists, copy only the make file.
      DashboardFileSrc = INMakeFileLocation
      j = "Failed-" + INMakeFile
      DashboardFileDst = os.path.join(os.getcwd(),j)
      #shutil.copyfile(DashboardFileSrc,DashboardFileDst)

      #CopyFiles(P1_ProjectLocation,os.getcwd(),".bat")
      #CopyFiles(P1_ProjectLocation,os.getcwd(),".sh")

   GeneratedFileLocation = ''
   
   if 1 == OutputDbgFileFound and 2 == BuildMode:
      Error = 0
      GeneratedFileLocation = DebugCofFileLocation
   elif 1 == OutputHexFileFound and 1 == BuildMode:
      Error = 0
      GeneratedFileLocation = DebugHexFileLocation
   else:
      Error = 1
   return(Error,GeneratedFileLocation)      


