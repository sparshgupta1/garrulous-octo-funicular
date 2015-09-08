import os
import re
import sys


def ExtractCompilerAndDevice(Line):
   
   Compiler = ''
   DevicePrefix = ''
   DeviceList = []
   CompilerKeyword = ''
   Modes = []
   ModeDetectorKwd = []
   
   
   Array = re.split(',',Line)
   
   Count = 0
   
   for ArrayElement in Array:
      if 0 == Count:
         Compiler = ArrayElement
      elif 1 == Count:
         DevicePrefix = ArrayElement
      elif 2 == Count:
         DeviceList = re.split('\|',ArrayElement)
      elif 3 == Count:
         CompilerKeyword = ArrayElement
      elif 4 == Count:
         if not ArrayElement == "NA":
            if re.search("\|",ArrayElement):
               Modes = re.split('\|',ArrayElement)
      elif 5 == Count:
         if not "NA" == ArrayElement:
            array1 = re.split('\|',ArrayElement)
            for i in array1:
               if "NA" == i:
                  ModeDetectorKwd.append('')
               else:
                  ModeDetectorKwd.append(i)
         
      Count = Count + 1

   return(Compiler, DevicePrefix, DeviceList, CompilerKeyword, Modes, ModeDetectorKwd)    
      


#############################################################
#### Extracts the device and compiler information from the 
#### compiler_dev_tools_reference.info file, residing at the
#### the same directory as the Scripts
#############################################################

def GetCompilerDeviceInfo():


   InfoFile = open("compiler_dev_tools_reference.info","r")

   StartCompilerscan = 0

   Compiler = ''
   DevicePrefix = ''
   DevList = []
   CompilerKeyword = ''
   Mode = []
   ModeDetector = []
   
   
   CompilerList = []
   DevicePrefixList = []
   DeviceList = []
   CompilerKeywordList = []
   Modes = []
   ModeDetectorKwd = []
   
   for Line in InfoFile:

      Line = Line.strip("\n|\r")

      if re.search("^_CompilerEnd_",Line):
         StartCompilerscan = 0    

      if 1 == StartCompilerscan:
         Line = Line.upper()
         Line = re.sub(' ','',Line)
         if re.search("^[A-Z]",Line):
            Compiler, DevicePrefix, DevList, CompilerKeyword, Mode, ModeDetector = ExtractCompilerAndDevice(Line)
         
            CompilerList.append(Compiler)
            DevicePrefixList.append(DevicePrefix)
            DeviceList.append(DevList)
            CompilerKeywordList.append(CompilerKeyword)
            Modes.append(Mode)
            ModeDetectorKwd.append(ModeDetector)
            

      if re.search("^_Compiler_",Line):
         StartCompilerscan = 1


   InfoFile.close()
   
   return(CompilerList, DevicePrefixList, DeviceList, CompilerKeywordList, Modes, ModeDetectorKwd)
   
#############################################################
#### Extracts the Hardware Tool information from the supplied
#### parameters..
#############################################################

def GetHWTools():
   
   InfoFile = open("compiler_dev_tools_reference.info","r")

   StartScan = 0
   
   ToolsList = []
  
   for Line in InfoFile:
      
      Line = Line.strip("\n|\r")
      
      if re.search("^_HWToolEnd_",Line):
         StartScan = 0
         
      if 1 == StartScan:
         
         Line = Line.upper()
         
         if re.search("^[A-Z]",Line):
            ToolsList.append(Line)
         
      if re.search("^_HWTool_",Line):
         StartScan = 1

   InfoFile.close()
   
   return(ToolsList)   
   
   


#############################################################
#### Extracts the information from the supplied
#### parameters..
#############################################################


def ExtractParameters(Parameters):

   CompilerList = []
   DevicePrefix = []
   DeviceList = []
   CompilerKeywordList = []
   Modes = []
   ModeDetectorKwd = []

   Error = 0
   DeviceError = 0  
   # Return Parameters
   
   P1_INDevice = ''
   P1_INCompiler = ''
   P1_RT_Test_HW_Tool = "NA"
   P1_BuildNumber = ''
   P1_BuildURL = ''
   ProjectArguments = []
   
   for Argument in Parameters:
      if re.search("^(http|https)",Argument.lower()):
         ProjectArguments.append(Argument)
      else:
         ProjectArguments.append(Argument.upper())
      
   # Get the parameters from the info file.
   
   CompilerList, DevicePrefixList, DeviceList, CompilerKeywordList, Modes, ModeDetectorKwd = GetCompilerDeviceInfo()
   
   Found = 0
   
   # Finding the Supplied Compiler
   
   for Compiler in CompilerList:
      for Argument in ProjectArguments:
         if Argument.upper() == Compiler:
            P1_INCompiler = Compiler
            Found = 1
            ProjectArguments.remove(Argument)
            break
      if 1 == Found:
         break
            
   
   # Finding the Supplied device
   
   
   Found = 0
   for LineNumber in range(len(DeviceList)):
      for Device in DeviceList[LineNumber]:
         for Arg in ProjectArguments:
            if re.search(Device,Arg) and not re.search(r"/|\\",Arg.lower()):
               if re.search("^" + Device,Arg):
                  P1_INDevice = Arg
                  ProjectArguments.remove(Arg)
                  Found = 1
                  break
               else:
                  if re.search("^" + DevicePrefixList[LineNumber], Arg):
                     P1_INDevice = re.sub(DevicePrefixList[LineNumber],'',Arg)
                     ProjectArguments.remove(Arg)
                     Found = 1
                     break
                  else:
                     DeviceError = 1
         if 1 == Found:
            break
            
      if 1 == Found:
         break
         
   ###### Finding HW Tool ##########
   
   HwToolsList = GetHWTools()
   
   Found = 0
   for Argument in ProjectArguments:
      P1_RT_Test_HW_Tool = "NA"

      for HwTool in HwToolsList:
         if Argument == HwTool or "NA" == Argument:
            P1_RT_Test_HW_Tool = Argument
            ProjectArguments.remove(Argument)
            Found = 1
            break

      if 1 == Found:
         break
   
   # Finding Build Number #
   
   for Argument in ProjectArguments:
      if re.search("^[0-9]",str(Argument)) and not re.search("[a-z]",str(Argument).lower()):
         P1_BuildNumber = Argument
         ProjectArguments.remove(Argument)
         break
   
   # Finding Build URL #
   
   for Argument in ProjectArguments:
      if re.search("^(http|https)",Argument.lower()):
         P1_BuildURL = Argument  
         ProjectArguments.remove(Argument)
         break
   
         
   if 1 == DeviceError:
      Error = 1
   
   elif not [] == ProjectArguments:
      Error = 2
      print "\nUnknown Options Encountered\n"
      print ProjectArguments
      
   return(Error, P1_INDevice, P1_INCompiler, P1_RT_Test_HW_Tool, P1_BuildNumber, P1_BuildURL)
   
   
   
   
   