#######  Imports ##########################



import re
import os
import sys
import xlrd
from xlrd import open_workbook 
import time
import datetime
import shutil
from glob import glob

##### Checkout Compiler Info File from ARBS SVN #####

def checkout_compiler_info_file():

   svnlink_compiler_info = "https://idc-dk-dev-sys2.mchp-main.com:8443/svn/ARBS/CompilerInstallationTest/compiler_info_file/"
   dest_folder_in_client = ''
   
   if 'win32' == sys.platform:
      dest_folder_in_client = "C:/ARBS_SUPPORT/compiler_info" 
      
      if os.path.exists(dest_folder_in_client):
         Cmd = "rmdir /S /Q " + '"' + dest_folder_in_client + '"'
         os.system('"' + Cmd + '"')
      
   elif 'linux2' == sys.platform:                                 # Linux
      dest_folder_in_client = "/home/ARBS_SUPPORT/compiler_info" 
      
      if os.path.exists(dest_folder_in_client):
         Cmd = "rm -rf " + os.path.normpath(dest_folder_in_client)
         os.system(Cmd)      
      
   elif 'darwin' == sys.platform:                                 # MAC 
      dest_folder_in_client = "/Users/ARBS_SUPPORT/compiler_info"
      
      if os.path.exists(dest_folder_in_client):
         Cmd = "rm -rf " + os.path.normpath(dest_folder_in_client)
         os.system(Cmd) 
   

   co_cmds_compiler_info_file = ' '
   co_cmds_compiler_info_file = co_cmds_compiler_info_file + "svn co" + " " + svnlink_compiler_info + " " +  dest_folder_in_client + "  --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
                                                                                                                                     
   os.system(co_cmds_compiler_info_file)
   
   

##### Checkout non ISP test input file from ARBS SVN #####
   
def checkout_nonisp_test_input_file():

   svnlink_testinputfile = "https://idc-dk-dev-sys2.mchp-main.com:8443/svn/ARBS/non_isp_test_input/"
   dest_folder_in_client = ''
      
   if 'win32' == sys.platform:
      dest_folder_in_client = "C:/ARBS_SUPPORT/testinputfile" 
      
      if os.path.exists(dest_folder_in_client):
         Cmd = "rmdir /S /Q " + '"' + dest_folder_in_client + '"'
         os.system('"' + Cmd + '"')
      
   elif 'linux2' == sys.platform:                                 # Linux
      dest_folder_in_client = "/home/ARBS_SUPPORT/testinputfile" 
      
      if os.path.exists(dest_folder_in_client):
         Cmd = "rm -rf " + os.path.normpath(dest_folder_in_client)
         os.system(Cmd)      
      
   elif 'darwin' == sys.platform:                                 # MAC 
      dest_folder_in_client = "/Users/ARBS_SUPPORT/testinputfile"
      
      if os.path.exists(dest_folder_in_client):
         Cmd = "rm -rf " + os.path.normpath(dest_folder_in_client)
         os.system(Cmd)

   co_cmds_testinputfile = ' '
   co_cmds_testinputfile = co_cmds_testinputfile + "svn co" + " " + svnlink_testinputfile + " " +  dest_folder_in_client + "  --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"

   os.system(co_cmds_testinputfile)
   
##### Checkout software csv file from devtools SVN #####
   
def checkout_software_csv():

   svnlink_software_csv = "https://chn-vm-apps.microchip.com/mchprepo/APPS/administrative/dev_tool"
   dest_folder_in_client = ''
      
   if 'win32' == sys.platform:
      dest_folder_in_client = "C:/ARBS_SUPPORT/softwarecsv" 
      
      if os.path.exists(dest_folder_in_client):
         Cmd = "rmdir /S /Q " + '"' + dest_folder_in_client + '"'
         os.system('"' + Cmd + '"')
      
   elif 'linux2' == sys.platform:                                 # Linux
      dest_folder_in_client = "/home/ARBS_SUPPORT/softwarecsv" 
      
      if os.path.exists(dest_folder_in_client):
         Cmd = "rm -rf " + os.path.normpath(dest_folder_in_client)
         os.system(Cmd)      
      
   elif 'darwin' == sys.platform:                                 # MAC 
      dest_folder_in_client = "/Users/ARBS_SUPPORT/softwarcsv"
      
      if os.path.exists(dest_folder_in_client):
         Cmd = "rm -rf " + os.path.normpath(dest_folder_in_client)
         os.system(Cmd)

   co_cmds_testinputfile = ' '
   co_cmds_testinputfile = co_cmds_testinputfile + "svn co" + " " + svnlink_software_csv + " " +  dest_folder_in_client + "  --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"

   os.system(co_cmds_testinputfile)  

######### DecodeCellInformation function #####

def DecodeCellInformation(CellInfo):
   
   ReturnData = ''
      
   if isinstance(CellInfo,float):
   
      ReturnData = str(int(CellInfo))
      
   else:
   
      ReturnData = CellInfo.encode('ascii','ignore')   
   
   return(ReturnData.strip(" "))
   
##### Create CIF file if not present #####

def createCIF():
   
   if 'win32' == sys.platform:
      path = "C:/ARBS_SUPPORT/CIF.txt"
      path = os.path.normpath(path)
      
      if(os.path.exists(path)):
         print "CIF file found\n"   
      else:   
         myfile = open('C:/ARBS_SUPPORT/CIF.txt','w')       
         print "CIF file created in windows\n"
      
   elif 'linux2' == sys.platform:         
      path = "/home/ARBS_SUPPORT/CIF.txt"
      path = os.path.normpath(path)
      
      if(os.path.exists(path)):
         print "CIF file found\n"
         
      else:         
         myfile = open('/home/ARBS_SUPPORT/CIF.txt','w')
         print "CIF file created in Linux\n"
         
   elif 'darwin' == sys.platform:         
      path = "/Users/ARBS_SUPPORT/CIF.txt"
      path = os.path.normpath(path)      
      if(os.path.exists(path)):
         print "CIF file found\n"
         
      else:         
         myfile = open('/Users/ARBS_SUPPORT/CIF.txt','w')         
         print "CIF file created in Mac\n"
         
##### Trigger Job #####


   
########## Get the category of the compiler - Released or Latest or Versions from the ARBS_TestInput.xls spreadsheet ############
   
