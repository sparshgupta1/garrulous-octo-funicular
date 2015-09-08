from __future__ import division
import os
import re
import sys
import stat
import shutil        # For Performing operations on Directories
import client_status
import make_operations
import time
from xml.dom.minidom import parse
import multiple_compiler_options

import xml_operation
import subprocess

import difflib      # Nalini: 17 Dec 2014 - add support for comparing hex files
import filecmp

import ldra_support

#######################################################
#######################################################
def RemoveRedundantItems(Items):
   ReturnItems = []
   
   for item in Items:
      
      Found = 0
      
      for i in ReturnItems:
         
         if i == item:
            Found = 1
            break
      
      if Found == 0:
         
         ReturnItems.append(item)
   
   
   ReturnItems = sorted(ReturnItems)
   
   return(ReturnItems)
   

#######################################################
#######################################################
def FindProjectDirectories(Path):


   FileNames = []
   DirNames = []
   
   ProjectDirectoryNames = []
   
   if os.path.isdir(Path):                                 # if the given path is a directory, 
      #os.chmod(Path,0777)                                  # First change it to a directory write permissions.
      for root, dirs, files in os.walk(Path):              # Now, List the directories and files available in the 
         for files1 in files:                                  # directory provided.
            if files1.endswith("configurations.xml"):
               temp = re.split("nbproject",root)[0]
               temp = temp.rstrip("\\")
               
               temp = temp.rstrip("/")
               proj_loc = ''
               proj_loc = temp
               temp = os.path.join(temp, "nbproject")
               temp = os.path.join(temp, "configurations.xml")
               
               if os.path.exists(temp):
                  ProjectDirectoryNames.append(proj_loc)
            FileNames.append(os.path.join(root,files1))        # If it is a file, join it with the root and append it into an array 
         for dirs1 in dirs:                                    # for processing further
            DirNames.append(os.path.join(root,dirs1))          # if it is a directory, then, do the same operation, mentioned above. 

         
      #for i in FileNames:                                      # Modify permissions for all the files to Write.
      #   os.chmod(i, 0777)

      #for i in DirNames:                                       # Similarly for directories
      #   os.chmod(i,0777)

   elif os.path.isfile(Path):                              # If the provided path is not a dir,but a file, 
      os.chmod(Path, 0777)    
   
   temp_proj_dirs = RemoveRedundantItems(ProjectDirectoryNames)
   
   for i in range(len(temp_proj_dirs)):
   
      if os.path.exists(temp_proj_dirs[i]):
      
         config_path = os.path.join(temp_proj_dirs[i], "nbproject")
         original_config_path = os.path.join(config_path, "configurations.xml.original")
         
         config_path = os.path.join(config_path, "configurations.xml")
         
         if os.path.exists(original_config_path):
            if os.path.exists(config_path):
               os.remove(config_path)
            
            # Recreate the configuration
            shutil.copy(original_config_path, config_path)            

   return(temp_proj_dirs)

#######################################################
#######################################################
def CopyLogFile(ProjectLocation):
      
   LogFilePtr = open("LogFile.txt","r")
   CompilerMessagesPtr = open("CompilerMessages.temp","a")
      
   StartLogging =  0
   
   for Line in LogFilePtr: 

      if re.search("_ARBS_Build_Ends_Here_",Line):
         StartLogging = 0
         
      if StartLogging == 1:
         CompilerMessagesPtr.write(Line)
         
      if re.search("_ARBS_Build_Started_",Line):
         StartLogging = 1
         CompilerMessagesPtr.write("\nProjectLocation: " + ProjectLocation + "\n")
         
   CompilerMessagesPtr.close()
   LogFilePtr.close()

#######################################################
#######################################################
def CopyLogFile1(ResultsDirectory, project_count):


   pass0_warn1_fail2, log_file_loc = 2, ''
   duration = "NA"
   pmem,dmem = "",""
   
   WarningInMessage = 0
   MakeExitStatus = 1
   OutputFilesGeneratedError = 1
   ErrorInMessage = 1
   
   results_file = str(project_count) + ".txt"
   results_file = os.path.join(ResultsDirectory, results_file)
   
   if os.path.exists(results_file):
      os.remove(results_file)
                     
   fptr = open(results_file, "w")   
   
   file_existance_check_timeout = 5       # Iterate 5 Times, before deciding the file not found
   file_existing  = 0
   
   while file_existance_check_timeout > 0:
   
      time.sleep(1)
      
      if os.path.exists("LogFile.txt"):
         
         file_existing = 1
         file_existance_check_timeout = 0 # Break the above while loop immediately
         
         LogFilePtr = open("LogFile.txt","r")
         for Line in LogFilePtr:

            if (re.search(r"warning:",Line,re.IGNORECASE) or re.search(r"warning \[",Line,re.IGNORECASE)) and (not re.search("This make file contains OS dependent code",Line,re.I)) and (not re.search("--chip=",Line)) and (not re.search("warning: %",Line)):
               WarningInMessage = 1
            if re.search("Make command exit status: No Errors",Line):
               MakeExitStatus = 0
            if re.search("Files Info: Output Files Generated Successfully",Line):
               OutputFilesGeneratedError = 0
            if re.search("BUILD_DURATION:",Line):
               duration = Line.strip("\n|\r")
               duration = re.split(":",duration)[1].strip(" ")
               
               
            if re.search("Total Program Memory used",Line) or re.search("Total program memory used", Line):
               dat = re.split(":",Line)[1]
               array = re.split(" ",dat)
               count = 0
               for xitems in array:
                  if xitems != '':
                     if count == 1:
                        xitems = re.sub("\(|\)", "", xitems)
                        pmem = xitems.strip(" ") + " Bytes"
                     if count == 2:
                        pmem = pmem + "(" + re.sub(" ","",xitems) + ")"
                        break
                     count = count + 1


            if re.search("Total Data Memory used",Line) or re.search("Total data memory used", Line):
               dat = re.split(":",Line)[1]
               array = re.split(" ",dat)
               count = 0
               for xitems in array:
                  if xitems != '':
                     if count == 1:
                        xitems = re.sub("\(|\)", "", xitems)
                        dmem = xitems.strip(" ") + " Bytes"
                     if count == 2:
                        dmem = dmem + "(" + re.sub(" ","",xitems) + ")"
                        break
                     count = count + 1 

            if re.search("Program space ", Line):
               dat = re.split("\(",Line)
               xitems = re.split("\)",dat[1])[0]
               pmem = xitems.strip(" ") + " Bytes"
               pmem = pmem + "(" + re.split("\)",dat[2])[0].strip(" ") + ")"

            if re.search("Data space ", Line):
               dat = re.split("\(",Line)
               xitems = re.split("\)",dat[1])[0]
               dmem = xitems.strip(" ") + " Bytes"
               dmem = dmem + "(" + re.split("\)",dat[2])[0].strip(" ") + ")"
               
            fptr.write(Line)

         if MakeExitStatus == 0 and OutputFilesGeneratedError == 0:
            ErrorInMessage = 0

         LogFilePtr.close()
         
      else:
         if file_existance_check_timeout > 0:
            file_existance_check_timeout = file_existance_check_timeout - 1
      
   if file_existing == 0:
   
      fptr.write("\n\nNo Compiler Messages found. \nPossibly Compiler Hang Error\n\n")
      
   time.sleep(0.2)  # Let the files copied completely
   
   fptr.close()
   
   if ErrorInMessage != 0:
      pass0_warn1_fail2 = 2
      
   elif WarningInMessage != 0:
      pass0_warn1_fail2 = 1
      
   else:
      pass0_warn1_fail2 = 0


   log_file_loc = results_file
   
   return(pass0_warn1_fail2, log_file_loc, duration, pmem, dmem)

#######################################################
#######################################################
def DeterminePassFailStatus():
   
   ProjectLocation = []
   ProjLocationChange = []
   ExecutingMakeFile = []
   PassFailStatus = []
   
   CompilerMessage = []
   
   _LcoCompilerMsg = ''
   
   _PLoc = ''
   _PrevPLoc = ''
   
   CompilerMessagesPtr = open("CompilerMessages.temp","r")
   
   ErrorInMessage = 1
   WarningInMessage = 0
   StartScan = 0
   CompilerMessageScan = 0
   
   MakeExitStatus = 1
   OutputFilesGeneratedError = 1
   
   for Line in CompilerMessagesPtr:
      
      if re.search("Make File Execution End",Line):
         CompilerMessageScan = 0
         CompilerMessage.append(_LcoCompilerMsg)
         StartScan = 0
         if ErrorInMessage == 1:
            PassFailStatus.append(2)
         elif WarningInMessage == 1:
            PassFailStatus.append(1)
         else:
            PassFailStatus.append(0)
         
      if CompilerMessageScan == 1:
         _LcoCompilerMsg = _LcoCompilerMsg + Line
      
      Line = Line.strip("\n|\r")
      if re.search("ProjectLocation",Line):
         _PLoc = Line

      if StartScan == 1:
         if (re.search(r"warning:",Line,re.IGNORECASE) or re.search(r"warning \[",Line,re.IGNORECASE)) and (not re.search("This make file contains OS dependent code",Line,re.I)) and (not re.search("--chip=",Line)) and (not re.search("warning: %",Line)):
            WarningInMessage = 1
         if re.search("Make command exit status: No Errors",Line):
            MakeExitStatus = 0
         if re.search("Files Info: Output Files Generated Successfully",Line):
            OutputFilesGeneratedError = 0
            
         if MakeExitStatus == 0 and OutputFilesGeneratedError == 0:
            ErrorInMessage = 0


      
      if re.search("Executing for Makefile",Line):
         
         if StartScan == 1:
            PassFailStatus.append(2)
            _TempCompMsg = "\n\nNo Compiler Messages found. \nPossibly Compiler Hang Error\n\n"
            CompilerMessage.append(_TempCompMsg)
         
         StartScan = 1
         ErrorInMessage = 1
         WarningInMessage = 0

         MakeExitStatus = 1
         OutputFilesGeneratedError = 1

         CompilerMessageScan = 1
         _LcoCompilerMsg = ''
         ExecutingMakeFile.append((re.split(":",Line)[1]).strip(" "))
         ProjectLocation.append(_PLoc)
         
         if _PrevPLoc == _PLoc:
            ProjLocationChange.append(0)
         else:
            _PrevPLoc = _PLoc
            ProjLocationChange.append(1)
      
      '''
      if re.search("End of Make File Messages",Line):
         StartScan = 0
         if ErrorInMessage == 1:
            PassFailStatus.append(2)
         elif WarningInMessage == 1:
            PassFailStatus.append(1)
         else:
            PassFailStatus.append(0)
        
         
      if StartScan == 1:
         if (re.search(r"warning:",Line,re.IGNORECASE) or re.search(r"warning \[",Line,re.IGNORECASE)) and (not re.search("This make file contains OS dependent code",Line,re.I)) and (not re.search("--chip=",Line)) and (not re.search("warning: %",Line)):
            WarningInMessage = 1
         if re.search("Make command exit status: No Errors",Line):
            ErrorInMessage = 0
            
     
      if re.search("Make File Messages",Line):
         StartScan = 1
         ErrorInMessage = 1
         WarningInMessage = 0
      '''

   if StartScan == 1:
      PassFailStatus.append(2)
      _TempCompMsg = "\n\nNo Compiler Messages found. \nPossibly Compiler Hang Error\n\n"
      CompilerMessage.append(_TempCompMsg)      
      
   CompilerMessagesPtr.close()
   return(ProjectLocation, ProjLocationChange, ExecutingMakeFile, PassFailStatus, CompilerMessage)

#######################################################
#######################################################
def GetMaxLength(ExecutingMakeFile):
   
   Len = 0
   
   for i in range(len(ExecutingMakeFile)):
      
      Length = len(ExecutingMakeFile[i]) + len(str(i)) + len(". ")
      
      if Len < Length:
         Len = Length
      
   return(Len)
#######################################################
#######################################################
def InsertSpaces(MaxLength, ExecutingMakeFile,i):
   #print MaxLength
   ReturnCommand = " "
   Length = len(ExecutingMakeFile) + len(str(i)) + len(". ")
   
   Len = MaxLength - Length

   offset = 10
   
   if MaxLength < 50:
      offset = 10 + round(MaxLength / 10)
   else:
      offset = round(MaxLength / 10)
   
   
   Len = Len + int(offset)
   
   for i in range(Len):
      ReturnCommand = ReturnCommand + "-"
   
   return(ReturnCommand)
