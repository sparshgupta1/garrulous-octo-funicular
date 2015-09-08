import re
import sys
import os
from xml.dom.minidom import parse
import time
import subprocess
import shutil
import glob
import ldra_rule_set


def get_source_files_from_directory(project_location, include_dir, exclude_dir):

   DirNames = []
   FileNames = []
   
   CFiles = []
   HFiles = []
   
   all_exclude_directories = []
   
   exclude_dir_ary = re.split(",", exclude_dir)
   for i in range(len(exclude_dir_ary)):
      temp = os.path.normpath(exclude_dir_ary[i])
      temp = re.sub(r"\\", "/", temp)
      all_exclude_directories.append(temp)
   
   
   
   
   include_dir_ary = re.split(",", include_dir)
   
   for i in range(len(include_dir_ary) + 1):
   
      FilePath = project_location
      
      if i == 0:
         FilePath = project_location
      else:
         FilePath = include_dir_ary[i-1]
      
      if not os.path.exists(FilePath):
         continue
      
      if os.path.isdir(FilePath):                                 # if the given path is a directory, 
         os.chmod(FilePath,0777)                                  # First change it to a directory write permissions.
         for root, dirs, files in os.walk(FilePath):              # Now, List the directories and files available in the 
            if not re.search("\.[x|X]|\.svn",root):
               for files1 in files:                                  # directory provided.
                  FileNames.append(os.path.join(root,files1))        # If it is a file, join it with the root and append it into an array 
               for dirs1 in dirs:                                    # for processing further
                  DirNames.append(os.path.join(root,dirs1))          # if it is a directory, then, do the same operation, mentioned above. 
         for i in FileNames:                                      # Modify permissions for all the files to Write.
            os.chmod(i, 0777)

         #for i in DirNames:                                       # Similarly for directories
         #   os.chmod(i,0777)

      #elif os.path.isfile(FilePath):                              # If the provided path is not a dir,but a file, 
      #   os.chmod(FilePath, 0777)    


      for file1 in FileNames:

         for exclude_dir in all_exclude_directories:
            temp = os.path.normpath(file1)
            temp = re.sub(r"\\", "/", temp)         
            if re.search(exclude_dir + "/", temp):
               continue
               
         if file1.endswith(".c"):
            temp = os.path.normpath(file1)
            temp = re.sub(r"\\", "/", temp)
            CFiles.append(temp)

         if file1.endswith(".h"):
            temp = os.path.normpath(file1)
            temp = re.sub(r"\\", "/", temp)
            HFiles.append(temp)
         
   return(CFiles, HFiles)
   
   
   

def get_source_files_from_config_file(project_location):
   
   source_files_in_project_array = []
   
   conf_file_location = os.path.join(project_location, "nbproject")
   conf_file_location = os.path.join(conf_file_location, "configurations.xml")
   
   if os.path.exists(conf_file_location):
      dom = parse(conf_file_location)
      all_item_Path = dom.getElementsByTagName("itemPath")
      for item_Path in all_item_Path:
         if item_Path.ELEMENT_NODE == item_Path.nodeType:
            if len(item_Path.childNodes) >= 1:
               parent_node = item_Path.parentNode
               if parent_node.ELEMENT_NODE == parent_node.nodeType:
                  if parent_node.attributes: 
                     for i in range(parent_node.attributes.length): 
                        a = parent_node.attributes.item(i)
                        if a.name == "projectFiles":
                           if a.value == "true":
                              temp = item_Path.childNodes[0].data.encode('ascii','ignore')
                              if temp.endswith(".c") or temp.endswith(".h"):
                                 
                                 # Find the Absolute Path of the source file.
                                 
                                 temp = os.path.join(project_location, temp)
                                 temp = os.path.normpath(temp)
                                 temp = re.sub(r"\\", "/", temp)
                                 
                                 if os.path.exists(temp):
                                    source_files_in_project_array.append(temp)
                           
   return(source_files_in_project_array)

def create_ldra_delete_set_command(ldra_log_file, set_name):
   command = ''
   command = command + "conrules -delete_set=" + set_name
   return(command)


def create_ldra_create_set_command(ldra_log_file, set_name):
   command = ''
   command = command + "conrules " + set_name + " -create_set=system 1q >> \"" + ldra_log_file + "\" 2>&1"
   return(command)
   
   
def create_ldra_add_files_to_set_command(ldra_log_file, set_name, source_files_list):
   command = ''
   for i in range(len(source_files_list)):
      
      if source_files_list[i] != '':
         command = command + "conrules " + set_name
         command = command + " -add_set_file=\"" + source_files_list[i] + "\""
         command = command + " >> \"" + ldra_log_file + "\" 2>&1\n"
      
   return(command)   

def create_ldra_analysis_command(ldra_log_file, set_name, analysis_options):
   command = ''
   command = command + "conrules " + set_name + " " + analysis_options + " >> " + ldra_log_file + " 2>&1"
   return(command)



def create_results_filter_command(ldra_log_file, set_name, filter_options, ldra_work_files_dir):
   command = ''
   
   glh_file = os.path.join(ldra_work_files_dir, set_name + "_tbwrkfls")
   glh_file = os.path.join(glh_file, set_name + ".glh")
   glh_file = os.path.normpath(glh_file)


   result_file = os.path.join(ldra_work_files_dir, set_name + "_tbwrkfls")
   result_file = os.path.join(result_file, set_name + ".txt")
   result_file = os.path.normpath(result_file)
   
   
   command = command + "tbglhapi result=" + glh_file + " flags=" + filter_options + " >> " + ldra_log_file + " 2>&1"
   return(command, result_file)

def execute_command(command, analysis_script, cwd=''):
   
   cwd1 = os.getcwd()
   if cwd == '':
      cwd1 = os.getcwd()
   else:
      cwd1 = cwd

   analyze_file = analysis_script + ".bat"
   newline_command = "echo ."
   if sys.platform == "win32":
      analyze_file = analysis_script + ".bat"
      #newline_command = "echo. >> " + ldra_log_file + " 2>&1"
   elif sys.platform == "linux2":
      analyze_file = analysis_script + ".sh"
      #newline_command = "echo >> " + ldra_log_file + " 2>&1"
   
   analyze_file = os.path.normpath(analyze_file)
   
   fptr = open(analyze_file, "w")
   fptr.write(command)
   fptr.close()


   command_for_exec = []
   
   if 'win32' == sys.platform:
      command_for_exec.append(analyze_file)
   else:
      command_for_exec.append("sh")
      command_for_exec.append(analyze_file)      
         
   ##################################################
   # Execute the script file
   Process1 = subprocess.Popen(command_for_exec)
   
   TimeOut = 0
   
   while(None == Process1.poll()):                 # Check for the existance of the process
      time.sleep(1)
      TimeOut = TimeOut + 1   
   
   print "Took " + str(TimeOut) + " Seconds"
   # Execution complete
   ##################################################
   return(Process1.returncode)
   
   
   
def append_string_to_file(string_content, file_path):
   if os.path.exists(file_path):
      fptr = open(file_path, "a")
   else:
      fptr = open(file_path, "w")
   
   fptr.write(string_content)
   
   fptr.close()
      