def GetCategory(Compilerinfosheet,comp_name):
      
   XC8Category = ''
   XC16Category = ''
   XC32Category = ''
   
   jobname = ''
   
   
   for RowNumber in range(Compilerinfosheet.nrows):
      for ColNumber in range(len(Compilerinfosheet.row_values(RowNumber))):
         
         if ColNumber == 5:
            CellValue = DecodeCellInformation(Compilerinfosheet.row_values(RowNumber)[ColNumber])
            CellValue = CellValue.strip(" |_")
            #CellValue = re.sub(" ","_",CellValue)
            
            comp_name = re.sub(" ",'',comp_name)
            xls_comp_name = re.sub(" ",'',CellValue)
            
            ##### For the list of computers in the cell, if it mactches the comp_name, execute on matching one #####
            
            xls_comp_name_lst = xls_comp_name.split(",")            
            for comp_list in xls_comp_name_lst:            
               if comp_name == comp_list:
                                          
                  getXC8InstallStatus = 0
                  getXC16InstallStatus = 0
                  getXC32InstallStatus = 0               
                  
                  XC8Category = DecodeCellInformation(Compilerinfosheet.row_values(RowNumber)[7])
                               
                  
                  XC16Category = DecodeCellInformation(Compilerinfosheet.row_values(RowNumber)[8])
                  XC32Category = DecodeCellInformation(Compilerinfosheet.row_values(RowNumber)[9])
                  
                  ##### Get Compiler info file location  #####

                  if 'win32' == sys.platform:
                     
                     compilerinfofilelocation = "C:/ARBS_SUPPORT/compiler_info/compiler_info_for_auto_installation.xls"
                     
                     if(os.path.exists(compilerinfofilelocation)):
                        print "compiler info file found\n"
                        
                     else:
                        print "compiler info file not found, cannot find categrories, exit\n"
                        exit()
                     
                     WorkBook = open_workbook(compilerinfofilelocation)
                     Compilerpathinfosheet = WorkBook.sheet_by_name("Windows") 
                     
                  elif 'linux2' == sys.platform:                                 
                     
                     compilerinfofilelocation = "/home/ARBS_SUPPORT/compiler_info/compiler_info_for_auto_installation.xls"
                     
                     if(os.path.exists(compilerinfofilelocation)):
                        print "compiler info file found\n"
                        
                     else:
                        print "compiler info file not found, cannot find categrories, exit\n"
                        exit()

                     WorkBook = open_workbook(compilerinfofilelocation)
                     Compilerpathinfosheet = WorkBook.sheet_by_name("Linux")
                     
                  elif 'darwin' == sys.platform:  

                     compilerinfofilelocation = "/Users/ARBS_SUPPORT/compiler_info/compiler_info_for_auto_installation.xls"
                     
                     if(os.path.exists(compilerinfofilelocation)):
                        print "compiler info file found\n"         
                              
                     else:
                        print "compiler info file not found, cannot find categrories, exit\n"
                        exit()      
                     
                     WorkBook = open_workbook(compilerinfofilelocation)
                     Compilerpathinfosheet = WorkBook.sheet_by_name("Mac")
                  
                  
                  if XC8Category != "Not Required" or XC8Category == "":                    
                     getXC8InstallStatus = XC8CompilerComparison(XC8Category,Compilerpathinfosheet)                                                      
                  else:                  
                     print "XC8Category is not required\n"               
                  
                  if XC16Category != "Not Required" or XC16Category == "":   
                     getXC16InstallStatus = XC16CompilerComparison(XC16Category,Compilerpathinfosheet)                                 
                  else:
                     print "XC16Category is not required\n"
                  
                  if XC32Category != "Not Required" or XC32Category == "":
                     getXC32InstallStatus = XC32CompilerComparison(XC32Category,Compilerpathinfosheet)                  
                  else:
                     print "XC32Category is not required\n"
                  
                  
                  #### Trigger the job if any of the compiler is changed i.e XC8InstallStatus, XC16InstallStatus, XC32InstallStatus is 1 #####
                  
                  
                  # if getXC8InstallStatus == 1 or getXC16InstallStatus ==1 or getXC32InstallStatus ==1:               
                     # jobname = DecodeCellInformation(Compilerinfosheet.row_values(RowNumber)[0])
                     # jobname = re.sub(" ","_",jobname)
                     
                     # trigger_job(jobname)
                  
                  
               
   
   
####### XC8 Compiler Comparison - b/w XLS and CI.txt , install and update CIF txt file ##########################################

def XC8CompilerComparison(XC8Category,Compilerpathinfosheet):
   
   PathXC8ReleasedinXLS = ''
   PathXC8ReleasedinCItext = ''
   PathXC8LatestinXLS = ''
   PathXC8LatestinCItext = ''
   PathXC8VersioninXLS = ''
   PathXC8VersioninCItext = ''
   XC8InstalStatus = 1
   XC8InstallPath = ''
   
   CIFfilepath = ''
   
   ##### Get the path of installer #####
   
   if 'win32' == sys.platform:       
      CIFfilepath = "C:\ARBS_SUPPORT\CIF.txt"
      
   elif 'linux2' == sys.platform:   
      CIFfilepath = "/home/ARBS_SUPPORT/CIF.txt"
      
   elif 'darwin' == sys.platform:      
      CIFfilepath = "/Users/ARBS_SUPPORT/CIF.txt"
      
   else:
   
      print " Unsupported platform\n"
      exit()
   
      ################## XC8 RELEASED #############################################################
            
   if XC8Category == "XC8;Released":
      print "The Category of XC8 is Released\n"
      
      ######## Get the path of XC8 Released from XLS #############################################
      
      for RowNumber in range(Compilerpathinfosheet.nrows):
         for ColNumber in range(len(Compilerpathinfosheet.row_values(RowNumber))):
         
            CellValue = DecodeCellInformation(Compilerpathinfosheet.row_values(RowNumber)[ColNumber])
         
            if re.search("XC8;Released;",CellValue):
               PathXC8ReleasedinXLS = re.sub("XC8;Released;","",CellValue)
            
      ####### Get the path of XC8 from CIF.txt and compare with xls path ####################################################

      Fileptr = open(CIFfilepath,'r')   

      XC8InstalStatus = 1
      
      for lines in Fileptr:        
         if re.search("XC8;",lines):
            lines = lines.strip("\n")            
            PathXC8CItext = re.split(";",lines)[1]
            
            if(PathXC8ReleasedinXLS == PathXC8CItext):               
               print "XC8 Installer availabe, Installation not required\n"
               XC8InstalStatus = 0
               break;
      
      ######## If comparison does not match start Installation ###################################
      if XC8InstalStatus == 1:       
      
         print "XC8 Installation required\n"
         XC8InstallPath = PathXC8ReleasedinXLS
         XC8InstallFolder = InstallXC8Compiler(XC8InstallPath,XC8Category)
         updateCIFXC8(XC8InstallPath,XC8InstallFolder,XC8Category)
         print "CIF file updated\n"
         
      
  ################## XC8 Latest #############################################################
      
   if XC8Category == "XC8;Latest":
      print "The Category of XC8 is Latest\n"
      
      ######## Get the path of XC8 Latest from XLS #############################################
      
      for RowNumber in range(Compilerpathinfosheet.nrows):
         for ColNumber in range(len(Compilerpathinfosheet.row_values(RowNumber))):
         
            CellValue = DecodeCellInformation(Compilerpathinfosheet.row_values(RowNumber)[ColNumber])
         
            if re.search("XC8;Latest;",CellValue):
               PathXC8LatestinXLS = re.sub("XC8;Latest;","",CellValue)
            
      ####### Get the path of XC8 from CIF.txt ####################################################

      Fileptr = open(CIFfilepath,'r')   

      XC8InstalStatus = 1
      
      for lines in Fileptr:        
         if re.search("XC8;",lines):
            lines = lines.strip("\n")            
            PathXC8CItext = re.split(";",lines)[1]
                       
            if(PathXC8LatestinXLS == PathXC8CItext):               
               print "XC8 Installer availabe, Installation not required\n"
               XC8InstalStatus = 0
               break;         
      
      
      ######## If comparison does not match start Installation ###################################
      if XC8InstalStatus == 1:       
      
         print "XC8 Installation required\n"
         XC8InstallPath = PathXC8LatestinXLS
         XC8InstallFolder = InstallXC8Compiler(XC8InstallPath,XC8Category)
         updateCIFXC8(XC8InstallPath,XC8InstallFolder,XC8Category)
         print "CIF file updated\n"
    
   ################ XC8 Version ###############################################################
   
   
   cmpword = "XC8;Version"
   if cmpword in XC8Category:
   
      print "The Category of XC8 is Version " + XC8Category + "\n"
                        
      ######## Get the path of XC8 Path from XLS #############################################
      
      for RowNumber in range(Compilerpathinfosheet.nrows):
         for ColNumber in range(len(Compilerpathinfosheet.row_values(RowNumber))):
         
            CellValue = DecodeCellInformation(Compilerpathinfosheet.row_values(RowNumber)[ColNumber])
         
            if re.search(XC8Category,CellValue):
               PathXC8VersioninXLS = re.sub(XC8Category,"",CellValue)
               PathXC8VersioninXLS = re.sub(";","",PathXC8VersioninXLS)
                    
                                    
      ####### Get the path of XC8 from CIF.txt ####################################################

      Fileptr = open(CIFfilepath,'r')   

      XC8InstalStatus = 1
      
      for lines in Fileptr:        
         if re.search("XC8;",lines):
            lines = lines.strip("\n")            
            PathXC8CItext = re.split(";",lines)[1]
            
            if(PathXC8VersioninXLS == PathXC8CItext):               
               print "XC8 Installer availabe, Installation not required\n"
               XC8InstalStatus = 0
               break;
      
      ######## If comparison does not match start Installation ###################################
      if XC8InstalStatus == 1:       
      
         print "XC8 Installation required\n"
         XC8InstallPath = PathXC8VersioninXLS         
         XC8InstallFolder = InstallXC8Compiler(XC8InstallPath,XC8Category)
         updateCIFXC8(XC8InstallPath,XC8InstallFolder,XC8Category)
         print "CIF file updated\n"
   
   return(XC8InstalStatus)
      