#######################################################
#######################################################   
def GetCompilerVersions(Compiler):
   
   built_in_compiler_path_ref_file = "mcpr_modified.mcpr"
   
   CompilerRevFileLocation = ''

   if os.path.exists(built_in_compiler_path_ref_file):
      CompilerRevFileLocation = built_in_compiler_path_ref_file
   else:
      if 'win32' == sys.platform:
         CompilerRevFileLocation = "C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr" 
      elif'linux2' == sys.platform:                                 # Linux
         CompilerRevFileLocation = "/home/ARBS_SUPPORT/LIN_ToolSuiteLocations.mcpr" 
      elif 'darwin' == sys.platform:                                 # MAC 
         CompilerRevFileLocation = "/Users/ARBS_SUPPORT/MAC_ToolSuiteLocations.mcpr"
         
   CompilerVersion = ''
   
   Fptr = open(CompilerRevFileLocation,"r")
   
   CompilerList = []
   Versions = []
   
   mplab_x_ver = ''
      
   for Line in Fptr:

      Line = Line.strip("\n|\r")

      if not re.search("^#",Line):

         if re.search("_MPLAB_X_VER_=",Line.upper()):
            Version = (re.split("_VER_",Line)[1]).strip(" ")
            Version = re.sub("=",'',Version)
            Version = re.sub(" ",'',Version)
            Version = re.sub("_",'',Version)
            mplab_x_ver = Version
            
         
         if Compiler.upper() == "ALL":
            SearchString = "_XC8_VER_|_XC16_VER_|_XC32_VER_"
         else:
            SearchString = "_" + Compiler.upper() + "_VER_"

         if re.search(SearchString,Line.upper()):
            CompilerVersion = (re.split("_VER_",Line)[0]).strip(" ")
            CompilerVersion = re.sub("=",'',CompilerVersion)
            CompilerVersion = re.sub(" ",'',CompilerVersion)
            CompilerVersion = re.sub("_",'',CompilerVersion)               
            CompilerList.append(CompilerVersion)
            CompilerVersion = (re.split("_VER_",Line)[1]).strip(" ")
            CompilerVersion = re.sub("=",'',CompilerVersion)
            CompilerVersion = re.sub(" ",'',CompilerVersion)
            CompilerVersion = re.sub("_",'',CompilerVersion)
            if CompilerVersion == '':
               CompilerVersion = ""
            Versions.append(CompilerVersion)               

   CompilerVersion = ''
   
   CompilerList.append("MPLAB_X")
   Versions.append(mplab_x_ver)
   
   for i in range(len(CompilerList)):
      CompilerVersion = CompilerVersion + CompilerList[i] + InsertSpaces(GetMaxLength(CompilerList),CompilerList[i],0) + '---- ' + Versions[i] + "\n"
   
   Fptr.close()
   return(CompilerVersion)
   
   
#######################################################
#######################################################      

def InsertLine():
   Command = ''
   for i in range(100):
      Command = Command + "+"
   return(Command)
   
######################################################
def SpaceTobeInserted(MaxLenSp,PassCount):
   Spaces = ''
   MaxLenSp1 = (MaxLenSp - len(str(PassCount)) + 2)
   for i in range(MaxLenSp1):
      Spaces = Spaces + ' '

   return(Spaces)
   
   
   
def get_svn_revision():
   svn_rev, svn_link = '',''
   
   if os.path.exists("Project"):
      command = "svn info Project > svn_log.txt" 
      
      if 'win32' == sys.platform:
         command = "svn info -r BASE Project > svn_log.txt 2>&1" 
         os.system('"' + command + '"')
      else:
         os.system(command)
      
      fptr = open("svn_log.txt","r")
      for line in fptr:
         line = re.sub("\n|\r",'',line)
         if re.search("^URL:",line):
            svn_link = re.split("URL:",line)[1].strip(" ")
         if re.search("^Last Changed Rev:",line):
            svn_rev = re.split("Last Changed Rev:",line)[1].strip(" ")
      fptr.close()
      
   return(svn_rev, svn_link)


#########################################################
def ReturnMonthString(Month):
   ReturnString = ''
   
   if Month == 1:
      ReturnString = "Jan"
   elif Month == 2:
      ReturnString = "Feb"
   elif Month == 3:
      ReturnString = "Mar"
   elif Month == 4:
      ReturnString = "Apr"
   elif Month == 5:
      ReturnString = "May"
   elif Month == 6:
      ReturnString = "Jun"
   elif Month == 7:
      ReturnString = "Jul"
   elif Month == 8:
      ReturnString = "Aug"
   elif Month == 9:
      ReturnString = "Sep"
   elif Month == 10:
      ReturnString = "Oct"
   elif Month == 11:
      ReturnString = "Nov"
   elif Month == 12:
      ReturnString = "Dec"
   
   return(ReturnString)

def get_date_time():   
   import datetime
   CurrentDate = datetime.datetime.now()
   date_string = ''
   time_string = ''
   # Date
   if CurrentDate.day <= 9:
      date_string = date_string + '0'
   date_string = date_string + str(CurrentDate.day) + " "
   date_string = date_string + ReturnMonthString(CurrentDate.month) + " "
   date_string = date_string + str(CurrentDate.year)
   # Time

   if CurrentDate.hour <= 9:
      time_string = time_string + '0'
   time_string = time_string + str(CurrentDate.hour) + ':'
   if CurrentDate.minute <= 9:
      time_string = time_string + '0'
   time_string = time_string + str(CurrentDate.minute)
   return(date_string, time_string)
################################################################  


def remove_all_make_files(project_location):
   
   FilePath = project_location

   if os.path.isdir(os.path.join(FilePath,"nbproject")):                                 # if the given path is a directory, 
      
      #shutil.rmtree(os.path.join(FilePath,"nbproject"),1)
      
      try:
         os.chmod(FilePath,0777)                                  # First change it to a directory write permissions.
      except:
         print "unable to change the file permissions"
         
      for root, dirs, files in os.walk(FilePath):              # Now, List the directories and files available in the 
         for files1 in files:                                  # directory provided.
            if files1.endswith(".mk"):
               os.unlink(os.path.join(root,files1))   
            if files1.endswith(".properties"):
               os.unlink(os.path.join(root,files1)) 
            if files1.endswith(".src"):
               os.unlink(os.path.join(root,files1)) 
            if files1.endswith(".bash"):
               os.unlink(os.path.join(root,files1)) 
               


def log_pre_build_error(message, ldra_enable=0):
   
   ResultSummaryFile = "0_ALL_MplabX_ResultSummary.html"
   ResultSummaryFilePtr = open(ResultSummaryFile,"w")
   ResultSummaryFilePtr.write("<br>\n" + message)
   ResultSummaryFilePtr.write("\n\n<br>--[*FAIL*]")
   ResultSummaryFilePtr.close()
   
   if ldra_enable == 1:
   
      results_dir = "LDRA_Report"

      if os.path.exists(results_dir):
         shutil.rmtree(results_dir, 1)

      os.makedirs(results_dir)
      
      ResultSummaryFile = os.path.join(results_dir, "ldra_report.htm")
      ResultSummaryFilePtr = open(ResultSummaryFile,"w")
      ResultSummaryFilePtr.write("<br>\n" + message)
      ResultSummaryFilePtr.write("\n\n<br>--[*FAIL*]")
      ResultSummaryFilePtr.close()      
   
#######################################################
#######################################################

def get_str(Compiler_Log_file_location,i,ExecutingMakeFile,ResultMessage):
   
   retn = str(i+1) + ". " + ExecutingMakeFile + " - " + ResultMessage + "\n"
   retn = retn + ("-" * len(retn)) + "\n"
   
   scan = 0
   if os.path.exists(Compiler_Log_file_location):
      fptr = open(Compiler_Log_file_location,"r")
      for line in fptr:
      
         if re.search("Make File Execution End",line):
            scan = 0   
         if scan == 1:
            retn = retn + line
         if re.search("Executing for Makefile",line):
            scan = 1
      
         
      fptr.close()
   retn = "\n\n\n" + retn + "\n" + ("*" * 50) + "\n"
   
   return(retn)

#######################################################
#######################################################
def find_library_projects_in_existing_project(ProjectLocation):

   
   lib_projects = []
   
   config_xml_file = os.path.join(ProjectLocation, "nbproject")
   config_xml_file = os.path.join(config_xml_file, "configurations.xml")
   
   dom = parse(config_xml_file)
   
   configurationDescriptor = dom.childNodes
   
   for _node in configurationDescriptor:
      if _node.ELEMENT_NODE == _node.nodeType:
         all_nodes = _node.childNodes
         for all_node in all_nodes:
            if all_node.ELEMENT_NODE == all_node.nodeType:
               if all_node.nodeName == "confs":
                  confs_nodes = all_node.childNodes
                  for confs_node in confs_nodes:
                     if confs_node.ELEMENT_NODE == confs_node.nodeType:
                        if confs_node.nodeName == "conf":
                           conf_nodes = confs_node.childNodes
                           for conf_node in conf_nodes:
                              if conf_node.ELEMENT_NODE == conf_node.nodeType:
                                 if conf_node.nodeName == "compileType":
                                    compileTypeChildNodes = conf_node.childNodes
                                    for compileTypeChildNode in compileTypeChildNodes:
                                       if compileTypeChildNode.ELEMENT_NODE == compileTypeChildNode.nodeType:
                                          if compileTypeChildNode.nodeName == "linkerTool":                                    
                                             linkerToolChildNodes = compileTypeChildNode.childNodes
                                             for linkerToolChildNode in linkerToolChildNodes:
                                                if linkerToolChildNode.ELEMENT_NODE == linkerToolChildNode.nodeType:
                                                   if linkerToolChildNode.nodeName == "linkerLibItems":
                                                      linkerLibItemsChildNodes = linkerToolChildNode.childNodes
                                                      for linkerLibItemsChildNode in linkerLibItemsChildNodes:
                                                         if linkerLibItemsChildNode.ELEMENT_NODE == linkerLibItemsChildNode.nodeType:
                                                            if linkerLibItemsChildNode.nodeName == "linkerLibProjectItem":
                                                               linkerLibProjectItemChildNodes = linkerLibItemsChildNode.childNodes
                                                               for linkerLibProjectItemChildNode in linkerLibProjectItemChildNodes:
                                                                  if linkerLibProjectItemChildNode.ELEMENT_NODE == linkerLibProjectItemChildNode.nodeType: 
                                                                     if linkerLibProjectItemChildNode.nodeName == "makeArtifact":
                                                                        proj_path = linkerLibProjectItemChildNode.attributes["PL"].value.encode('ascii','ignore')
                                                                        
                                                                        # if the library project path is a relative path
                                                                        
                                                                        if re.search("\.\.",proj_path):
                                                                           proj_path = os.path.join(ProjectLocation, proj_path)
                                                                        
                                                                        proj_path = os.path.normpath(proj_path)
                                                                        
                                                                        lib_projects.append(proj_path)
   
   lib_projects = RemoveRedundantItems(lib_projects)
   
   return(lib_projects)

def fold_html_cell_string(in_string, fold_length):

   count = 0
   out_string = ''
   temp_count = 0
   
   for i in range(len(in_string)):
      count = count + 1
      temp_count = temp_count + 1
      out_string = out_string + in_string[i]

      if count >= fold_length and (in_string[i] == "/" or in_string[i] == "\\"):
         if (len(in_string) - temp_count) >= 3:
            out_string = out_string + "&nbsp&nbsp<br>"
         count = 0
   
   return(out_string)

def get_isp_installation_paths(CompilerPathRefFile):

   _HARMONY_INSTALLED_LOCATION_ = "NA"
   _HARMONY_INSTALLER_PLIB_INCLUDE_SEARCH_PATH_ = "NA"
   _HARMONY_PLIB_INSTALLER_LIB_PATH_ = "NA"
   _ISP_WS_ = ""
   
   isp_installation_dir = "NA"
   isp_include_search_path = "NA"
   isp_archived_lib_path = "NA"
   
   test_type = "TRUNK"
   isp_version = "NA"
   
   branch_svn_path = "NA"
   branch_include_search_path = "NA"
   branch_lib_path = "NA"
   
   isp_ws = ""
   
   if os.path.exists(CompilerPathRefFile):
   
      mcpr_file_pointer = open(CompilerPathRefFile,"r")
   
      for line in mcpr_file_pointer:
         line = line.strip("\n|\r")
         line = line.strip(" ")
         if line != '':
            
            if not re.search("^#",line):

               if re.search("^_ISP_BRANCH_SVN_LINK_",line):
                  branch_svn_path = re.split("=",line)[1]
                  
               if re.search("^_ISP_PLIB_BRANCH_INCLUDE_SEARCH_PATH_",line):
                  branch_include_search_path = re.split("=",line)[1]
                  
               if re.search("^_ISP_PLIB_BRANCH_LIB_PATH_",line):
                  branch_lib_path = re.split("=",line)[1]
                  
               if re.search("^_ISP_PLIB_INSTALLATION_DIR_PATH_",line):
                  isp_installation_dir = re.split("=",line)[1]
                  
               if re.search("^_ISP_PLIB_INSTALLER_INCLUDE_SEARCH_PATH_",line):
                  isp_include_search_path = re.split("=",line)[1]
                  
               if re.search("^_ISP_PLIB_INSTALLATION_VER_",line):
                  isp_version = re.split("=",line)[1]                  
               
               if re.search("^_ISP_PLIB_INSTALLER_LIB_PATH_",line):
                  isp_archived_lib_path = re.split("=",line)[1]
                  
               if re.search("^_ISP_TEST_TYPE_",line):
                  test_type = re.split("=",line)[1] 
               
               if re.search("^_ISP_WS_",line):
                  _ISP_WS_ = re.split("=",line)[1]


               if re.search("^_HARMONY_INSTALLED_LOCATION_",line):
                  _HARMONY_INSTALLED_LOCATION_ = re.split("=",line)[1]
               if re.search("^_HARMONY_INSTALLER_PLIB_INCLUDE_SEARCH_PATH_",line):
                  _HARMONY_INSTALLER_PLIB_INCLUDE_SEARCH_PATH_ = re.split("=",line)[1]
               if re.search("^_HARMONY_PLIB_INSTALLER_LIB_PATH_",line):
                  _HARMONY_PLIB_INSTALLER_LIB_PATH_ = re.split("=",line)[1]
                  
                  
                  
      
   if isp_installation_dir != "NA":
      isp_include_search_path = os.path.join(isp_installation_dir,isp_include_search_path)
      isp_include_search_path = os.path.normpath(isp_include_search_path)
      isp_include_search_path = re.sub(r"\\","/",isp_include_search_path)
      
      isp_archived_lib_path = os.path.join(isp_installation_dir,isp_archived_lib_path)
      isp_archived_lib_path = os.path.normpath(isp_archived_lib_path)
      isp_archived_lib_path = re.sub(r"\\","/",isp_archived_lib_path)      


   for i in range(len(sys.argv)):
      
      if re.search("^-test_type=",sys.argv[i]):
         test_type = re.split('=',sys.argv[i])[1]
         
      if re.search("^-link=",sys.argv[i]):
         
         branch_svn_path = re.split('=',sys.argv[i])[1]
         
         branch_svn_path = re.sub("\"","",branch_svn_path)
   
   return(_HARMONY_INSTALLED_LOCATION_, _HARMONY_INSTALLER_PLIB_INCLUDE_SEARCH_PATH_, _HARMONY_PLIB_INSTALLER_LIB_PATH_, _ISP_WS_)
   
   