def execute_ldra_commands(ldra_commands_array, directory_switch, comments_array, project_source_files, ldra_log_file, analysis_script, set_name):

   #print ldra_commands_array, directory_switch, project_source_files
   local_ldra_commands_array = []
   local_ldra_commands_array_raw = []
   
   local_directory_switch = []
   local_comments = []
   
   
   ldra_bin_path, ldra_work_files_dir = get_ldra_bin_path()
   set_directory = set_name + "_tbwrkfls"
   set_directory = os.path.join(ldra_work_files_dir, set_directory)
   
   if os.path.exists(set_directory):
      shutil.rmtree(set_directory, 1)
   
   #######################################################
   # Append Source file, if any
   #######################################################
   for i in range(len(ldra_commands_array)):
      
      master_command = ldra_commands_array[i]
      
      if re.search("_LDRA_VAR_SRC_FILES_", ldra_commands_array[i]):
         
         # In case of Windows Computer, add the files one by one.
         
         if sys.platform == 'win32':
            for j in range(len(project_source_files)):
               master_command = re.sub("_LDRA_VAR_SRC_FILES_", '"' + project_source_files[j] + '"', ldra_commands_array[i]) + " "
               local_ldra_commands_array_raw.append(master_command)
               local_ldra_commands_array.append(master_command + " >> \"" + ldra_log_file + "\" 2>&1")
               local_directory_switch.append(directory_switch[i])
               local_comments.append(comments_array[i])
                  
         else:
            cmd_ary = re.split(" ", ldra_commands_array[i])
            temp_cmd = ''

            iteration_enabled = 1
            files_count = 0

            while iteration_enabled == 1:
               temp_cmd = ""
               iteration_enabled = 0
               for cmd in cmd_ary:
                  temp = cmd
                  if re.search("_LDRA_VAR_SRC_FILES_", cmd):
                     src_added_command = ""
                     for j in range(len(project_source_files) - files_count):

                        src_added_command = src_added_command + re.sub("_LDRA_VAR_SRC_FILES_", '"' + project_source_files[files_count] + '"', cmd) + " "
                        files_count = files_count + 1

                        if len(src_added_command) > 7000:
                           iteration_enabled = 1
                           break

                     temp = src_added_command.strip(" ")
                  temp_cmd = temp_cmd + temp + " "

               master_command = temp_cmd

               if iteration_enabled == 1:
                  local_ldra_commands_array_raw.append(master_command)
                  local_ldra_commands_array.append(master_command + " >> \"" + ldra_log_file + "\" 2>&1")          
                  local_directory_switch.append(directory_switch[i])
                  local_comments.append(comments_array[i])

            if iteration_enabled == 0:
               local_ldra_commands_array_raw.append(master_command)
               local_ldra_commands_array.append(master_command + " >> \"" + ldra_log_file + "\" 2>&1")          
               local_directory_switch.append(directory_switch[i])
               local_comments.append(comments_array[i])

      else:
         local_ldra_commands_array_raw.append(master_command)
         local_ldra_commands_array.append(master_command + " >> \"" + ldra_log_file + "\" 2>&1")
         local_directory_switch.append(directory_switch[i])
         local_comments.append(comments_array[i])
   

   
   #######################################################
   # End of Append Source file
   #######################################################
   
   
   #######################################################
   # Executing each command in the array
   #######################################################
   
   for i in range(len(local_ldra_commands_array)):
      cwd = os.getcwd()
      
      if os.path.exists(local_directory_switch[i]):
         os.chdir(local_directory_switch[i])
         
      log_file_string_content = "\n"
      log_file_string_content = log_file_string_content + ("*" * 50) + "\n"
      log_file_string_content = log_file_string_content + "ARBS Executing " + local_comments[i] + "\n"
      log_file_string_content = log_file_string_content + "Command:\n" + local_ldra_commands_array_raw[i] + "\n"
      log_file_string_content = log_file_string_content + ("*" * 50) + "\n"   
      log_file_string_content = log_file_string_content + "\nLog as follows\n" + ("-" * 50) + "\n\n"
      append_string_to_file(log_file_string_content, ldra_log_file)   
      print "\n\n***** Executing command " + str(i+1) + " of " + str(len(local_ldra_commands_array)) + " *****\n\n"
      command_result = execute_command(local_ldra_commands_array[i], analysis_script)
      
      log_file_string_content = "\n" + ("*" * 50) + "\n"
      log_file_string_content = log_file_string_content + "End of Command Execution\n"
      log_file_string_content = log_file_string_content + ("*" * 50) + "\n"      
      append_string_to_file(log_file_string_content, ldra_log_file)
      os.chdir(cwd)


def _execute_ldra_commands(ldra_log_file, set_name, source_files_list, analysis_options, filter_options, analysis_script, ldra_work_files_dir, results_log_file_name, ldra_bin_path, CREATE_SET_COMMAND_TEMPLATE, ADD_FILES_TO_SET_COMMAND_TEMPLATE, ANALYSIS_COMMAND_TEMPLATE, FILTER_COMMAND_TEMPLATE):
   print CREATE_SET_COMMAND_TEMPLATE, ADD_FILES_TO_SET_COMMAND_TEMPLATE, ANALYSIS_COMMAND_TEMPLATE, FILTER_COMMAND_TEMPLATE
   
   ARBS_ADD_SET_NAME
   ARBS_ADD_SET_TYPE
   ARBS_ADD_SOURCE_FILE
   ARBS_ADD_ANALYZE_OPTIONS
   ARBS_ADD_LDRA_WORK_FILES_LOCATION
   ARBS_ADD_FILTER_FLAGS
   
   #CREATE_SET_COMMAND_TEMPLATE = re.sub("", , ADD_FILES_TO_SET_COMMAND_TEMPLATE, ANALYSIS_COMMAND_TEMPLATE, FILTER_COMMAND_TEMPLATE)
   
   ###############################################
   # Delete Existing Set
   ###############################################
   command = create_ldra_delete_set_command(ldra_log_file, set_name)
   execute_command(command, analysis_script)

   ###############################################
   # Create a new Set
   ###############################################   
   log_file_string_content = "\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"
   log_file_string_content = log_file_string_content + "ARBS Executing Create Set Command\n"
   command = create_ldra_create_set_command(ldra_log_file, set_name)
   log_file_string_content = log_file_string_content + "Command:\n" + command + "\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"   
   log_file_string_content = log_file_string_content + "\nLog as follows\n" + ("-" * 50) + "\n\n"
   append_string_to_file(log_file_string_content, ldra_log_file)
   command_result = execute_command(command, analysis_script)
   log_file_string_content = "\n" + ("*" * 50) + "\n"
   log_file_string_content = log_file_string_content + "End of Create Set Command Execution\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"      
   append_string_to_file(log_file_string_content, ldra_log_file)
   if command_result != 0:
      log_file_string_content = "\n\n" + ("*" * 50) + "\n"
      log_file_string_content = log_file_string_content + "ERROR\nAbove command execution ended up in failure. Exiting now.\n"
      log_file_string_content = log_file_string_content + ("*" * 50) + "\n"      
      append_string_to_file(log_file_string_content, ldra_log_file)      
      return
   
   time.sleep(1)
   ###############################################
   # Add Files to the new Set
   ###############################################   
   log_file_string_content = "\n\n\n\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"
   log_file_string_content = log_file_string_content + "ARBS Adding Files to the set\n"
   #log_file_string_content = log_file_string_content + ("*" * 50) + "\n"   
   #log_file_string_content = log_file_string_content + "\nLog as follows\n" + ("-" * 50) + "\n\n"
   command = create_ldra_add_files_to_set_command(ldra_log_file, set_name, source_files_list)
   log_file_string_content = log_file_string_content + "Command:\n" + command + "\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"   
   log_file_string_content = log_file_string_content + "\nLog as follows\n" + ("-" * 50) + "\n\n"
   append_string_to_file(log_file_string_content, ldra_log_file)
   command_result = execute_command(command, analysis_script)
   log_file_string_content = "\n" + ("*" * 50) + "\n"
   log_file_string_content = log_file_string_content + "End of Adding Files\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"      
   append_string_to_file(log_file_string_content, ldra_log_file)   
   if command_result != 0:
      log_file_string_content = "\n\n" + ("*" * 50) + "\n"
      log_file_string_content = log_file_string_content + "ERROR\nAbove command execution ended up in failure. Exiting now.\n"
      log_file_string_content = log_file_string_content + ("*" * 50) + "\n"      
      append_string_to_file(log_file_string_content, ldra_log_file)      
      return
      
      
   time.sleep(1)   
   ###############################################
   # Execute analysis
   ###############################################    
   log_file_string_content = "\n\n\n\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"
   log_file_string_content = log_file_string_content + "ARBS Executing Analysis Command\n"
   #log_file_string_content = log_file_string_content + ("*" * 50) + "\n"   
   #log_file_string_content = log_file_string_content + "\nLog as follows\n" + ("-" * 50) + "\n\n"  
   #append_string_to_file(log_file_string_content, ldra_log_file)
   command = create_ldra_analysis_command(ldra_log_file, set_name, analysis_options)
   log_file_string_content = log_file_string_content + "Command:\n" + command + "\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"   
   log_file_string_content = log_file_string_content + "\nLog as follows\n" + ("-" * 50) + "\n\n"
   append_string_to_file(log_file_string_content, ldra_log_file)
   command_result = execute_command(command, analysis_script)
   log_file_string_content = "\n" + ("*" * 50) + "\n"
   log_file_string_content = log_file_string_content + "End of Analysis\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"      
   append_string_to_file(log_file_string_content, ldra_log_file)   
   if command_result != 0:
      log_file_string_content = "\n\n" + ("*" * 50) + "\n"
      log_file_string_content = log_file_string_content + "ERROR\nAbove command execution ended up in failure. Exiting now.\n"
      log_file_string_content = log_file_string_content + ("*" * 50) + "\n"      
      append_string_to_file(log_file_string_content, ldra_log_file)      
      return
      

   time.sleep(1)
   ###############################################
   # Execute Filter
   ###############################################    
   log_file_string_content = "\n\n\n\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"
   log_file_string_content = log_file_string_content + "ARBS Executing Results Filter Command\n"
   #log_file_string_content = log_file_string_content + ("*" * 50) + "\n"   
   #log_file_string_content = log_file_string_content + "\nLog as follows\n" + ("-" * 50) + "\n\n"  
   #append_string_to_file(log_file_string_content, ldra_log_file)
   command, result_file = create_results_filter_command(ldra_log_file, set_name, filter_options, ldra_work_files_dir)
   log_file_string_content = log_file_string_content + "Command:\n" + command + "\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"   
   log_file_string_content = log_file_string_content + "\nLog as follows\n" + ("-" * 50) + "\n\n"
   append_string_to_file(log_file_string_content, ldra_log_file)
   
   cwd = os.getcwd()
   os.chdir(ldra_bin_path)
   command_result = execute_command(command, analysis_script, cwd)
   os.chdir(cwd)
   
   log_file_string_content = "\n" + ("*" * 50) + "\n"
   log_file_string_content = log_file_string_content + "End of Results Filter Command Execution\n"
   log_file_string_content = log_file_string_content + ("*" * 50) + "\n"      
   append_string_to_file(log_file_string_content, ldra_log_file)   
   if command_result != 0:
      log_file_string_content = "\n\n" + ("*" * 50) + "\n"
      log_file_string_content = log_file_string_content + "ERROR\nAbove command execution ended up in failure. Exiting now.\n"
      log_file_string_content = log_file_string_content + ("*" * 50) + "\n"      
      append_string_to_file(log_file_string_content, ldra_log_file)      
      return   
   else:
      if os.path.exists(result_file):
         shutil.copy(result_file, results_log_file_name)
     
   time.sleep(1)
   
   
   
   