############################## Install XC8 Compiler #####################################

def InstallXC8Compiler(XC8InstallPath,XC8Category):

   XC8Uninstaller_FullPath = ''
   XC8UninstallerCommands = ''
   XC8Installercommands = ''
   XC8InstallerActivationKey = ''
   XC8ActivationKeyPath = "C:/Program Files/Microchip/xclm/bin/xclm.exe"
   XC8ActivationKeyCommands = '"' + XC8ActivationKeyPath + '"' + " " + "-actkey" + " " + "4047-7489-2868-2425" 
     
   if 'win32' == sys.platform:      
              
      ##### Copy installer from Sangam to Installer path on Windows #####
      
      path = "C:\\InstallerPath"
      path = os.path.normpath(path)
      installerpath = ''
   
      if(os.path.exists(path)):
         os.system("rmdir /S /Q " + path)
     
      os.system("mkdir " + '"' + path + '"')   
      copycmd = "copy " + '"' + XC8InstallPath + '"' + " " + '"' + path + '"'    
   
      os.system(copycmd)      
      time.sleep(59)
      
      ##### If category is not Latest, Install in a common folder of that version #####
      
      if XC8Category != "XC8;Latest":
      
         for root,dirs,files in os.walk(path):
            for filename in files:
               if filename.endswith(".exe"):
                  installerpath = path + "\\" + filename
         
         XC8InstallFolder = ''
         instfold = os.path.split(XC8InstallPath)[1]
         instfold = re.sub('.exe','',instfold)

         XC8InstallFolder = os.path.normpath(os.path.join("C:\\ARBS_SUPPORT\\microchip\\xc8\\", instfold))      
      
      ##### If the category is Latest Install in Latest folder #####
      
      if XC8Category == "XC8;Latest":         
         
         for root,dirs,files in os.walk(path):
            for filename in files:
               if filename.endswith(".exe"):
                  installerpath = path + "\\" + filename
         
         XC8InstallFolder = "C:\\ARBS_SUPPORT\\microchip\\xc8\\Latest"
         
         if os.path.exists(XC8InstallFolder):
            os.system("rmdir /S /Q " + XC8InstallFolder)

      
      XC8Installercommands = installerpath + " " + "--mode unattended --unattendedmodeui none --installer-language en --prefix" + " " + '"' + XC8InstallFolder + '"' + " " + "--netservername localhost"
      
      
      ##### Execute Installation #####
      print "\nExecuting Installation"
      os.system(XC8Installercommands)  
      time.sleep(59)      
       
   elif 'linux2' == sys.platform:
         
      ##### Copy installer to local folder #####
      
      path = "/home/ARBS_SUPPORT/temp_installer/"         
   
      if(os.path.exists(path)):
         os.system("rm -rf "+ " " + path)
     
      os.system("mkdir " + " " + path )    
          
      copycmd = "wget -nd -m -P" + " " + path + " " + XC8InstallPath      
      os.system(copycmd)   
      time.sleep(59)
             
      ##### Change installer path to local path in Linux #####
 
      run_path = os.path.split(XC8InstallPath)[1]
      InstallPath = path + run_path

      permission_cmds = "chmod a+x" + " " + InstallPath
      os.system(permission_cmds)
      
      ##### Execute Installation on Linux for XC8 #####
      
      ##### If category is not Latest, Install in a common folder of that version #####
      
      if XC8Category != "XC8;Latest":
      
         XC8InstallFolder = ''
         instfold = os.path.split(XC8InstallPath)[1]
         instfold = re.sub('.run','',instfold)

         XC8InstallFolder = os.path.normpath(os.path.join("/home/ARBS_SUPPORT/microchip/xc8/", instfold))
      
      ##### If the category is Latest install in Latest folder #####
      
      if XC8Category == "XC8;Latest":
      
         XC8InstallFolder = "/home/ARBS_SUPPORT/microchip/xc8/Latest"
         if os.path.exists(XC8InstallFolder):         
            Cmd = "echo dishan2442 | sudo -S rm -rf" + " " + XC8InstallFolder
            os.system(Cmd)            
      
      XC8Installercommands = "echo dishan2442|sudo -S " + " " + InstallPath + " " + "--mode unattended --unattendedmodeui none --installer-language en --prefix" + " " + XC8InstallFolder + " " + "--netservername localhost"
      
      print "\nExecuting Installation"
      os.system(XC8Installercommands)  
      time.sleep(122)
      
   elif 'darwin' == sys.platform:
      
      XC8Uninstaller_Path = "/Applications/microchip/xc8"        

      if os.path.exists(XC8Uninstaller_Path): 
         Cmd = "echo microchip | sudo -S rm -r " + " " + XC8Uninstaller_Path
         os.system(Cmd)
      
      ##### Change installer path to mounted path in Linux by replacing //idc-ws-... to testmount #####
 
      XC8InstallPath = re.sub("//idc-ws-isparbs.microchip.com/compiler_installers/Installers/","/Users/ARBS_SUPPORT/test_mount/Installers/",XC8InstallPath)     
      
      ##### mount and unmount dmg folder to ../current_installer/cur_inst #####
      
      dmg_mount_dir = "/Users/ARBS_SUPPORT/test_mount/current_installer/cur_inst/"
      
      if os.path.exists(dmg_mount_dir):
      
         print "dmg mount folder exists\n"
         unmount_cmd = "umount" + " " + dmg_mount_dir
         os.system(unmount_cmd) 
         
      else: 
      
         print "dmg mount folder does not exists, creating new mount folder\n"
         
         os.system("mkdir /Users/ARBS_SUPPORT/test_mount/current_installer/")
         os.system("mkdir /Users/ARBS_SUPPORT/test_mount/current_installer/cur_inst/")
         
      dmg_mount_cmd = "hdiutil attach -mountpoint" + " " + dmg_mount_dir + " " +  XC8InstallPath
      os.system(dmg_mount_cmd)
      
      installer_availability_status = 0
      path_cur_inst = ""
      XC8InstallPath_Mac = ""
      for root,dirs,files in os.walk(dmg_mount_dir):           
         for i in files:               
            if i == "osx-intel":             
               path_cur_inst = root
               installer_availability_status = 1
               
         
      if installer_availability_status == 1:         
         print "Mac installer available\n"            
      else:         
         print " Mac installer for current category is un available and installation terminated\n"
         exit()
         
      XC8InstallPath_Mac =  path_cur_inst + "/osx-intel" 
                       
      ##### Execute Installation on Mac for XC8 #####         
      
      XC8Installercommands = "sudo" + " " + XC8InstallPath_Mac + " " + "--mode unattended  --unattendedmodeui none --installer-language en --prefix  /Applications/microchip/xc8/ --netservername localhost"
              
      print "\nExecuting Installation"
      os.system(XC8Installercommands)  
      time.sleep(122)     
      
      
   return(XC8InstallFolder)
   
