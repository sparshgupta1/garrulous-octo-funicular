import os
import sys
import re
import subprocess
import time
import client_status


def remove_previous_results_file():
   for root, dirs, files in os.walk(os.getcwd()):              # Now, List the directories and files available in the 
      for files1 in files:                                  # directory provided.
         if files1.endswith(".html"):   
            f = os.path.join(root, files1)
            os.remove(f)
            

def get_isp_installation_paths(CompilerPathRefFile):

   _HARMONY_INSTALLED_LOCATION_ = "NA"
   _HARMONY_INSTALLER_PLIB_INCLUDE_SEARCH_PATH_ = "NA"
   _HARMONY_PLIB_INSTALLER_LIB_PATH_ = "NA"
   _ISP_WS_ = ""
   _ISP_TEST_TYPE_ = ""
   _ISP_TEST_LINK_ = ""
   _ISP_SHARED_WS_BRANCH_ = ""
   _ISP_SHARED_WS_TRUNK_ = ""

   _ISP_WS_TRUNK_ = ""
   _ISP_TEST_LINK_TRUNK_ = ""
   _ISP_WS_BRANCH_ = ""
   _ISP_TEST_LINK_BRANCH_ = ""

   
   
   isp_installation_dir = "NA"
   isp_include_search_path = "NA"
   isp_archived_lib_path = "NA"
   
   test_type = ""
   test_link = ""
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
                  _ISP_TEST_TYPE_ = re.split("=",line)[1] 
               
               if re.search("^_ISP_TEST_LINK_=",line):
                  _ISP_TEST_LINK_ = re.split("=",line)[1] 
                  
               if re.search("^_ISP_WS_",line):
                  _ISP_WS_ = re.split("=",line)[1]

               if re.search("^_ISP_SHARED_WS_BRANCH_",line):
                  _ISP_SHARED_WS_BRANCH_ = re.split("=",line)[1]

               if re.search("^_ISP_SHARED_WS_TRUNK_",line):
                  _ISP_SHARED_WS_TRUNK_ = re.split("=",line)[1]                  


               if re.search("^_ISP_WS_TRUNK_",line):
                  _ISP_WS_TRUNK_ = re.split("=",line)[1]  
               if re.search("^_ISP_TEST_LINK_TRUNK_",line):
                  _ISP_TEST_LINK_TRUNK_ = re.split("=",line)[1]  
               if re.search("^_ISP_WS_BRANCH_",line):
                  _ISP_WS_BRANCH_ = re.split("=",line)[1]  
               if re.search("^_ISP_TEST_LINK_BRANCH_",line):
                  _ISP_TEST_LINK_BRANCH_ = re.split("=",line)[1]                    

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
         #_ISP_TEST_TYPE_ = test_type

      if re.search("^-link=",sys.argv[i]) or re.search("^-test_link=",sys.argv[i]):
         
         branch_svn_path = re.split('=',sys.argv[i])[1]
         
         branch_svn_path = re.sub("\"","",branch_svn_path)
         
         #_ISP_TEST_LINK_ = branch_svn_path
         
   return(_HARMONY_INSTALLED_LOCATION_, _HARMONY_INSTALLER_PLIB_INCLUDE_SEARCH_PATH_, _HARMONY_PLIB_INSTALLER_LIB_PATH_, _ISP_WS_, _ISP_TEST_TYPE_, _ISP_TEST_LINK_, _ISP_SHARED_WS_BRANCH_, _ISP_SHARED_WS_TRUNK_, _ISP_WS_TRUNK_, _ISP_TEST_LINK_TRUNK_, _ISP_WS_BRANCH_, _ISP_TEST_LINK_BRANCH_)





current_file_path = sys.argv[0]

new_path = os.path.split(current_file_path)[0]

if new_path != '':
   os.chdir(new_path)
   
   

if os.path.isdir(os.getcwd()):                                 # if the given path is a directory, 

   for root, dirs, files in os.walk(os.getcwd()):              # Now, List the directories and files available in the 
      for files1 in files:                                  # directory provided.
         if files1.endswith(".statinfo"):
            os.unlink(os.path.join(root,files1))   
         if files1.endswith(".errinfo"):
            os.unlink(os.path.join(root,files1)) 
               
               
