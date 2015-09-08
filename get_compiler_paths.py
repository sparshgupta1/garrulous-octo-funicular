import os
import sys
import re
import shutil
import time
from collections import namedtuple
from xlrd import open_workbook 

import compiler_web_parser

################################################################
# This Module Decodes the Floating Point numbers stored in the 
# Spreadsheet Cell. It ignores the unicode characters, if any 
# in the cell and converts into ASCII string
################################################################

def DecodeCellInformation(CellInfo):
   
   ReturnData = ''
      
   if isinstance(CellInfo,float):
   
      ReturnData = str(int(CellInfo))
      
   else:
   
      ReturnData = CellInfo.encode('ascii','ignore')   
   
   return(ReturnData.strip(" "))
   
def obtain_latest_svn_message(xc16Category):
   if 'LatestReleaseWithDailyPartSupport' in xc16Category or 'LastReleaseWithDailyPartSupport' in xc16Category:      
      if 'win32' == sys.platform:
         SVNLogFile = 'C:/ARBS_SUPPORT/svnLogForDPS.txt'
      elif'linux2' == sys.platform:                                 # Linux
         SVNLogFile = '/home/ARBS_SUPPORT/svnLogForDPS.txt'
      elif 'darwin' == sys.platform:                                 # MAC 
         SVNLogFile = '/Users/ARBS_SUPPORT/svnLogForDPS.txt'
      else:
        print 'Operating System not supported.'
        sys.exit(201)
      if os.path.isfile(SVNLogFile):
         Fileptr = open(SVNLogFile, 'r')
         AllLogLines = []
         AllLogLines = Fileptr.readlines()
         Fileptr.close()

         try:
            dps_with_xc16Category = filter(lambda x:(xc16Category in ((x.split(':')[0]).split('@')[0])),AllLogLines)
            dps_with_xc16Category = sorted(dps_with_xc16Category, key=lambda x:((x.split(':')[0]).split('@')[1]),reverse=True)
            return (dps_with_xc16Category[0][dps_with_xc16Category[0].rfind(':')+1:]).strip()
         except Exception, e:
            print e
            return 'ERROR_OBTAINING_SVN_MESSAGE'
      else:
         print '%s not created, verify that dailypartsupport installation was done successfully or not' %(SVNLogFile)
         return 'VERIFY_DAILYPARTSUPPORT_INSTALLATION_LOGFILE_NOT_PRESENT'
   else:
      print 'SVN message should be obtained for dailypartsupport categories only.'
      return ''   
   
def reconstruct_svn_path(Link):
   return_link = ""
   
   temp = re.sub(r"\\", "/", Link)
   temp = re.sub("//", "/", temp)
   
   temp1 = re.split("/", temp)
   for item in temp1:
      if item != '':
         return_link = return_link + item + "/"
   
   return_link = return_link.strip("/")
   if re.search(":/[a-z|A-Z]", return_link):
      return_link = re.sub(":/", "://", return_link)
      
   return(return_link)
   
   
   

spreadsheet_svn_link = "https://idc-dk-dev-sys2.mchp-main.com:8443/svn/ARBS/non_isp_test_input/"   

if len(sys.argv) > 1:
   spreadsheet_svn_link = reconstruct_svn_path(sys.argv[1])

current_file_path = sys.argv[0]

new_path = os.path.split(current_file_path)[0]

if new_path != '':
   os.chdir(new_path)
   
   
   
current_job_name = os.environ['JOB_NAME']
current_job_name = re.split(r"/|\\",current_job_name)[0]

if current_job_name == "__MLA__":
   test_input_XLSheetLocation = "csvfile/tempDir/arbs_software.csv"
else:  
   test_input_XLSheetLocation = "non_isp_test_input/tempDir/non_isp_arbs_test_input.xls"
   
cif_spreadsheet_location = "compiler_info_file/tempDir/compiler_info_for_auto_installation.xls"