############## Update CIF file with new Install path for XC8 ########################################
      
def updateCIFXC8(XC8InstallPath,XC8InstallFolder,XC8Category):   
      
      
   if 'win32' == sys.platform:         
      Fileptr = open("C:/ARBS_SUPPORT/CIF.txt",'a')         
   elif 'linux2' == sys.platform:         
      Fileptr = open("/home/ARBS_SUPPORT/CIF.txt",'a')         
   elif 'darwin' == sys.platform:         
      Fileptr = open("/Users/ARBS_SUPPORT/CIF.txt",'a')
   
   XC8_ver = os.path.split(XC8InstallPath)[1]
   XC8_ver = re.sub("win.exe",'', XC8_ver)
   XC8_ver = re.sub("linux.run",'', XC8_ver)
   
   Temp = "\n" + "XC8;" + XC8InstallPath + ";" + XC8InstallFolder + ";" + XC8_ver + ";" + XC8Category
   
   Fileptr.write(Temp)
   Fileptr.close()

####### XC16 Compiler Comparison - b/w XLS and CI.txt , install and update CIF txt file ##########################################

def XC16CompilerComparison(XC16Category,Compilerpathinfosheet):
   
   PathXC16ReleasedinXLS = ''
   PathXC16ReleasedinCItext = ''
   PathXC16LatestinXLS = ''
   PathXC16LatestinCItext = ''
   PathXC16VersioninXLS = ''
   PathXC16VersioninCItext = ''
   XC16InstalStatus = 1
   XC16InstallPath = ''
   
   CIFfilepath = ''
   
   ##### Get the path of installer #####
   
   if 'win32' == sys.platform:       
      CIFfilepath = "C:\ARBS_SUPPORT\CIF.txt"
      
   elif 'linux2' == sys.platform:   
      CIFfilepath = "/home/ARBS_SUPPORT/CIF.txt"
      
   elif 'darwin' == sys.platform:      
      CIFfilepath = "/Users/ARBS_SUPPORT/CIF.txt"
      
   else:
   
      print " Unsupported platform\n"
      exit()
   
      ################## XC16 RELEASED #############################################################
            
   if XC16Category == "XC16;Released":
      print "The Category of XC16 is Released\n"
      
      ######## Get the path of XC16 Released from XLS #############################################
      
      for RowNumber in range(Compilerpathinfosheet.nrows):
         for ColNumber in range(len(Compilerpathinfosheet.row_values(RowNumber))):
         
            CellValue = DecodeCellInformation(Compilerpathinfosheet.row_values(RowNumber)[ColNumber])
         
            if re.search("XC16;Released;",CellValue):
               PathXC16ReleasedinXLS = re.sub("XC16;Released;","",CellValue)
            
      ####### Get the path of XC16 from CIF.txt and compare with xls path ####################################################

      Fileptr = open(CIFfilepath,'r')   

      XC16InstalStatus = 1
      
      for lines in Fileptr:        
         if re.search("XC16;",lines):
            lines = lines.strip("\n")            
            PathXC16CItext = re.split(";",lines)[1]
            
            if(PathXC16ReleasedinXLS == PathXC16CItext):               
               print "XC16 Installer availabe, Installation not required\n"
               XC16InstalStatus = 0
               break;
      
      ######## If comparison does not match start Installation ###################################
      if XC16InstalStatus == 1:       
      
         print "XC16 Installation required\n"
         XC16InstallPath = PathXC16ReleasedinXLS
         XC16InstallFolder = InstallXC16Compiler(XC16InstallPath,XC16Category)
         updateCIFXC16(XC16InstallPath,XC16InstallFolder,XC16Category)
         print "CIF file updated\n"
         
      
  ################## XC16 Latest #############################################################
      
   if XC16Category == "XC16;Latest":
      print "The Category of XC16 is Latest\n"
      
      ######## Get the path of XC16 Latest from XLS #############################################
      
      for RowNumber in range(Compilerpathinfosheet.nrows):
         for ColNumber in range(len(Compilerpathinfosheet.row_values(RowNumber))):
         
            CellValue = DecodeCellInformation(Compilerpathinfosheet.row_values(RowNumber)[ColNumber])
         
            if re.search("XC16;Latest;",CellValue):
               PathXC16LatestinXLS = re.sub("XC16;Latest;","",CellValue)
            
      ####### Get the path of XC16 from CIF.txt ####################################################

      Fileptr = open(CIFfilepath,'r')   

      XC16InstalStatus = 1
      
      for lines in Fileptr:        
         if re.search("XC16;",lines):
            lines = lines.strip("\n")            
            PathXC16CItext = re.split(";",lines)[1]
                       
            if(PathXC16LatestinXLS == PathXC16CItext):               
               print "XC16 Installer availabe, Installation not required\n"
               XC16InstalStatus = 0
               break;         
      
      
      ######## If comparison does not match start Installation ###################################
      if XC16InstalStatus == 1:       
      
         print "XC16 Installation required\n"
         XC16InstallPath = PathXC16LatestinXLS
         XC16InstallFolder = InstallXC16Compiler(XC16InstallPath,XC16Category)
         updateCIFXC16(XC16InstallPath,XC16InstallFolder,XC16Category)
         print "CIF file updated\n"
    
   ################ XC16 Version ###############################################################
   cmpword = "XC16;Version"
   if cmpword in XC16Category:
   
      print "The Category of XC16 is Version " + XC16Category + "\n"
                        
      ######## Get the path of XC16 Path from XLS #############################################
      
      for RowNumber in range(Compilerpathinfosheet.nrows):
         for ColNumber in range(len(Compilerpathinfosheet.row_values(RowNumber))):
         
            CellValue = DecodeCellInformation(Compilerpathinfosheet.row_values(RowNumber)[ColNumber])
         
            if re.search(XC16Category,CellValue):
               PathXC16VersioninXLS = re.sub(XC16Category,"",CellValue)
               PathXC16VersioninXLS = re.sub(";","",PathXC16VersioninXLS)
                    
                                    
      ####### Get the path of XC16 from CIF.txt ####################################################

      Fileptr = open(CIFfilepath,'r')   

      XC16InstalStatus = 1
      
      for lines in Fileptr:        
         if re.search("XC16;",lines):
            lines = lines.strip("\n")            
            PathXC16CItext = re.split(";",lines)[1]
            
            if(PathXC16VersioninXLS == PathXC16CItext):               
               print "XC16 Installer availabe, Installation not required\n"
               XC16InstalStatus = 0
               break;
      
      ######## If comparison does not match start Installation ###################################
      if XC16InstalStatus == 1:       
      
         print "XC16 Installation required\n"
         XC16InstallPath = PathXC16VersioninXLS
         XC16InstallFolder = InstallXC16Compiler(XC16InstallPath,XC16Category)
         updateCIFXC16(XC16InstallPath,XC16InstallFolder,XC16Category)
         print "CIF file updated\n"
   
   return(XC16InstalStatus)
      