CompilerTobeUsed = "ALL"
print sys.argv
print len(sys.argv)
if len(sys.argv) <= 1 or len(sys.argv) >= 10:
   print "ERROR - Invalid Usage \n"
   print '*' * 10 + "USAGE" + '*' * 10 + "\n"
   print "python BuildDirectory.py <Directory with Projects within Quotes> <Optional Compiler to be used>\n"
   print "  Compiler to be used: \n \
            This parameter is optional. If not given, the native compiler of mcp file and make file will be taken\n\
            PICC - Identify the mcp files and make files, which are compatible to PICC Compiler and use PICC Compiler\n \
            PICC18 - Identify the mcp files and make files, which are compatible to PICC18 Compiler and use PICC18 Compiler\n \
            C18 - Identify the mcp files and make files, which are compatible to C18 Compiler and use C18 Compiler\n \
            XC8 - Identify the mcp files and make files, which are compatible to XC8 (projects created with PICC, PICC18 and XC8) Compiler and use XC8 Compiler\n \
            XC8-C18 - Identify the mcp files and make files created with C18 Compiler and use C18 Drivers in XC8 Compiler\n \
            C30 - Identify the mcp files and make files, which are compatible to C30 Compiler and use C30 Compiler\n \
            XC16 - Identify the mcp files and make files, which are compatible to XC16 (projects created with C30 and XC16) Compiler and use XC16 Compiler\n \
            C32 - Identify the mcp files and make files, which are compatible to C32 Compiler and use C32 Compiler\n \
            XC32 - Identify the mcp files and make files, which are compatible to XC32 (projects created with C32 and XC32) Compiler and use XC32 Compiler\n\n \
            "
   exit()
   

CompilerPathRefFile = ''
if 'win32' == sys.platform:
   CompilerPathRefFile = "C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr" 
elif 'linux2' == sys.platform:                                 # Linux
   CompilerPathRefFile = "/home/ARBS_SUPPORT/LIN_ToolSuiteLocations.mcpr" 
elif 'darwin' == sys.platform:                                 # MAC 
   CompilerPathRefFile = "/Users/ARBS_SUPPORT/MAC_ToolSuiteLocations.mcpr" 

########################################
# Put make command into the System path
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
               

   

proj_dir = ''   
job_name = ''    
compiler_name = ''
compiler_options_file = ''

add_command = ''


remove_previous_results_file()




test_type = "TRUNK"
test_link = "NA"

ldra_enable = 0

_HARMONY_INSTALLED_LOCATION_, _HARMONY_INSTALLER_PLIB_INCLUDE_SEARCH_PATH_, _HARMONY_PLIB_INSTALLER_LIB_PATH_, _ISP_WS_, _ISP_TEST_TYPE_, _ISP_TEST_LINK_, _ISP_SHARED_WS_BRANCH_, _ISP_SHARED_WS_TRUNK_, _ISP_WS_TRUNK_, _ISP_TEST_LINK_TRUNK_, _ISP_WS_BRANCH_, _ISP_TEST_LINK_BRANCH_ = get_isp_installation_paths(CompilerPathRefFile)

 
      
if _ISP_TEST_TYPE_ == "":
   _ISP_TEST_TYPE_ = ""
   _ISP_TEST_LINK_ = ""



for i in range(len(sys.argv)):
   options = sys.argv[i]
   if re.search("^-test_type=",options):
      t_type = re.split("=", options)[1]

      _ISP_TEST_TYPE_ = t_type

      if t_type == "TRUNK":
         if _ISP_WS_TRUNK_ != "":
            _ISP_WS_ = _ISP_WS_TRUNK_ + "/isp/software/isp_root"
            _ISP_TEST_LINK_ = _ISP_TEST_LINK_TRUNK_
      elif t_type == "BRANCH":
         if _ISP_WS_BRANCH_ != "":
            _ISP_WS_ = _ISP_WS_BRANCH_ + "/isp/software/isp_root"
            _ISP_TEST_LINK_ = _ISP_TEST_LINK_BRANCH_


# In case of non availability of shared paths, use the absolute path
if _ISP_SHARED_WS_BRANCH_ == '':
   _ISP_SHARED_WS_BRANCH_ = _ISP_WS_
if _ISP_SHARED_WS_TRUNK_ == '':
   _ISP_SHARED_WS_TRUNK_ = _ISP_WS_   
   
   