def get_ldra_bin_path():
   CompilerPathRefFile = ''
   if 'win32' == sys.platform:
      CompilerPathRefFile = "C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr" 
   elif 'linux2' == sys.platform:                                 # Linux
      CompilerPathRefFile = "/home/ARBS_SUPPORT/LIN_ToolSuiteLocations.mcpr" 
   elif 'darwin' == sys.platform:                                 # MAC 
      CompilerPathRefFile = "/Users/ARBS_SUPPORT/MAC_ToolSuiteLocations.mcpr" 

   ########################################
   # Put make command into the System path
   ldra_path = ''
   ldra_work_files = ''
   
   if os.path.exists(CompilerPathRefFile):

      mcpr_file_pointer = open(CompilerPathRefFile,"r")
      for line in mcpr_file_pointer:
         if re.search("_LDRA_PATH_=", line):
            ldra_path = re.split("=", line)[1]
            ldra_path = ldra_path.strip("\r").strip("\n").strip("\r").strip("\n") 
            ldra_path = ldra_path.strip(" ")
            ldra_path = ldra_path.rstrip("/")
            ldra_path = ldra_path.rstrip(r"\\")   
         elif re.search("_LDRA_WORK_FILES_=", line):
            ldra_work_files = re.split("=", line)[1]
            ldra_work_files = ldra_work_files.strip("\r").strip("\n").strip("\r").strip("\n") 
            ldra_work_files = ldra_work_files.strip(" ")
            ldra_work_files = ldra_work_files.rstrip("/")
            ldra_work_files = ldra_work_files.rstrip(r"\\")              
   return(os.path.normpath(ldra_path), os.path.normpath(ldra_work_files))
   
   
   
   

def create_results_dir():

   result_raw_directory = "Archives"
   result_raw_directory = os.path.join(result_raw_directory,"ldra")
   result_raw_directory = "LDRA_Report"
   
   ResultsDirectory = result_raw_directory
   
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

   return(ResultsDirectory, result_raw_directory)
   


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

def create_error_html_file(supplied_directory, options_file_location, error_type="INPUT_FILE"):

   html_string = "<html>\n<head>\n<title>LDRA_ResultSummary</title>\n</head>\n<body>\n<font face=Courier >\n"
   
   
   html_string = html_string + "<b>ARBS_Build_Mechanism_For_LDRA Analysis Rev Beta_0V2</b><br><br>\n"
   
   html_string = html_string + "<br><b>LDRA Options File Location: </b>\"" + options_file_location + "\"<br><br>\n"
   
   if error_type == "INPUT_FILE":
   
      if os.path.exists(options_file_location):
         analysis_options, filter_options, set_type, rule_filter_set = get_user_options(options_file_location)
         html_string = html_string + "Analysis Options: " + analysis_options + "<br>\n"
         html_string = html_string + "Set Type: " + set_type + "<br>\n"
         html_string = html_string + "Filter Flags: " + filter_options + "<br><br>\n"
         html_string = html_string + "Directory used for analysis: " + supplied_directory + "<br>\n"
         html_string = html_string + "<br><br><b>Please feed all the options in the csv file to proceed LDRA Analysis</b><br>\n"
      else:
         html_string = html_string + "<br><br>Unable to access the options file " + options_file_location + "<br>\n"
   
   elif error_type == "SRC_MISSING":
   
      if os.path.exists(options_file_location):
         analysis_options, filter_options, set_type, rule_filter_set = get_user_options(options_file_location)
         html_string = html_string + "Analysis Options: " + analysis_options + "<br>\n"
         html_string = html_string + "Set Type: " + set_type + "<br>\n"
         html_string = html_string + "Filter Flags: " + filter_options + "<br><br>\n"
         html_string = html_string + "Directory used for analysis: " + supplied_directory + "<br>\n"
         
         html_string = html_string + "<br><br><b>The given directory has no source files available</b><br>\n"
      else:
         html_string = html_string + "<br><br>Unable to access the options file " + options_file_location + "<br><br>\n"
         html_string = html_string + "Directory used for analysis: " + supplied_directory + "<br>\n"         
         html_string = html_string + "<br><br><b>The given directory has no source files available</b><br>\n"
         
         
   html_string = html_string + "<br><b><font color=red >" + ("[FAIL] [*FAIL*] " * 5) + "</b></font><br>"
   
   html_string = html_string + "</font>\n</body>\n</html>\n"
   
   results_html_file_name = "LDRA_Report/ldra_report.htm"
   fptr = open(results_html_file_name, "w")
   fptr.write(html_string)
   fptr.close()

   return (results_html_file_name)

            
            
            
def get_job_details():
   svn_link = ''
   job_name = ''
   
   PRCount = 0
   
   for Parameter in sys.argv:
      PRCount = PRCount + 1

      if PRCount == 2:
         DirectoryForScan = Parameter
      elif PRCount >= 3:
         if re.search("-link=",Parameter.lower()):
            Parameter = re.sub("-link=",'',Parameter)
            svn_link = Parameter
            if 'win32' == sys.platform:
               svn_link = re.sub(r"\\","/",svn_link)
               svn_link = re.sub(":/","://",svn_link)
         elif re.search("-pro=",Parameter.lower()):
            Parameter = re.sub("-pro=",'',Parameter)
            ProjectName = Parameter
         elif re.search("-job=",Parameter.lower()):
            Parameter = re.sub("-job=",'',Parameter)
            job_name = Parameter             
         elif re.search("-test_link=",Parameter.lower()):
            Parameter = re.sub("-test_link=",'',Parameter)
            svn_link = Parameter  
   return(svn_link, job_name)

def create_result_html_file(ldra_project_locations, ldra_command_log_locations, ldra_result_locations, ldra_options_file, ldra_bin_path):

   html_string = "<html>\n<head>\n<title>LDRA_ResultSummary</title>\n</head>\n<body>\n<font face=Courier >\n"
   
   svn_link, job_name = get_job_details()

   html_string = html_string + "<b>ARBS_Build_Mechanism_For_LDRA Analysis Rev Beta_0V2</b><br><br>\n"
   
   html_string = html_string + "<b>Job Name: </b>" + job_name + "<br>"
   
   html_string = html_string + "<b>Test Code SVN Link: </b>" + "<a href=\"" + svn_link + "\">" + svn_link + "</a><br>" 
   html_string = html_string + "<br><b>LDRA Options File Location: </b>\"" + ldra_options_file + "\"<br><br>\n"

   if os.path.exists(ldra_options_file):
      analysis_options, filter_options, set_type, rule_filter_set = get_user_options(ldra_options_file)
      html_string = html_string + "Analysis Options: " + analysis_options + "<br>\n"
      html_string = html_string + "Set Type: " + set_type + "<br>\n"
      html_string = html_string + "Filter Flags: " + filter_options + "<br>\n"
      html_string = html_string + "Rules Filter: " + rule_filter_set + "<br><br>\n"
      
   html_string = html_string + "<b>LDRA binary path: </b>" + ldra_bin_path + "<br><br>\n"
   
   html_string = html_string + "<br><br><b>Results for individual projects</b><br>\n" + ("-" * 31) + "<br><br>\n"

   max_len = GetMaxLength(ldra_project_locations)
   
   for i in range(len(ldra_project_locations)):
      html_string = html_string + str(i+1) + ". " + ldra_project_locations[i] + InsertSpaces(max_len, ldra_project_locations[i], i+1)
      html_string = html_string + " <a href=\"" + ldra_result_locations[i] + "\">" + "[ RESULT ]" + "</a>, " 
      html_string = html_string + "<a href=\"" + ldra_command_log_locations[i] + "\">" + "Console Messages" + "<br></a>\n" 
   
   html_string = html_string + "</font>\n</body>\n</html>\n"
   
   results_html_file_name = "LDRA_Report/ldra_report.htm"
   fptr = open(results_html_file_name, "w")
   fptr.write(html_string)
   fptr.close()
   
   '''
   StatisticsFileString = ''
   
   StatisticsFileName = "LDRA_Statistics.statinfo"
   
   StatisticsFileString = StatisticsFileString + "\nPROJECT_NAME:" + job_name + "\n"
   StatisticsFileString = StatisticsFileString + "\nRESULT_FILE_NAME:" + results_html_file_name + "\n"
   StatisticsFilePtr = open(StatisticsFileName,"w")
   StatisticsFilePtr.write(StatisticsFileString)
   StatisticsFilePtr.close()    
   '''
   return(results_html_file_name)