############################## Install XC16 Compiler #####################################

def InstallXC16Compiler(XC16InstallPath,XC16Category):

   XC16Uninstaller_FullPath = ''
   XC16UninstallerCommands = ''
   XC16Installercommands = ''
   XC16InstallerActivationKey = ''
   XC16ActivationKeyPath = "C:/Program Files/Microchip/xclm/bin/xclm.exe"
   XC16ActivationKeyCommands = '"' + XC16ActivationKeyPath + '"' + " " + "-actkey" + " " + "4047-74169-216616-2425" 
     
   if 'win32' == sys.platform:      
              
      ##### Copy installer from Sangam to Installer path on Windows #####
      
      path = "C:\\InstallerPath"
      path = os.path.normpath(path)
      installerpath = ''
   
      if(os.path.exists(path)):
         os.system("rmdir /S /Q " + path)
     
      os.system("mkdir " + '"' + path + '"')   
      copycmd = "copy " + '"' + XC16InstallPath + '"' + " " + '"' + path + '"'    
   
      os.system(copycmd)      
      time.sleep(59)
      
      ##### If category is not Latest, Install in a common folder of that version #####
      if XC16Category != "XC16;Latest":
      
         for root,dirs,files in os.walk(path):
            for filename in files:
               if filename.endswith(".exe"):
                  installerpath = path + "\\" + filename
         
         XC16InstallFolder = ''
         instfold = os.path.split(XC16InstallPath)[1]
         instfold = re.sub('.exe','',instfold)

         XC16InstallFolder = os.path.normpath(os.path.join("C:\\ARBS_SUPPORT\\microchip\\xc16\\", instfold))      
      
      ##### If the category is Latest Install in Latest folder #####
      
      if XC16Category == "XC16;Latest":
      
         for root,dirs,files in os.walk(path):
            for filename in files:
               if filename.endswith(".exe"):
                  installerpath = path + "\\" + filename
         
         XC16InstallFolder = "C:\\ARBS_SUPPORT\\microchip\\xc16\\Latest"
         
         if os.path.exists(XC16InstallFolder):
            os.system("rmdir /S /Q " + XC16InstallFolder)

      
      XC16Installercommands = installerpath + " " + "--mode unattended --unattendedmodeui none --installer-language en --prefix" + " " + '"' + XC16InstallFolder + '"' + " " + "--netservername localhost" + " " + "--ModifyAll 1"
   
      
      ##### Execute Installation #####
      print "\nExecuting Installation"
      os.system(XC16Installercommands)  
      time.sleep(59)      
       
   elif 'linux2' == sys.platform:
         
      ##### Copy installer to local folder #####
      
      path = "/home/ARBS_SUPPORT/temp_installer/"         
   
      if(os.path.exists(path)):
         os.system("rm -rf "+ " " + path)
     
      os.system("mkdir " + " " + path )    
          
      copycmd = "wget -nd -m -P" + " " + path + " " + XC16InstallPath      
      os.system(copycmd)   
      time.sleep(59)
             
      ##### Change installer path to local path in Linux #####
 
      run_path = os.path.split(XC16InstallPath)[1]
      InstallPath = path + run_path

      permission_cmds = "chmod a+x" + " " + InstallPath
      os.system(permission_cmds)
      
      ##### Execute Installation on Linux for XC16 #####
      ##### If category is not Latest, Install in a common folder of that version #####
      
      if XC16Category != "XC16;Latest":
      
         XC16InstallFolder = ''
         instfold = os.path.split(XC16InstallPath)[1]
         instfold = re.sub('.run','',instfold)

         XC16InstallFolder = os.path.normpath(os.path.join("/home/ARBS_SUPPORT/microchip/xc16/", instfold))
         
      if XC16Category == "XC16;Latest":
      
         XC16InstallFolder = "/home/ARBS_SUPPORT/microchip/xc16/Latest"
         
         if os.path.exists(XC16InstallFolder):         
            Cmd = "echo dishan2442 | sudo -S rm -rf" + " " + XC16InstallFolder
            os.system(Cmd)
      
      XC16Installercommands = "echo dishan2442|sudo -S " + " " + InstallPath + " " + "--mode unattended --unattendedmodeui none --installer-language en --prefix" + " " + XC16InstallFolder + " " + "--netservername localhost" + " " + "--ModifyAll 1"
      
      print "\nExecuting Installation"
      os.system(XC16Installercommands)  
      time.sleep(122)
      
   elif 'darwin' == sys.platform:
      
      XC16Uninstaller_Path = "/Applications/microchip/xc16"        

      if os.path.exists(XC16Uninstaller_Path): 
         Cmd = "echo microchip | sudo -S rm -r " + " " + XC16Uninstaller_Path
         os.system(Cmd)
      
      ##### Change installer path to mounted path in Linux by replacing //idc-ws-... to testmount #####
 
      XC16InstallPath = re.sub("//idc-ws-isparbs.microchip.com/compiler_installers/Installers/","/Users/ARBS_SUPPORT/test_mount/Installers/",XC16InstallPath)      
      
      ##### mount and unmount dmg folder to ../current_installer/cur_inst #####
      
      dmg_mount_dir = "/Users/ARBS_SUPPORT/test_mount/current_installer/cur_inst/"
      
      if os.path.exists(dmg_mount_dir):
      
         print "dmg mount folder exists\n"
         unmount_cmd = "umount" + " " + dmg_mount_dir
         os.system(unmount_cmd) 
         
      else: 
      
         print "dmg mount folder does not exists, creating new mount folder\n"
         
         os.system("mkdir /Users/ARBS_SUPPORT/test_mount/current_installer/")
         os.system("mkdir /Users/ARBS_SUPPORT/test_mount/current_installer/cur_inst/")
         
      dmg_mount_cmd = "hdiutil attach -mountpoint" + " " + dmg_mount_dir + " " +  XC16InstallPath
      os.system(dmg_mount_cmd)
      
      installer_availability_status = 0
      path_cur_inst = ""
      XC16InstallPath_Mac = ""
      for root,dirs,files in os.walk(dmg_mount_dir):           
         for i in files:               
            if i == "osx-intel":             
               path_cur_inst = root
               installer_availability_status = 1
               
         
      if installer_availability_status == 1:         
         print "Mac installer available\n"            
      else:         
         print " Mac installer for current category is un available and installation terminated\n"
         exit()
         
      XC16InstallPath_Mac =  path_cur_inst + "/osx-intel"   
                       
      ##### Execute Installation on Mac for XC16 #####         
      
      XC16Installercommands = "sudo" + " " + XC16InstallPath_Mac + " " + "--mode unattended  --unattendedmodeui none --installer-language en --prefix  /Applications/microchip/xc16/ --netservername localhost"
              
      print "\nExecuting Installation"
      os.system(XC16Installercommands)  
      time.sleep(122)     
      
      
   return(XC16InstallFolder)
   