for i in range(len(sys.argv)):
   if i == 1:
      proj_dir = sys.argv[i]
      
      '''
      proj_dir = re.sub("%","",proj_dir)

      #if re.search("WORKSPACE",proj_dir)
      proj_dir = re.sub("WORKSPACE","",proj_dir)
      cwd = os.getcwd()
      proj_dir = os.path.join(cwd,proj_dir)
      '''

      
      #add_command = add_command + '"' + os.path.normpath(proj_dir) + '"'
      
   if i == 2:
      compiler_name = sys.argv[i]
      if compiler_name == '':
         compiler_name = "ALL"
      add_command = add_command + " " + "-com=" + compiler_name

   if i >= 3:
      options = sys.argv[i]
      
      if re.search("^-test_type=",options):

         if _ISP_TEST_TYPE_ != '':
            options = "-test_type=" + re.sub("\"", "", _ISP_TEST_TYPE_)
      
      if re.search("^-test_link=",options):
         if _ISP_TEST_LINK_ != '':
            options = "-test_link=" + re.sub("\"", "", _ISP_TEST_LINK_)        
      
      if re.search("^-en_ldra", options):
         ldra_enable = 1
         
      add_command = add_command + " " + options

      
final_isp_ws = ""

if re.search(";", proj_dir):
   _proj_dir = ""
   ary = re.split(";", proj_dir)
   for a in ary:
      temp = a
      if (not re.search("_ISP_WS_", a)) and re.search("_ISP_WS_", proj_dir):
         temp = "_ISP_WS_/" + a
      _proj_dir = _proj_dir + temp + ";"
   
   proj_dir = _proj_dir.strip(";")

if _ISP_TEST_TYPE_ == "INSTALLER":

   temp = re.sub(r"\\","/",_HARMONY_INSTALLED_LOCATION_)
   proj_dir = re.sub("_ISP_WS_",temp,proj_dir)
   final_isp_ws = temp
   
else:
  
   if ldra_enable == 1:
      
      if _ISP_TEST_TYPE_ == "BRANCH":
         temp = re.sub(r"\\","/",_ISP_SHARED_WS_BRANCH_)
         temp = temp + "/isp/software/isp_root"
         proj_dir = re.sub("_ISP_WS_",temp,proj_dir)
         final_isp_ws = temp
         
      elif _ISP_TEST_TYPE_ == "TRUNK":
         temp = re.sub(r"\\","/",_ISP_SHARED_WS_TRUNK_)
         temp = temp + "/isp/software/isp_root"
         proj_dir = re.sub("_ISP_WS_",temp,proj_dir)   
         final_isp_ws = temp
   else:   
      temp = re.sub(r"\\","/",_ISP_WS_)
      proj_dir = re.sub("_ISP_WS_",temp,proj_dir)
      final_isp_ws = temp
      
proj_dir = re.sub(r"\\", "/", proj_dir)

if len(proj_dir) > 2:
   if not re.search("^//",proj_dir):   # if the given path is not a shared directory, proceed with the formatting of path.
      proj_dir = re.sub("//","/",proj_dir)
      proj_dir = re.sub("//","/",proj_dir)


      proj_dir = os.path.abspath(proj_dir)

proj_dir = os.path.normpath(proj_dir)


add_command = '"' + proj_dir + '"' + " " + re.sub("_ISP_WS_", final_isp_ws, add_command)

   
   
      
job_name = os.getenv('JOB_NAME', "LOCAL_RUN")  #os.environ['JOB_NAME']
job_name = re.split(r"/|\\",job_name)[0]
add_command = add_command + " " + "-job=" + job_name      

#print add_command

if os.path.exists("db_results_file.txt"):
   try:
      os.remove("db_results_file.txt")
   except:
      print "Unable to remove db_results_file.txt"
      
########################################
if ldra_enable == 0:
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
   
########################################   

if 'win32' == sys.platform:
   
   Command = "python -u build_mplab_8.py " + add_command

   BatFile = open("BatFileMP8.bat",'w')
   BatFile.write(Command)
   BatFile.close()
   
   Command = "python -u build_mplab_x.py " + add_command

   BatFile = open("BatFileMPX.bat",'w')
   BatFile.write(Command)
   BatFile.close()

   if ldra_enable == 0:
      Process1 = subprocess.Popen("BatFileMP8.bat")
   Process2 = subprocess.Popen("BatFileMPX.bat")

   if ldra_enable == 0:
      while(Process1.poll() == None): 
         time.sleep(1)

   while(Process2.poll() == None): 
      time.sleep(1)
      
   sys.exit(Process2.returncode)
      
else:
   Command = "python build_mplab_x.py " + add_command
   BatFile = open("BatFileMPX.sh",'w')
   BatFile.write(Command)
   BatFile.close()

   sys.exit(os.system("sh BatFileMPX.sh"))

  