def convert_include_directories(include_dirs, CompilerPathRefFile):

   return_path = ''
   if include_dirs == '':
      return_path = ''
   else:
      _HARMONY_INSTALLED_LOCATION_, _HARMONY_INSTALLER_PLIB_INCLUDE_SEARCH_PATH_, _HARMONY_PLIB_INSTALLER_LIB_PATH_, _ISP_WS_ = get_isp_installation_paths(CompilerPathRefFile)
      
      return_path = re.sub("_HARMONY_INSTALLED_LOCATION_", re.sub(r"\\", "/", _HARMONY_INSTALLED_LOCATION_), include_dirs)
      return_path = re.sub("_HARMONY_INSTALLER_PLIB_INCLUDE_SEARCH_PATH_", re.sub(r"\\", "/", _HARMONY_INSTALLER_PLIB_INCLUDE_SEARCH_PATH_), return_path)
      return_path = re.sub("_HARMONY_PLIB_INSTALLER_LIB_PATH_", re.sub(r"\\", "/", _HARMONY_PLIB_INSTALLER_LIB_PATH_), return_path)
      return_path = re.sub("_ISP_WS_", _ISP_WS_, return_path)

   return(re.sub(r"\\","/",return_path))



def GetCommonString(ListOfItems, Paths0_PlainText1):
   CommonString = ''
   
   LocalListOfItems = []
   if len(ListOfItems) == 0:
      CommonString = "SoMe_x:@#$"
   
   elif len(ListOfItems) == 1:
      
      CommonString = "SoMe_x:@#$"
      
   else:
   
      if Paths0_PlainText1 == 0:                # In case of Path, the change in the next Path should not be accounted 
         for i in ListOfItems:
            i = re.sub(r"\\","/",i)
            if re.search("/",i):
               Array = re.split("/",i)
               LocalListOfItems.append(Array)   # Split the path, based on the "/" character

      if len(LocalListOfItems) == len(ListOfItems):   # if any of the paths does not have "/" char, treat it as plain string.
         ListOfItems = LocalListOfItems
      else:
         Paths0_PlainText1 = 1


      MinLen = len(ListOfItems[0])              # The Common String Finding Engine starts from here.

      for i in ListOfItems:
         if len(i) < MinLen:   
            MinLen = len(i)

      FirstElement = ListOfItems[0]

      BreakAllLoops = 0

      for i in range(MinLen):
         MisMatchFoundInOneItem = 0
         for item in ListOfItems:
            if item[i] != FirstElement[i]:
               MisMatchFoundInOneItem = 1
         if MisMatchFoundInOneItem == 0:
            CommonString = CommonString + FirstElement[i]
            if Paths0_PlainText1 == 0:
               CommonString = CommonString + "/"
         else:
            break
     
      
   return(CommonString)

def compare_files(file_1, file_2):
   print "*" * 25
   print "*FILES COMPARISION*"
   print file_1
   print file_2
   print "*" * 25
   
   # # Nalini: 17 Dec 2014 - add support for comparing hex files

   if((file_1 == "") or (file_2 == "")):
      ## "0: One or both files missing"
      print "*No Hex File found for comparison -- one or both files missing*"
      return 0

   elif ((filecmp.cmp(file_1, file_2, shallow=1)) == False):
      ## "2: Files are different"
      print "*Changes detected in Hex File -- files are different*"
      # Call to Diff_Files is commented out for now
      # Diff_Files(cmpfile1, cmpfile2)
      return 2

   else:
      ## "1: Files are identical"
      print "*Hex File is not changed -- files are identical*"
      return 1


# # Nalini: 17 Dec 2014 - add support for comparing hex files
# Diff_Files function generates a diff report for the two input files. Diff report can be generated in text or html format 
# Diff_Files is commented out for now
# 
# def Diff_Files(infile1, infile2):    
#     
#     # paths of files to store diff output
#     textout = "diff.txt"
#     htmlout = "diff.html"
#     
#     if (infile1 != ""):
#         f1 = open(infile1, 'r')
#         f1lines = f1.readlines()
#         f1.close()
#     
#     if (infile2 != ""):
#         f2 = open(infile2, 'r')
#         f2lines = f2.readlines()
#         f2.close()
#     
#     out = open(textout, 'a')
#     for line in difflib.unified_diff(f1lines, f2lines, fromfile='file1', tofile='file2'):
#         out.write(line)
#     out.close()
#     
#     diff = difflib.HtmlDiff()    
#     html = diff.make_file(f1lines, f2lines, fromdesc='file1', todesc='file2')
#     out = open(htmlout, 'a')
#     out.writelines(html)
#     out.close()
#     return
   
def copy_files_for_commit(make_file_number, ProjectLocation, commit_artifacts_files, dir_for_storing_commit_artifacts, project_make_file, commit_artifact_name, commit_artifact_dir, commit_en, COSVNLink, DirectoryForScan):

   ###############################################################################
   ###############################################################################
   commit_directory = "commit_dir"
   
   file_comparision_result = 0
   
   if make_file_number == 0:
   
      ProjectLocation1 = re.sub(r"\\", "/", ProjectLocation)
      
      temp_proj_loc = re.split("Project", ProjectLocation1)[1].strip(" ").strip("/|\\").strip(" ")
      temp_dir_for_scan = re.split("Project", DirectoryForScan)[1].strip(" ").strip("/|\\").strip(" ")
      
      temp = ProjectLocation1 # Dummy Assignment for variable initialization
      
      if temp_dir_for_scan == '':
         temp = COSVNLink.strip("/") + "/" + temp_proj_loc
      else:
         temp = re.sub(temp_dir_for_scan, "", temp_proj_loc)
         temp = COSVNLink.strip("/") + "/" + temp
      
      # temp is the project directory   
      svn_project_link = temp
      arti_link = os.path.join(svn_project_link, commit_artifact_dir)
      
      arti_link = os.path.normpath(arti_link)
      arti_link = re.sub(r"\\","/",arti_link)
      arti_link = re.sub(":/","://",arti_link)
      svn_base_path = arti_link
      
      if os.path.exists(commit_directory):
         try:
            shutil.rmtree(commit_directory)
         except:
            print "unable to remove CO Dir"

      try:
         os.mkdir(commit_directory)
      except:
         print "unable to mkdir"
         
      co_command = "svn co \"" + svn_base_path + "\" \"" + commit_directory + "\" " + " --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
      print co_command
      os.system(co_command)
   ######################################################################
   ######################################################################
   
   
   FileNames = []
   DirNames = []
   
   project_name = ''
   project_folder_name = ''
   
   temp = os.path.split(ProjectLocation)[0]
   project_folder_name = os.path.split(temp)[1]
   
   configuration_name = re.sub("Makefile-","",project_make_file)
   configuration_name = re.sub(".mk","",configuration_name)
   
   
   
   config_xml_file = os.path.join(ProjectLocation, "nbproject")
   config_xml_file = os.path.join(config_xml_file, "project.xml")
   
   if os.path.exists(config_xml_file):
   
      dom = parse(config_xml_file)
      proj_name_node = dom.getElementsByTagName("name")[0]
      if len(proj_name_node.childNodes) >= 1:
         project_name = proj_name_node.childNodes[0].data.encode('ascii','ignore')    
   
   if project_name == '':
      project_name = os.path.split(ProjectLocation)[1]
   
   
   if os.path.isdir(ProjectLocation):                                 # if the given path is a directory, 
      for root, dirs, files in os.walk(ProjectLocation):              # Now, List the directories and files available in the 
         if not re.search("\.svn",root):
            for files1 in files:                                  # directory provided.
               FileNames.append(os.path.join(root,files1))        # If it is a file, join it with the root and append it into an array 
            for dirs1 in dirs:                                    # for processing further
               DirNames.append(os.path.join(root,dirs1))          # if it is a directory, then, do the same operation, mentioned above. 
 
   commit_artifacts_files = re.sub(" ","", commit_artifacts_files)
   artifact_types = re.split(",",commit_artifacts_files)
   for i in range(len(FileNames)):
      for j in range(len(artifact_types)):
         if os.path.splitext(FileNames[i])[1] == os.path.splitext(artifact_types[j])[1]:
            
            final_file_name = ''
            
            if commit_artifact_name != '':
            
               temp = commit_artifact_name
               temp = re.sub("\[F\]", project_folder_name, temp)
               temp = re.sub("\[C\]", configuration_name, temp)
               temp = re.sub("\[P\]", project_name, temp)
               temp = temp + os.path.splitext(artifact_types[j])[1]
               
               final_file_name = temp
               
               shutil.copy(FileNames[i], os.path.join(dir_for_storing_commit_artifacts, temp))
            else:
               shutil.copy(FileNames[i], dir_for_storing_commit_artifacts)
               
               final_file_name = os.path.split(FileNames[i])[1]
            
            file_comparision_result = compare_files(FileNames[i], os.path.join(commit_directory, final_file_name))
   
   if commit_en == 1:
      
      ProjectLocation1 = re.sub(r"\\", "/", ProjectLocation)
      
      temp_proj_loc = re.split("Project", ProjectLocation1)[1].strip(" ").strip("/|\\").strip(" ")
      temp_dir_for_scan = re.split("Project", DirectoryForScan)[1].strip(" ").strip("/|\\").strip(" ")
      
      temp = ProjectLocation1 # Dummy Assignment for variable initialization
      
      if temp_dir_for_scan == '':
         temp = COSVNLink.strip("/") + "/" + temp_proj_loc
      else:
         temp = re.sub(temp_dir_for_scan, "", temp_proj_loc)
         temp = COSVNLink.strip("/") + "/" + temp
      
      # temp is the project directory   
      svn_project_link = temp
      arti_link = os.path.join(svn_project_link, commit_artifact_dir)
      
      arti_link = os.path.normpath(arti_link)
      arti_link = re.sub(r"\\","/",arti_link)
      arti_link = re.sub(":/","://",arti_link)
      
      print arti_link
      
      
      

      if os.path.exists(commit_directory):
         try:
            shutil.rmtree(commit_directory)
         except:
            print "unable to remove CO Dir"

      try:
         os.mkdir(commit_directory)
      except:
         print "unable to mkdir"
      
      svn_base_path = arti_link
      error = 1
      
      split_residue = ''
      
      iteration = 5
      
      while error == 1:
      
         if iteration > 0:
            iteration = iteration - 1
         else:
            return
            
         co_command = "svn ls \"" + svn_base_path + "\"" + " --depth empty --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
         print co_command
         if os.system(co_command) == 0:
            error = 0
         else:
            a = os.path.split(svn_base_path)
            svn_base_path = a[0]
            svn_base_path = os.path.normpath(svn_base_path)
            svn_base_path = re.sub(r"\\","/",svn_base_path)
            svn_base_path = re.sub(":/","://",svn_base_path)            
            split_residue = a[1] + "/" + split_residue
            time.sleep(1)
      
      
      if os.path.exists(commit_directory):
         try:
            shutil.rmtree(commit_directory)
         except:
            print "unable to remove CO Dir"


         
      
      co_command = "svn co \"" + svn_base_path + "\" \"" + commit_directory + "\" " + " --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
      print co_command
      os.system(co_command)
      temp = os.path.join(commit_directory, split_residue.strip(" ").rstrip("/")).strip(r"\\")
      
      try:
         os.makedirs(temp)
      except:
         print "unable to mkdir"
         
         
      dirfiles = os.listdir(dir_for_storing_commit_artifacts)
      for file in dirfiles:
         shutil.copy(os.path.join(dir_for_storing_commit_artifacts, file), temp)
      
      cwd = os.getcwd()
      os.chdir(commit_directory)
      print os.getcwd()
      
      #co_command = "svn cleanup \"" + os.getcwd() + "\"" + " --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
      #os.system(co_command)
      
      co_command = "svn add \"*\"" + " --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
      os.system(co_command)
         
      co_command = "svn commit -m \"Adding Artifacts from ARBS Build Result\" --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
      print co_command
      os.system(co_command)  
         
      os.chdir(cwd)
      
   return(file_comparision_result)
#######################################################
#######################################################
if __name__ == "__main__":
   