############## Update CIF file with new Install path for XC16 ########################################
      
def updateCIFXC16(XC16InstallPath,XC16InstallFolder,XC16Category):   
      
      
   if 'win32' == sys.platform:         
      Fileptr = open("C:/ARBS_SUPPORT/CIF.txt",'a')         
   elif 'linux2' == sys.platform:         
      Fileptr = open("/home/ARBS_SUPPORT/CIF.txt",'a')         
   elif 'darwin' == sys.platform:         
      Fileptr = open("/Users/ARBS_SUPPORT/CIF.txt",'a')
   
   XC16_ver = os.path.split(XC16InstallPath)[1]
   XC16_ver = re.sub("win.exe",'', XC16_ver)
   XC16_ver = re.sub("linux.run",'', XC16_ver)
   
   Temp = "\n" + "XC16;" + XC16InstallPath + ";" + XC16InstallFolder + ";" + XC16_ver + ";" + XC16Category
   
   Fileptr.write(Temp)
   Fileptr.close()
   
####### XC32 Compiler Comparison - b/w XLS and CI.txt , install and update CIF txt file ##########################################

def XC32CompilerComparison(XC32Category,Compilerpathinfosheet):
   
   PathXC32ReleasedinXLS = ''
   PathXC32ReleasedinCItext = ''
   PathXC32LatestinXLS = ''
   PathXC32LatestinCItext = ''
   PathXC32VersioninXLS = ''
   PathXC32VersioninCItext = ''
   XC32InstalStatus = 1
   XC32InstallPath = ''
   
   CIFfilepath = ''
   
   ##### Get the path of installer #####
   
   if 'win32' == sys.platform:       
      CIFfilepath = "C:\ARBS_SUPPORT\CIF.txt"
      
   elif 'linux2' == sys.platform:   
      CIFfilepath = "/home/ARBS_SUPPORT/CIF.txt"
      
   elif 'darwin' == sys.platform:      
      CIFfilepath = "/Users/ARBS_SUPPORT/CIF.txt"
      
   else:
   
      print " Unsupported platform\n"
      exit()
   
      ################## XC32 RELEASED #############################################################
            
   if XC32Category == "XC32;Released":
      print "The Category of XC32 is Released\n"
      
      ######## Get the path of XC32 Released from XLS #############################################
      
      for RowNumber in range(Compilerpathinfosheet.nrows):
         for ColNumber in range(len(Compilerpathinfosheet.row_values(RowNumber))):
         
            CellValue = DecodeCellInformation(Compilerpathinfosheet.row_values(RowNumber)[ColNumber])
         
            if re.search("XC32;Released;",CellValue):
               PathXC32ReleasedinXLS = re.sub("XC32;Released;","",CellValue)
            
      ####### Get the path of XC32 from CIF.txt and compare with xls path ####################################################

      Fileptr = open(CIFfilepath,'r')   

      XC32InstalStatus = 1
      
      for lines in Fileptr:        
         if re.search("XC32;",lines):
            lines = lines.strip("\n")            
            PathXC32CItext = re.split(";",lines)[1]
            
            if(PathXC32ReleasedinXLS == PathXC32CItext):               
               print "XC32 Installer availabe, Installation not required\n"
               XC32InstalStatus = 0
               break;
      
      ######## If comparison does not match start Installation ###################################
      if XC32InstalStatus == 1:       
      
         print "XC32 Installation required\n"
         XC32InstallPath = PathXC32ReleasedinXLS
         XC32InstallFolder = InstallXC32Compiler(XC32InstallPath,XC32Category)
         updateCIFXC32(XC32InstallPath,XC32InstallFolder,XC32Category)
         print "CIF file updated\n"
         
      
  ################## XC32 Latest #############################################################
      
   if XC32Category == "XC32;Latest":
      print "The Category of XC32 is Latest\n"
      
      ######## Get the path of XC32 Latest from XLS #############################################
      
      for RowNumber in range(Compilerpathinfosheet.nrows):
         for ColNumber in range(len(Compilerpathinfosheet.row_values(RowNumber))):
         
            CellValue = DecodeCellInformation(Compilerpathinfosheet.row_values(RowNumber)[ColNumber])
         
            if re.search("XC32;Latest;",CellValue):
               PathXC32LatestinXLS = re.sub("XC32;Latest;","",CellValue)
            
      ####### Get the path of XC32 from CIF.txt ####################################################

      Fileptr = open(CIFfilepath,'r')   

      XC32InstalStatus = 1
      
      for lines in Fileptr:        
         if re.search("XC32;",lines):
            lines = lines.strip("\n")            
            PathXC32CItext = re.split(";",lines)[1]
                       
            if(PathXC32LatestinXLS == PathXC32CItext):               
               print "XC32 Installer availabe, Installation not required\n"
               XC32InstalStatus = 0
               break;         
      
      
      ######## If comparison does not match start Installation ###################################
      if XC32InstalStatus == 1:       
      
         print "XC32 Installation required\n"
         XC32InstallPath = PathXC32LatestinXLS
         XC32InstallFolder = InstallXC32Compiler(XC32InstallPath,XC32Category)
         updateCIFXC32(XC32InstallPath,XC32InstallFolder,XC32Category)
         print "CIF file updated\n"
    
   ################ XC32 Version ###############################################################
   cmpword = "XC32;Version"
   if cmpword in XC32Category:
   
      print "The Category of XC32 is Version " + XC32Category + "\n"
                        
      ######## Get the path of XC32 Path from XLS #############################################
      
      for RowNumber in range(Compilerpathinfosheet.nrows):
         for ColNumber in range(len(Compilerpathinfosheet.row_values(RowNumber))):
         
            CellValue = DecodeCellInformation(Compilerpathinfosheet.row_values(RowNumber)[ColNumber])
         
            if re.search(XC32Category,CellValue):
               PathXC32VersioninXLS = re.sub(XC32Category,"",CellValue)
               PathXC32VersioninXLS = re.sub(";","",PathXC32VersioninXLS)
                    
                                    
      ####### Get the path of XC32 from CIF.txt ####################################################

      Fileptr = open(CIFfilepath,'r')   

      XC32InstalStatus = 1
      
      for lines in Fileptr:        
         if re.search("XC32;",lines):
            lines = lines.strip("\n")            
            PathXC32CItext = re.split(";",lines)[1]
            
            if(PathXC32VersioninXLS == PathXC32CItext):               
               print "XC32 Installer availabe, Installation not required\n"
               XC32InstalStatus = 0
               break;
      
      ######## If comparison does not match start Installation ###################################
      if XC32InstalStatus == 1:       
      
         print "XC32 Installation required\n"
         XC32InstallPath = PathXC32VersioninXLS
         XC32InstallFolder = InstallXC32Compiler(XC32InstallPath,XC32Category)
         updateCIFXC32(XC32InstallPath,XC32InstallFolder,XC32Category)
         print "CIF file updated\n"
      
   return(XC32InstalStatus)   