def get_commands_to_be_executed(options_file):
   
   delete_set_command = ""   
   create_set_command = ""
   add_files_to_set_command = ""
   add_system_variables_file_command = ""
   add_system_search_path_file_command = ""
   analysis_command = ""
   filter_command = ""
   statistics_xml_file_creation_command = ""
   results_file = ""
   result_artifacts = ""
   
   fptr = open(options_file, "r")

   for _line in fptr:
      line = _line.strip("\n|\r")
      if re.search("^DELETE_SET_COMMAND_BINARY_AND_OPTIONS,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if not re.search("^#", items) and item_count > 1:
               if items != '':
                  delete_set_command = delete_set_command + items.strip(" ") + " "
         
         delete_set_command = delete_set_command.strip(" ")
         
      if re.search("^CREATE_SET_COMMAND_BINARY_AND_OPTIONS,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if not re.search("^#", items) and item_count > 1:
               if items != '':
                  create_set_command = create_set_command + items.strip(" ") + " "
         
         create_set_command = create_set_command.strip(" ")

      if re.search("^ADD_FILES_TO_SET_COMMAND_BINARY_AND_OPTIONS,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if not re.search("^#", items) and item_count > 1:
               if items != '':
                  add_files_to_set_command = add_files_to_set_command + items.strip(" ") + " "
         
         add_files_to_set_command = add_files_to_set_command.strip(" ")

      if re.search("^ADD_SYSTEM_VARIABLES_FILE_TO_SET_BINARY_AND_OPTIONS,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if not re.search("^#", items) and item_count > 1:
               if items != '':
                  add_system_variables_file_command = add_system_variables_file_command + items.strip(" ") + " "
         
         add_system_variables_file_command = add_system_variables_file_command.strip(" ")
         
      if re.search("^ADD_SYSTEM_SEARCH_PATH_FILE_BINARY_AND_OPTIONS,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if not re.search("^#", items) and item_count > 1:
               if items != '':
                  add_system_search_path_file_command = add_system_search_path_file_command + items.strip(" ") + " "
         
         add_system_search_path_file_command = add_system_search_path_file_command.strip(" ")
      
      if re.search("^ANALYSIS_COMMAND_BINARY_AND_OPTIONS,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if not re.search("^#", items) and item_count > 1:
               if items != '':
                  analysis_command = analysis_command + items.strip(" ") + " "
         
         analysis_command = analysis_command.strip(" ")

      if re.search("^FILTER_COMMAND_BINARY_AND_OPTIONS,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if not re.search("^#", items) and item_count > 1:
               if items != '':
                  filter_command = filter_command + items.strip(" ") + " "
         
         filter_command = filter_command.strip(" ")



      if re.search("^STATISTICS_XML_EXTRACTION_BINARY_AND_OPTIONS,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if not re.search("^#", items) and item_count > 1:
               if items != '':
                  statistics_xml_file_creation_command = statistics_xml_file_creation_command + items.strip(" ") + " "
         
         statistics_xml_file_creation_command = statistics_xml_file_creation_command.strip(" ")
         
         
      if re.search("^RESULT_FILE,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if not re.search("^#", items) and item_count > 1:
               if items != '':
                  results_file = results_file + items.strip(" ") + " "
         
         results_file = results_file.strip(" ")

      if re.search("^RESULT_ARTIFACT,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if not re.search("^#", items) and item_count > 1:
               if items != '':
                  result_artifacts = result_artifacts + items.strip(" ") + " "
         
         result_artifacts = result_artifacts.strip(" ")
   fptr.close()
   
   return(delete_set_command, create_set_command, add_files_to_set_command, add_system_variables_file_command, add_system_search_path_file_command, analysis_command, filter_command, statistics_xml_file_creation_command, results_file, result_artifacts)         

def get_user_options(options_file):
   
   ANALYSIS_OPERATION = ""
   FILTER_FLAGS = ""
   SET_TYPE = ""
   RULE_FILTER_SET = ""
   
   temp_include_rule_filter_set = ""
   temp_exclude_rule_filter_set = ""
   
   fptr = open(options_file, "r")
   
   for _line in fptr:
      line = _line.strip("\n|\r")
      
      if re.search("^ANALYSIS_OPERATION,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if re.search("^#", items):
               break            
            if item_count > 1:
               if items != '':
                  ANALYSIS_OPERATION = ANALYSIS_OPERATION + items.strip(" ")    
      if re.search("^FILTER_FLAGS,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if re.search("^#", items):
               break            
            if item_count > 1:
               if items != '':
                  FILTER_FLAGS = FILTER_FLAGS + items.strip(" ")   
      if re.search("^SET_TYPE,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if re.search("^#", items):
               break            
            if item_count > 1:
               if items != '':
                  SET_TYPE = SET_TYPE + items.strip(" ")   

      if re.search("^RULE_FILTER_INCLUDE,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if re.search("^#", items):
               break            
            if item_count > 1:
               if items != '':
                  temp_include_rule_filter_set = items.strip(" ")  

      if re.search("^RULE_FILTER_EXCLUDE,", line):
         ary = re.split(",", line)
         item_count = 0
         for items in ary:
            item_count = item_count + 1
            if re.search("^#", items):
               break            
            if item_count > 1:
               if items != '':
                  temp_exclude_rule_filter_set = items.strip(" ")  
                  
   fptr.close()
   
   
   ldra_rules_set = ldra_rule_set.get_ldra_rule_set()
   
   if temp_include_rule_filter_set != "":
      
      RULE_FILTER_SET = temp_include_rule_filter_set
      
      if temp_exclude_rule_filter_set != "":
         
         inc_ary = re.split(";", temp_include_rule_filter_set)
         exc_ary = re.split(";", temp_exclude_rule_filter_set)
         
         new_inc_ary = []
         
         for inc_element in inc_ary:
            
            replace_with_key = 0
            _new_inc_ary = []
            
            for key in ldra_rules_set:
               if inc_element == key:
                  for ldra_rule_name in range(len(ldra_rules_set[key])):
                     append_this_rule = 1
                     for exc_element in exc_ary:
                        if ldra_rules_set[key][ldra_rule_name].strip(";") == exc_element:
                           replace_with_key = 1
                           append_this_rule = 0
                     
                     if append_this_rule == 1:
                        _new_inc_ary.append(ldra_rules_set[key][ldra_rule_name].strip(";"))
            
            if replace_with_key == 0:
               new_inc_ary.append(inc_element)
               
            else:
               for item in _new_inc_ary:
                  new_inc_ary.append(item)
         
         inc_ary = new_inc_ary
         
         temp_final_rule_set = ""
         
         for inc_element in inc_ary:
            option_found_in_exc = 0
            for exc_element in exc_ary:
               if inc_element.strip(" ") == exc_element.strip(" "):
                  option_found_in_exc = 1
            
            if option_found_in_exc == 0:
               temp_final_rule_set = temp_final_rule_set + inc_element + "; "
         
         RULE_FILTER_SET = temp_final_rule_set.strip(";").strip(" ")
         
   print RULE_FILTER_SET

   return(ANALYSIS_OPERATION, FILTER_FLAGS, SET_TYPE, RULE_FILTER_SET)
   
   
def get_ldra_options(options_file, ldra_set_name, system_variables_file="", system_search_path_file=""):
   
   input_error = 0
   
   ldra_commands_array = []
   directory_switch = []
   comments_array = []
   
   stat_xml_file_location = ''
   
   delete_set_command, create_set_command, add_files_to_set_command, add_system_variables_file_command, add_system_search_path_file_command, analysis_command, filter_command, statistics_xml_file_creation_command, results_file, result_artifacts = get_commands_to_be_executed(options_file)
   
   
   if create_set_command == '' or add_files_to_set_command == '' or analysis_command == '':  # if any of the 3 basic command goes missing in the user supplied csv file, go for the default csv file for options
      local_commands_file = "ldra_default_comand_options.csv"
      delete_set_command, create_set_command, add_files_to_set_command, add_system_variables_file_command, add_system_search_path_file_command, analysis_command, filter_command, statistics_xml_file_creation_command, results_file, result_artifacts = get_commands_to_be_executed(local_commands_file)
   
   ANALYSIS_OPERATION, FILTER_FLAGS, SET_TYPE, RULE_FILTER_SET = get_user_options(options_file)
      
   if SET_TYPE == '' or ANALYSIS_OPERATION == '':
      print "error"
      input_error = 1
   else:
      ldra_bin_path, ldra_work_files_dir = get_ldra_bin_path()
      
      if delete_set_command != '':
      
         delete_set_command = re.sub("_LDRA_VAR_SET_NAME_", ldra_set_name, delete_set_command)
         delete_set_command = re.sub("_LDRA_VAR_SET_TYPE_", SET_TYPE, delete_set_command)
         #delete_set_command = re.sub("_LDRA_VAR_SRC_FILES_", "", delete_set_command)
         delete_set_command = re.sub("_LDRA_VAR_ANALYSIS_OPERATION_", ANALYSIS_OPERATION, delete_set_command)
         delete_set_command = re.sub("_LDRA_VAR_WORKFILES_DIR_LOCATION_", ldra_work_files_dir, delete_set_command)
         delete_set_command = re.sub("_LDRA_VAR_FILTER_FLAGS_", FILTER_FLAGS, delete_set_command)

         delete_set_command = re.sub(r"\\\\", r"\\", delete_set_command)
         delete_set_command = re.sub(r"\\", "/", delete_set_command)

         ldra_commands_array.append(delete_set_command)
         directory_switch.append(ldra_bin_path)
         message = "Executing the create set command"
         comments_array.append(message)
      
      
      create_set_command = re.sub("_LDRA_VAR_SET_NAME_", ldra_set_name, create_set_command)
      create_set_command = re.sub("_LDRA_VAR_SET_TYPE_", SET_TYPE, create_set_command)
      #create_set_command = re.sub("_LDRA_VAR_SRC_FILES_", "", create_set_command)
      create_set_command = re.sub("_LDRA_VAR_ANALYSIS_OPERATION_", ANALYSIS_OPERATION, create_set_command)
      create_set_command = re.sub("_LDRA_VAR_WORKFILES_DIR_LOCATION_", ldra_work_files_dir, create_set_command)
      create_set_command = re.sub("_LDRA_VAR_FILTER_FLAGS_", FILTER_FLAGS, create_set_command)
      
      create_set_command = re.sub(r"\\\\", r"\\", create_set_command)
      create_set_command = re.sub(r"\\", "/", create_set_command)
      
      ldra_commands_array.append(create_set_command)
      directory_switch.append(ldra_bin_path)
      message = "Executing the create set command"
      comments_array.append(message)
      
      add_files_to_set_command = re.sub("_LDRA_VAR_SET_NAME_", ldra_set_name, add_files_to_set_command)
      add_files_to_set_command = re.sub("_LDRA_VAR_SET_TYPE_", SET_TYPE, add_files_to_set_command)
      #add_files_to_set_command = re.sub("_LDRA_VAR_SRC_FILES_", "", add_files_to_set_command)
      add_files_to_set_command = re.sub("_LDRA_VAR_ANALYSIS_OPERATION_", ANALYSIS_OPERATION, add_files_to_set_command)
      add_files_to_set_command = re.sub("_LDRA_VAR_WORKFILES_DIR_LOCATION_", ldra_work_files_dir, add_files_to_set_command)
      add_files_to_set_command = re.sub("_LDRA_VAR_FILTER_FLAGS_", FILTER_FLAGS, add_files_to_set_command)

      add_files_to_set_command = re.sub(r"\\\\", r"\\", add_files_to_set_command)
      add_files_to_set_command = re.sub(r"\\", "/", add_files_to_set_command)
      
      ldra_commands_array.append(add_files_to_set_command)
      directory_switch.append(ldra_bin_path)
      message = "Adding Files to the set"
      comments_array.append(message)
      
      
      if system_variables_file != "":
         if add_system_variables_file_command != "":
            if os.path.exists(system_variables_file):
               
               add_system_variables_file_command = re.sub("_LDRA_VAR_SET_NAME_", ldra_set_name, add_system_variables_file_command)
               add_system_variables_file_command = re.sub("_LDRA_VAR_SET_TYPE_", SET_TYPE, add_system_variables_file_command)
               #add_system_variables_file_command = re.sub("_LDRA_VAR_SRC_FILES_", "", add_system_variables_file_command)
               add_system_variables_file_command = re.sub("_LDRA_VAR_ANALYSIS_OPERATION_", ANALYSIS_OPERATION, add_system_variables_file_command)
               add_system_variables_file_command = re.sub("_LDRA_VAR_WORKFILES_DIR_LOCATION_", ldra_work_files_dir, add_system_variables_file_command)
               add_system_variables_file_command = re.sub("_LDRA_VAR_FILTER_FLAGS_", FILTER_FLAGS, add_system_variables_file_command)
               add_system_variables_file_command = re.sub("_LDRA_VAR_SYSTEM_VARIABLES_FILE_PATH_", '"' + re.sub(r"\\", "/", os.path.normpath(os.path.abspath(system_variables_file))) + '"', add_system_variables_file_command)
               add_system_variables_file_command = re.sub(r"\\\\", r"\\", add_system_variables_file_command)
               add_system_variables_file_command = re.sub(r"\\", "/", add_system_variables_file_command)

               ldra_commands_array.append(add_system_variables_file_command)
               directory_switch.append(ldra_bin_path)
               message = "Adding System Variables File"
               comments_array.append(message)
      
      if system_search_path_file != "":
         if add_system_search_path_file_command != "":
            if os.path.exists(system_search_path_file):
               add_system_search_path_file_command = re.sub("_LDRA_VAR_SET_NAME_", ldra_set_name, add_system_search_path_file_command)
               add_system_search_path_file_command = re.sub("_LDRA_VAR_SET_TYPE_", SET_TYPE, add_system_search_path_file_command)
               #add_system_search_path_file_command = re.sub("_LDRA_VAR_SRC_FILES_", "", add_system_search_path_file_command)
               add_system_search_path_file_command = re.sub("_LDRA_VAR_ANALYSIS_OPERATION_", ANALYSIS_OPERATION, add_system_search_path_file_command)
               add_system_search_path_file_command = re.sub("_LDRA_VAR_WORKFILES_DIR_LOCATION_", ldra_work_files_dir, add_system_search_path_file_command)
               add_system_search_path_file_command = re.sub("_LDRA_VAR_FILTER_FLAGS_", FILTER_FLAGS, add_system_search_path_file_command)
               add_system_search_path_file_command = re.sub("_LDRA_VAR_SYSTEM_SEARCH_FILE_PATH_", '"' + re.sub(r"\\", "/", os.path.normpath(os.path.abspath(system_search_path_file))) + '"', add_system_search_path_file_command)

               add_system_search_path_file_command = re.sub(r"\\\\", r"\\", add_system_search_path_file_command)
               add_system_search_path_file_command = re.sub(r"\\", "/", add_system_search_path_file_command)

               ldra_commands_array.append(add_system_search_path_file_command)
               directory_switch.append(ldra_bin_path)
               message = "Adding System Search Paths File"
               comments_array.append(message)            
      
      
      analysis_command = re.sub("_LDRA_VAR_SET_NAME_", ldra_set_name, analysis_command)
      analysis_command = re.sub("_LDRA_VAR_SET_TYPE_", SET_TYPE, analysis_command)
      #analysis_command = re.sub("_LDRA_VAR_SRC_FILES_", "", analysis_command)
      analysis_command = re.sub("_LDRA_VAR_ANALYSIS_OPERATION_", ANALYSIS_OPERATION, analysis_command)
      analysis_command = re.sub("_LDRA_VAR_WORKFILES_DIR_LOCATION_", ldra_work_files_dir, analysis_command)
      analysis_command = re.sub("_LDRA_VAR_FILTER_FLAGS_", FILTER_FLAGS, analysis_command)

      analysis_command = re.sub(r"\\\\", r"\\", analysis_command)
      analysis_command = re.sub(r"\\", "/", analysis_command)
      
      ldra_commands_array.append(analysis_command)
      directory_switch.append(ldra_bin_path)
      message = "Performing Analysis"
      comments_array.append(message)



      statistics_xml_file_creation_command = re.sub("_LDRA_VAR_SET_NAME_", ldra_set_name, statistics_xml_file_creation_command)
      statistics_xml_file_creation_command = re.sub("_LDRA_VAR_SET_TYPE_", SET_TYPE, statistics_xml_file_creation_command)
      #statistics_xml_file_creation_command = re.sub("_LDRA_VAR_SRC_FILES_", "", statistics_xml_file_creation_command)
      statistics_xml_file_creation_command = re.sub("_LDRA_VAR_ANALYSIS_OPERATION_", ANALYSIS_OPERATION, statistics_xml_file_creation_command)
      statistics_xml_file_creation_command = re.sub("_LDRA_VAR_WORKFILES_DIR_LOCATION_", ldra_work_files_dir, statistics_xml_file_creation_command)
      statistics_xml_file_creation_command = re.sub("_LDRA_VAR_FILTER_FLAGS_", FILTER_FLAGS, statistics_xml_file_creation_command)

      statistics_xml_file_creation_command = re.sub(r"\\\\", r"\\", statistics_xml_file_creation_command)
      statistics_xml_file_creation_command = re.sub(r"\\", "/", statistics_xml_file_creation_command)
      
      
      if re.search("\.xml", statistics_xml_file_creation_command.lower()):
         ary = re.split(" ", statistics_xml_file_creation_command)
         for item in ary:
            if re.search("\.xml", item.lower()):
               stat_xml_file_location = re.split("=", item)[1]
               stat_xml_file_location = re.sub("\"", "", stat_xml_file_location)
               break
      
      if statistics_xml_file_creation_command != '':
         ldra_commands_array.append(statistics_xml_file_creation_command)
         directory_switch.append(ldra_bin_path)
         message = "Creating Statistics XML File"
         comments_array.append(message)
      
      
      
      if FILTER_FLAGS != "" or RULE_FILTER_SET != "":
      
         temp_final_command = ""
         
         filter_command_ary = re.split(" ", filter_command)
         
         for _command in filter_command_ary:
            skip_this = 0
            
            if re.search("_LDRA_VAR_RULE_FILTER_", _command):
               if RULE_FILTER_SET == "":
                  skip_this = 1

            if re.search("_LDRA_VAR_FILTER_FLAGS_", _command):
               if FILTER_FLAGS == "":
                  skip_this = 1
                  
            if skip_this == 0:
               temp_final_command = temp_final_command + _command + " "
         
         filter_command = temp_final_command.strip(" ")
         
         filter_command = re.sub("_LDRA_VAR_SET_NAME_", ldra_set_name, filter_command)
         filter_command = re.sub("_LDRA_VAR_SET_TYPE_", SET_TYPE, filter_command)
         #filter_command = re.sub("_LDRA_VAR_SRC_FILES_", "", filter_command)
         filter_command = re.sub("_LDRA_VAR_ANALYSIS_OPERATION_", ANALYSIS_OPERATION, filter_command)
         filter_command = re.sub("_LDRA_VAR_WORKFILES_DIR_LOCATION_", ldra_work_files_dir, filter_command)
         filter_command = re.sub("_LDRA_VAR_FILTER_FLAGS_", FILTER_FLAGS, filter_command)
         filter_command = re.sub("_LDRA_VAR_RULE_FILTER_", RULE_FILTER_SET, filter_command)
         
         #filter_command = os.path.normpath(filter_command)
         filter_command = re.sub(r"\\\\", r"\\", filter_command)
         filter_command = re.sub(r"\\", "/", filter_command)
         
         if filter_command != '':
         
            ldra_commands_array.append(filter_command)
            directory_switch.append(ldra_bin_path)

            message = "Running Filter Flags"
            comments_array.append(message)
      
      results_file = re.sub("_LDRA_VAR_SET_NAME_", ldra_set_name, results_file)
      results_file = re.sub("_LDRA_VAR_SET_TYPE_", SET_TYPE, results_file)
      #results_file = re.sub("_LDRA_VAR_SRC_FILES_", "", results_file)
      results_file = re.sub("_LDRA_VAR_ANALYSIS_OPERATION_", ANALYSIS_OPERATION, results_file)
      results_file = re.sub("_LDRA_VAR_WORKFILES_DIR_LOCATION_", ldra_work_files_dir, results_file)
      results_file = re.sub("_LDRA_VAR_FILTER_FLAGS_", FILTER_FLAGS, results_file)
      #results_file = os.path.normpath(results_file)
      
      result_artifacts = re.sub("_LDRA_VAR_SET_NAME_", ldra_set_name, result_artifacts)
      result_artifacts = re.sub("_LDRA_VAR_SET_TYPE_", SET_TYPE, result_artifacts)
      #result_artifacts = re.sub("_LDRA_VAR_SRC_FILES_", "", result_artifacts)
      result_artifacts = re.sub("_LDRA_VAR_ANALYSIS_OPERATION_", ANALYSIS_OPERATION, result_artifacts)
      result_artifacts = re.sub("_LDRA_VAR_WORKFILES_DIR_LOCATION_", ldra_work_files_dir, result_artifacts)
      result_artifacts = re.sub("_LDRA_VAR_TOOLSUITE_DIR_LOCATION_", ldra_bin_path, result_artifacts)
      result_artifacts = re.sub("_LDRA_VAR_FILTER_FLAGS_", FILTER_FLAGS, result_artifacts)      
      #result_artifacts = os.path.normpath(result_artifacts)
      
   #print create_set_command, add_files_to_set_command, analysis_command, filter_command, results_file, result_artifacts   
   return(ldra_commands_array, directory_switch, comments_array, input_error, results_file, result_artifacts, stat_xml_file_location)
   
   '''
   sys.exit()
   
   
   analysis_options = ''
   filter_options = ''
   set_type = ''
   
   CREATE_SET_COMMAND_BINARY = ''
   ADD_FILES_TO_SET_COMMAND_BINARY = ''
   ANALYSIS_COMMAND_BINARY = ''
   FILTER_COMMAND_BINARY = ''

   CREATE_SET_COMMAND_BINARY, ADD_FILES_TO_SET_COMMAND_BINARY, ANALYSIS_COMMAND_BINARY, FILTER_COMMAND_BINARY
   
   if os.path.exists(options_file):
      fptr = open(options_file, "r")
      for line in fptr:
         temp = re.sub("\n", "", line)
         temp = re.sub("\r", "", temp)
         if re.search("^#", temp):
            print "This is a Comment"
         elif temp != '':
            array = re.split(",", temp)
            if len(array) >= 2:
               if array[0] == "ANALYSIS_OPERATION":
                  analysis_options = array[1]
               if array[0] == "FILTER_FLAGS":
                  filter_options = array[1]
               if array[0] == "SET_TYPE":
                  set_type = array[1]
               
               if array[0] == "CREATE_SET_COMMAND_BINARY":
                  CREATE_SET_COMMAND_BINARY = array[1].strip(" ")
               if array[0] == "ADD_FILES_TO_SET_COMMAND_BINARY":
                  ADD_FILES_TO_SET_COMMAND_BINARY = array[1].strip(" ")
               if array[0] == "ANALYSIS_COMMAND_BINARY":
                  ANALYSIS_COMMAND_BINARY = array[1].strip(" ")
               if array[0] == "FILTER_COMMAND_BINARY":
                  FILTER_COMMAND_BINARY = array[1].strip(" ")
      fptr.close()         
   commands_reference_file = "ldra_support.info"
   
   CREATE_SET_COMMAND_TEMPLATE = ''
   ADD_FILES_TO_SET_COMMAND_TEMPLATE = ''
   ANALYSIS_COMMAND_TEMPLATE = ''
   FILTER_COMMAND_TEMPLATE = ''
   
   if os.path.exists(commands_reference_file):
      fptr = open(commands_reference_file, "r")
      scan = 0
      for line in fptr:
         temp_line = re.sub("\n", "", line)
         temp_line = re.sub("\r", "", temp_line)
         if re.search("^#", temp_line):
            print "This is a Comment"
         elif temp_line != '':
            if temp_line == "_END_":
               scan = 0
            if scan > 0:
               if scan == 1:
                  if CREATE_SET_COMMAND_BINARY != "":
                     if temp_line != "":
                        temp = re.split(":", temp_line)[0]
                        if temp.upper() == CREATE_SET_COMMAND_BINARY.upper():
                           CREATE_SET_COMMAND_TEMPLATE = re.split(":", temp_line)[1]
               if scan == 2:
                  if ADD_FILES_TO_SET_COMMAND_BINARY != "":
                     if temp_line != "":
                        temp = re.split(":", temp_line)[0]
                        if temp.upper() == ADD_FILES_TO_SET_COMMAND_BINARY.upper():
                           ADD_FILES_TO_SET_COMMAND_TEMPLATE = re.split(":", temp_line)[1]                  
               if scan == 3:
                  if ANALYSIS_COMMAND_BINARY != "":
                     if temp_line != "":
                        temp = re.split(":", temp_line)[0]
                        if temp.upper() == ANALYSIS_COMMAND_BINARY.upper():
                           ANALYSIS_COMMAND_TEMPLATE = re.split(":", temp_line)[1]                
               if scan == 4:
                  if FILTER_COMMAND_BINARY != "":
                     if temp_line != "":
                        temp = re.split(":", temp_line)[0]
                        if temp.upper() == FILTER_COMMAND_BINARY.upper():
                           FILTER_COMMAND_TEMPLATE = re.split(":", temp_line)[1] 
                           
                           
            if temp_line == "_CREATE_SET_":
               scan = 1
            if temp_line == "_ADD_FILES_TO_SET_":
               scan = 2
            if temp_line == "_ANALYZE_":
               scan = 3
            if temp_line == "_FILTER_":
               scan = 4
               
      fptr.close()
   
   return(analysis_options, filter_options, set_type, CREATE_SET_COMMAND_TEMPLATE, ADD_FILES_TO_SET_COMMAND_TEMPLATE, ANALYSIS_COMMAND_TEMPLATE, FILTER_COMMAND_TEMPLATE)
   '''

def get_statistics_info_from_xml_file(stat_xml_file_location):
   print stat_xml_file_location

   count_advisory = 0
   count_required = 0
   count_mandatory = 0
   file_error = 1

   xml_path = os.path.normpath(stat_xml_file_location)
   if os.path.exists(xml_path) and os.path.isfile(xml_path):
      file_error = 0
      dom = parse(xml_path)
      all_violations = dom.getElementsByTagName("violation")
      for violation in all_violations:
         if violation.ELEMENT_NODE == violation.nodeType:
            if violation.attributes: 
               for i in range(violation.attributes.length): 
                  a = violation.attributes.item(i)
                  if a.name == "level":
                     level = a.value.encode('ascii','ignore')
                     if re.search("mandatory", level.lower()):
                        count_mandatory = count_mandatory + 1
                     elif re.search("required", level.lower()):
                        count_required = count_required + 1                        
                     elif re.search("advisory", level.lower()):
                        count_advisory = count_advisory + 1


   
   return(count_mandatory, count_required, count_advisory, file_error)
   
   

def analyze(project_locations, supplied_directory, ldra_options_file, ldra_set_name, test_type, test_link, include_dir="", exclude_dir="", system_variables_file="", system_search_path_file=""):
   ldra_project_locations = []
   ldra_result_locations = []
   ldra_command_log_locations = []
   
   no_of_src_fls_analysed = 0
   
   ldra_set_name = ldra_set_name.strip(" ")
   if ldra_set_name == '':
      ldra_set_name = "ARBS_TEST_SET"
   
   ldra_bin_path, ldra_work_files_dir = get_ldra_bin_path()
   
   script_workspace = os.getcwd()
   
   if ldra_bin_path != '':
      if 'win32' == sys.platform:
         os.environ["PATH"] = ldra_bin_path + ";" + os.environ["PATH"]
      else:
         os.environ["PATH"] = ldra_bin_path + ":" + os.environ["PATH"] 
      
   results_dir, result_raw_directory = create_results_dir()   
   
   ldra_commands_array, directory_switch, comments_array, input_error, results_file, result_artifacts, stat_xml_file_location = get_ldra_options(ldra_options_file, ldra_set_name, system_variables_file, system_search_path_file)
   
   
   #print analysis_options, "\n", filter_options, "\n", set_type, "\n", CREATE_SET_COMMAND_TEMPLATE, "\n", ADD_FILES_TO_SET_COMMAND_TEMPLATE, "\n", ANALYSIS_COMMAND_TEMPLATE, "\n", FILTER_COMMAND_TEMPLATE
   
   if input_error != 0:
   
      results_html_file_name = create_error_html_file(supplied_directory, ldra_options_file, "INPUT_FILE")
      
      StatisticsFileString = ''

      StatisticsFileName = "LDRA_Statistics.statinfo"
      svn_link, job_name = get_job_details()
      StatisticsFileString = StatisticsFileString + "\nLDRA_BUILD\n"
      StatisticsFileString = StatisticsFileString + "\nPROJECT_NAME:" + job_name + "\n"
      StatisticsFileString = StatisticsFileString + "\nRESULT_FILE_NAME:" + re.sub(r"\\", "/", results_html_file_name) + "\n"
      #StatisticsFileString = StatisticsFileString + "\nCONSOLE_LOG:" + re.sub(r"\\", "/", os.path.join(results_dir, message_log_file_name)) + "\n"
      StatisticsFileString = StatisticsFileString + "\nNUMBER_OF_SRC_FILES:" + str(no_of_src_fls_analysed) + "\n"
      StatisticsFileString = StatisticsFileString + "\nSUPPLIED_DIRECTORY:" + supplied_directory + "\n"
      StatisticsFileString = StatisticsFileString + "\nBUILD_OS:" + sys.platform + "\n"
      if test_type != '':
         StatisticsFileString = StatisticsFileString + "TEST_TYPE:" + test_type + "\n"
         if test_link != '':
            StatisticsFileString = StatisticsFileString + "TEST_LINK:" + re.sub(" ","%20",test_link) + "\n"         

      StatisticsFilePtr = open(StatisticsFileName,"w")
      StatisticsFilePtr.write(StatisticsFileString)
      StatisticsFilePtr.close() 
         
   else:
      #project_locations = []
      
      if len(project_locations) == 0:
         
         wrf_fls_dir = os.path.join(ldra_work_files_dir, ldra_set_name + "_tbwrkfls")
         if os.path.exists(wrf_fls_dir):
            shutil.rmtree(wrf_fls_dir, 1)
         
         results_dir = "LDRA_Report"
         
         if os.path.exists(results_dir):
            shutil.rmtree(results_dir, 1)
         
         os.makedirs(results_dir)
         
         project_source_files = []
         
         if (re.search(";", supplied_directory) or os.path.isfile(supplied_directory)):
            ary = re.split(";", supplied_directory)
            for files in ary:
               project_source_files.append(re.sub(r"\\", "/", files))
         else:
            CFiles, HFiles = get_source_files_from_directory(supplied_directory, include_dir, exclude_dir)

            project_source_files = CFiles
            
         no_of_src_fls_analysed = len(project_source_files)
         
         i = 0
         
         # if there are no source files available, exit with error
         if len(project_source_files) > 0:
         
            analysis_script = "analysis_" + str(i)
            analysis_script = os.path.join(script_workspace, analysis_script)

            message_log_file_name = "ldra_console_log_" + str(i) + ".txt"
            ldra_log_file = os.path.join(results_dir, message_log_file_name)
            ldra_log_file = os.path.normpath(ldra_log_file)


            #results_log_file_name = "ldra_result_log_" + str(i) + ".txt"
            ldra_result_file = os.path.join(results_dir, os.path.split(results_file)[1])
            ldra_result_file = os.path.normpath(ldra_result_file)


            if os.path.exists(analysis_script):
               os.remove(analysis_script)
            if os.path.exists(ldra_log_file):
               os.remove(ldra_log_file)

            ldra_log_file = os.path.join(os.getcwd(), ldra_log_file)

            ldra_log_file = os.path.normpath(ldra_log_file)

            set_name = ldra_set_name

            #analysis_options = "1q"

            #execute_ldra_commands(ldra_log_file, set_name, project_source_files, analysis_options, filter_options, analysis_script, ldra_work_files_dir, ldra_result_file, ldra_bin_path, CREATE_SET_COMMAND_TEMPLATE, ADD_FILES_TO_SET_COMMAND_TEMPLATE, ANALYSIS_COMMAND_TEMPLATE, FILTER_COMMAND_TEMPLATE)
            execute_ldra_commands(ldra_commands_array, directory_switch, comments_array, project_source_files, ldra_log_file, analysis_script, ldra_set_name)
            violations_mandatory, violations_required, violations_advisory, stat_xml_file_available_error = get_statistics_info_from_xml_file(stat_xml_file_location)
            #print os.path.normpath(results_file), os.path.normpath(result_artifacts)

            # Copy the Results file to the results directory
            if results_file != '':
               if os.path.exists(results_file):
                  shutil.copy(results_file, ldra_result_file)

            # Copy the other artifacts to the results directory
            if result_artifacts != '':
               rary = re.split(";", result_artifacts)
               for item in rary:
                  if os.path.exists(os.path.split(item)[0]):
                     item = os.path.normpath(item)
                     all_files_to_be_copied = glob.glob(item)
                     for file in all_files_to_be_copied:
                        shutil.copy(file, results_dir)



            results_file_available = 0
            if os.path.exists(ldra_result_file):
               results_file_available = 1
            else:
               fptr = open(ldra_result_file, "w")
               fptr.write("FAIL\n\nThere were no results generated from the LDRA Commands\n\n")
               fptr.close()


            svn_link, job_name = get_job_details()

            results_html_file_name = ldra_result_file

            StatisticsFileString = ''

            StatisticsFileName = "LDRA_Statistics.statinfo"

            StatisticsFileString = StatisticsFileString + "\nLDRA_BUILD\n"
            StatisticsFileString = StatisticsFileString + "\nPROJECT_NAME:" + job_name + "\n"
            StatisticsFileString = StatisticsFileString + "\nRESULT_FILE_NAME:" + re.sub(r"\\", "/", results_html_file_name) + "\n"
            StatisticsFileString = StatisticsFileString + "\nCONSOLE_LOG:" + re.sub(r"\\", "/", os.path.join(results_dir, message_log_file_name)) + "\n"
            StatisticsFileString = StatisticsFileString + "\nNUMBER_OF_SRC_FILES:" + str(len(project_source_files)) + "\n"
            StatisticsFileString = StatisticsFileString + "\nSUPPLIED_DIRECTORY:" + supplied_directory + "\n"
            StatisticsFileString = StatisticsFileString + "\nBUILD_OS:" + sys.platform + "\n"
            
            if stat_xml_file_available_error == 0 and results_file_available == 1:
               StatisticsFileString = StatisticsFileString + "\nVIOLATIONS_MANDATORY:" + str(violations_mandatory) + "\n"
               StatisticsFileString = StatisticsFileString + "\nVIOLATIONS_REQUIRED:" + str(violations_required) + "\n"
               StatisticsFileString = StatisticsFileString + "\nVIOLATIONS_ADVISORY:" + str(violations_advisory) + "\n"
               
               
            if test_type != '':
               StatisticsFileString = StatisticsFileString + "TEST_TYPE:" + test_type + "\n"
               if test_link != '':
                  StatisticsFileString = StatisticsFileString + "TEST_LINK:" + re.sub(" ","%20",test_link) + "\n"         

            StatisticsFilePtr = open(StatisticsFileName,"w")
            StatisticsFilePtr.write(StatisticsFileString)
            StatisticsFilePtr.close() 
   
         
         
         
      else:
         
         temp_ldra_set_name = ldra_set_name
         total_violations_mandatory = 0
         total_violations_required = 0
         total_violations_advisory = 0
         for i in range(len(project_locations)):

            ##############################################################
            project_name = ""
            config_xml_file = os.path.join(project_locations[i], "nbproject")
            config_xml_file = os.path.join(config_xml_file, "project.xml")
            
            if os.path.exists(config_xml_file):

               dom = parse(config_xml_file)
               proj_name_node = dom.getElementsByTagName("name")[0]
               if len(proj_name_node.childNodes) >= 1:
                  project_name = proj_name_node.childNodes[0].data.encode('ascii','ignore')    
            
            set_name = temp_ldra_set_name + "_" + project_name + "_" + str(i)
            
            if project_name == '':
               project_name = os.path.split(project_locations[i])[1] + "_" + str(i)
      
               set_name = temp_ldra_set_name + "_" + project_name + "_" + str(i)

            #analysis_options = "1q"
            ldra_set_name = set_name
            #execute_ldra_commands(ldra_log_file, set_name, project_source_files, analysis_options, filter_options, analysis_script, ldra_work_files_dir, ldra_result_file, ldra_bin_path, CREATE_SET_COMMAND_TEMPLATE, ADD_FILES_TO_SET_COMMAND_TEMPLATE, ANALYSIS_COMMAND_TEMPLATE, FILTER_COMMAND_TEMPLATE)
            wrf_fls_dir = os.path.join(ldra_work_files_dir, ldra_set_name + "_tbwrkfls")
            if os.path.exists(wrf_fls_dir):
               shutil.rmtree(wrf_fls_dir, 1)
            ##############################################################   
               
            project_source_files = get_source_files_from_config_file(project_locations[i])
            
            
            # if there are no source files available, exit with error
            if len(project_source_files) == 0:
               # Continue with the next available project
               continue
               
            
            
            analysis_script = "analysis_" + ldra_set_name
            analysis_script = os.path.join(script_workspace, analysis_script)
            
            message_log_file_name = "ldra_log_" + ldra_set_name + ".txt"
            ldra_log_file = os.path.join(results_dir, message_log_file_name)
            ldra_log_file = os.path.normpath(ldra_log_file)


           
            if os.path.exists(analysis_script):
               os.remove(analysis_script)
            if os.path.exists(ldra_log_file):
               os.remove(ldra_log_file)

            ldra_log_file = os.path.join(os.getcwd(), ldra_log_file)

            ldra_log_file = os.path.normpath(ldra_log_file)
            
           
            # This is for recreation of the set commands
            
            ldra_commands_array, directory_switch, comments_array, input_error, results_file, result_artifacts, stat_xml_file_location = get_ldra_options(ldra_options_file, ldra_set_name, system_variables_file, system_search_path_file)

            #print ldra_commands_array, directory_switch, comments_array, input_error, results_file, result_artifacts
            #sys.exit()
            #results_log_file_name = ldra_set_name + ".txt"
            ldra_result_file = os.path.join(results_dir, os.path.split(results_file)[1])
            ldra_result_file = os.path.normpath(ldra_result_file)

            print ldra_result_file
            #sys.exit()
            
            execute_ldra_commands(ldra_commands_array, directory_switch, comments_array, project_source_files, ldra_log_file, analysis_script, ldra_set_name)
            
            violations_mandatory, violations_required, violations_advisory, stat_xml_file_available_error = get_statistics_info_from_xml_file(stat_xml_file_location)
            total_violations_mandatory = total_violations_mandatory + violations_mandatory
            total_violations_required = total_violations_required + violations_required
            total_violations_advisory = total_violations_advisory + violations_advisory
            
            no_of_src_fls_analysed = no_of_src_fls_analysed + len(project_source_files)
            
            print os.path.normpath(results_file), os.path.normpath(result_artifacts)
            
            # Copy the Results file to the results directory
            if results_file != '':
               if os.path.exists(results_file):
                  shutil.copy(results_file, ldra_result_file)
            
            # Copy the other artifacts to the results directory
            if result_artifacts != '':
               rary = re.split(";", result_artifacts)
               for item in rary:
                  if os.path.exists(os.path.split(item)[0]):
                     item = os.path.normpath(item)
                     all_files_to_be_copied = glob.glob(item)
                     for file in all_files_to_be_copied:
                        shutil.copy(file, results_dir)
                     
                     
                  
            print ldra_result_file
            if not os.path.exists(ldra_result_file):
               fptr = open(ldra_result_file, "w")
               fptr.write("FAIL\n\nThere were no results generated from the LDRA Commands\n\n")
               fptr.close()



            #ldra_log_file_for_html_result = os.path.join(result_raw_directory, message_log_file_name)
            ldra_log_file_for_html_result = os.path.normpath(message_log_file_name)
            ldra_log_file_for_html_result = re.sub(r"\\", "/", ldra_log_file_for_html_result)

            #ldra_result_file_for_html_result = os.path.join(result_raw_directory, )
            ldra_result_file_for_html_result = os.path.split(results_file)[1]
            #ldra_result_file_for_html_result = os.path.normpath(os.path.split(results_file)[1])
            ldra_result_file_for_html_result = re.sub(r"\\", "/", ldra_result_file_for_html_result)


            
            ldra_command_log_locations.append(ldra_log_file_for_html_result)
            ldra_project_locations.append(project_locations[i])
            ldra_result_locations.append(ldra_result_file_for_html_result)


         if no_of_src_fls_analysed > 0:   # Atlease if one file is analyzed in any of the projects, proceed
         
            results_html_file_name = create_result_html_file(ldra_project_locations, ldra_command_log_locations, ldra_result_locations, ldra_options_file, ldra_bin_path)

            svn_link, job_name = get_job_details()

            StatisticsFileString = ''

            StatisticsFileName = "LDRA_Statistics.statinfo"

            StatisticsFileString = StatisticsFileString + "\nLDRA_BUILD\n"
            StatisticsFileString = StatisticsFileString + "\nPROJECT_NAME:" + job_name + "\n"
            StatisticsFileString = StatisticsFileString + "\nRESULT_FILE_NAME:" + re.sub(r"\\", "/", results_html_file_name) + "\n"
            #StatisticsFileString = StatisticsFileString + "\nCONSOLE_LOG:" + re.sub(r"\\", "/", os.path.join(results_dir, message_log_file_name)) + "\n"
            StatisticsFileString = StatisticsFileString + "\nNUMBER_OF_SRC_FILES:" + str(no_of_src_fls_analysed) + "\n"
            StatisticsFileString = StatisticsFileString + "\nSUPPLIED_DIRECTORY:" + supplied_directory + "\n"
            StatisticsFileString = StatisticsFileString + "\nBUILD_OS:" + sys.platform + "\n"


            if stat_xml_file_available_error == 0:
               StatisticsFileString = StatisticsFileString + "\nVIOLATIONS_MANDATORY:" + str(total_violations_mandatory) + "\n"
               StatisticsFileString = StatisticsFileString + "\nVIOLATIONS_REQUIRED:" + str(total_violations_required) + "\n"
               StatisticsFileString = StatisticsFileString + "\nVIOLATIONS_ADVISORY:" + str(total_violations_advisory) + "\n"
               
               
            if test_type != '':
               StatisticsFileString = StatisticsFileString + "TEST_TYPE:" + test_type + "\n"
               if test_link != '':
                  StatisticsFileString = StatisticsFileString + "TEST_LINK:" + re.sub(" ","%20",test_link) + "\n"         

            StatisticsFilePtr = open(StatisticsFileName,"w")
            StatisticsFilePtr.write(StatisticsFileString)
            StatisticsFilePtr.close() 


      # if there are no source files available, exit with error
      if (no_of_src_fls_analysed) == 0:

         results_html_file_name = create_error_html_file(supplied_directory, ldra_options_file, "SRC_MISSING")
         
         StatisticsFileString = ''

         StatisticsFileName = "LDRA_Statistics.statinfo"
         svn_link, job_name = get_job_details()
         StatisticsFileString = StatisticsFileString + "\nLDRA_BUILD\n"
         StatisticsFileString = StatisticsFileString + "\nPROJECT_NAME:" + job_name + "\n"
         StatisticsFileString = StatisticsFileString + "\nRESULT_FILE_NAME:" + re.sub(r"\\", "/", results_html_file_name) + "\n"
         #StatisticsFileString = StatisticsFileString + "\nCONSOLE_LOG:" + re.sub(r"\\", "/", os.path.join(results_dir, message_log_file_name)) + "\n"
         StatisticsFileString = StatisticsFileString + "\nNUMBER_OF_SRC_FILES:" + str(no_of_src_fls_analysed) + "\n"
         StatisticsFileString = StatisticsFileString + "\nSUPPLIED_DIRECTORY:" + supplied_directory + "\n"
         StatisticsFileString = StatisticsFileString + "\nBUILD_OS:" + sys.platform + "\n"
         if test_type != '':
            StatisticsFileString = StatisticsFileString + "TEST_TYPE:" + test_type + "\n"
            if test_link != '':
               StatisticsFileString = StatisticsFileString + "TEST_LINK:" + re.sub(" ","%20",test_link) + "\n"         

         StatisticsFilePtr = open(StatisticsFileName,"w")
         StatisticsFilePtr.write(StatisticsFileString)
         StatisticsFilePtr.close()          