##############################################
# Checkout both the SS
##############################################
if current_job_name != "__MLA__":
   
   if os.path.exists(test_input_XLSheetLocation):
      os.remove(test_input_XLSheetLocation)
      
   SVNLink = spreadsheet_svn_link  
   Command = "svn co " + '"' +  SVNLink + '"' + ' "' + os.path.join(os.path.sep,os.getcwd(),'non_isp_test_input','tempDir') + '"' + " --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"

   os.system(Command)

if os.path.exists(cif_spreadsheet_location):
   os.remove(cif_spreadsheet_location)
   
SVNLink = "https://idc-dk-dev-sys2.mchp-main.com:8443/svn/ARBS/CompilerInstallationTest/compiler_info_file/"
Command = "svn co " + '"' +  SVNLink + '"' + ' "' + os.path.join(os.path.sep,os.getcwd(),'compiler_info_file','tempDir') + '"' + " --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"

os.system(Command)
##############################################
##############################################
##############################################

spreadsheet_index = 0

cif_text_file_location = ''
if 'win32' == sys.platform:
   spreadsheet_index = 0
   cif_text_file_location = "C:/ARBS_SUPPORT/CIF.txt"
   iif_text_file_location = "C:/ARBS_SUPPORT/iif.txt" 
elif'linux2' == sys.platform:                                 # Linux
   spreadsheet_index = 1
   cif_text_file_location = "/home/ARBS_SUPPORT/CIF.txt"
   iif_text_file_location = "/home/ARBS_SUPPORT/iif.txt"  
elif 'darwin' == sys.platform:                                 # MAC 
   spreadsheet_index = 2
   cif_text_file_location = "/Users/ARBS_SUPPORT/CIF.txt"
   iif_text_file_location = "/Users/ARBS_SUPPORT/iif.txt" 

local_mcpr_file = os.path.join(os.getcwd(),"mcpr_modified.mcpr")
if os.path.exists(local_mcpr_file):
   os.remove(local_mcpr_file)