############################## Install XC32 Compiler #####################################

def InstallXC32Compiler(XC32InstallPath,XC32Category):

   XC32Uninstaller_FullPath = ''
   XC32UninstallerCommands = ''
   XC32Installercommands = ''
   XC32InstallerActivationKey = ''
   XC32ActivationKeyPath = "C:/Program Files/Microchip/xclm/bin/xclm.exe"
   XC32ActivationKeyCommands = '"' + XC32ActivationKeyPath + '"' + " " + "-actkey" + " " + "4047-74329-232632-2425" 
     
   if 'win32' == sys.platform:      
              
      ##### Copy installer from Sangam to Installer path on Windows #####
      
      path = "C:\\InstallerPath"
      path = os.path.normpath(path)
      installerpath = ''
   
      if(os.path.exists(path)):
         os.system("rmdir /S /Q " + path)
     
      os.system("mkdir " + '"' + path + '"')   
      copycmd = "copy " + '"' + XC32InstallPath + '"' + " " + '"' + path + '"'    
   
      os.system(copycmd)      
      time.sleep(59)
      
      ##### If category is not Latest, Install in a common folder of that version #####
      
      if XC32Category != "XC32;Latest":
      
         for root,dirs,files in os.walk(path):
            for filename in files:
               if filename.endswith(".exe"):
                  installerpath = path + "\\" + filename
         
         XC32InstallFolder = ''
         instfold = os.path.split(XC32InstallPath)[1]
         instfold = re.sub('.exe','',instfold)

         XC32InstallFolder = os.path.normpath(os.path.join("C:\\ARBS_SUPPORT\\microchip\\xc32\\", instfold))

      ##### If the category is Latest Install in Latest folder #####
      
      if XC32Category == "XC32;Latest":
      
         for root,dirs,files in os.walk(path):
            for filename in files:
               if filename.endswith(".exe"):
                  installerpath = path + "\\" + filename
         
         XC32InstallFolder = "C:\\ARBS_SUPPORT\\microchip\\xc32\\Latest"
         
         if os.path.exists(XC32InstallFolder):
            os.system("rmdir /S /Q " + XC32InstallFolder)
         
      XC32Installercommands = installerpath + " " + "--mode unattended --unattendedmodeui none --installer-language en --prefix" + " " + '"' + XC32InstallFolder + '"' + " " + "--netservername localhost" + " " + "--ModifyAll 1"
   
      
      ##### Execute Installation #####
      print "\nExecuting Installation"
      os.system(XC32Installercommands)  
      time.sleep(59)      
       
   elif 'linux2' == sys.platform:
         
      ##### Copy installer to local folder #####
      
      path = "/home/ARBS_SUPPORT/temp_installer/"         
   
      if(os.path.exists(path)):
         os.system("rm -rf "+ " " + path)
     
      os.system("mkdir " + " " + path )    
          
      copycmd = "wget -nd -m -P" + " " + path + " " + XC32InstallPath      
      os.system(copycmd)   
      time.sleep(59)
             
      ##### Change installer path to local path in Linux #####
 
      run_path = os.path.split(XC32InstallPath)[1]
      InstallPath = path + run_path

      permission_cmds = "chmod a+x" + " " + InstallPath
      os.system(permission_cmds)
      
      ##### Execute Installation on Linux for XC32 #####
      
      ##### If category is not Latest, Install in a common folder of that version #####
      
      if XC32Category != "XC32;Latest":

         XC32InstallFolder = ''
         instfold = os.path.split(XC32InstallPath)[1]
         instfold = re.sub('.run','',instfold)

         XC32InstallFolder = os.path.normpath(os.path.join("/home/ARBS_SUPPORT/microchip/xc32/", instfold))
         
      ##### If the category is Latest install in Latest folder #####
      
      if XC32Category == "XC32;Latest":
      
         XC32InstallFolder = "/home/ARBS_SUPPORT/microchip/xc32/Latest"
         if os.path.exists(XC32InstallFolder):         
            Cmd = "echo dishan2442 | sudo -S rm -rf" + " " + XC32InstallFolder
            os.system(Cmd)
      
      XC32Installercommands = "echo dishan2442|sudo -S " + " " + InstallPath + " " + "--mode unattended --unattendedmodeui none --installer-language en --prefix" + " " + XC32InstallFolder + " " + "--netservername localhost" + " " + "--ModifyAll 1"
      
      print "\nExecuting Installation"
      os.system(XC32Installercommands)  
      time.sleep(23)
      
   elif 'darwin' == sys.platform:
      
      XC32Uninstaller_Path = "/Applications/microchip/xc32"        

      if os.path.exists(XC32Uninstaller_Path): 
         Cmd = "echo microchip | sudo -S rm -r " + " " + XC32Uninstaller_Path
         os.system(Cmd)
      
      ##### Change installer path to mounted path in Linux by replacing //idc-ws-... to testmount #####
 
      XC32InstallPath = re.sub("//idc-ws-isparbs.microchip.com/compiler_installers/Installers/","/Users/ARBS_SUPPORT/test_mount/Installers/",XC32InstallPath)      
      
      ##### mount and unmount dmg folder to ../current_installer/cur_inst #####
      
      dmg_mount_dir = "/Users/ARBS_SUPPORT/test_mount/current_installer/cur_inst/"
      
      if os.path.exists(dmg_mount_dir):
      
         print "dmg mount folder exists\n"
         unmount_cmd = "umount" + " " + dmg_mount_dir
         os.system(unmount_cmd) 
         
      else: 
      
         print "dmg mount folder does not exists, creating new mount folder\n"
         
         os.system("mkdir /Users/ARBS_SUPPORT/test_mount/current_installer/")
         os.system("mkdir /Users/ARBS_SUPPORT/test_mount/current_installer/cur_inst/")
         
      dmg_mount_cmd = "hdiutil attach -mountpoint" + " " + dmg_mount_dir + " " +  XC32InstallPath
      os.system(dmg_mount_cmd)
      
      installer_availability_status = 0
      path_cur_inst = ""
      XC32InstallPath_Mac = ""
      for root,dirs,files in os.walk(dmg_mount_dir):           
         for i in files:               
            if i == "osx-intel":             
               path_cur_inst = root
               installer_availability_status = 1
               
         
      if installer_availability_status == 1:         
         print "Mac installer available\n"            
      else:         
         print " Mac installer for current category is un available and installation terminated\n"
         exit()
         
      XC32InstallPath_Mac =  path_cur_inst + "/osx-intel"   
                       
      ##### Execute Installation on Mac for XC32 #####         
      
      XC32Installercommands = "sudo" + " " + XC32InstallPath_Mac + " " + "--mode unattended  --unattendedmodeui none --installer-language en --prefix  /Applications/microchip/xc32/ --netservername localhost"
              
      print "\nExecuting Installation"
      os.system(XC32Installercommands)  
      time.sleep(23)     
      
      
   return(XC32InstallFolder)
   
############## Update CIF file with new Install path for XC32 ########################################
      