############

   CompilerToBeUsed = ''
   DirectoryForScan = ''
   CheckoutRevision = ''
   COSVNLink = ''
   ProjectName = ''
   job_name = ''
   multiple_options_build = 0
   commit_artifacts_files = ''
   commit_artifact_name = ''
   commit_artifact_dir = ''
   
   ldra_include_dir=""
   ldra_exclude_dir=""
   ldra_system_variables_file=""
   ldra_system_search_path_file=""
   
   mysql_log_result = 0
   
   enable_ldra_analysis = 0
   ldra_options_file = ''
   ldra_set_name = ''
   
   report_gen_project_location = []
   report_gen_configuration = []
   report_generation_result = []

   if len(sys.argv) <= 1:
      print "\nError ! \nFeed the Project Directory and/or the compiler to be used for build"
      log_pre_build_error("\nError ! \nFeed the Project Directory and/or the compiler to be used for build", 1)
      exit()

   if len(sys.argv) >= 15:
      print "\nError ! \n Unknown number of parameters passed"
      log_pre_build_error("\nError ! \n Unknown number of parameters passed", 1)
      exit()   

   PRCount = 0
   test_type = ''
   test_link = ''
   user_input_compiler_options_file = ''
   
   include_dirs = ''

   for Parameter in sys.argv:
      PRCount = PRCount + 1

      if PRCount == 2:
         DirectoryForScan = Parameter
      elif PRCount >= 3:
         if re.search("-cor=",Parameter.lower()):
            CheckoutRevision = re.sub("-cor=",'',Parameter)
         elif re.search("-com=",Parameter.lower()):
            Parameter = re.sub("-com=",'',Parameter)
            CompilerToBeUsed = Parameter.upper()
         elif re.search("-link=",Parameter.lower()):
            Parameter = re.sub("-link=",'',Parameter)
            COSVNLink = Parameter
            if 'win32' == sys.platform:
               COSVNLink = re.sub(r"\\","/",COSVNLink)
               COSVNLink = re.sub(":/","://",COSVNLink)
         elif re.search("-pro=",Parameter.lower()):
            Parameter = re.sub("-pro=",'',Parameter)
            ProjectName = Parameter
         elif re.search("-job=",Parameter.lower()):
            Parameter = re.sub("-job=",'',Parameter)
            job_name = Parameter            
         elif re.search("-test_type=",Parameter.lower()):
            Parameter = re.sub("-test_type=",'',Parameter)
            test_type = Parameter  
         elif re.search("-test_link=",Parameter.lower()):
            Parameter = re.sub("-test_link=",'',Parameter)
            test_link = Parameter  
         elif re.search("-cop=",Parameter.lower()):
            Parameter = re.sub("-cop=",'',Parameter)
            user_input_compiler_options_file = Parameter              
         elif re.search("-include_dir=",Parameter.lower()):
            Parameter = re.sub("-include_dir=",'',Parameter)
            include_dirs = Parameter
         elif re.search("-commit_artifacts=",Parameter.lower()):
            commit_artifacts_files = re.split("=",Parameter)[1]  
            commit_artifacts_files = commit_artifacts_files.strip(" ")
            commit_artifacts_files = re.sub(" ","",commit_artifacts_files)
            commit_artifacts_files = re.sub("\"","",commit_artifacts_files)
            commit_artifacts_files = re.sub("\'","",commit_artifacts_files)
            
         elif re.search("-commit_artifact_name=",Parameter.lower()):
            Parameter = re.sub("-commit_artifact_name=",'',Parameter)
            commit_artifact_name = Parameter
            
         elif re.search("-commit_artifact_dir=",Parameter.lower()):
            Parameter = re.sub("-commit_artifact_dir=",'',Parameter)
            commit_artifact_dir = Parameter
            
         elif re.search("-mysql_log_result",Parameter.lower()):
            mysql_log_result = 1  
         
         elif re.search("-en_ldra",Parameter.lower()):
            enable_ldra_analysis = 1
         elif re.search("-ldra_options_file=",Parameter.lower()):
            Parameter = re.sub("-ldra_options_file=",'',Parameter)
            ldra_options_file = Parameter
         elif re.search("-ldra_set_name=",Parameter.lower()):
            Parameter = re.sub("-ldra_set_name=",'',Parameter)
            ldra_set_name = Parameter
         elif re.search("-ldra_include_dir=",Parameter.lower()):
            Parameter = re.sub("-ldra_include_dir=",'',Parameter)
            ldra_include_dir = Parameter
         elif re.search("-ldra_exclude_dir=",Parameter.lower()):
            Parameter = re.sub("-ldra_exclude_dir=",'',Parameter)
            ldra_exclude_dir = Parameter
         elif re.search("-ldra_system_variables_file=",Parameter.lower()):
            Parameter = re.sub("-ldra_system_variables_file=",'',Parameter)
            ldra_system_variables_file = Parameter
         elif re.search("-ldra_system_search_path_file=",Parameter.lower()):
            Parameter = re.sub("-ldra_system_search_path_file=",'',Parameter)
            ldra_system_search_path_file = Parameter            
            
   
            

   StatisticsFileString = "MPLAB_TYPE:X\n"
   
   StatisticsFileName = CompilerToBeUsed + "_MPLABX_Statistics.statinfo"
   EmailErrorFileName = CompilerToBeUsed + "_MPLABX.errinfo"
   
   if enable_ldra_analysis == 0:
   
      ClientSetupStatus, ErrorMessage = client_status.Get()

      ErrorFileName = CompilerToBeUsed + "_ClientSetupError_MPLABX.html"

      if ClientSetupStatus != 0:
         Fptr = open(ErrorFileName,"w")
         Fptr.write(ErrorMessage)
         Fptr.close()

         Fptr = open(EmailErrorFileName,"w")
         Fptr.write(ErrorMessage)
         Fptr.close()

         exit()
      
   McpFileNames = []
   McpFileDir = []

   if DirectoryForScan == '':
      print "\nError ! \nNo directory specified"
      log_pre_build_error("Project Directory: " + DirectoryForScan + "<br>\nError ! \nNo directory specified", enable_ldra_analysis)
      exit()
   
   if not (CompilerToBeUsed == "ALL" or CompilerToBeUsed == "C18" or CompilerToBeUsed == "C30" or CompilerToBeUsed == "C32" or CompilerToBeUsed == "PICC" or CompilerToBeUsed == "PICC18" or CompilerToBeUsed == '' or CompilerToBeUsed == "XC8" or CompilerToBeUsed == "XC8-C18" or CompilerToBeUsed == "XC16" or CompilerToBeUsed == "XC32"):
      print "Unknown Compiler"
      log_pre_build_error("Unknown Compiler")
      exit()
   
   
   if CompilerToBeUsed == '':
      CompilerToBeUsed = "ALL"
      
   if not (re.search(";", DirectoryForScan) or os.path.isfile(DirectoryForScan)):  # in case of LDRA input, these will be files.
      if not os.path.exists(DirectoryForScan):
         print "\nError ! \nSpecified Directory not found"
         log_pre_build_error(DirectoryForScan + "<br>\nError ! \nSpecified Directory not found", enable_ldra_analysis)
         exit()
   
   built_in_compiler_path_ref_file = "mcpr_modified.mcpr"
   CompilerPathRefFile = ''
   
   if os.path.exists(built_in_compiler_path_ref_file):
      CompilerPathRefFile = built_in_compiler_path_ref_file
   else:
      
      if 'win32' == sys.platform:
         CompilerPathRefFile = "C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr" 
      elif 'linux2' == sys.platform:                                 # Linux
         CompilerPathRefFile = "/home/ARBS_SUPPORT/LIN_ToolSuiteLocations.mcpr" 
      elif 'darwin' == sys.platform:                                 # MAC 
         CompilerPathRefFile = "/Users/ARBS_SUPPORT/MAC_ToolSuiteLocations.mcpr"
      
   if not os.path.exists(CompilerPathRefFile):
   
      print "Error !!\n Compiler Paths References File not found"
      exit()
      
   ############
   CompilerPathRefFile = ''
   
   if os.path.exists(built_in_compiler_path_ref_file):
      CompilerPathRefFile = built_in_compiler_path_ref_file
      
   else:   
   
      if 'win32' == sys.platform:
         CompilerPathRefFile = "C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr" 
      elif'linux2' == sys.platform:                                 # Linux
         CompilerPathRefFile = "/home/ARBS_SUPPORT/LIN_ToolSuiteLocations.mcpr" 
      elif 'darwin' == sys.platform:                                 # MAC 
         CompilerPathRefFile = "/Users/ARBS_SUPPORT/MAC_ToolSuiteLocations.mcpr"
      
   include_dirs = convert_include_directories(include_dirs, CompilerPathRefFile)
   
   ProjectLocations = []
   
   if not (re.search(";", DirectoryForScan) or os.path.isfile(DirectoryForScan)):  # in case of LDRA input, these will be files.
      ProjectLocations = FindProjectDirectories(os.path.normpath(DirectoryForScan))   
   
   if enable_ldra_analysis == 1:
      if ldra_set_name == '':
         ldra_set_name = job_name
      ldra_support.analyze(ProjectLocations, os.path.normpath(DirectoryForScan), ldra_options_file, ldra_set_name, test_type, test_link, ldra_include_dir, ldra_exclude_dir, ldra_system_variables_file, ldra_system_search_path_file)
      sys.exit()
   
   
   
   Project_Location = []
   ProjLocationChange = []
   ExecutingMakeFile = []
   PassFailStatus = []
   CompilerMessage = []
   HexFileChangeStatus = []
   
   Compiler_Log_file_location = []
   
   build_dur = []
   row_options_file, col_options_file, user_input_compilers = [],[],[]
   
   if user_input_compiler_options_file != '':
      if os.path.exists(user_input_compiler_options_file):
         row_options_file, col_options_file, user_input_compilers = multiple_compiler_options.get_user_options(user_input_compiler_options_file)
         #print row_options_file, col_options_file
         if len(user_input_compilers) > 0:
            multiple_options_build = 1
   
   ###################################################################
   # Generating the Results File in the results Directory
   ###################################################################
   ResultsFinalDirectory = ''
   
   if ProjectName != '':
      ResultsFinalDirectory = ProjectName + "_" + CompilerToBeUsed
      StatisticsFileName = ProjectName + "_" + StatisticsFileName
   else:
      ResultsFinalDirectory = CompilerToBeUsed
      
      
   ResultsDirectory = os.path.join(os.getcwd(),"Archives")
   ResultsDirectory = os.path.join(ResultsDirectory,"MplabX")
   ResultsDirectory = os.path.join(ResultsDirectory,ResultsFinalDirectory)
   
   UsageResultsDirectory = '"' + ResultsDirectory + '"'
   
   if 'win32' == sys.platform:

      if os.path.exists(ResultsDirectory):
         RemoveCommand = "rmdir /S /Q " + os.path.normpath(UsageResultsDirectory)
         os.system('"' + RemoveCommand + '"')
      
      CreateResultsDirectoryCommand = "mkdir " + os.path.normpath(UsageResultsDirectory)

      os.system('"' + CreateResultsDirectoryCommand + '"')

   else:
      if os.path.exists(ResultsDirectory):
         RemoveCommand = "rm -rf " + os.path.normpath(UsageResultsDirectory)

         CmdFilePtr = open("CmdFile.sh","w")
         CmdFilePtr.write(RemoveCommand)
         CmdFilePtr.close()
         
         os.system("sh CmdFile.sh")
      
      CreateResultsDirectoryCommand = "mkdir -p " + os.path.normpath(UsageResultsDirectory)

      CmdFilePtr = open("CmdFile.sh","w")
      CmdFilePtr.write(CreateResultsDirectoryCommand)
      CmdFilePtr.close()
      
      os.system("sh CmdFile.sh")
      os.remove("CmdFile.sh")
      
   #######################################################################
   # m_ variable arrays for multiple build options
   m_project_location = []
   m_configuration = []
   m_result = []
   m_result_file_location = []
   m_pmem = []
   m_dmem = []
   m_build_dur = []
   m_col_options = []
   m_row_options = []
   m_tgt_compiler = []
   m_run_conf_default_option = []
   
   m_col_merge = []
   
   dir_for_storing_commit_artifacts = "artifact_dir"
   
   if ProjectLocations != []:
   
      if os.path.exists(os.path.join(os.getcwd(),"CompilerMessages.temp")):
         os.remove("CompilerMessages.temp")

      project_location_change = 0
      project_count = 0
      
      ProjectLocations = sorted(ProjectLocations)
      pcount_temp = 0
      
      temp_config_holding_dir = "config_modified"
      
      if os.path.exists(temp_config_holding_dir):
         shutil.rmtree(temp_config_holding_dir, 1)
      try:
         os.mkdir(temp_config_holding_dir)
      except:
         print ""
               
               
      for ProjectLocation in ProjectLocations:
         pcount_temp = pcount_temp + 1
         project_location_change = 1
         LogFileLocation = os.path.join(os.getcwd(),"LogFile.txt")
         #os.chmod(os.getcwd(),0777)
         if os.path.exists(LogFileLocation):
            os.chmod(LogFileLocation,0777)
            os.remove(LogFileLocation)
         
         remove_all_make_files(ProjectLocation)
         
         time.sleep(1)
         
         project_config_file_size_error = 0
         config_file = os.path.join(ProjectLocation, "nbproject")
         config_file = os.path.join(config_file, "configurations.xml")
         
         config_file_size = int(os.path.getsize(config_file))
         if config_file_size > 10000000 or config_file_size == 0:
            project_config_file_size_error = 1
         
         project_xml_file_error = xml_operation.find_valid_xml(config_file)
         ## clear it for every project ##
         if commit_artifacts_files != '':
            
            if os.path.exists(dir_for_storing_commit_artifacts):
            
               shutil.rmtree(dir_for_storing_commit_artifacts, 1)
            
            os.mkdir(dir_for_storing_commit_artifacts)
               
         if multiple_options_build == 0:
            
            if project_config_file_size_error == 0 and project_xml_file_error == 0:
            
               make_operations.re_create_make_files(CompilerPathRefFile, ProjectLocation, include_dirs)
               make_operations.re_create_misc_make_files(ProjectLocation)
               time.sleep(1)
               lib_project_locations = find_library_projects_in_existing_project(ProjectLocation)

               for lib_project_location in lib_project_locations:

                  make_operations.re_create_make_files(CompilerPathRefFile, lib_project_location, include_dirs)
                  Command = "python main.py -project_location=\"" + lib_project_location + '"'
                  os.system(Command)
                  time.sleep(2)
                  #make_operations.re_create_misc_make_files(lib_project_location)            

               #project_make_files, _count = make_operations.FindMakeFile(os.path.join(ProjectLocation, "nbproject"))
               project_make_files, compilers = xml_operation.get_all_project_config(ProjectLocation)
               _count = len(project_make_files)
            else:
               project_make_files = ["Unknown"]
               _count = 1
               
            project_make_files = sorted(project_make_files)

            print '*' * 50
            print "Building the Project Location: " + ProjectLocation
            print '*' * 50
            pass0_fail2 = 2
            hex_file_change = 0
            
            for i in range(len(project_make_files)):

               project_count = project_count + 1
               
               print "\n\n*** " + str(pcount_temp) + "/" + str(len(ProjectLocations)) + ", " + str(i+1) + "/" + str(len(project_make_files)) + ", PLOC:" + ProjectLocation + ", CONF:" + project_make_files[i] + " ***\n"
               
               Project_Location.append(ProjectLocation)            
               ProjLocationChange.append(project_location_change)
               project_location_change = 0
               configuration_name = re.sub("Makefile-","",project_make_files[i])
               configuration_name = re.sub(".mk","",configuration_name)
               
               project_build_error = 0
               
               make_file_not_available_error = 0
               
               
               
               if not os.path.exists(os.path.join(os.path.join(ProjectLocation, "nbproject"), "Makefile-" + configuration_name + ".mk")):
                  make_file_not_available_error = 1
               else:
                  make_file_size = int(os.path.getsize(os.path.join(os.path.join(ProjectLocation, "nbproject"), "Makefile-" + configuration_name + ".mk")))
                  if make_file_size == 0:
                     make_file_not_available_error = 1
               
               if project_config_file_size_error != 0 or make_file_not_available_error != 0 or project_xml_file_error != 0:
                  project_build_error = 1
               
               if project_build_error == 0:
                  _compiler = xml_operation.get_compiler(ProjectLocation, configuration_name)
               else:
                  _compiler = "Unknown"
                  
               if len(_compiler) < 4:
                  _count = len(_compiler)
                  while _count < 4:
                     _compiler = _compiler + " "
                     _count = _count + 1
               ExecutingMakeFile.append("[" + _compiler + "] " + configuration_name)
               
               
               rerun = 1
               rerun_count = 2
               
               if project_build_error == 0:
               
                  while rerun != 0:

                     if os.path.exists(LogFileLocation):
                        #os.chmod(LogFileLocation,0777)
                        os.remove(LogFileLocation)

                     time.sleep(0.1)

                     Command = "python -u main.py -project_location=\"" + ProjectLocation + '" ' + "-make_file=" + project_make_files[i] + " -commit_artifacts=" + re.sub(" ","",commit_artifacts_files)

                     if CompilerToBeUsed.upper() != "ALL":
                        Command = Command + " -in_compiler=" + CompilerToBeUsed
                     try:
                        system_exit_retry = 2
                        exec_failure = 0
                        while os.system(Command) != 0:
                           exec_failure = 1
                           if system_exit_retry > 0:
                              system_exit_retry = system_exit_retry - 1
                              time.sleep(10)
                              make_operations.re_create_make_files(CompilerPathRefFile, ProjectLocation, include_dirs)
                              make_operations.re_create_misc_make_files(ProjectLocation)
                              time.sleep(1)                        
                           else:
                              rerun = 0   # max number of iterations reached, No need to rerun. 
                              break
                        
                        if exec_failure == 0:
                           rerun = 0   # Everything is fine, No need to rerun. 
                        
                     except:
                        LogFileLocation = os.path.join(os.getcwd(),"LogFile.txt")
                        #if not os.path.exists(LogFileLocation):
                        Text = "\n\n_ARBS_Build_Started_\n"
                        Text = Text + "Executing for Makefile: ERROR Unknown\n"
                        Text = Text + "Error: File access Error encountered in execution\nPlease test this project manually\n"
                        Text = Text + "Make File Execution End"
                        Text = Text + "\n_ARBS_Build_Ends_Here_"
                        LogFilePtr = open("LogFile.txt",'a')
                        LogFilePtr.write(Text)
                        LogFilePtr.close()

                     #os.chmod(LogFileLocation,0777)
                     time.sleep(1)  # Wait for 5 Seconds before starting for copy of results file

                     pass0_fail2, log_file_loc, dur, pmem, dmem = CopyLogFile1(ResultsDirectory, project_count)

                     if commit_artifacts_files != '' and COSVNLink != '' and commit_artifact_dir != '':
                        commit_en = 0
                        if i == len(project_make_files) - 1:
                           commit_en = 1   
                        hex_file_change = copy_files_for_commit(i, ProjectLocation, commit_artifacts_files, dir_for_storing_commit_artifacts, project_make_files[i], commit_artifact_name, commit_artifact_dir, commit_en, COSVNLink, DirectoryForScan)

                     if rerun !=0:
                        if pass0_fail2 == 2 or dur == "NA":
                           rerun = 1
                           if rerun_count > 0:
                              rerun_count = rerun_count - 1
                           else:
                              rerun = 0
                        else:
                           rerun = 0
               else:
               
                  LogFileLocation = os.path.join(os.getcwd(),"LogFile.txt")
                  #if not os.path.exists(LogFileLocation):
                  Text = "\n\n_ARBS_Build_Started_\n"
                  if project_config_file_size_error != 0:
                     Text = Text + "Executing for Makefile: Unknown\n"
                     Text = Text + "Error: Project Configuration file size is exceeding 10MB, which is unexpected\n\n"

                  elif project_xml_file_error != 0:
                     Text = Text + "Executing for Makefile: " + project_make_files[i] + "\n"
                     Text = Text + "Error: Unable to process the project configurations. Possibly project XML file is corrupt\n\n"
                     
                  elif make_file_not_available_error != 0:
                     Text = Text + "Executing for Makefile: " + project_make_files[i] + "\n"
                     Text = Text + "Error: MPLAB X IDE is unable to create make file for the configuration\n\n"
                     Text = Text + "Error: File access Error encountered in execution\n"

                     
                  Text = Text + "Make File Execution End"
                  Text = Text + "\n_ARBS_Build_Ends_Here_"                     
                  LogFilePtr = open("LogFile.txt",'w')
                  LogFilePtr.write(Text)
                  LogFilePtr.close()

                  #os.chmod(LogFileLocation,0777)
                  time.sleep(1)  # Wait for 5 Seconds before starting for copy of results file

                  pass0_fail2, log_file_loc, dur, pmem, dmem = CopyLogFile1(ResultsDirectory, project_count)   
                  pass0_fail2 = 2
                  dur = "NA"
                  pmem = "NA"
                  dmem = "NA"
                  
               '''
               pass0_fail2 = pass0_fail2 + 1
               if pass0_fail2 >= 3:
                  pass0_fail2 = 0
               log_file_loc = "sdfkvjsdfkvnjsdfv"
               pmem = "23458809 Bytes"
               dmem = "3958 Bytes"
               dur = "24 Sec"
               '''   
               PassFailStatus.append(pass0_fail2)
               Compiler_Log_file_location.append(log_file_loc)
               build_dur.append(dur)
               HexFileChangeStatus.append(hex_file_change)
               
               
            remove_all_make_files(ProjectLocation)
            
            
            
            
            
            
            
         else:
            
            m_configuration_1d = []
            #row_options, col_options = multiple_compiler_options.get_user_options(user_input_compiler_options_file)
            #print row_options, col_options
            
            #if len(col_options) == 0:
            #   col_options.append("default_options")
            #if len(row_options) == 0:
            #   row_options.append("default_options")
               
            # Create make files for the Library projects, if any. 
            # This is a workaround for the make file creator not creating the make files for the attached library projects.
            project_count = project_count + 1
            all_conf = []

            _row_options = []
            _col_options = []
            _run_conf_default_option = []
            _tgt_compiler = []
               
            if project_config_file_size_error == 0 and project_xml_file_error == 0:
            
               lib_project_locations = find_library_projects_in_existing_project(ProjectLocation)
               for lib_project_location in lib_project_locations:

                  make_operations.re_create_make_files(CompilerPathRefFile, lib_project_location, include_dirs)
                  Command = "python main.py -project_location=\"" + lib_project_location + '"'
                  os.system(Command)
                  time.sleep(2)            




               _all_conf, _all_compiler = xml_operation.get_all_project_config(ProjectLocation)

            else:
               _all_conf, _all_compiler = ["unknown_configuration"], ["XC32"]
               
            # Sort all the configuration
            #_all_conf = sorted(_all_conf)

            for i in range(len(_all_conf)):
               if _all_compiler[i] == "XC8" or _all_compiler[i] == "XC16" or _all_compiler[i] == "XC32":

                  _tgt_compiler.append(_all_compiler[i])

                  # Flitering out All XC compilers f
                  # only XC compilers are supported for multiple build options
                  #row_options_file, col_options_file, user_input_compilers
                  #print _all_compiler[i]
                  all_conf.append(_all_conf[i])
                  found = 0
                  for j in range(len(user_input_compilers)):
                     if _all_compiler[i] == user_input_compilers[j]:
                        found = 1
                        _row_options.append(row_options_file[j])
                        _col_options.append(col_options_file[j])
                        break
                  if found == 0:
                     _row_options.append(["default_options"])
                     _col_options.append(["default_options"]) 
                     _run_conf_default_option.append(1)
                  else:
                     _run_conf_default_option.append(0)


            
               #for i in range(len(all_conf)):
               #   print all_conf[i]
               #   print _row_options[i]
               #   print _col_options[i]
               #   print _run_conf_default_option[i]
               #   print _tgt_compiler[i]
               
            

            
            all_conf_results_1d = []
            all_conf_result_file_location = []
            all_conf_pmem = []
            all_conf_dmem = []
            all_conf_build_dur = []
            all_conf_row_options = []
            all_conf_col_options = []
            all_conf_compiler = []
            all_run_default_options = []
            
            
            for i in range(len(all_conf)):

               m_configuration_1d.append(all_conf[i])
               row_results_1d = []
               row_result_file_location = []
               row_pmem = []
               row_dmem = []
               row_build_dur = []
               
               all_conf_row_options.append(_row_options[i])
               all_conf_col_options.append(_col_options[i])
               all_conf_compiler.append(_tgt_compiler[i])
               all_run_default_options.append(_run_conf_default_option[i])
               
               row_options = _row_options[i]
               col_options = _col_options[i]
               
               if row_options == []:
                  row_options.append("default_options")
               if col_options == []:
                  col_options.append("default_options") 

               for j in range(len(row_options)):

                  col_results_1d = []
                  col_result_file_location = []
                  col_pmem = []
                  col_dmem = []
                  col_build_dur = []
                  pass0_fail2 = 2
                  for k in range(len(col_options)):
                  
                     if project_config_file_size_error == 0 and project_xml_file_error == 0:
                                          
                        # 
                        # Update the compiler option in the configuration
                        #
                        tgt_compiler, update_done = multiple_compiler_options.update_configuration(ProjectLocation, all_conf[i], re.split(",",col_options[k]), re.split(",",row_options[j]))

                        temp_xml = str(project_count) + str(i) + str(j) + str(k) + ".xml"
                        temp_xml = os.path.join(temp_config_holding_dir, temp_xml)

                        config_xml_path = os.path.join(ProjectLocation, "nbproject/configurations.xml")
                        config_xml_path = os.path.normpath(config_xml_path)
                        try:
                           shutil.copy(config_xml_path, temp_xml)
                        except:
                           print ""

                        # Create the make files
                        make_operations.re_create_make_files(CompilerPathRefFile, ProjectLocation, include_dirs)
                        make_operations.re_create_misc_make_files(ProjectLocation)
                        time.sleep(1)   
                        make_file_size = 0
                        
                        if os.path.exists(os.path.join(os.path.join(ProjectLocation, "nbproject"), "Makefile-" + all_conf[i] + ".mk")):
                           make_file_size = int(os.path.getsize(os.path.join(os.path.join(ProjectLocation, "nbproject"), "Makefile-" + all_conf[i] + ".mk")))

                        if os.path.exists(os.path.join(os.path.join(ProjectLocation, "nbproject"), "Makefile-" + all_conf[i] + ".mk")) and make_file_size != 0:

                           #
                           # Copied from above
                           #
                           #
                           rerun = 1
                           rerun_count = 2

                           while rerun != 0:

                              if os.path.exists(LogFileLocation):
                                 #os.chmod(LogFileLocation,0777)
                                 os.remove(LogFileLocation)

                              time.sleep(0.2)

                              Command = "python main.py -project_location=\"" + ProjectLocation + '" ' + "-make_file=" + all_conf[i]

                              if tgt_compiler != "":
                                 Command = Command + " -in_compiler=" + tgt_compiler
                              #print Command
                              try:
                                 system_exit_retry = 2
                                 exec_failure = 0
                                 while os.system(Command) != 0:
                                    exec_failure = 1
                                    if system_exit_retry > 0:
                                       system_exit_retry = system_exit_retry - 1
                                       time.sleep(10)
                                       make_operations.re_create_make_files(CompilerPathRefFile, ProjectLocation, include_dirs)
                                       make_operations.re_create_misc_make_files(ProjectLocation)
                                       time.sleep(1)                        
                                    else:
                                       rerun = 0   # max number of iterations reached, No need to rerun
                                       break

                                 if exec_failure == 0:
                                    rerun = 0   # everything is fine, No need to rerun
                              except:
                                 LogFileLocation = os.path.join(os.getcwd(),"LogFile.txt")
                                 #if not os.path.exists(LogFileLocation):
                                 Text = "\n\n_ARBS_Build_Started_\n"
                                 Text = Text + "Executing for Makefile: ERROR Unknown\n"
                                 Text = Text + "Error: File access Error encountered in execution\nPlease test this project manually\n"
                                 Text = Text + "Make File Execution End"
                                 Text = Text + "\n_ARBS_Build_Ends_Here_"
                                 LogFilePtr = open("LogFile.txt",'a')
                                 LogFilePtr.write(Text)
                                 LogFilePtr.close()

                              #os.chmod(LogFileLocation,0777)
                              time.sleep(0.5)  # Wait for 5 Seconds before starting for copy of results file

                              pass0_fail2, log_file_loc, dur, pmem, dmem = CopyLogFile1(ResultsDirectory, str(project_count) + str(i) + str(j) + str(k))

                              log_file_loc = "Archives/MplabX/" + ResultsFinalDirectory + "/" + str(project_count) + str(i) + str(j) + str(k) + ".txt"

                              if rerun != 0:

                                 if pass0_fail2 == 2 or dur == "NA":
                                    rerun = 1
                                    if rerun_count > 0:
                                       rerun_count = rerun_count - 1
                                    else:
                                       rerun = 0
                                 else:
                                    rerun = 0
                        else:
                           LogFileLocation = os.path.join(os.getcwd(),"LogFile.txt")
                           #if not os.path.exists(LogFileLocation):
                           Text = "\n\n_ARBS_Build_Started_\n"
                           Text = Text + "Executing for Makefile: Unknown\n"
                           Text = Text + "Error: MPLAB X IDE is not able to generate make file for the project configuration " + all_conf[i] + "\n\n"
                           Text = Text + "Make File Execution End"
                           Text = Text + "\n_ARBS_Build_Ends_Here_"
                           LogFilePtr = open("LogFile.txt",'w')
                           LogFilePtr.write(Text)
                           LogFilePtr.close()                        

                           time.sleep(0.5)  # Wait for 5 Seconds before starting for copy of results file

                           pass0_fail2, log_file_loc, dur, pmem, dmem = CopyLogFile1(ResultsDirectory, str(project_count) + str(i) + str(j) + str(k))

                           log_file_loc = "Archives/MplabX/" + ResultsFinalDirectory + "/" + str(project_count) + str(i) + str(j) + str(k) + ".txt"
                           pass0_fail2 = 2
                           dur = "NA"
                           pmem = "NA"
                           dmem = "NA"                           
                     else:
                     
                        LogFileLocation = os.path.join(os.getcwd(),"LogFile.txt")
                        #if not os.path.exists(LogFileLocation):
                        Text = "\n\n_ARBS_Build_Started_\n"
                        Text = Text + "Executing for Makefile: Unknown\n"
                        
                        if project_config_file_size_error != 0:
                           Text = Text + "Executing for Makefile: Unknown\n"
                           Text = Text + "Error: Project Configuration file size is exceeding 10MB, which is unexpected\n\n"

                        elif project_xml_file_error != 0:
                           Text = Text + "Executing for Makefile: " + all_conf[i] + "\n"
                           Text = Text + "Error: Unable to process the project configurations. Possibly project XML file is corrupt\n\n"

                           
                        Text = Text + "Make File Execution End"
                        Text = Text + "\n_ARBS_Build_Ends_Here_"
                        LogFilePtr = open("LogFile.txt",'w')
                        LogFilePtr.write(Text)
                        LogFilePtr.close()                        

                        time.sleep(0.5)  # Wait for 5 Seconds before starting for copy of results file

                        pass0_fail2, log_file_loc, dur, pmem, dmem = CopyLogFile1(ResultsDirectory, str(project_count) + str(i) + str(j) + str(k))

                        log_file_loc = "Archives/MplabX/" + ResultsFinalDirectory + "/" + str(project_count) + str(i) + str(j) + str(k) + ".txt"
                        pass0_fail2 = 2
                        dur = "NA"
                        pmem = "NA"
                        dmem = "NA"
                     
                     '''
                     pass0_fail2 = pass0_fail2 + 1
                     if pass0_fail2 >= 3:
                        pass0_fail2 = 1
                     log_file_loc = "sdfkvjsdfkvnjsdfv"
                     pmem = "23458809 Bytes"
                     dmem = "3958 Bytes"
                     dur = "24 Sec"
                     '''
                     
                     
                     
                     ExecutingMakeFile.append("temp")
                     PassFailStatus.append(pass0_fail2)
                     #Compiler_Log_file_location.append(log_file_loc)
                     #build_dur.append(dur)
                     
                     col_results_1d.append(pass0_fail2)
                     col_result_file_location.append(log_file_loc)
                     col_pmem.append(pmem)
                     col_dmem.append(dmem)
                     col_build_dur.append(dur)   
                     
                     
                     
                     #
                     #
                     # End of copy
                     #
                     #

                     
                  
                  row_results_1d.append(col_results_1d)
                  row_result_file_location.append(col_result_file_location)
                  row_pmem.append(col_pmem)
                  row_dmem.append(col_dmem)
                  row_build_dur.append(col_build_dur)
               
               
               all_conf_results_1d.append(row_results_1d)
               all_conf_result_file_location.append(row_result_file_location)
               all_conf_pmem.append(row_pmem)
               all_conf_dmem.append(row_dmem)
               all_conf_build_dur.append(row_build_dur)
            
            time.sleep(1)
            multiple_compiler_options.revert_configuration(ProjectLocation)
            m_project_location.append(ProjectLocation)
            m_result.append(all_conf_results_1d)
            m_configuration.append(m_configuration_1d) 
            m_result_file_location.append(all_conf_result_file_location)
            m_pmem.append(all_conf_pmem)
            m_dmem.append(all_conf_dmem)
            m_build_dur.append(all_conf_build_dur)
            
            m_row_options.append(all_conf_row_options)
            m_col_options.append(all_conf_col_options)
            m_tgt_compiler.append(all_conf_compiler)
            m_run_conf_default_option.append(all_run_default_options)
            


      if os.path.exists("com"):
         shutil.rmtree("com",1)      
         
         
      ProjectLocation = Project_Location
      #ProjectLocation, ProjLocationChange, ExecutingMakeFile, PassFailStatus, CompilerMessage = DeterminePassFailStatus()

      ###########################################################
      # Finding Statistics
      ###########################################################
      TotalProjCount = 0
      TotalProjPassCount = 0
      TotalProjWarnCount = 0
      TotalProjFailCount = 0


      CentTotalProjPassCount = 0
      CentTotalProjWarnCount = 0
      CentTotalProjFailCount = 0

      for i in range(len(ExecutingMakeFile)):
         TotalProjCount = TotalProjCount + 1
         if PassFailStatus[i] == 0:
            TotalProjPassCount = TotalProjPassCount + 1
         elif PassFailStatus[i] == 1:
            TotalProjWarnCount = TotalProjWarnCount + 1
         else:
            TotalProjFailCount = TotalProjFailCount + 1
      
      if len(ExecutingMakeFile) > 0:
         CentTotalProjPassCount = round((TotalProjPassCount/TotalProjCount),4) * 100
         CentTotalProjWarnCount = round((TotalProjWarnCount/TotalProjCount),4) * 100
         CentTotalProjFailCount = round((TotalProjFailCount/TotalProjCount),4) * 100
   



   ###########################################################
   # Creating Results File
   ###########################################################
   



   StatisticsFileString = StatisticsFileString + "\nPROJECT_NAME:" + ProjectName + "\n"
   StatisticsFileString = StatisticsFileString + "\nCOMPILER_NAME:" + CompilerToBeUsed + "\n"
   StatisticsFileString = StatisticsFileString + "\nBUILD_OS:" + sys.platform + "\n"
   
   Temp = "0_" + ResultsFinalDirectory + "_MplabX_ResultSummary.html"

   StatisticsFileString = StatisticsFileString + "\nRESULT_FILE_NAME:" + Temp + "\n"
   
   ResultSummaryFile = os.path.join(os.getcwd(), Temp)
   
   ResultsFilePtr = open(ResultSummaryFile,"w")
   
   if ProjectLocations == []:
      ResultsFilePtr.write("No MPLAB X Project Directory found")
      ResultsFilePtr.close()
      exit()
      
      
   ResultsFilePtr.write("<html>\n<head>\n<title>MplabX_ResultSummary</title>\n</head>\n<body>\n<font face=Courier >\n")
   
   ResultMessage = ''
   
   svn_rev, svn_link = get_svn_revision()   
   
   ResultMessage = "<b>ARBS_Build_Mechanism_For_MPLAB_X_Projects Rev Beta_0V1</b>\n"
   
   if job_name != '':
      ResultMessage = ResultMessage + "<b>Job Name: </b>" + job_name + "\n"
      
   ResultMessage = ResultMessage + "<b>Directory: </b>" + DirectoryForScan + "\n"
   _date, _time = get_date_time()
   ResultMessage = ResultMessage + "<b>Time: </b>" + _date + " " + _time + "\n\n" + InsertLine()
   
   ResultMessage = ResultMessage + "\n<!--TOOLS_LOCATION_START-->\n<b>Tools Version:</b>\n-------------------\n" + GetCompilerVersions(CompilerToBeUsed) + "\n" + InsertLine()  + "\n<!--TOOLS_LOCATION_END-->\n"
   
   if test_type == '':
      if not CheckoutRevision == '':
         ResultMessage = ResultMessage + "<b>SVN Link: </b>" + "<a href=%s>%s</a>"%(re.sub(" ","%20",COSVNLink),COSVNLink) + "\n<b>Checkout Revision: </b>" + CheckoutRevision + "\n\n" + InsertLine() + "\n\n"
      elif svn_link != '':
         ResultMessage = ResultMessage + "<b>SVN Link: </b>" + "<a href=%s>%s</a>"%(re.sub(" ","%20",svn_link),svn_link) + "\n<b>Checkout Revision: </b>" + svn_rev + "\n\n" + InsertLine() + "\n\n"
   else:
      ResultMessage = ResultMessage + "<b>Test Type: </b>" + test_type + "\n\n"
      ResultMessage = ResultMessage + "<!--\nSTAT_TEST_TYPE:" + test_type + ":\n-->\n"
      if test_link != '':
         ResultMessage = ResultMessage + "<b>Test Link: </b>" + "<a href=%s>%s</a>"%(re.sub(" ","%20",test_link),test_link) + "\n\n" + InsertLine() + "\n"
         ResultMessage = ResultMessage + "<!--\nSTAT_TEST_LINK:" + re.sub(" ","%20",test_link) + ":\n-->\n"

   ########################################
   # Detect the max no of spaces to be inserted, before displaying the %
   MaxLenSp = 0
   MaxLenSp = len(str(TotalProjCount))
   
   if len(str(TotalProjPassCount)) > MaxLenSp:
      MaxLenSp = len(str(TotalProjPassCount))
   if len(str(TotalProjWarnCount)) > MaxLenSp:
      MaxLenSp = len(str(TotalProjWarnCount))
   if len(str(TotalProjFailCount)) > MaxLenSp:
      MaxLenSp = len(str(TotalProjFailCount))
   
   #########################################
   
   
   
   ###### Creating Test Summary #########
   
   ResultMessage = ResultMessage + "<b>Test Summary:</b>\n---------------\n"
   ResultMessage = ResultMessage + "Total Number of Projects Executed: " + str(TotalProjCount) + "\n"
   ResultMessage = ResultMessage + "Passed                           : " + str(TotalProjPassCount) + SpaceTobeInserted(MaxLenSp,TotalProjPassCount) + '(' + str(CentTotalProjPassCount) + '%)' + "\n"
   ResultMessage = ResultMessage + "Passed with Warnings             : " + str(TotalProjWarnCount) + SpaceTobeInserted(MaxLenSp,TotalProjWarnCount) + '(' + str(CentTotalProjWarnCount) + '%)' + "\n"
   ResultMessage = ResultMessage + "Failed                           : " + str(TotalProjFailCount) + SpaceTobeInserted(MaxLenSp,TotalProjFailCount) + '(' + str(CentTotalProjFailCount) + '%)' + "\n"
   
   ResultMessage = ResultMessage + "<!--\nSTAT_TOTAL_PROJECTS:" + str(TotalProjCount) + ":\n"
   ResultMessage = ResultMessage + "STAT_TOTAL_P:" + str(TotalProjPassCount) + ":\n"
   ResultMessage = ResultMessage + "STAT_TOTAL_W:" + str(TotalProjWarnCount) + ":\n"
   ResultMessage = ResultMessage + "STAT_TOTAL_F:" + str(TotalProjFailCount) + ":\n"
   
   ResultMessage = ResultMessage + "STAT_HW_TOOL:NA:\n"
   ResultMessage = ResultMessage + "STAT_OS:" + sys.platform + ":\n-->"
   
   
   StatisticsFileString = StatisticsFileString + "\nTOTAL_NUMBER_OF_PROJECTS:" + str(TotalProjCount) + "\n"
   StatisticsFileString = StatisticsFileString + "\nTOTAL_PASS_COUNT:" + str(TotalProjPassCount) + "\n" + "\nTOTAL_PASS_CENT:" + str(CentTotalProjPassCount) + "\n"
   StatisticsFileString = StatisticsFileString + "\nTOTAL_PASS_WARN_COUNT:" + str(TotalProjWarnCount) + "\n" + "\nTOTAL_PASS_WARN_CENT:" + str(CentTotalProjWarnCount) + "\n"
   StatisticsFileString = StatisticsFileString + "\nTOTAL_FAIL_COUNT:" + str(TotalProjFailCount) + "\n" + "\nTOTAL_FAIL_CENT:" + str(CentTotalProjFailCount) + "\n"
   
   
   
   if not CheckoutRevision == '':
      StatisticsFileString = StatisticsFileString + "\nSVN_REPO_LINK:" + str(COSVNLink) + "\n" + "\nCHECKED_OUT_REVISION:" + str(CheckoutRevision) + "\n"
   else:
      StatisticsFileString = StatisticsFileString + "\nSVN_REPO_LINK:" + str(svn_link) + "\n" + "\nCHECKED_OUT_REVISION:" + str(svn_rev) + "\n"
   
   if test_type != '':
      StatisticsFileString = StatisticsFileString + "TEST_TYPE:" + test_type + "\n"
      if test_link != '':
         StatisticsFileString = StatisticsFileString + "TEST_LINK:" + re.sub(" ","%20",test_link) + "\n"
      elif COSVNLink != '':
         StatisticsFileString = StatisticsFileString + "TEST_LINK:" + re.sub(" ","%20",COSVNLink) + "\n"
   
   StatisticsFileString = StatisticsFileString + "\n" + GetCompilerVersions(CompilerToBeUsed)

   ResultMessage = ResultMessage + "\n" + InsertLine() + "\n\n"
   
   ResultMessage = ResultMessage + "\n\n<b>Individual Project Execution Result:</b>\n-----------------------------------------\n"
   
   ResultMessage = re.sub("\n","<br>\n",ResultMessage)
   ResultMessage = re.sub("  ","&nbsp;&nbsp;",ResultMessage)
   
   all_pass_message = ""
   all_warn_message = ""
   all_fail_message = ""

  
   

   ResultMessage = ResultMessage + "<a href=\"Results_ALL_PASS.html\">"
   ResultMessage = ResultMessage + "Click here for Pass only messages" 
   ResultMessage = ResultMessage + "<br></a>\n"

   ResultMessage = ResultMessage + "<a href=\"Results_ALL_PASS_WARN.html\">"
   ResultMessage = ResultMessage + "Click here for Pass, with warnings only messages" 
   ResultMessage = ResultMessage + "<br></a>\n"

   ResultMessage = ResultMessage + "<a href=\"Results_ALL_FAIL.html\">"
   ResultMessage = ResultMessage + "Click here for Fail only messages" 
   ResultMessage = ResultMessage + "<br></a>\n" 

   #ResultMessage = ResultMessage + "<a href=\"Archives/MplabX/" + ResultsFinalDirectory + "/" + "Results_ALL_PASS.txt\">"
   #ResultMessage = ResultMessage + "Click here for Pass only messages" 
   #ResultMessage = ResultMessage + "<br></a>\n"

   #ResultMessage = ResultMessage + "<a href=\"Archives/MplabX/" + ResultsFinalDirectory + "/" + "Results_ALL_FAIL.txt\">"
   #ResultMessage = ResultMessage + "Click here for Fail only messages" 
   #ResultMessage = ResultMessage + "<br></a>\n"   
   build_number = os.getenv('BUILD_NUMBER', "LOCAL_RUN")

   ResultMessage = ResultMessage + "<!--ARBS_AXIS_CONFIG:" + job_name + "-->\n"
   build_number = os.getenv('BUILD_NUMBER', "LOCAL_RUN")   
   ResultMessage = ResultMessage + "<!--ARBS_BUILD_NUMBER:" + str(build_number) + "\n-->\n"
   ResultMessage = ResultMessage + "<!--ARBS_RESULT_START_TAG-->\n"
   
   
   
   if multiple_options_build == 0:   
   
      MaxLength = GetMaxLength(ExecutingMakeFile)
      
      
      pcount = 0
      wcount = 0
      fcount = 0
      
      proj = ""
      __report_gen_configuration = []
      __report_generation_result = []
      for i in range(len(ExecutingMakeFile)):
         local_result_msg = ""
         
         
         if ProjLocationChange[i] == 1:
            local_result_msg = local_result_msg + "\n<br><b>" + ProjectLocation[i] + "</b>\n<br>"
            proj = local_result_msg
            pcount = 0
            wcount = 0
            fcount = 0      
            
            if i != 0:
               report_gen_configuration.append(__report_gen_configuration)
               report_generation_result.append(__report_generation_result)
               
            report_gen_project_location.append(ProjectLocation[i])
            __report_gen_configuration = []
            __report_generation_result = []
            

            
         __report_gen_configuration.append(ExecutingMakeFile[i])
         __report_generation_result.append(PassFailStatus[i])

         if i == (len(ExecutingMakeFile) - 1):
            report_gen_configuration.append(__report_gen_configuration)
            report_generation_result.append(__report_generation_result)
            
            
         local_result_msg = str(i+1) + ". " + ExecutingMakeFile[i]

         local_result_msg = local_result_msg + InsertSpaces(MaxLength, ExecutingMakeFile[i],i+1)

         local_result_msg = local_result_msg + "<a href=\"Archives/MplabX/" + ResultsFinalDirectory + "/" + str(i+1) + ".txt\">"
         
         hex_file_change_string = ''
         
         if commit_artifacts_files != '' and COSVNLink != '' and commit_artifact_dir != '':
            hex_file_change_string =  ", <b>HEX File Change Status:</b>"
            if HexFileChangeStatus[i] == 0:
               hex_file_change_string = hex_file_change_string + " No Hex File found for comparison"
            if HexFileChangeStatus[i] == 1:
               hex_file_change_string = hex_file_change_string + "Hex File is not changed"
            if HexFileChangeStatus[i] == 2:
               hex_file_change_string = hex_file_change_string + "<font color=RED><b>Changes detected in Hex File</b></font>"               
               
               
         if PassFailStatus[i] == 0:
            local_result_msg = local_result_msg + "[ PASS ]"
         elif PassFailStatus[i] == 1:
            local_result_msg = local_result_msg + "[ PASS with Warnings ]"
         else:
            local_result_msg = local_result_msg + "<b><font color=RED>[*FAIL*]</font></b>"

         local_result_msg = local_result_msg + "</a>, Build Duration: " + build_dur[i] + hex_file_change_string + "<br>\n"


         # Placed here to obtain the entire local_result_msg variable
         if PassFailStatus[i] == 0:
            if pcount == 0:
               all_pass_message = all_pass_message + proj
            all_pass_message = all_pass_message + local_result_msg
            pcount = pcount + 1
         elif PassFailStatus[i] == 1:
            if wcount == 0:
               all_warn_message = all_warn_message + proj
            all_warn_message = all_warn_message + local_result_msg
            wcount = wcount + 1
         else:
            if fcount == 0:
               all_fail_message = all_fail_message + proj
            all_fail_message = all_fail_message + local_result_msg
            fcount = fcount + 1
            
         if ProjLocationChange[i] == 1:   
            ResultMessage = ResultMessage + proj + local_result_msg
         else:
            ResultMessage = ResultMessage + local_result_msg
      
      
      ResultMessage = ResultMessage + "\n<!--ARBS_RESULT_END_TAG-->\n"
      ResultMessage = ResultMessage + "\n<br>\n<br>\n" + ("+" * 100) 
      ResultMessage = ResultMessage + "\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n"
      #ResultMessage = ResultMessage + "<b>Compiler Messages :</b><br><br>"
   
   else:
   
      ###########################################################
      # Getting Number of columns and column names
      col_length = 0
      col_heading = []
      col_compiler_done = []
      
      project_row_span = []
      project_each_configuration_row_span = []
      
      for i in range(len(m_project_location)):
         #print m_project_location[i]
         
         config_row_span = []
         temp_row_span = 0
         for j in range(len(m_configuration[i])):
            #print m_configuration[i][j]
            #print m_tgt_compiler[i][j]
            
            col_found = 0
            for comp in col_compiler_done:
               if comp == m_tgt_compiler[i][j]:
                  col_found = 1
            if col_found == 0:
               col_compiler_done.append(m_tgt_compiler[i][j])
            
            config_row_span.append(len(m_row_options[i][j]))
            temp_row_span = temp_row_span + len(m_row_options[i][j])
            
            
            for k in range(len(m_row_options[i][j])):
               #print "ROW:" + m_row_options[i][j][k]
               if len(m_col_options[i][j]) > col_length:
                  col_length = len(m_col_options[i][j])
               temp_col_heading = []
               for l in range(len(m_col_options[i][j])):
                  #print "COL:" + m_col_options[i][j][l]
                  #print m_result[i][j][k][l]
                  temp_col_heading.append("<i>[" + m_tgt_compiler[i][j] + "]</i>" + m_col_options[i][j][l])
                  
               if col_found == 0 and m_run_conf_default_option[i][j] == 0:
                  #col_length = col_length + 1
                  if len(col_heading) < len(temp_col_heading):
                     for _i in range(len(col_heading)):
                        col_heading[_i] = col_heading[_i] + " <i>or</i> <br>" + temp_col_heading[_i]
                     
                     temp = len(col_heading)
                     for _i in range(len(temp_col_heading) - temp):
                        col_heading.append(temp_col_heading[temp + _i])
                  else:
                     for _i in range(len(temp_col_heading)):
                        col_heading[_i] = col_heading[_i] + " <i>or</i> <br>" + temp_col_heading[_i]                        

                        
               col_found = 1     

         project_row_span.append(temp_row_span)
         project_each_configuration_row_span.append(config_row_span)
         
      ####################################################
      ####################################################
      
      #html_string = "<html>\n<head>\n<title>Make File Test summary</title>\n</head>\n<body>\n<font face=Courier >\n"
      html_string = ''
      html_string = html_string + "<TABLE BORDER=\"5\"    WIDTH=\"100%\"   CELLPADDING=\"4\" CELLSPACING=\"3\"><TR ALIGN=\"LEFT\">\n"
      html_string = html_string + "<TD width=\"5%\" rowspan=\"2\"><p align=\"center\"><b>Project Location</b></TD>\n"         
      html_string = html_string + "<TD width=\"5%\" rowspan=\"2\"><p align=\"center\"><b>Project Configuration</b></TD>\n"
      #col_length = (len(col_length) * 3) + 1
      _col_length = str(col_length + 1)

      html_string = html_string + "<TD colspan=\"" + _col_length + "\"><p align=\"center\"><b>Test Result</b><br>Code Size(CS)<br>Data Size(DS)<br>Build Duration(BD)</TD>\n"                  
      html_string = html_string + "</TR>\n"

      ######################################################
      # Populating next row - heading
      ######################################################
      html_string = html_string + "<TR>\n"
      html_string = html_string + "<TD width=\"5%\" rowspan=\"1\"><p align=\"center\"><b>Options</b></TD>\n"
      for i in range(len(col_heading)):
         html_string = html_string + "<TD><p align=\"center\">" + col_heading[i] + "</TD>\n"
      html_string = html_string + "</TR>\n"

      ######################################################
      # Populating next row - heading
      ######################################################
      #html_string = html_string + "<TR>\n"
      #for i in range(len(col_heading)):
      #    html_string = html_string + "<TD><p align=\"center\"><b>Test Result</b><br>Code Size(CS)<br>Data Size(DS)<br>Build Duration(BD)</TD>\n"
      #    #html_string = html_string + "<TD><p align=\"center\"><b>Program Memory</b></TD>\n"
      #    #html_string = html_string + "<TD><p align=\"center\"><b>Data Memory</b></TD>\n"
      #html_string = html_string + "</TR>\n"
      
      
      pcount = 0
      wcount = 0
      fcount = 0
      
      _ExecutingMakeFile = []
      
      for i in range(len(m_project_location)):
         for j in range(len(m_configuration[i])):
            for k in range(len(m_row_options[i][j])):
               for l in range(len(m_col_options[i][j])):
                  #print m_row_options[i][j][k]
                  _ExecutingMakeFile.append(m_configuration[i][j] + " [" + "<i>COL:</i>" + m_col_options[i][j][l] + " / <i>ROW:</i>" + m_row_options[i][j][k] + "]")
                  
                  
      MaxLength = GetMaxLength(_ExecutingMakeFile)         
      
      opt_count = 0
      
      for i in range(len(m_project_location)):
         pcount = 0
         wcount = 0
         fcount = 0
         
         report_gen_project_location.append(m_project_location[i])
         __report_gen_configuration = []
         __report_generation_result = []
         
         report_gen_config_result = 0
         
         for j in range(len(m_configuration[i])):
            for k in range(len(m_row_options[i][j])):
               for l in range(len(m_col_options[i][j])):
                  if m_result[i][j][k][l] == 0:
                  
                     temp = ""
                     temp = temp + "\n<br>" + _ExecutingMakeFile[opt_count] + InsertSpaces(MaxLength, _ExecutingMakeFile[opt_count],0)
                     temp = temp + "<a href=\"" + m_result_file_location[i][j][k][l] + "\"><font color=\"#398C29\"><b>[ PASS ]</b></font></a>\n"
                        
                     if pcount == 0:
                        temp = "\n<br><br><b>" + str(i+1) + ". " + m_project_location[i] + "</b>" + temp

                     all_pass_message = all_pass_message + temp
                     pcount = pcount + 1
                     
                  elif m_result[i][j][k][l] == 1:

                     temp = ""
                     temp = temp + "\n<br>" + _ExecutingMakeFile[opt_count] + InsertSpaces(MaxLength, _ExecutingMakeFile[opt_count],0)
                     temp = temp + "<a href=\"" + m_result_file_location[i][j][k][l] + "\"><font color=\"#398C29\"><b>[ PASS</b>, with warnings ]</font></a>\n"
                        
                     if wcount == 0:
                        temp = "\n<br><br><b>" + str(i+1) + ". " + m_project_location[i] + "</b>" + temp

                     all_warn_message = all_warn_message + temp
                     wcount = wcount + 1
                     
                     if report_gen_config_result != 2:
                        report_gen_config_result = 1
                        
                  else:
                  
                     temp = ""
                     temp = temp + "\n<br>" + _ExecutingMakeFile[opt_count] + InsertSpaces(MaxLength, _ExecutingMakeFile[opt_count],0)
                     temp = temp + "<a href=\"" + m_result_file_location[i][j][k][l] + "\"><font color=\"#FF0000\"><b>[*FAIL*]</b></font></a>\n"
                        
                     if fcount == 0:
                        temp = "\n<br><br><b>" + str(i+1) + ". " + m_project_location[i] + "</b>" + temp

                     all_fail_message = all_fail_message + temp
                     fcount = fcount + 1
                     report_gen_config_result = 2
                  opt_count = opt_count + 1
                  
            __report_gen_configuration.append(m_configuration[i][j])
            __report_generation_result.append(report_gen_config_result)  
            
         report_gen_configuration.append(__report_gen_configuration)
         report_generation_result.append(__report_generation_result)
         
         
      for i in range(len(m_project_location)):

         ###################################################
         # Populate Project Name
         ###################################################
         if len(m_configuration[i]) == 0:
            continue

         html_string = html_string + "<TR>\n"
         #rowspan = len(row_options) * len(m_configuration[i])
         rowspan = str(project_row_span[i])
         html_string = html_string + "<TD valign=\"top\" rowspan=\"" + rowspan + "\">" + fold_html_cell_string((str(i+1) + ". " + m_project_location[i]),8) + "</TD>\n"
         #html_string = html_string + "<TD rowspan=\"" + rowspan + "\">" + str(i+1) + ". " + m_project_location[i] + "</TD>\n"

         ###################################################
         # Populate Configuration Name
         ###################################################

            
         for j in range(len(m_configuration[i])):

            if j != 0:
               html_string = html_string + "<TR>\n"               

            #rowspan = len(row_options)
            rowspan = str(project_each_configuration_row_span[i][j])
            html_string = html_string + "<TD rowspan=\"" + rowspan + "\">[" + m_tgt_compiler[i][j] + "]<br>" + fold_html_cell_string(m_configuration[i][j],10) + "</TD>\n"

            for k in range(len(m_row_options[i][j])):

               if k != 0:
                  html_string = html_string + "<TR>\n"    

               html_string = html_string + "<TD><i>" + m_row_options[i][j][k] + "</i></TD>\n"

               for l in range(len(m_col_options[i][j])):

                  pmem = m_pmem[i][j][k][l]
                  dmem = m_dmem[i][j][k][l]

                  if m_pmem[i][j][k][l] == '':
                     pmem = "NA"
                     if m_result[i][j][k][l] <= 1:
                        pmem = pmem + "<br>(Library Build)"
                  if m_dmem[i][j][k][l] == '':
                     dmem = "NA"
                     if m_result[i][j][k][l] <= 1:
                        dmem = dmem + "<br>(Library Build)"                     

                  if m_result[i][j][k][l] == 2:
                     pmem = "NA"
                     dmem = "NA"
                     
                  temp_col_span_string = ''
                  if m_run_conf_default_option[i][j] == 0:
                     temp_col_span_string = ""
                  else:
                     temp_col_span_string = " align=\"center\" colspan=\"" + str(col_length) + "\"" 
                  
                  if m_result[i][j][k][l] == 0:
                     html_string = html_string + "<TD" + temp_col_span_string + "><a href=\"" + m_result_file_location[i][j][k][l] + "\"><font color=\"#398C29\"><b>PASS</b></font></a><br>CS: " + pmem + "<br>DS: " + dmem + "<br>BD: " + m_build_dur[i][j][k][l] + "</TD>"
                  elif m_result[i][j][k][l] == 1:
                     html_string = html_string + "<TD" + temp_col_span_string + "><a href=\"" + m_result_file_location[i][j][k][l] + "\"><font color=\"#398C29\"><b>PASS</b>, with warnings</font></a><br>CS: " + pmem + "<br>DS: " + dmem + "<br>BD: " + m_build_dur[i][j][k][l] + "</TD>"
                  else:
                     html_string = html_string + "<TD" + temp_col_span_string + "><a href=\"" + m_result_file_location[i][j][k][l] + "\"><font color=\"#FF0000\"><b>[*FAIL*]</b></font></a><br>CS: " + pmem + "<br>DS: " + dmem + "<br>BD: " + m_build_dur[i][j][k][l] + "</TD>"

               if col_length > len(m_col_options[i][j]) and m_run_conf_default_option[i][j] == 0:
                  rem_unfilled_cols = col_length - len(m_col_options[i][j])
                  
                  html_string = html_string + "<TD align=\"center\" colspan=\"" + str(rem_unfilled_cols) + "\">-NA-</TD>"
                  #for l in range(col_length - len(m_col_options[i][j])):
                     


                  #html_string = html_string + "<TD>" + pmem + "</TD>\n"
                  #html_string = html_string + "<TD>" + dmem + "</TD>\n"

               html_string = html_string + "</TR>\n"
            html_string = html_string + "</TR>\n"
         html_string = html_string + "</TR>\n"
      ResultMessage = ResultMessage + "<br><br>" + html_string + "</TABLE>\n" 
      ResultMessage = ResultMessage + "\n<!--ARBS_RESULT_END_TAG-->\n"
      
      
      
   #ResultMessage = ResultMessage + "<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n<br>\n"
   ResultMessage = ResultMessage + "</font>\n</body>\n</html>\n"
   
   ResultsFilePtr.write(ResultMessage)
   ResultsFilePtr.close()
   
   #print multiple_options_build
   #if multiple_options_build >= 1: 

   #############################################################
   # Writing Pass ans Fail Messages
   #############################################################

   pass_file_name = os.path.join(os.getcwd(),"Results_ALL_PASS.html")
   warn_file_name = os.path.join(os.getcwd(),"Results_ALL_PASS_WARN.html")
   fail_file_name = os.path.join(os.getcwd(),"Results_ALL_FAIL.html")


   if all_pass_message == '':
      all_pass_message = "<html>\n<head>\n<title>MplabX_ResultSummary</title>\n</head>\n<body>\n<font face=Courier >\n<b>No Passed Projects/Configurations Found</b></font>\n</body>\n</html>\n"
   else:
      all_pass_message = "<html>\n<head>\n<title>MplabX_ResultSummary</title>\n</head>\n<body>\n<font face=Courier >\n<b>Consolidated Report for All the configurations Passed</b><br><br>" + all_pass_message + "</font>\n</body>\n</html>\n"

   if all_warn_message == '':
      all_warn_message = "<html>\n<head>\n<title>MplabX_ResultSummary</title>\n</head>\n<body>\n<font face=Courier >\n<b>No Projects/Configurations Found with Pass with Warnings</b></font>\n</body>\n</html>\n"
   else:
      all_warn_message = "<html>\n<head>\n<title>MplabX_ResultSummary</title>\n</head>\n<body>\n<font face=Courier >\n<b>Consolidated Report for All the configurations with Passed with Warnings</b><br><br>" + all_warn_message + "</font>\n</body>\n</html>\n"

   if all_fail_message == '':
      all_fail_message = "<html>\n<head>\n<title>MplabX_ResultSummary</title>\n</head>\n<body>\n<font face=Courier >\n<b>No Failed Projects/Configurations Found</b></font>\n</body>\n</html>\n"   
   else:
      all_fail_message = "<html>\n<head>\n<title>MplabX_ResultSummary</title>\n</head>\n<body>\n<font face=Courier >\n<b>Consolidated Report for All the configurations Failed</b><br><br>" + all_fail_message + "</font>\n</body>\n</html>\n"



   pass_file_ptr = open(pass_file_name,"w")
   warn_file_ptr = open(warn_file_name,"w")
   fail_file_ptr = open(fail_file_name,"w")

   pass_file_ptr.write(all_pass_message)
   warn_file_ptr.write(all_warn_message)
   fail_file_ptr.write(all_fail_message)

   pass_file_ptr.close()
   warn_file_ptr.close()
   fail_file_ptr.close()

   '''
   failures_available = 0
   pass_available = 0

   pass_file_ptr.write("Consolidated message for All Passed Projects\n\n")
   fail_file_ptr.write("Consolidated message for All Failed Projects\n\n")

   for i in range(len(ExecutingMakeFile)):

      if PassFailStatus[i] == 0:
         pass_available = 1
         ResultMessage = "PASS"
         pass_file_ptr.write(str(i+1) + ". " + ExecutingMakeFile[i] + " - " + ResultMessage + "\n")
      elif PassFailStatus[i] == 1:
         ResultMessage = "PASS with Warnings" 
         pass_available = 1
         pass_file_ptr.write(str(i+1) + ". " + ExecutingMakeFile[i] + " - " + ResultMessage + "\n")
      else:
         ResultMessage = "FAIL" 
         failures_available = 1
         fail_file_ptr.write(str(i+1) + ". " + ExecutingMakeFile[i] + " - " + ResultMessage + "\n")

   for i in range(len(ExecutingMakeFile)):

      if PassFailStatus[i] == 0:
         ResultMessage = "PASS"
         pass_file_ptr.write(get_str(Compiler_Log_file_location[i],i,ExecutingMakeFile[i],ResultMessage))
      elif PassFailStatus[i] == 1:
         ResultMessage = "PASS with Warnings" 
         pass_file_ptr.write(get_str(Compiler_Log_file_location[i],i,ExecutingMakeFile[i],ResultMessage))
      else:
         ResultMessage = "FAIL" 
         fail_file_ptr.write(get_str(Compiler_Log_file_location[i],i,ExecutingMakeFile[i],ResultMessage))


   if failures_available == 0:
      fail_file_ptr.write("No Failed Projects Found")
   if pass_available == 0:
      pass_file_ptr.write("No Passed Projects Found")

   fail_file_ptr.close()
   pass_file_ptr.close()
   '''
   if os.path.exists(os.path.join(os.getcwd(),"CompilerMessages.temp")):
      os.remove("CompilerMessages.temp")         
   
   
      
   StatisticsFilePtr = open(StatisticsFileName,"w")
   StatisticsFilePtr.write(StatisticsFileString)
   StatisticsFilePtr.close()      
   
   project_path_common_string = GetCommonString(report_gen_project_location,0)
   project_path_common_string = os.path.normpath(project_path_common_string)
   project_path_common_string = re.sub(r"\\","/",project_path_common_string)

   if mysql_log_result == 1:
      
      text_string = "OS:" + sys.platform + "\n"
      text_string = text_string + "START_JobName:" + job_name + "\n"
      for i in range(len(report_gen_project_location)):
         
         
         ProjectLocation = re.sub(r"\\","/",report_gen_project_location[i]) 
         #ProjectLocation = re.sub(project_path_common_string,"",ProjectLocation)
         if re.search("/apps/", ProjectLocation):
         
            ProjectLocation = re.split("/apps/", ProjectLocation)[1]
            ProjectLocation = "apps/" + ProjectLocation
            text_string = text_string + "START_Project\n"
            text_string = text_string + "Project_Location;\"" + ProjectLocation + "\"\n" 

            for j in range(len(report_gen_configuration[i])):
               result_string = "FAIL"

               if report_generation_result[i][j] == 0:
                  result_string = "PASS"
               if report_generation_result[i][j] == 1:
                  result_string = "PASS With Warnings"

               text_string = text_string + "Project_configuration=\"" + report_gen_configuration[i][j] + "\";Result=\"" + result_string + "\"\n"   

            text_string = text_string + "END_Project\n"
      
      text_string = text_string + "END_JobName\n"
      
      results_file = "db_results_file.txt"
      
      fptr = open(results_file, "w")
      fptr.write(text_string)
      fptr.close()
      
      # Below is commented, as it is moved to server
      
      '''
      command_array = ["java", "-jar", "hdcr.jar", results_file]
      
      try:
      
         error_code = subprocess.call(command_array)
         if error_code != 0:
            print "Unable to upload the results to Database"
            
      except:
      
         print command_array
         print "Unable to upload the results to Database"  
         
      '''
      
 
      
      