if (os.path.exists(test_input_XLSheetLocation) and os.path.exists(cif_spreadsheet_location) and 
   os.path.exists(cif_text_file_location)):

   ti_job_names = []
   ti_build_computer_names = []
   ti_xc8_compiler_cat = []
   ti_xc16_compiler_cat = []
   ti_xc32_compiler_cat = []
   dict_mplabx_ide_cat_wrt_job = {}
      
   if current_job_name == "__MLA__":
   
      fptr = open(test_input_XLSheetLocation,"r")
      
      xc8_cat = ''
      xc16_cat = ''
      xc32_cat = ''
      
      for line in fptr:
         if re.search("^XC8Category",line) and len(re.split(",",line)) >= 2:
            temp = re.split(",",line)[1]
            temp = re.sub(" ",'',temp)
            temp = re.sub("\n|\r",'',temp)
            xc8_cat = temp
         if re.search("^XC16Category",line) and len(re.split(",",line)) >= 2:
            temp = re.split(",",line)[1]
            temp = re.sub(" ",'',temp)
            temp = re.sub("\n|\r",'',temp)
            xc16_cat = temp
         if re.search("^XC32Category",line) and len(re.split(",",line)) >= 2:
            temp = re.split(",",line)[1]
            temp = re.sub(" ",'',temp)
            temp = re.sub("\n|\r",'',temp)
            xc32_cat = temp            
      
      fptr.close()
      
      ti_job_names.append(current_job_name)
      ti_build_computer_names.append("")
      ti_xc8_compiler_cat.append(xc8_cat)
      ti_xc16_compiler_cat.append(xc16_cat)
      ti_xc32_compiler_cat.append(xc32_cat)
      
   else:
   
      WorkBook = open_workbook(test_input_XLSheetLocation)
      FirstSheet = WorkBook.sheet_by_index(0)

      NoOfRows = FirstSheet.nrows

      for i in range(FirstSheet.nrows):
         if i >= 5:
            if DecodeCellInformation(FirstSheet.row_values(i)[0]) != '' and DecodeCellInformation(FirstSheet.row_values(i)[5]) != '':
               job_name = DecodeCellInformation(FirstSheet.row_values(i)[0])
               job_name = job_name.strip(" ")
               job_name = re.sub(" ","_",job_name)
               ti_job_names.append(job_name)
               ti_build_computer_names.append(DecodeCellInformation(FirstSheet.row_values(i)[5]))
               ti_xc8_compiler_cat.append(DecodeCellInformation(FirstSheet.row_values(i)[7]))
               ti_xc16_compiler_cat.append(DecodeCellInformation(FirstSheet.row_values(i)[8]))
               ti_xc32_compiler_cat.append(DecodeCellInformation(FirstSheet.row_values(i)[9]))
               dict_mplabx_ide_cat_wrt_job[job_name] = DecodeCellInformation(FirstSheet.row_values(i)[21])

   ################################################################
   ################################################################
   WorkBook = open_workbook(cif_spreadsheet_location)
   FirstSheet = WorkBook.sheet_by_index(spreadsheet_index)

   NoOfRows = FirstSheet.nrows

   cif_all_installer_paths = []

   for i in range(FirstSheet.nrows):
      if i >= 9:
         if DecodeCellInformation(FirstSheet.row_values(i)[0]) != '':
            cif_all_installer_paths.append(DecodeCellInformation(FirstSheet.row_values(i)[0]))   

   ide_category = None

   xc8_installer_path = ''
   xc16_installer_path = ''
   xc32_installer_path = ''

   xc8_compiler_path = ''
   xc16_compiler_path = ''
   xc32_compiler_path = ''
   ide_installation_path = ''

   xc8_compiler_version = ''
   xc16_compiler_version = ''
   xc32_compiler_version = ''
   ide_installation_version = ''

   for i in range(len(ti_job_names)):
      if ti_job_names[i] == current_job_name:
         if 'LastReleaseWithPartSupport' in ti_xc16_compiler_cat[i] \
                or 'LastMajorRelease' in ti_xc16_compiler_cat[i] \
                or 'LatestMajorRelease' in ti_xc16_compiler_cat[i] \
                or 'LastReleaseWithDailyPartSupport' \
                in ti_xc16_compiler_cat[i] \
                or 'LatestReleaseWithDailyPartSupport' \
                in ti_xc16_compiler_cat[i]:
                xc16_installer_path = compiler_web_parser.ParseWebPageAndObtainUrl(compilerType='xc16',programCategory=ti_xc16_compiler_cat[i].split(';')[1],os=sys.platform)[-1]            
                xc16_installer_path = ti_xc16_compiler_cat[i] + ';' + xc16_installer_path
         for installer_path in cif_all_installer_paths:
            if re.search("^" + ti_xc8_compiler_cat[i].lower(), installer_path.lower()) and ti_xc8_compiler_cat[i] != '':
               xc8_installer_path = installer_path
            if re.search("^" + ti_xc16_compiler_cat[i].lower(), installer_path.lower()) and ti_xc16_compiler_cat[i] != '':
               if (ti_xc16_compiler_cat[i].lower() == 'xc16;'+installer_path.split(';')[1].lower()):
                  xc16_installer_path = installer_path
            if re.search("^" + ti_xc32_compiler_cat[i].lower(), installer_path.lower()) and ti_xc32_compiler_cat[i] != '':
               xc32_installer_path = installer_path            

         if ti_job_names[i] in dict_mplabx_ide_cat_wrt_job:
            ide_category = dict_mplabx_ide_cat_wrt_job[ti_job_names[i]]




   ###################################################
   # Get Data from Local CIF Text File
   ###################################################
   cif_text_file_data = []

   shutil.copy(cif_text_file_location, os.getcwd()) 

   cif_local_text_file = os.path.split(cif_text_file_location)[1]

   cif_text_file_ptr = open(cif_local_text_file,"r")
   print xc8_installer_path, "\n\n"
   
   for line in cif_text_file_ptr:
   
      line = re.sub("\n|\r",'',line)
      line = line.strip(" ")

      cif_text_file_data.append(line)
      ###################################################
      # For XC8
      ###################################################
      if re.search("^XC8;",line):
         array = re.split(";",line)
         if len(array) >= 4 and len(re.split(";",xc8_installer_path)) == 3:
            if array[1] == re.split(";",xc8_installer_path)[2]:
               xc8_compiler_path = array[2]
               xc8_compiler_version = array[3]
      ###################################################
      # For XC16
      ###################################################
      if re.search("^XC16;",line):
         array = re.split(";",line)
         if len(array) >= 4  and len(re.split(";",xc16_installer_path)) == 3:
            if (array[1] == re.split(";",xc16_installer_path)[2]) and (';'.join(array[-2:]) == ';'.join(xc16_installer_path.split(';')[:2])):
               xc16_compiler_path = array[2]
               if 'LastReleaseWithPartSupport' \
                        in xc16_installer_path.split(';')[1] \
                        or 'LastMajorRelease' \
                        in xc16_installer_path.split(';')[1] \
                        or 'LatestMajorRelease' \
                        in xc16_installer_path.split(';')[1] \
                        or 'LastReleaseWithDailyPartSupport' \
                        in xc16_installer_path.split(';')[1] \
                        or 'LatestReleaseWithDailyPartSupport' \
                        in xc16_installer_path.split(';')[1]:
                        if 'LastReleaseWithDailyPartSupport' \
                        in xc16_installer_path.split(';')[1] \
                        or 'LatestReleaseWithDailyPartSupport' \
                        in xc16_installer_path.split(';')[1]:
                           svnMessage = obtain_latest_svn_message(xc16_installer_path.split(';')[1])
                           xc16_compiler_version = array[3] + '#' + xc16_installer_path.split(';')[1] + '#' +svnMessage
                        else:
                           xc16_compiler_version = array[3] + '#' + xc16_installer_path.split(';')[1]
               else:
                  xc16_compiler_version = array[3]
      ###################################################
      # For XC32
      ###################################################   
      if re.search("^XC32;",line):
         array = re.split(";",line)
         if len(array) >= 4  and len(re.split(";",xc32_installer_path)) == 3:
            if array[1] == re.split(";",xc32_installer_path)[2]:
               xc32_compiler_path = array[2]
               xc32_compiler_version = array[3]


   cif_text_file_ptr.close()

   os.remove(cif_local_text_file)

   MPLABXIDEInformation = namedtuple('MPLABXIDEInformation', ['Location','Version'])


   if os.path.exists(iif_text_file_location):      
      if (ide_category != None):
         ###################################################
         # Get Data from Local IIF Text File
         ###################################################
         iif_text_file_data = []
         shutil.copy(iif_text_file_location, os.getcwd()) 
         iif_local_text_file = os.path.split(iif_text_file_location)[1]

         iif_text_file_ptr = open(iif_local_text_file,"r")
         for line in iif_text_file_ptr:
            line = re.sub("\n|\r",'',line)
            line = line.strip(" ")
            if (line == ''):
               continue

            if len((line.split(':')[1]).split(';')) >= 3 :
               array = (line.split(':')[1]).split(';')
               if (array[-1] == ide_category):
                  if (os.path.exists(array[0])):
                     iif_text_file_data.append(MPLABXIDEInformation(Location=array[0],Version=array[1]))

         if (len(iif_text_file_data) != 0):
            iif_text_file_data = sorted(iif_text_file_data,reverse = True,key=lambda x: x.Version)
            ide_installation_path = iif_text_file_data[0].Location
            ide_installation_version = iif_text_file_data[0].Version

         iif_text_file_ptr.close()

         os.remove(iif_local_text_file)



   ########################################################
   # Copy mcpr file to local ARBS_SUPPORT dir
   ########################################################

   arbs_support_mcpr_file = ''
   if 'win32' == sys.platform:
      arbs_support_mcpr_file = "C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr" 
   elif'linux2' == sys.platform:                                 # Linux
      arbs_support_mcpr_file = "/home/ARBS_SUPPORT/LIN_ToolSuiteLocations.mcpr" 
   elif 'darwin' == sys.platform:                                 # MAC 
      arbs_support_mcpr_file = "/Users/ARBS_SUPPORT/MAC_ToolSuiteLocations.mcpr"



   local_mcpr_file = os.path.join(os.getcwd(),"mcpr_modified.mcpr")
   shutil.copy(arbs_support_mcpr_file, local_mcpr_file) 

   if xc8_compiler_path != '':

      fptr = open(local_mcpr_file,"r")
      lines_array = []
      for line in fptr:
         line = re.sub("\n|\r","",line)
         if re.search("^_XC8_PATH_=",line):
            line = "_XC8_PATH_=" + xc8_compiler_path
         if re.search("^_XC8_VER_=",line):
            line = "_XC8_VER_=" + xc8_compiler_version
         lines_array.append(line)

      fptr.close()

      fptr = open(local_mcpr_file,"w")

      for line in lines_array:

         fptr.write(line + "\n")

      fptr.close()

   if xc16_compiler_path != '':

      fptr = open(local_mcpr_file,"r")
      lines_array = []
      for line in fptr:
         line = re.sub("\n|\r","",line)
         if re.search("^_XC16_PATH_=",line):
            line = "_XC16_PATH_=" + xc16_compiler_path
         if re.search("^_XC16_VER_=",line):
            line = "_XC16_VER_=" + xc16_compiler_version
         lines_array.append(line)

      fptr.close()

      fptr = open(local_mcpr_file,"w")

      for line in lines_array:

         fptr.write(line + "\n")

      fptr.close()


   if xc32_compiler_path != '':

      fptr = open(local_mcpr_file,"r")
      lines_array = []
      for line in fptr:
         line = re.sub("\n|\r","",line)
         if re.search("^_XC32_PATH_=",line):
            line = "_XC32_PATH_=" + xc32_compiler_path
         if re.search("^_XC32_VER_=",line):
            line = "_XC32_VER_=" + xc32_compiler_version
         lines_array.append(line)

      fptr.close()

      fptr = open(local_mcpr_file,"w")

      for line in lines_array:

         fptr.write(line + "\n")

      fptr.close()

   if ide_installation_path != '':

      fptr = open(local_mcpr_file,"r")
      lines_array = []
      for line in fptr:
         line = re.sub("\n|\r","",line)
         if re.search("^_MPLAB_X_INSTALLATION_PATH_=",line):
            line = "_MPLAB_X_INSTALLATION_PATH_=" + ide_installation_path
         if re.search("^_MPLAB_X_VER_=",line):
            line = "_MPLAB_X_VER_=" + ide_installation_version
         lines_array.append(line)

      fptr.close()

      fptr = open(local_mcpr_file,"w")

      for line in lines_array:

         fptr.write(line + "\n")

      fptr.close()      


if os.path.exists(os.path.split(test_input_XLSheetLocation)[0]):
   shutil.rmtree(os.path.split(test_input_XLSheetLocation)[0],"true")

if os.path.exists(os.path.split(cif_spreadsheet_location)[0]):
   shutil.rmtree(os.path.split(cif_spreadsheet_location)[0],"true")



   '''

   command = "java -jar idc_ws_isparbs_hudson-cli.jar -s http://idc-ws-isparbs.mchp-main.com:8080/ offline-node chn-vm-arbslnx --username AutoJobCreator --password AutoJobCreator"

   os.system(command)

   i = 300

   while i >= 0:
      time.sleep(1)
      i = i-1
      print i

   command = "java -jar idc_ws_isparbs_hudson-cli.jar -s http://idc-ws-isparbs.mchp-main.com:8080/ online-node chn-vm-arbslnx --username AutoJobCreator --password AutoJobCreator"

   os.system(command)


   '''