def updateCIFXC32(XC32InstallPath,XC32InstallFolder,XC32Category):   
      
      
   if 'win32' == sys.platform:         
      Fileptr = open("C:/ARBS_SUPPORT/CIF.txt",'a')         
   elif 'linux2' == sys.platform:         
      Fileptr = open("/home/ARBS_SUPPORT/CIF.txt",'a')         
   elif 'darwin' == sys.platform:         
      Fileptr = open("/Users/ARBS_SUPPORT/CIF.txt",'a')
   
   XC32_ver = os.path.split(XC32InstallPath)[1]
   XC32_ver = re.sub("win.exe",'', XC32_ver)
   XC32_ver = re.sub("linux.run",'', XC32_ver)
   
   Temp = "\n" + "XC32;" + XC32InstallPath + ";" + XC32InstallFolder + ";" + XC32_ver + ";" + XC32Category
   
   Fileptr.write(Temp)
   Fileptr.close()
   
def GetCategory_mla(softwarecsvfilelocation,comp_name):

   ##### Read Categories from software.csv #####
   
   fptr = open(softwarecsvfilelocation,"r")
      
   XC8Category = ''
   XC16Category = ''
   XC32Category = ''
   
   for line in fptr:
      if re.search("^XC8Category",line):
         temp = re.split(",",line)[1]
         temp = re.sub(" ",'',temp)
         temp = re.sub("\n|\r",'',temp)
         XC8Category = temp
      if re.search("^XC16Category",line):
         temp = re.split(",",line)[1]
         temp = re.sub(" ",'',temp)
         temp = re.sub("\n|\r",'',temp)
         XC16Category = temp
      if re.search("^XC32Category",line):
         temp = re.split(",",line)[1]
         temp = re.sub(" ",'',temp)
         temp = re.sub("\n|\r",'',temp)
         XC32Category = temp            
   
   fptr.close()

   
   ##### Get Compiler info file location  #####

   if 'win32' == sys.platform:
      
      compilerinfofilelocation = "C:/ARBS_SUPPORT/compiler_info/compiler_info_for_auto_installation.xls"
      
      if(os.path.exists(compilerinfofilelocation)):
         print "compiler info file found\n"
         
      else:
         print "compiler info file not found, cannot find categrories, exit\n"
         exit()
      
      WorkBook = open_workbook(compilerinfofilelocation)
      Compilerpathinfosheet = WorkBook.sheet_by_name("Windows") 
      
   elif 'linux2' == sys.platform:                                 
      
      compilerinfofilelocation = "/home/ARBS_SUPPORT/compiler_info/compiler_info_for_auto_installation.xls"
      
      if(os.path.exists(compilerinfofilelocation)):
         print "compiler info file found\n"
         
      else:
         print "compiler info file not found, cannot find categrories, exit\n"
         exit()

      WorkBook = open_workbook(compilerinfofilelocation)
      Compilerpathinfosheet = WorkBook.sheet_by_name("Linux")
      
   elif 'darwin' == sys.platform:  

      compilerinfofilelocation = "/Users/ARBS_SUPPORT/compiler_info/compiler_info_for_auto_installation.xls"
      
      if(os.path.exists(compilerinfofilelocation)):
         print "compiler info file found\n"         
               
      else:
         print "compiler info file not found, cannot find categrories, exit\n"
         exit()      
      
      WorkBook = open_workbook(compilerinfofilelocation)
      Compilerpathinfosheet = WorkBook.sheet_by_name("Mac")
   
   
   if XC8Category != "Not Required" or XC8Category == "":                    
      XC8CompilerComparison(XC8Category,Compilerpathinfosheet)
   
   else:
      print "XC8Category is Not Required\n"
      
   
   if XC16Category != "Not Required" or XC16Category == "":   
      XC16CompilerComparison(XC16Category,Compilerpathinfosheet)
   
   else:
      print "XC16Category is Not Required\n"
   
   if XC32Category != "Not Required" or XC32Category == "":
      XC32CompilerComparison(XC32Category,Compilerpathinfosheet)
   
   else:
      print "XC32Category is Not Required\n"
       

###### MAIN ##############################

if __name__ == "__main__":         
   
   
   ##### Check whether csv file is available in ARBS_WS/projectdir #####
      
   cur_working_dir = os.getcwd()
   
   
   flag_mla = 0
   
   for root,dirs,files in os.walk(cur_working_dir):
      for filename in files:
         if filename.endswith(".csv"):
            if re.search("^arbs_software",filename):
               print "Software.csv file exists\n"
               flag_mla = 1
   
   
   
   if flag_mla == 0:  
   
      ##### Checkout Compiler info file from ARBS SVN #####
      ##### Checkout non isp test input file from ARBS SVN #####
      
      checkout_compiler_info_file()
      checkout_nonisp_test_input_file()

      ##### Create CIF if not present in C:ARBS_SUPPORT folder #####   
   
      createCIF()     
      
      ##### Un Mount and Mount installer path in MAC #####
      
      if 'darwin' == sys.platform:
               
         unmount_path = "/Users/test_mount/Installers"
         if os.path.exists(unmount_path):
            
           print "mount folder exists\n"
           print "un mounting installers folder\n"
           
           os.system("echo microchip | sudo -S umount /Users/test_mount/Installers")
                   
         else:
            
           os.system("echo microchip | sudo -S mkdir /Users/test_mount/Installers")
           print "created test_mount folder\n"
            
         cmds_mount_Mac = "echo microchip | sudo -S mount -t cifs //idc-ws-isparbs.microchip.com/compiler_installers/Installers  /Users/test_mount/Installers -o username=i14552,password=dishanm_2442,domain=mchp-main.com" 
         os.system(cmds_mount_Mac)
            
         if(os.path.exists("/home/test_mount/Installers/Released")):
            print "Mounting successfull\n" 
             
      ##### Get the computer name before installation to read the categories for that computer in the test input file #####
      
      comp_name = sys.argv[1] 
      
      
      ############# Get Categories of all Compilers from test input file ########################################
      
      if 'win32' == sys.platform:
         
         testinputsheetlocation =  "C:/ARBS_SUPPORT/testinputfile/non_isp_arbs_test_input.xls"
         
         if(os.path.exists(testinputsheetlocation)):
            print "test input file found\n"
            
         else:
            print "test input file not found, cannot find categrories, exit\n"
            exit()      
         
      elif 'linux2' == sys.platform:                                 
         
         testinputsheetlocation = "/home/ARBS_SUPPORT/testinputfile/non_isp_arbs_test_input.xls"
         
         if(os.path.exists(testinputsheetlocation)):
            print "test input file found\n"
            
         else:
            print "test input file not found, cannot find categrories, exit\n"
            exit()       
         
      elif 'darwin' == sys.platform:  

         testinputsheetlocation = "/Users/ARBS_SUPPORT/testinputfile/non_isp_arbs_test_input.xls"
         
         if(os.path.exists(testinputsheetlocation)):
            print "test input file found\n"
            
      else:
         print "test input file not found, cannot find categrories, exit\n"
         exit()
      
      
      WorkBook = open_workbook(testinputsheetlocation)
      Compilercategorysheet = WorkBook.sheet_by_name("jobs_input") 
      
      
      GetCategory(Compilercategorysheet,comp_name)
     
   
           
   
   
   
   
         
      
         
   
   
   
   
   