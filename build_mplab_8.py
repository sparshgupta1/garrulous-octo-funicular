from __future__ import division
import os
import sys
import re
import stat
import shutil        # For Performing operations on Directories
import subprocess
import time
import stat
import picc_options   # picc_options.Extract
import client_status

##################################

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
   
   
#########################################

def BuildCommand(Command,LogFile,McpFileName,SourceFileName):
   
   
   McpFileNameOnly = os.path.split(McpFileName)[1]
   McpFileNameOnly = os.path.splitext(McpFileNameOnly)[0]
   SrcFileNameOnly = os.path.split(SourceFileName)[1]
   SrcFileNameOnly = os.path.splitext(SrcFileNameOnly)[0]
   
   BatchFileName = McpFileNameOnly + "_" + SrcFileNameOnly + ".bat"
   
   BatFile = open(BatchFileName,'w')
   BatFile.write(Command)
   BatFile.close()

   '''
   LogFilePtr = open(LogFile,'a')
   LogFilePtr.write("\nARBS_EXECUTING_COMMAND: " + Command + "\n")
   LogFilePtr.close()
   '''
   Process1 = subprocess.Popen('"' + BatchFileName + '"')
   TimeoutCounter = 0
   
   ForceExitDetected = 0
   
   OldLineCount = 0
   NewLineCount = 0
      
   while(Process1.poll() == None): 
   
      time.sleep(1)
      TimeoutCounter = TimeoutCounter + 1
      
      NewLineCount = GetNumberOfLines(LogFile)

      if NewLineCount != OldLineCount:
         OldLineCount = NewLineCount
         TimeoutCounter = 0
            
      if TimeoutCounter >= 300:              # Maximum Timeout is 300 Seconds to exit the Command
         
         ForceExitDetected = 1
         print "\n\nARBS_Info: Trying to kill the hanged process and its children processes\n\n"
         TimeoutCounter = 0
         os.system("taskkill /PID " + str(Process1.pid) + " /F /T")
         time.sleep(1)

   if ForceExitDetected == 1:
   
      LogFilePtr = open(LogFile,'a')
      LogFilePtr.write("\nExitStatus: 1\nHang Detected\n")
      LogFilePtr.close()

   #os.remove(BatchFileName)  

   
##################################


def FindCompiler(McpFile):
   McpFilePtr = open(McpFile,"r")
   Compiler = ''
   
   PIC18FDeviceDetected = 0
   
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r")
      
      if re.search("^device=PIC18", Line):
         PIC18FDeviceDetected = 1
         
      if re.search("suite_guid=",Line):
      
         if re.search("\{5B7D72DD-9861-47BD-9F60-2BE967BF8416\}",Line):
            Compiler = "C18"
            break

         if re.search("\{479DDE59-4D56-455E-855E-FFF59A3DB57E\}",Line):
            Compiler = "C30"
            break         

         if re.search("\{14495C23-81F8-43F3-8A44-859C583D7760\}",Line):
            Compiler = "C32"
            break 

         '''                           ## No Support for XC8 Compiler, as the MCP file is not in decodable state. Will add support, once it is got.
         if re.search("\{507D93FD-16F1-4270-980F-0C7C0207E6D3\}",Line):
            Compiler = "XC8"
            break 
         '''
         
         if re.search("\{9BCCB495-CD65-480A-BA76-63D8E78B117F\}",Line):
            Compiler = "XC16"
            break 
            
         if re.search("\{62D235D8-2DB2-49CD-AF24-5489A6015337\}",Line):
            Compiler = "XC32"
            break 

         if re.search("\{507D93FD-16F1-4270-980F-0C7C0207E6D3\}",Line):
            if PIC18FDeviceDetected == 0:
               Compiler = "PICC"
            else:
               Compiler = "PICC18"
            break 

         if re.search("\{38171385-97B2-4EC5-BF2C-C2C027BA5B04\}",Line):
            Compiler = "XC8"
            break 
            
   McpFilePtr.close()
   
   return(Compiler)
   
##################################   
   
def FindDevice(McpFile):

   McpFilePtr = open(McpFile,"r")
   Device = ''
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r") 
      
      if re.search("device=",Line):
      
         Device = re.split("device=",Line)[1]
         break 
 
   McpFilePtr.close()
   
   return(Device)
   
#################################
def PrintExecutingCommandToLogFile(LogFile, Command):

   LogFilePtr = open(LogFile,'a')
   LogFilePtr.write("\n_EXECUTING_COMMAND_: " + Command + "\n\n\n")
   LogFilePtr.close()
   

def AddMessage(Message,LogFile):
   LogFilePtr = open(LogFile,'a')
   LogFilePtr.write(Message)
   LogFilePtr.close()
   
def AddLoggingOption(LogFile):
   Command = " >> " + '"' + LogFile + '"' " 2>&1\n"
   return(Command)
   
#################################

def PrintExitCode(LogFile):
   Command = "\necho ExitStatus: %ERRORLEVEL%" + AddLoggingOption(LogFile) + "\n"
   return(Command)

#################################
def ExtractMcpFileNameFromPath(McpFile):
   return(os.path.splitext(os.path.split(McpFile)[1])[0])
#################################

def FindSrcFiles(McpFile):

   StartOtherFileScan = 0
   StartGettingFiles = 0
   
   Count = 0
   
   OtherFileTag = []
   Files = []
   FileNumber = []
   
   McpFilePtr = open(McpFile,"r")
   
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r")

      if re.search("SUITE_INFO",Line):
         StartGettingFiles = 0
         break
      if StartGettingFiles == 1:
         if OtherFileTag[Count] == "no":
            Files.append(Line[9:])
            FileNumber.append(Line[5:8])
         Count = Count + 1
      if re.search("\[FILE_INFO\]",Line):
         StartOtherFileScan = 0
         StartGettingFiles = 1
         Count = 0
      if StartOtherFileScan == 1:
         OtherFileTag.append(Line[9:])
      if re.search("\[OTHER_FILES\]",Line):
         StartOtherFileScan = 1
   
   McpFilePtr.close()
   
   return(Files,FileNumber)


###################################

def GetFiles(McpFile):
   SrcFilesExtn = []
   HeaderFilesExtn = []
   ObjFilesExtn = []
   LibFilesExtn = []
   LkrFilesExtn = []
   
   SrcFileList = []
   SrcFileTag = []
   HeaderFileList = []
   ObjFileList = []
   LibFileList = []
   LkrFileList = []
   
   SrcFiles = []
   
   StartScan = 0
   McpFilePtr = open(McpFile,'r')
   
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r")
      
      if re.search("\[CAT_SUBFOLDERS\]",Line):
         StartScan = 0   

      if StartScan == 1:
         if re.search("filter_src",Line):
            SrcFilesExtn = re.split(';',re.sub("\*",'',re.split("=",Line)[1]))
         if re.search("filter_inc",Line):
            HeaderFilesExtn = re.split(';',re.sub("\*",'',re.split("=",Line)[1]))
         if re.search("filter_obj",Line):
            ObjFilesExtn = re.split(';',re.sub("\*",'',re.split("=",Line)[1]))
         if re.search("filter_lib",Line):
            LibFilesExtn = re.split(';',re.sub("\*",'',re.split("=",Line)[1]))
         if re.search("filter_lkr",Line):
            LkrFilesExtn = re.split(';',re.sub("\*",'',re.split("=",Line)[1]))

      if re.search("\[CAT_FILTERS\]",Line):
         StartScan = 1
   
   McpFilePtr.close()
   
   SrcFiles,FileNumber = FindSrcFiles(McpFile)
   
   Count = 0
   FileNumberR = []
   for FileName in SrcFiles:
      
      Count = Count + 1
      
      for SrcExtn in SrcFilesExtn:
         if FileName.endswith(SrcExtn.upper()) or FileName.endswith(SrcExtn.lower()):
            SrcFileList.append(FileName)
            FileNumberR.append(FileNumber[Count - 1])
      for HdrExtn in HeaderFilesExtn:
         if FileName.endswith(HdrExtn.upper()) or FileName.endswith(HdrExtn.lower()):
            HeaderFileList.append(FileName)
            
      for ObjExtn in ObjFilesExtn:
         if FileName.endswith(ObjExtn.upper()) or FileName.endswith(ObjExtn.lower()):
            ObjFileList.append(FileName)

      for LibExtn in LibFilesExtn:
         if FileName.endswith(LibExtn.upper()) or FileName.endswith(LibExtn.lower()):
            LibFileList.append(FileName)

      for LkrExtn in LkrFilesExtn:
         if FileName.endswith(LkrExtn.upper()) or FileName.endswith(LkrExtn.lower()):
            LkrFileList.append(FileName)
            
            
   return(SrcFileList,FileNumberR,HeaderFileList,ObjFileList,LibFileList,LkrFileList)
   
####################################

def GetDirs(McpFile):
   
   TempDir = os.path.normpath(os.path.split(McpFile)[0])
   
   IncludeDirList = []
   IncludeDirListASM = []
   LibDirList = []
   LkrDirList = []


   McpFilePtr = open(McpFile,'r')
   
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r")
      
      if re.search("dir_tmp=",Line):
         TempDir = re.split("=",Line)[1]
         TempDir = os.path.normpath(os.path.join(os.path.split(McpFile)[0],TempDir))

      if re.search("dir_inc=",Line):
         TempDir1 = re.split("=",Line)[1] 
         if not TempDir1 == '':
            IncludeDirList = re.split(';',TempDir1)

      if re.search("dir_sin=",Line):
         TempDir1 = re.split("=",Line)[1] 
         if not TempDir1 == '':
            IncludeDirListASM = re.split(';',TempDir1)

      if re.search("dir_lib=",Line):
         TempDir1 = re.split("=",Line)[1]
         if not TempDir1 == '':
            LibDirList = re.split(';',TempDir1)
            
      if re.search("dir_lkr=",Line):
         TempDir1 = re.split("=",Line)[1]
         if not TempDir1 == '':
            LkrDirList = re.split(';',TempDir1)            
            
   McpFilePtr.close()

   return(TempDir,IncludeDirList,IncludeDirListASM,LibDirList,LkrDirList)
   
#################################################
   
def GetCommand(Line):

   Command = ''
   TempLine = ''
   
   #if ACTIVE_FILE_SETTINGS == 0:
      
   if re.search("}=",Line):
      Command = re.split("}=",Line)[1]
   
   #else:      
   #
   #   for j in ACTIVE_FILE_SETTINGSArray:
   #      k = re.split("}[0-9][0-9][0-9]_active=yes",j)[0]
   #      if re.search(k,Line):
   #         
   #         if re.search("}[0-9][0-9][0-9]=",Line):
   #         
   #            Command = re.split("}[0-9][0-9][0-9]=",Line)[1]
   #            
   #      else:
   #         if re.search("}=",Line):
   #            Command = re.split("}=",Line)[1]   
   #            break

   return(Command)
   
#################################################
def GetOutputFileType(McpFile):

   OutputFileType = ".cof"
   
   LibraryBuildOption = "NA"
   
   Generic16Bit = 0
   
   OtherOptions = ''
   
   McpFilePtr = open(McpFile,'r')
   
   for Line in McpFilePtr:
      
      Line = Line.strip("\n|\r")
      
      if re.search("suite_state=",Line):
      
         Options = re.split("suite_state=",Line)[1]
         Array = re.split(" ",Options)
         for i in Array:
            if not i.strip(" ") == '':
               if re.search("-omf=elf",i):
                  OutputFileType = ".elf"

               elif re.search("build-library",i):
                  LibraryBuildOption = "BuildLibrary"

               elif re.search("generic-16bit",i):
                  Generic16Bit = 1

               else:
                  OtherOptions = OtherOptions + i + " "
         
   McpFilePtr.close()
   
   return(OutputFileType, LibraryBuildOption, Generic16Bit, OtherOptions)
   
def ExtractLinkerOptions(McpFile, ScriptDir, CompilerToBeUsed):
   
   CompilerOptions = ''
   ASMCompilerOptions = ''
   LinkerOptions = ''
   MapOption = ''
   
   NewASMCompilerOptions = ''
   
   MapGen = 0
   ObjGen = 0
   
   '''
   McpFilePtr = open(McpFile,"r")
   
   ACTIVE_FILE_SETTINGS = 0
   ACTIVE_FILE_SETTINGSArray = []
   StartScanforACTIVE_FILE_SETTINGS = 0
   
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r")
      if re.search("INSTRUMENTED_TRACE",Line):
         StartScanforACTIVE_FILE_SETTINGS = 0
         break
      if StartScanforACTIVE_FILE_SETTINGS == 1:
         if re.search("=yes$",Line):
            ACTIVE_FILE_SETTINGSArray.append(Line)
            ACTIVE_FILE_SETTINGS = 1         
      if re.search("ACTIVE_FILE_SETTINGS",Line):
         StartScanforACTIVE_FILE_SETTINGS = 1
      
   McpFilePtr.close()
   '''
   
   McpFilePtr = open(McpFile,"r")
   
   McpFileName = ExtractMcpFileNameFromPath(McpFile)
   
   Compiler = FindCompiler(McpFile)
   
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r")
      
      if Compiler == "C32":
         #if re.search(r"TS{9C698E0A-CBC9-4EFF-AE7D-B569F93E7322}",Line):
         #   CompilerOptions = CompilerOptions + " " + GetCommand(Line,ACTIVE_FILE_SETTINGS,ACTIVE_FILE_SETTINGSArray)
         if re.search(r"TS{77F59DA1-3C53-4677-AC5F-A03EB0125170}",Line):
            LinkerOptions = LinkerOptions + " " + GetCommand(Line)
         
      if Compiler == "C30":
         #if re.search(r"TS{25AC22BD-2378-4FDB-BFB6-7345A15512D3}",Line):
         #   CompilerOptions = CompilerOptions + " " + GetCommand(Line,ACTIVE_FILE_SETTINGS,ACTIVE_FILE_SETTINGSArray)
         if re.search(r"TS{7DAC9A1D-4C45-45D6-B25A-D117C74E8F5A}",Line):
            LinkerOptions = LinkerOptions + " " + GetCommand(Line)

         #if re.search(r"TS{7D9C6ECE-785D-44CB-BA22-17BF2E119622}",Line):
         #   NewASMCompilerOptions = GetCommand(Line,ACTIVE_FILE_SETTINGS,ACTIVE_FILE_SETTINGSArray)
         #   if NewASMCompilerOptions != '':
         #      ASMCompilerOptions = ASMCompilerOptions + ',' + re.sub(' ',',',NewASMCompilerOptions)
               
               
      if Compiler == "C18":
         #if re.search(r"TS{C2AF05E7-1416-4625-923D-E114DB6E2B96}=",Line):
         #   CompilerOptions = CompilerOptions + " " + GetCommand(Line,ACTIVE_FILE_SETTINGS,ACTIVE_FILE_SETTINGSArray)
         if re.search(r"TS{BFD27FBA-4A02-4C0E-A5E5-B812F3E7707C}",Line):
            LinkerOptions = LinkerOptions + " " + GetCommand(Line)         

         #if re.search(r"TS{DD2213A8-6310-47B1-8376-9430CDFC013F}",Line):
         #   NewASMCompilerOptions = GetCommand(Line,ACTIVE_FILE_SETTINGS,ACTIVE_FILE_SETTINGSArray)
         #   if NewASMCompilerOptions != '':
         #      ASMCompilerOptions = ASMCompilerOptions + ' ' + NewASMCompilerOptions
      
      ##########################################
      # Adding Support for XC Compilers
      ##########################################
      if Compiler == "XC16":
         if re.search(r"TS{21A8AA9B-E75C-40B6-B3AE-9CBC16FF2EF9}",Line):
            LinkerOptions = LinkerOptions + " " + GetCommand(Line)  
            
      if Compiler == "XC32":
         if re.search(r"TS{29D3B6CC-DCAB-4659-8011-FFF75BB7F8D7}",Line):
            LinkerOptions = LinkerOptions + " " + GetCommand(Line)          
      
      if Compiler == "PICC" or Compiler == "PICC18":
         if re.search(r"TS{3FF1D5F2-E530-4850-9F70-F61D55BD1AC9}=",Line):
            if not (CompilerToBeUsed == "PICC" or CompilerToBeUsed == "PICC18"):
               CompilerToBeUsed = Compiler            
            Temp, LinkerOptions = picc_options.Extract(re.sub(r"TS{3FF1D5F2-E530-4850-9F70-F61D55BD1AC9}=",'',Line), CompilerToBeUsed, ScriptDir)
         
      if Compiler == "XC8":
         if re.search(r"TS{F42384DA-C7ED-4A02-880F-0F5E88735CE2}=",Line):
            if not (CompilerToBeUsed == "XC8"):
               CompilerToBeUsed = Compiler  
            Temp, LinkerOptions = picc_options.Extract(re.sub(r"TS{F42384DA-C7ED-4A02-880F-0F5E88735CE2}=",'',Line), CompilerToBeUsed, ScriptDir)

   
   if Compiler == "C18":
      LinkerOptions = re.sub("\$\(BINDIR_\)",'',LinkerOptions)
      LinkerOptions = re.sub("\$\(TARGETBASE\)",McpFileName,LinkerOptions) 
      LinkerOptions = " /u_CRUNTIME " + LinkerOptions

   if Compiler == "C30" or Compiler == "C32" or Compiler == "XC16" or Compiler == "XC32":
      
      OutputFileType, LibraryBuildOption, Generic16Bit, OtherOptions = GetOutputFileType(McpFile)
      
      if LibraryBuildOption == "BuildLibrary":
         
         LinkerOptions = "ARBS_BUILD_LIBRARY"
      
      else:
      
         C30_WlExceptions = ["-fast-math", "-legacy-libc"]
         C32_WlExceptions = ["-O0","-O1","-O2","-Os","-O3", "-nostdlib", "-mips16", "-mno-float", "-legacy-libc"]
         
         ##########################
         OptionsArray = re.split(" ",LinkerOptions)
         
         WlOptions = "-Wl,--defsym=__MPLAB_BUILD=1"
         LinkerOptions = OtherOptions.strip(" ")
         
         WlOptionsArray = []
         LinkerOptionsArray = []
         
         WlOptionsEnd = 0
         
         LibraryOptionsArray = []

         if Compiler == "C30" or Compiler == "XC16":
            LibraryOptionsArray = C30_WlExceptions
         else:
            LibraryOptionsArray = C32_WlExceptions
                     
         for Options in OptionsArray:
            if not Options.strip(" ") == '':
               if re.search("^-o\"",Options):
                  WlOptionsEnd = 1
                  if Compiler == "C30" or Compiler == "XC16":
                     LinkerOptions = LinkerOptions + " -o\"" + McpFileName + OutputFileType + "\""
                  else:
                     LinkerOptions = LinkerOptions + " -o\"" + McpFileName + ".elf\""               

               elif re.search("^-Map=",Options):
                  WlOptions = WlOptions + "," + "-Map=\"" + McpFileName + ".map\""

               else:

                     
                  PutInsideWlOption = 1
                  
                  for Element in LibraryOptionsArray:
                     if Element == Options:
                        PutInsideWlOption = 0
                        break
                  
                  if not re.search("^-",Options):
                     PutInsideWlOption = 0
                     
                  if PutInsideWlOption == 1:
                     WlOptions = WlOptions + "," + Options
                  else:
                     LinkerOptions = LinkerOptions + " " + Options
             
               
               '''
               elif WlOptionsEnd == 0 and (not re.search("^\"",Options)):
                  WlOptions = WlOptions + "," + Options

               else:
                  LinkerOptions = LinkerOptions + " " + Options
               '''
               
         LinkerOptions = " " + LinkerOptions + " " + WlOptions
         '''
         for Options in OptionsArray:
            if not re.search("-Map=",Options):
               if not re.search("^-o",Options):
                  if re.search("^-",Options):
                     LinkerOptions = LinkerOptions + "," + Options
                  else:
                     LinkerOptions = Options + " " + LinkerOptions
               else:
                  if Compiler == "C30" or Compiler == "XC16":
                     LinkerOptions = " -o\"" + McpFileName + OutputFileType + "\" " + LinkerOptions
                  else:
                     LinkerOptions = " -o\"" + McpFileName + ".elf\" " + LinkerOptions
            else:
               LinkerOptions = LinkerOptions + "," + "-Map=\"" + McpFileName + ".map\""
         
         LinkerOptions = " " + LinkerOptions
         '''
         
         '''
         ##########################
         if re.search("-Map=",LinkerOptions):
            LinkerOptions = re.sub("\$\(BINDIR_\)",'',LinkerOptions)
            LinkerOptions = re.sub("\$\(TARGETBASE\)",'',LinkerOptions)
            LinkerOptions = re.sub("-Map=\".map\"",'',LinkerOptions)
            MapGen = 1


         if re.search("-o",LinkerOptions):
            LinkerOptions = re.sub("\$\(BINDIR_\)",'',LinkerOptions)
            LinkerOptions = re.sub("\$\(TARGETBASE\)",'',LinkerOptions)
            LinkerOptions = re.sub("\$\(TARGETSUFFIX\)",'',LinkerOptions)
            LinkerOptions = re.sub("-o\".\"",'',LinkerOptions)
            ObjGen = 1

         MipsOptionExisting = 0
         if re.search("-mips16",LinkerOptions):
            MipsOptionExisting = 1

         LinkerOptions = re.sub(" -",",-",LinkerOptions)
         LinkerOptions = re.sub(' ','',LinkerOptions)

         OutputFileGenerationOption = ''



         if ObjGen == 1:
            if Compiler == "C30" or Compiler == "XC16":
               OutputFileGenerationOption = " -o\"" + McpFileName + OutputFileType + "\" " 
            else:
               OutputFileGenerationOption = " -o\"" + McpFileName + ".elf\" " 

         if MipsOptionExisting == 1:                                 # -mips16 should not be in the command -Wl
            LinkerOptions = re.sub(",-mips16",'',LinkerOptions)
            LinkerOptions = OutputFileGenerationOption + " -mips16 -Wl" + LinkerOptions
         else:
            LinkerOptions = OutputFileGenerationOption + " -Wl" + LinkerOptions

         if MapGen == 1:
            MapOption = ",-Map=\"" + McpFileName + ".map\" "
         '''   

   McpFilePtr.close()
   return(LinkerOptions,MapOption)
   
################################################

def GetCompilerPaths(ScriptDir):
   AsmWinPath = ''
   C18Path = ''
   C30Path = ''
   C32Path = ''

   AsmWinExe = ''
   C18CompExe = ''
   C18LkrExe = ''
   C18AsExe = ''
   
   C30gccExe = ''
   C30arExe = ''
   C30HexGenExe = ''
   
   C32gccExe = ''
   C32arExe = ''
   C32HexGenExe = ''
   
   XC8Path = ''
   XC16Path = ''
   XC32Path = '' 
   
   XC8CompExe = ''
   XC8LkrExe = ''
   XC8_C18CompExe = ''
   XC8_C18LkrExe = ''
   XC8_C18AsExe = ''
   
   XC16gccExe = ''
   XC16arExe = ''
   XC16HexGenExe = ''
   
   XC32gccExe = ''
   XC32arExe = ''
   XC32HexGenExe = ''
   
   PICCPath = ''
   PICC18Path = ''
   
   PICCCompExe = ''
   
   PICC18CompExe = ''
   
   #PathFile = os.path.join(ScriptDir,"CompilerPaths.info")
   
   PathFile = os.path.join(ScriptDir,"mcpr_modified.mcpr")
   
   if not os.path.exists(PathFile):
      PathFile = "C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr"
   
   PathFilePtr = open(PathFile,"r")
   GetNextLine = 0
   
   for Line in PathFilePtr:
   
      Line = Line.strip("\n|\r")
      Line = re.sub("\"",'',Line)
      Line = Line.strip(" ")
      
      
      if re.search("^_ASMWIN_PATH_=",Line):
         AsmWinPath = re.sub("_ASMWIN_PATH_=",'',Line)
      if re.search("^_C18_PATH_=",Line):
         C18Path = re.sub("_C18_PATH_=",'',Line)
      if re.search("^_C30_PATH_=",Line):
         C30Path = re.sub("_C30_PATH_=",'',Line)
      if re.search("^_C32_PATH_=",Line):
         C32Path = re.sub("^_C32_PATH_=",'',Line)
         
      # XC Stuff #
      if re.search("^_XC8_PATH_=",Line):
         XC8Path = re.sub("^_XC8_PATH_=",'',Line)
      if re.search("^_XC16_PATH_=",Line):
         XC16Path = re.sub("^_XC16_PATH_=",'',Line)
      if re.search("^_XC32_PATH_=",Line):
         XC32Path = re.sub("^_XC32_PATH_=",'',Line)         
      ############
      
      # PICC Stuff #
      if re.search("^_PICC_PATH_=",Line):
         PICCPath = re.sub("^_PICC_PATH_=",'',Line)
      if re.search("^_PICC18_PRO_PATH_=",Line):
         PICC18Path = re.sub("^_PICC18_PRO_PATH_=",'',Line)          
      ############
      
      if re.search("_MPASM_MP_CC_=",Line):
         AsmWinExe = re.sub("_MPASM_MP_CC_=",'',Line)
         
      if re.search("_C18_MP_CC_=",Line):
         C18CompExe = re.sub("_C18_MP_CC_=",'',Line)
      if re.search("_C18_MP_LD_=",Line):
         C18LkrExe = re.sub("_C18_MP_LD_=",'',Line)
      if re.search("_C18_MP_AS_=",Line):
         C18AsExe = re.sub("_C18_MP_AS_=",'',Line)
         
         
      if re.search("_C30_MP_CC_=",Line):
         C30gccExe = re.sub("_C30_MP_CC_=",'',Line)
      if re.search("_C30_MP_AR_=",Line):
         C30arExe = re.sub("_C30_MP_AR_=",'',Line)
      if re.search("_C30_MP_HEX_=",Line):
         C30HexGenExe = re.sub("_C30_MP_HEX_=",'',Line)
         
      if re.search("_C32_MP_CC_=",Line):
         C32gccExe = re.sub("_C32_MP_CC_=",'',Line)  
      if re.search("_C32_MP_AR_=",Line):
         C32arExe = re.sub("_C32_MP_AR_=",'',Line)         
      if re.search("_C32_MP_HEX_=",Line):
         C32HexGenExe = re.sub("_C32_MP_HEX_=",'',Line)

      # XC Stuff #
      if re.search("_XC8_MP_CC_=",Line):
         XC8CompExe = re.sub("_XC8_MP_CC_=",'',Line)
      if re.search("_XC8_MP_LD_=",Line):
         XC8LkrExe = re.sub("_XC8_MP_LD_=",'',Line)
      if re.search("_XC8_C18EXE_MP_CC_=",Line):
         XC8_C18CompExe = re.sub("_XC8_C18EXE_MP_CC_=",'',Line)
      if re.search("_XC8_C18EXE_MP_LD_=",Line):
         XC8_C18LkrExe = re.sub("_XC8_C18EXE_MP_LD_=",'',Line)
      if re.search("_XC8_C18EXE_MP_AS_=",Line):
         XC8_C18AsExe = re.sub("_XC8_C18EXE_MP_AS_=",'',Line)         
         
         
      if re.search("_XC16_MP_CC_=",Line):
         XC16gccExe = re.sub("_XC16_MP_CC_=",'',Line)
      if re.search("_XC16_MP_AR_=",Line):
         XC16arExe = re.sub("_XC16_MP_AR_=",'',Line)
      if re.search("_XC16_MP_HEX_=",Line):
         XC16HexGenExe = re.sub("_XC16_MP_HEX_=",'',Line)
         
      if re.search("_XC32_MP_CC_=",Line):
         XC32gccExe = re.sub("_XC32_MP_CC_=",'',Line)  
      if re.search("_XC32_MP_AR_=",Line):
         XC32arExe = re.sub("_XC32_MP_AR_=",'',Line)         
      if re.search("_XC32_MP_HEX_=",Line):
         XC32HexGenExe = re.sub("_XC32_MP_HEX_=",'',Line)
      ############         
      
      
      # PICC Stuff
      if re.search("_PICC_MP_CC_=",Line):
         PICCCompExe = re.sub("_PICC_MP_CC_=",'',Line)  
      if re.search("_PICC18_MP_LD_=",Line):
         PICC18CompExe = re.sub("_PICC18_MP_LD_=",'',Line)        
      ############
   PathFilePtr.close()

   return(AsmWinPath, C18Path, C30Path, C32Path, AsmWinExe, C18CompExe, C18LkrExe, C18AsExe, C30gccExe, C30arExe,  C30HexGenExe, C32gccExe, C32arExe, C32HexGenExe, XC8Path, XC16Path, XC32Path, XC8CompExe, XC8LkrExe, XC8_C18CompExe, XC8_C18LkrExe, XC8_C18AsExe, XC16gccExe, XC16arExe,  XC16HexGenExe, XC32gccExe, XC32arExe, XC32HexGenExe, PICCPath, PICC18Path, PICCCompExe, PICC18CompExe)

################################################

def ForceKillTaskIfExists(ExeName,LogFile):
   
   ExeToKill = ExeName
   
   Command = "set ExecStatus=%ERRORLEVEL% "

   Command = Command + "\ntasklist /FI \"IMAGENAME eq " + ExeToKill + "\" 2>NUL | find /I /N \"" + ExeToKill + "\">NUL"
   Command = Command + "\nIF ERRORLEVEL 1 goto Passed"
   Command = Command + "\ntaskkill /im " + ExeToKill + " /F /T"
   Command = Command + "\necho ExitStatus: 1" + AddLoggingOption(LogFile)
   Command = Command + "echo Error: Compiler/Linker Hang Detected" + AddLoggingOption(LogFile)
   Command = Command + "sleep 2"

   '''
   ExeToKill = "dwwin.exe"
   
   Command = Command + "\ntasklist /FI \"IMAGENAME eq " + ExeToKill + "\" 2>NUL | find /I /N \"" + ExeToKill + "\">NUL"
   Command = Command + "\nIF ERRORLEVEL 1 goto Passed"
   Command = Command + "\ntaskkill /im " + ExeToKill + " /F /T"
   Command = Command + "\necho ExitStatus: 1" + AddLoggingOption(LogFile)
   Command = Command + "\nError: Compiler/Linker Hang Detected" + AddLoggingOption(LogFile)
   Command = Command + "\nsleep 2"

   ExeToKill = "ld.exe"
   
   Command = Command + "\ntasklist /FI \"IMAGENAME eq " + ExeToKill + "\" 2>NUL | find /I /N \"" + ExeToKill + "\">NUL"
   Command = Command + "\nIF ERRORLEVEL 1 goto Passed"
   Command = Command + "\ntaskkill /im " + ExeToKill + " /F /T"
   Command = Command + "\necho ExitStatus: 1" + AddLoggingOption(LogFile)
   Command = Command + "\nError: Compiler/Linker Hang Detected" + AddLoggingOption(LogFile)
   Command = Command + "\nsleep 2"
   '''
   
   Command = Command + "\n:Passed\n"
   
   return(Command)

def GetBuildOptionsKeyWord(Compiler,Type):
   
   Kwd = ''
   
   if Compiler == "PICC" or Compiler == "PICC18":
      if Type =="C":
         Kwd = "TS{3FF1D5F2-E530-4850-9F70-F61D55BD1AC9}"
      elif Type == "ASM":
         Kwd = "TS{3FF1D5F2-E530-4850-9F70-F61D55BD1AC9}"

   if Compiler == "XC8":
      if Type =="C":
         Kwd = "TS{F42384DA-C7ED-4A02-880F-0F5E88735CE2}"
      elif Type == "ASM":
         Kwd = "TS{F42384DA-C7ED-4A02-880F-0F5E88735CE2}"
         
   
   if Compiler == "C18":
      if Type =="C":
         Kwd = "TS{C2AF05E7-1416-4625-923D-E114DB6E2B96}"
      elif Type == "ASM":
         Kwd = "TS{DD2213A8-6310-47B1-8376-9430CDFC013F}"

   elif Compiler == "C30":
      if Type =="C":
         Kwd = "TS{25AC22BD-2378-4FDB-BFB6-7345A15512D3}"
      elif Type == "ASM":
         Kwd = "TS{7D9C6ECE-785D-44CB-BA22-17BF2E119622}"
         
   elif Compiler == "C32":
      if Type =="C":
         Kwd = "TS{9C698E0A-CBC9-4EFF-AE7D-B569F93E7322}"
      elif Type == "ASM":
         Kwd = ''
 
   elif Compiler == "XC16":
      if Type =="C":
         Kwd = "TS{F9CE474D-6A6C-401D-A11E-BEE01B244D79}"
      elif Type == "ASM":
         Kwd = "TS{8493B2ED-D539-4951-86C9-24D5331F0393}"

   elif Compiler == "XC32":
      if Type =="C":
         Kwd = "TS{1F324EFA-C0BA-4A8F-A85A-B21644939CAD}"
      elif Type == "ASM":
         Kwd = "TS{6F324298-6323-4781-8C43-43FA5E6F3646}"
         
   return(Kwd)
         
################################################

def ExtractBuildOption(McpFile,FileNumber,Compiler,CompilerToBeUsed,FileExtn,ScriptDir):
   Command = ''
   
   
   LineToBeExtracted = ''
   
   StartScan = 0
   
   Kwd = GetBuildOptionsKeyWord(Compiler,FileExtn)
   
   LineToBeExtracted = Kwd + '='
   
   #############
   GenericCommand = ''
   McpFilePtr = open(McpFile,'r')
   
   StartScan = 0
   
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r")   
      
      if re.search("INSTRUMENTED_TRACE|ACTIVE_FILE_SETTINGS",Line):
         StartScan = 0
      
      if StartScan == 1:
         if re.search(LineToBeExtracted,Line):
            if re.split(LineToBeExtracted,Line)[1] != '':
               GenericCommand = re.split(LineToBeExtracted,Line)[1]
      if re.search("TOOL_SETTINGS",Line):
         StartScan = 1
   
   McpFilePtr.close()
   
   #############
   
   
   McpFilePtr = open(McpFile,'r')
   
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r")
      
      if re.search("INSTRUMENTED_TRACE",Line):
         StartScan = 0
         break
      if StartScan == 1:
         j = Kwd + FileNumber + "_active=yes"
         if re.search(j,Line):
            LineToBeExtracted = Kwd + FileNumber + '='
            break
      if re.search("ACTIVE_FILE_SETTINGS",Line):
         StartScan = 1
      
   McpFilePtr.close()
   
   McpFilePtr = open(McpFile,'r')
   
   StartScan = 0
   
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r")   
      
      if re.search("INSTRUMENTED_TRACE|ACTIVE_FILE_SETTINGS",Line):
         StartScan = 0

      if StartScan == 1:
         if re.search(LineToBeExtracted,Line):
            if re.split(LineToBeExtracted,Line)[1] != '':
               Command = re.split(LineToBeExtracted,Line)[1]
            
      if re.search("TOOL_SETTINGS",Line):
         StartScan = 1
   
   McpFilePtr.close()
   
   ## Implementation for PICC
   
   if Compiler == "PICC" or Compiler == "PICC18" or Compiler == "XC8":
      GenericCommandArray = re.split(" ",GenericCommand)
      FileSpecificCommandArray = re.split(" ",Command)
      for i in FileSpecificCommandArray:
         i = i.strip(" ")
         i = i.strip("\n")
         FSC = re.split("=",i)[0]
         Found = 0
         for j in GenericCommandArray:
            j = j.strip(" ")
            j = j.strip("\n")
            GCA = re.split("=",j)[0]
            
            if FSC == GCA:
               if i == j:
                  Found = 1
                  break
               else:
                  GenericCommandArray.remove(j)
                  break
         
         if Found == 0:
            if i != '':
               GenericCommandArray.append(i)
      
      Command = ''
      
      for i in GenericCommandArray:
         Command = Command + i + " "
      
      Command = Command.strip(" ")
      
      if not (CompilerToBeUsed == "PICC" or CompilerToBeUsed == "PICC18" or CompilerToBeUsed == "XC8"):
         CompilerToBeUsed = Compiler
         
      Command, Temp = picc_options.Extract(Command, CompilerToBeUsed, ScriptDir) 
   
   return(Command)
   
   
   
################################################
def GetBuildDirectoryPolicy(McpFile):
   
   BuildOption = ''
   
   McpFilePtr = open(McpFile,'r')
      
   for Line in McpFilePtr:
      Line = Line.strip("\n|\r")
      if re.search("BuildDirPolicy=BuildDirIsSourceDir",Line):
         BuildOption = "SRCDir"
      if re.search("BuildDirPolicy=BuildDirIsProjectDir",Line):
         BuildOption = "PRODir"
      if not BuildOption == '':
         break
   McpFilePtr.close()
   return(BuildOption)

################################################

def GetSrcDirPath(src,mcp):

   Count = 0

   for i in range(100):
      if re.search(r"^..\\",src):
         src = re.sub(r"^..\\",'',src)
         Count = Count + 1

   src = os.path.split(src)[0]
   mcp = os.path.split(mcp)[0]

   for i in range(Count):
      mcp = os.path.split(mcp)[0]

   return(os.path.normpath(os.path.join(mcp,src)))
###################################################

def ModifyToWritePermission(func, path, exc_info):             # Modify the Files and Directories to Write Mode
    import stat
    if not os.access(path, os.W_OK):                           # Is the error an access error ?
      os.chmod(path, 0777)
      func(path)                                               # Recrussive change of mode of all the Files
    else:
      raise
      
'''
def RemoveSwitchDirOption(BuildDirectoryPolicy,McpFile):

   #Command = ''
   #
   #if BuildDirectoryPolicy == "SRCDir":
   #   Command = 'cd "' + os.path.normpath(os.path.split(McpFile)[0]) + '"' + "\n\n"
   #
   #return(Command)
   
   os.chdir(os.path.normpath(os.path.split(McpFile)[0]))
'''   
   
###################################################
def SwitchDirOption(CdDirPath):
   
   #Command = ''
   #
   #if BuildDirectoryPolicy == "SRCDir":
   #   if not CdDirPath == '':
   #      Command = "\n" + 'cd "' + os.path.normpath(CdDirPath) + '"' + "\n"
   #
   #return(Command)
   if os.path.exists(CdDirPath):
      os.chdir(CdDirPath)
      

################################################

def CompilerDecision(CompilerToBeUsed, Compiler):
   
   CompilerBinariesToBeUsed = ''
   
   CompilerBinariesToBeUsed = Compiler
   
   if CompilerToBeUsed == "XC8":
      if Compiler == "PICC" or Compiler == "PICC18":
         CompilerBinariesToBeUsed = CompilerToBeUsed
  
   elif CompilerToBeUsed == "XC16":
      if Compiler == "C30":
         CompilerBinariesToBeUsed = CompilerToBeUsed

   elif CompilerToBeUsed == "XC32":
      if Compiler == "C32":
         CompilerBinariesToBeUsed = CompilerToBeUsed
   
   elif CompilerToBeUsed == "XC8-C18":
      if Compiler == "C18":
         CompilerBinariesToBeUsed = CompilerToBeUsed
   
   return(CompilerBinariesToBeUsed)
   
   
   

def GetExecutorBinaries(McpFile, CompilerToBeUsed, ScriptDir):
   
   ASMWinPath = ''
   CompilerBinaryPath = ''
   LinkerBinaryPath = ''
   ArchiverBinaryPath = ''
   HexGenBinaryPath = ''
   
   Compiler = FindCompiler(McpFile)
   AsmWinPath, C18Path, C30Path, C32Path, AsmWinExe, C18CompExe, C18LkrExe, C18AsExe, C30gccExe, C30arExe,  C30HexGenExe, C32gccExe, C32arExe, C32HexGenExe, XC8Path, XC16Path, XC32Path, XC8CompExe, XC8LkrExe, XC8_C18CompExe, XC8_C18LkrExe, XC8_C18AsExe, XC16gccExe, XC16arExe,  XC16HexGenExe, XC32gccExe, XC32arExe, XC32HexGenExe, PICCPath, PICC18Path, PICCCompExe, PICC18CompExe = GetCompilerPaths(ScriptDir)
   
   AsmWinExePath = '"' + os.path.normpath(os.path.join(AsmWinPath,AsmWinExe)) + '"' 
   
   C18CompExePath = '"' + os.path.normpath(os.path.join(C18Path,C18CompExe)) + '"' 
   C18LkrExePath = '"' + os.path.normpath(os.path.join(C18Path,C18LkrExe)) + '"' 
   C18AsExePath = '"' + os.path.normpath(os.path.join(C18Path,C18AsExe)) + '"' 
   C30gccExePath =  '"' + os.path.normpath(os.path.join(C30Path,C30gccExe)) + '"'
   C30arExePath =  '"' + os.path.normpath(os.path.join(C30Path,C30arExe)) + '"'
   C30HexGenExePath =  '"' + os.path.normpath(os.path.join(C30Path,C30HexGenExe)) + '"'
   C32gccExePath =  '"' + os.path.normpath(os.path.join(C32Path,C32gccExe)) + '"'
   C32arExePath =  '"' + os.path.normpath(os.path.join(C32Path,C32arExe)) + '"'
   C32HexGenExePath =  '"' + os.path.normpath(os.path.join(C32Path,C32HexGenExe)) + '"'
   
   XC8CompExePath = '"' + os.path.normpath(os.path.join(XC8Path,XC8CompExe)) + '"' 
   XC8LkrExePath = '"' + os.path.normpath(os.path.join(XC8Path,XC8LkrExe)) + '"' 
   XC8_C18CompExePath = '"' + os.path.normpath(os.path.join(XC8Path,XC8_C18CompExe)) + '"' 
   XC8_C18LkrExePath = '"' + os.path.normpath(os.path.join(XC8Path,XC8_C18LkrExe)) + '"' 
   XC8_C18AsExePath = '"' + os.path.normpath(os.path.join(XC8Path,XC8_C18AsExe)) + '"' 

   XC16gccExePath =  '"' + os.path.normpath(os.path.join(XC16Path,XC16gccExe)) + '"'
   XC16arExePath =  '"' + os.path.normpath(os.path.join(XC16Path,XC16arExe)) + '"'
   XC16HexGenExePath =  '"' + os.path.normpath(os.path.join(XC16Path,XC16HexGenExe)) + '"'
   XC32gccExePath =  '"' + os.path.normpath(os.path.join(XC32Path,XC32gccExe)) + '"'
   XC32arExePath =  '"' + os.path.normpath(os.path.join(XC32Path,XC32arExe)) + '"'
   XC32HexGenExePath =  '"' + os.path.normpath(os.path.join(XC32Path,XC32HexGenExe)) + '"'
   
   PICCCompExePath = '"' + os.path.normpath(os.path.join(PICCPath,PICCCompExe)) + '"'
   PICC18CompExePath = '"' + os.path.normpath(os.path.join(PICC18Path,PICC18CompExe)) + '"' 
   
   CompilerBinaries = CompilerDecision(CompilerToBeUsed, Compiler)
   
   if CompilerBinaries == "PICC":
      ASMWinPath = AsmWinExePath
      CompilerBinaryPath = PICCCompExePath
      LinkerBinaryPath = PICCCompExePath
      ArchiverBinaryPath = PICCCompExePath
      HexGenBinaryPath = PICCCompExePath

   elif CompilerBinaries == "PICC18":
      ASMWinPath = AsmWinExePath
      CompilerBinaryPath = PICC18CompExePath
      LinkerBinaryPath = PICC18CompExePath
      ArchiverBinaryPath = PICC18CompExePath
      HexGenBinaryPath = PICC18CompExePath         

   elif CompilerBinaries == "C18":
      ASMWinPath = C18AsExePath
      CompilerBinaryPath = C18CompExePath
      LinkerBinaryPath = C18LkrExePath
      ArchiverBinaryPath = C18LkrExePath
      HexGenBinaryPath = C18LkrExePath 

   elif CompilerBinaries == "XC8-C18":
      ASMWinPath = XC8_C18AsExePath
      CompilerBinaryPath = XC8_C18CompExePath
      LinkerBinaryPath = XC8_C18LkrExePath
      ArchiverBinaryPath = XC8_C18LkrExePath
      HexGenBinaryPath = XC8_C18LkrExePath 

   elif CompilerBinaries == "XC8":
      ASMWinPath = AsmWinExePath
      CompilerBinaryPath = XC8CompExePath
      LinkerBinaryPath = XC8CompExePath
      ArchiverBinaryPath = XC8CompExePath
      HexGenBinaryPath = XC8CompExePath 

   elif CompilerBinaries == "C30":
      ASMWinPath = AsmWinExePath
      CompilerBinaryPath = C30gccExePath
      LinkerBinaryPath = C30gccExePath
      ArchiverBinaryPath = C30arExePath
      HexGenBinaryPath = C30HexGenExePath 

   elif CompilerBinaries == "XC16":
      ASMWinPath = AsmWinExePath
      CompilerBinaryPath = XC16gccExePath
      LinkerBinaryPath = XC16gccExePath
      ArchiverBinaryPath = XC16arExePath
      HexGenBinaryPath = XC16HexGenExePath 

   elif CompilerBinaries == "C32":
      ASMWinPath = AsmWinExePath
      CompilerBinaryPath = C32gccExePath
      LinkerBinaryPath = C32gccExePath
      ArchiverBinaryPath = C32arExePath
      HexGenBinaryPath = C32HexGenExePath          

   elif CompilerBinaries == "XC32":
      ASMWinPath = AsmWinExePath
      CompilerBinaryPath = XC32gccExePath
      LinkerBinaryPath = XC32gccExePath
      ArchiverBinaryPath = XC32arExePath
      HexGenBinaryPath = XC32HexGenExePath     
         
   return(ASMWinPath, CompilerBinaryPath, LinkerBinaryPath, ArchiverBinaryPath, HexGenBinaryPath)



def BuildIndividualExecutor(McpFile,LogFile,ScriptDir,CompilerToBeUsed):
   
   TempDir = ''
   IncludeDirList = []
   LibDirList = []
   LkrDirList = []

   SrcFileList = []
   FileNumberR = []
   HeaderFileList = []
   ObjFileList = []
   LibFileList = []
   LkrFileList = []

   '''
   AsmWinExe = "MPASMWIN.exe"
   C18CompExe = "mcc18.exe"
   C18LkrExe = "mplink.exe"
   C30gccExe = "pic30-gcc.exe"
   C30arExe = "pic30-ar.exe"
   C30HexGenExe = "pic30-bin2hex.exe"
   C32gccExe = "pic32-gcc.exe"
   C32HexGenExe = "pic32-bin2hex.exe"
   
   binAsmWinExe = AsmWinExe
   binC18CompExe = os.path.normpath(os.path.join("bin",C18CompExe))
   binC18LkrExe = os.path.normpath(os.path.join("bin",C18LkrExe))
   binC30gccExe = os.path.normpath(os.path.join("bin",C30gccExe))
   binC30arExe = os.path.normpath(os.path.join("bin",C30arExe))
   binC30HexGenExe = os.path.normpath(os.path.join("bin",C30HexGenExe))
   binC32gccExe = os.path.normpath(os.path.join("bin",C32gccExe))
   binC32HexGenExe = os.path.normpath(os.path.join("bin",C32HexGenExe))
   '''
   
   AsmWinPath = ''
   C18Path = ''
   C30Path = ''
   C32Path = ''
   


   LocalObjectFileArray = []
   Compiler = ''
   Device = ''
   
   TempDir, IncludeDirList, IncludeDirListASM, LibDirList, LkrDirList = GetDirs(McpFile)
   SrcFileList, FileNumberR, HeaderFileList, ObjFileList, LibFileList, LkrFileList = GetFiles(McpFile)
   
   ASMWinPath, CompilerBinaryPath, LinkerBinaryPath, ArchiverBinaryPath, HexGenBinaryPath = GetExecutorBinaries(McpFile, CompilerToBeUsed, ScriptDir)
   
   LinkerOptions,MapOption = ExtractLinkerOptions(McpFile, ScriptDir, CompilerToBeUsed)

   BuildDirectoryPolicy = GetBuildDirectoryPolicy(McpFile)
   CdDirPath = []
   
   if BuildDirectoryPolicy == "SRCDir":
      for i in range(len(SrcFileList)):
         
         CdDirPath.append(GetSrcDirPath(SrcFileList[i],McpFile))
         
         SrcFileList[i] = os.path.split(SrcFileList[i])[1]

   Compiler = FindCompiler(McpFile)
   Device = re.sub("DSPIC|PIC",'',FindDevice(McpFile).upper())
   
   if TempDir != os.path.normpath(os.path.split(McpFile)[0]):
      if os.path.exists(TempDir):
         shutil.rmtree(TempDir,onerror=ModifyToWritePermission)
         
      os.makedirs(TempDir)
   
   McpFileName = ExtractMcpFileNameFromPath(McpFile)
   
   if Compiler == "PICC" or Compiler == "PICC18" or Compiler =="XC8":
      Command = ''
      LocalObjectFileArray = []
      #### Compiler Options ####
      Count = 0
      
      ObjectFileExtn = ".p1"
      
      for SrcFile in SrcFileList:
         Count = Count + 1
         
         #print SrcFile
         if BuildDirectoryPolicy == "SRCDir":
            SrcFile = os.path.join(CdDirPath[Count - 1],SrcFile)  # PICC uses absolute path to build
         else:
            SrcFile = os.path.join(os.getcwd(),SrcFile)  # PICC uses absolute path to build
         
         SrcFile = os.path.normpath(SrcFile)
         
         if SrcFile.endswith(".c") or SrcFile.endswith(".C"):
            ObjectFileExtn = ".p1"
         else:
            ObjectFileExtn = ".obj"
         
         if TempDir == '' or BuildDirectoryPolicy == "SRCDir":
            DotOFiles = '"' + os.path.splitext(SrcFile)[0] + ObjectFileExtn + '"'
         else:
            #DotOFiles = '"' + TempDir + "\\" + os.path.splitext(SrcFile)[0] + ObjectFileExtn + '"'
            DotOFiles = '"' + os.path.splitext(os.path.split(SrcFile)[1])[0] + ObjectFileExtn + '"'

         LocalObjectFileArray.append(DotOFiles) 

         CompilerOptions = ExtractBuildOption(McpFile,FileNumberR[Count - 1],Compiler,CompilerToBeUsed,"C",ScriptDir)

         
         if BuildDirectoryPolicy == "SRCDir":

            SwitchDirOption(CdDirPath[Count - 1])

         Command = CompilerBinaryPath 

         Command = Command + " --pass1 "
         
         Command = Command + ' "' + SrcFile + '" -q --chip=' + Device

         for IncludeDir in IncludeDirList:
            Command = Command + ' "' + "-I" + IncludeDir + '"'

         Command = Command + ' ' + CompilerOptions            

         PrintExecutingCommandToLogFile(LogFile, Command)

         Command = Command + AddLoggingOption(LogFile)

         Command = Command + PrintExitCode(LogFile)

         BuildCommand(Command,LogFile,McpFile,SrcFile)

         if BuildDirectoryPolicy == "SRCDir":

            SwitchDirOption(os.path.normpath(os.path.split(McpFile)[0]))
               
      #### Linker Options ####
      
      Command = CompilerBinaryPath
                     
      Command = Command + " --chip=" + Device + ' '
      
      Command = Command + " -o\"" + McpFileName + ".cof\"" + " -m\"" + McpFileName + ".map\"" 
      
      #for LibDir in LibDirList:
      #   Command = Command + ' "' + LibDir + '"'

      for IncludeDir in IncludeDirList:
         Command = Command + ' "' + "-I" + IncludeDir + '"'

      if not LkrFileList == []:
         Command = Command + " " + '"' + LkrFileList[0] + '"'
      
      for LocalObject in LocalObjectFileArray:
         
         L = re.sub("^\"\.",'\"',LocalObject)
         L = re.sub(r"\"\\",'\"',L)
         
         Command = Command + " " + L
         
      Command = Command + LinkerOptions
      
      PrintExecutingCommandToLogFile(LogFile, Command)
      
      Command = Command + AddLoggingOption(LogFile)
      
      #Command = Command + ForceKillTaskIfExists(C18LkrExe,LogFile)
      
      Command = Command + PrintExitCode(LogFile)
      
      BuildCommand(Command,LogFile,McpFile,"C18Lkr")

   
   if Compiler == "C18":
      
      Command = ''
      LocalObjectFileArray = []
      #### Compiler Options ####
      Count = 0
      
      for SrcFile in SrcFileList:
         
         Count = Count + 1
         
         if TempDir == '':
            DotOFiles = '"' + os.path.splitext(os.path.split(SrcFile)[1])[0] + ".o" + '"'
         else:
            DotOFiles = '"' + TempDir + "\\" + os.path.splitext(os.path.split(SrcFile)[1])[0] + ".o" + '"'

         LocalObjectFileArray.append(DotOFiles) 

         if SrcFile.endswith(".c") or SrcFile.endswith(".C"):
            
            CompilerOptions = ExtractBuildOption(McpFile,FileNumberR[Count - 1],Compiler,CompilerToBeUsed,"C",ScriptDir)
            
            if BuildDirectoryPolicy == "SRCDir":
               
               SwitchDirOption(CdDirPath[Count - 1])
            
            Command = CompilerBinaryPath
            
            Command = Command + " -p=" + Device
            
            for IncludeDir in IncludeDirList:
               Command = Command + " -I" + '"' + IncludeDir + '"'

            Command = Command + ' "' + SrcFile + '"' + " -fo="

            Command = Command + DotOFiles + ' ' + CompilerOptions
            
            PrintExecutingCommandToLogFile(LogFile, Command)
            
            Command = Command + AddLoggingOption(LogFile)
                        
            Command = Command + PrintExitCode(LogFile)
            
            BuildCommand(Command,LogFile,McpFile,SrcFile)
            
            if BuildDirectoryPolicy == "SRCDir":
            
               SwitchDirOption(os.path.normpath(os.path.split(McpFile)[0]))
         else:
            
            ASMCompilerOptions = ExtractBuildOption(McpFile,FileNumberR[Count - 1],Compiler,CompilerToBeUsed,"ASM",ScriptDir)
            
            if BuildDirectoryPolicy == "SRCDir":
               
               SwitchDirOption(CdDirPath[Count - 1])
               
            SrcNameOnly = os.path.splitext(os.path.split(SrcFile)[1])[0]
            
            ASMCompilerOptions = re.sub("\$\(BINDIR_\)",'',ASMCompilerOptions)
            ASMCompilerOptions = re.sub("\$\(INFILEBASE\)",SrcNameOnly,ASMCompilerOptions)

            Command = ASMWinPath 
            
            Command = Command + " /q" + " /p" + Device + " " + SrcFile + " /l" + SrcNameOnly + ".lst /e" + SrcNameOnly + ".err /o" + DotOFiles + " " + ASMCompilerOptions + ' ' 
            
            PrintExecutingCommandToLogFile(LogFile, Command)
            
            Command = Command + AddLoggingOption(LogFile)
            
            #Command = Command + ForceKillTaskIfExists(AsmWinExe,LogFile)
            
            Command = Command + PrintExitCode(LogFile)
            
            BuildCommand(Command,LogFile,McpFile,SrcFile)
            
            if BuildDirectoryPolicy == "SRCDir":
            
               SwitchDirOption(os.path.normpath(os.path.split(McpFile)[0]))
               
               
      #### Linker Options ####
      
      Command = LinkerBinaryPath
               
      Command = Command + " /p" + Device + ' '
      
      for LibDir in LibDirList:
         Command = Command + " /l" + '"' + LibDir + '"'
      Command = Command + " /l" + '"' + os.path.normpath(os.path.join(C18Path,"lkr")) + '" ' 
         
      if not LkrFileList == []:
         Command = Command + " " + '"' + LkrFileList[0] + '"'
      
      for LocalObject in LocalObjectFileArray:
         
         L = re.sub("^\"\.",'\"',LocalObject)
         L = re.sub(r"\"\\",'\"',L)
         
         Command = Command + " " + L
         
      Command = Command + LinkerOptions
      
      PrintExecutingCommandToLogFile(LogFile, Command)
      
      Command = Command + AddLoggingOption(LogFile)
      
      #Command = Command + ForceKillTaskIfExists(C18LkrExe,LogFile)
      
      Command = Command + PrintExitCode(LogFile)
      
      BuildCommand(Command,LogFile,McpFile,"C18Lkr")
   
   
   
   
   if Compiler == "C32" or Compiler == "XC32":
      
      Command = ''
      LocalObjectFileArray = []

      ## Compiler Options ##
      Count = 0
      for SrcFile in SrcFileList:
         Count = Count + 1
         
         CompilerOptions = ExtractBuildOption(McpFile,FileNumberR[Count - 1],Compiler,CompilerToBeUsed,"C",ScriptDir)
         
         if BuildDirectoryPolicy == "SRCDir":

            SwitchDirOption(CdDirPath[Count - 1])
               
         if TempDir == '':
            DotOFiles = '"' + os.path.splitext(os.path.split(SrcFile)[1])[0] + ".o" + '"'
            DotDFiles = '"' + os.path.splitext(os.path.split(SrcFile)[1])[0] + ".d" + '"'
         else:
            DotOFiles = '"' + TempDir + "\\" + os.path.splitext(os.path.split(SrcFile)[1])[0] + ".o" + '"'
            DotDFiles = '"' + TempDir + "\\" + os.path.splitext(os.path.split(SrcFile)[1])[0] + ".d" + '"'
            
         LocalObjectFileArray.append(DotOFiles)
         
         Command = CompilerBinaryPath   
                  
         Command = Command + " -mprocessor=" + Device + " -x c -c " + '"' + SrcFile + '"' + " -o" + DotOFiles + " -MMD -MF" + DotDFiles
         
         if not IncludeDirList == []:
            for IncludeDir in IncludeDirList:
               Command = Command + " -I" + '"' + IncludeDir + '"'
         Command = Command + ' ' + CompilerOptions 
         
         PrintExecutingCommandToLogFile(LogFile, Command)
         
         Command = Command + AddLoggingOption(LogFile)
         
         #Command = Command + ForceKillTaskIfExists(C32gccExe,LogFile)
         
         Command = Command + PrintExitCode(LogFile)
         
         BuildCommand(Command,LogFile,McpFile,SrcFile)
         
         if BuildDirectoryPolicy == "SRCDir":

            SwitchDirOption(os.path.normpath(os.path.split(McpFile)[0]))
         

      ## Linker Options ##
      if LinkerOptions == "ARBS_BUILD_LIBRARY":
         
         
         Command = ArchiverBinaryPath  
            
        
         McpFileName = ExtractMcpFileNameFromPath(McpFile)
         
         Command = Command + " r " + '"' + McpFileName + ".a" + '"'
         
         for LocalObject in LocalObjectFileArray:
            L = re.sub("^\"\.",'\"',LocalObject)
            L = re.sub(r"\"\\",'\"',L)
            Command  = Command + ' ' + L          
         
         PrintExecutingCommandToLogFile(LogFile, Command)
         
         Command = Command + AddLoggingOption(LogFile)  
         
      else:

         Command = CompilerBinaryPath  
            
         Command = Command + " -mprocessor=" + Device 

         for LocalObject in LocalObjectFileArray:
            L = re.sub("^\"\.",'\"',LocalObject)
            L = re.sub(r"\"\\",'\"',L)
            Command  = Command + ' ' + L


         if not LibFileList == []:
            for DirName in LibFileList:
               Command = Command + ' "' + DirName + '"'

         ### Files ###
         Command = Command + LinkerOptions

         if not LkrFileList == []:
            Command = Command + ",--script=" + '"' + LkrFileList[0] + '"'


         ### Directories ###
         if not LibDirList == []:
            for DirName in LibDirList:
               Command = Command + ",-L" + '"' + DirName + '"'

         #Command = Command + MapOption 

         PrintExecutingCommandToLogFile(LogFile, Command)

         Command = Command + AddLoggingOption(LogFile)

      Command = Command + PrintExitCode(LogFile)
   
      BuildCommand(Command,LogFile,McpFile,"C30Lkr")
         
         
   
   
   if Compiler == "C30" or Compiler == "XC16":
      
      Command = ''
      LocalObjectFileArray = []
      OutputFileType, LibraryBuildOption, Generic16Bit, OtherOptions = GetOutputFileType(McpFile)
      ## Compiler Options ##
      Count = 0

      for SrcFile in SrcFileList:
         Count = Count + 1
         if TempDir == '':
            DotOFiles = '"' + os.path.splitext(os.path.split(SrcFile)[1])[0] + ".o" + '"'
         else:
            DotOFiles = '"' + TempDir + "\\" + os.path.splitext(os.path.split(SrcFile)[1])[0] + ".o" + '"'
            
         LocalObjectFileArray.append(DotOFiles)
         
         if SrcFile.endswith(".c") or SrcFile.endswith(".C"):
            CompilerOptions = ExtractBuildOption(McpFile,FileNumberR[Count - 1],Compiler,CompilerToBeUsed,"C",ScriptDir)
            
            if BuildDirectoryPolicy == "SRCDir":

               SwitchDirOption(CdDirPath[Count - 1])

            ## Decide which compiler to be used, based on the parameters and compiler available in the mcp file
            ##################################################################################################
            Command = CompilerBinaryPath
            ###################################################################################################
            
            if re.search("elf", OutputFileType):
               Command = Command + " -omf=elf"
               
            if Generic16Bit == 0:
               Command = Command + " -mcpu=" + Device + " -x c -c " + '"' + SrcFile + '"' + " -o" + DotOFiles
            else:
               Command = Command + " -mcpu=generic-16bit" + " -x c -c " + '"' + SrcFile + '"' + " -o" + DotOFiles

            if not IncludeDirList == []:
               for IncludeDir in IncludeDirList:
                  Command = Command + " -I" + '"' + IncludeDir + '"'
            Command = Command + ' ' + CompilerOptions 
            
            PrintExecutingCommandToLogFile(LogFile, Command)
            
            Command = Command + AddLoggingOption(LogFile)
            
            #Command = Command + ForceKillTaskIfExists(C30gccExe,LogFile)
            
            Command = Command + PrintExitCode(LogFile)
            
            BuildCommand(Command,LogFile,McpFile,SrcFile)
            
            if BuildDirectoryPolicy == "SRCDir":

               SwitchDirOption(os.path.normpath(os.path.split(McpFile)[0]))
         
         else:
            
            ASMCompilerOptions = ExtractBuildOption(McpFile,FileNumberR[Count - 1],Compiler,CompilerToBeUsed,"ASM",ScriptDir)
            
            if BuildDirectoryPolicy == "SRCDir":

               SwitchDirOption(CdDirPath[Count - 1])
            
            ## Decide which compiler to be used, based on the parameters and compiler available in the mcp file
            ##################################################################################################
            Command = CompilerBinaryPath
            ###################################################################################################
            
            Command = Command + " -mcpu=" + Device + " -c "                #   + '"' + SrcFile + '"' + " -o" + DotOFiles
            
            Command = Command + ' "' + SrcFile + '"' + " -o" + DotOFiles

            if not IncludeDirListASM == []:
               Command = Command + " -Wa"
               for IncludeDir in IncludeDirListASM:
                  Command = Command + ",-I" + '"' + IncludeDir + '"'            
            else:
               Command = Command + " -Wa"
               
            if not ASMCompilerOptions == '':
               Command = Command + ',' + ASMCompilerOptions
               
            PrintExecutingCommandToLogFile(LogFile, Command)
            
            Command = Command + AddLoggingOption(LogFile)
            
            #Command = Command + ForceKillTaskIfExists(C30gccExe,LogFile)
            
            Command = Command + PrintExitCode(LogFile)            
            
            BuildCommand(Command,LogFile,McpFile,SrcFile)
            
            if BuildDirectoryPolicy == "SRCDir":

               SwitchDirOption(os.path.normpath(os.path.split(McpFile)[0]))
            
            
      
      
      ## Linker Options ##
      if LinkerOptions == "ARBS_BUILD_LIBRARY":
         
         ## Decide which ar to be used, based on the parameters and compiler available in the mcp file
         ##################################################################################################
         Command = ArchiverBinaryPath
         ###################################################################################################
         
         if re.search("elf", OutputFileType):
            Command = Command + " -omf=elf"  
            
         McpFileName = ExtractMcpFileNameFromPath(McpFile)
         
         Command = Command + " r " + '"' + McpFileName + ".a" + '"'
         
         for LocalObject in LocalObjectFileArray:
            L = re.sub("^\"\.",'\"',LocalObject)
            L = re.sub(r"\"\\",'\"',L)
            Command  = Command + ' ' + L          
         
         PrintExecutingCommandToLogFile(LogFile, Command)
         
         Command = Command + AddLoggingOption(LogFile)          
         
      else:
         
         ## Decide which Linker to be used, based on the parameters and compiler available in the mcp file
         ##################################################################################################
         Command = CompilerBinaryPath
         ###################################################################################################

         if re.search("elf", OutputFileType):
            Command = Command + " -omf=elf"       

         Command = Command + " -mcpu=" + Device 

         for LocalObject in LocalObjectFileArray:
            L = re.sub("^\"\.",'\"',LocalObject)
            L = re.sub(r"\"\\",'\"',L)
            Command  = Command + ' ' + L 

         if not LibFileList == []:
            for DirName in LibFileList:
               Command = Command + ' "' + DirName + '"'

         ### Files ###
         Command = Command + LinkerOptions

         if LkrFileList == []:
            Command = Command + ",-Tp" + Device + ".gld"
         else:
            Command = Command + ",--script=" + '"' + LkrFileList[0] + '"'
         ### Directories ###
         if not LibDirList == []:
            for DirName in LibDirList:
               Command = Command + ",-L" + '"' + DirName + '"'

         #Command = Command + MapOption 
         
         PrintExecutingCommandToLogFile(LogFile, Command)
         
         Command = Command + AddLoggingOption(LogFile) 

         #Command = Command + ForceKillTaskIfExists(C30gccExe,LogFile)
      
      Command = Command + PrintExitCode(LogFile)
      
      BuildCommand(Command,LogFile,McpFile,"C32Lkr")

   '''
   if not TempDir == '':
      L = re.sub("^\.",'',TempDir)
      L = re.sub(r"\\",'',L)
      TempDir = L
   '''
   
   # return(Command,TempDir)
      
#####################################################
#####################################################
      
#####################################################
#####################################################
   
def FindMcpFiles(FilePath, CompilerToBeUsed):

   DirNames = []
   FileNames = []
   
   McpFiles = []

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
      if file1.endswith(".mcp"):
         Compiler = FindCompiler(file1)
         if CompilerToBeUsed == "ALL":
            if Compiler == "XC8" or Compiler == "XC16" or Compiler == "XC32" or Compiler == "C18":
               McpFiles.append(os.path.normpath(file1))
         else:
            # Compatibility Matrix implemented here #
            if CompilerToBeUsed == "XC8-C18":
               if Compiler == "C18":
                  McpFiles.append(os.path.normpath(file1))
                  
            #elif CompilerToBeUsed == "XC8":
            #   if Compiler == "PICC" or Compiler == "PICC18" or Compiler == "XC8":
            #      McpFiles.append(os.path.normpath(file1))
            #
            #elif CompilerToBeUsed == "XC16":
            #   if Compiler == "C30" or Compiler == "XC16":
            #      McpFiles.append(os.path.normpath(file1))
            #
            #elif CompilerToBeUsed == "XC32":
            #   if Compiler == "C32" or Compiler == "XC32":
            #      McpFiles.append(os.path.normpath(file1))
            #      
            elif CompilerToBeUsed == Compiler:
               McpFiles.append(os.path.normpath(file1))
               
   return(McpFiles)



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
   
################### MAIN !!! ############################   
   
def GetCompilerVersions(CompilerToBeUsed,ScriptDir):

   '''
   AsmWinExe = "MPASMWIN.exe"
   C18CompExe = "mcc18.exe"
   C18LkrExe = "mplink.exe"
   C30gccExe = "pic30-gcc.exe"
   C30HexGenExe = "pic30-bin2hex.exe"
   C32gccExe = "pic32-gcc.exe"
   C32HexGenExe = "pic32-bin2hex.exe"
     
   AsmWinPath = ''
   C18Path = ''
   C30Path = ''
   C32Path = ''

   AsmWinPath, C18Path, C30Path, C32Path = GetCompilerPaths(ScriptDir)

   binAsmWinExe = AsmWinExe
   binC18CompExe = os.path.normpath(os.path.join("bin",C18CompExe))
   binC18LkrExe = os.path.normpath(os.path.join("bin",C18LkrExe))
   binC30gccExe = os.path.normpath(os.path.join("bin",C30gccExe))
   binC30HexGenExe = os.path.normpath(os.path.join("bin",C30HexGenExe))
   binC32gccExe = os.path.normpath(os.path.join("bin",C32gccExe))
   binC32HexGenExe = os.path.normpath(os.path.join("bin",C32HexGenExe))
   
   AsmWinExePath = '"' + os.path.normpath(os.path.join(AsmWinPath,binAsmWinExe)) + '"' 
   C18CompExePath = '"' + os.path.normpath(os.path.join(C18Path,binC18CompExe)) + '"' 
   C18LkrExePath = '"' + os.path.normpath(os.path.join(C18Path,binC18LkrExe)) + '"' 
   C30gccExePath =  '"' + os.path.normpath(os.path.join(C30Path,binC30gccExe)) + '"'
   C30HexGenExePath =  '"' + os.path.normpath(os.path.join(C30Path,binC30HexGenExe)) + '"'
   C32gccExePath =  '"' + os.path.normpath(os.path.join(C32Path,binC32gccExe)) + '"'
   C32HexGenExePath =  '"' + os.path.normpath(os.path.join(C32Path,binC32HexGenExe)) + '"'
  
   C18Version = ''
   C30Version = ''
   C32Version = ''
   VerFileName = "version.txt"
   '''
   
   VersionsPathFile = os.path.join(ScriptDir,"mcpr_modified.mcpr")
   
   if not os.path.exists(VersionsPathFile):
      VersionsPathFile = "C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr"
   
   VersionsPathFilePtr = open(VersionsPathFile,'r')
   
   ASMWINver = ''
   C18Version = ''
   C30Version = ''
   C32Version = ''
   
   XC8Version = ''
   XC16Version = ''
   XC32Version = ''
   
   for Line in VersionsPathFilePtr:
      
      Line = Line.strip("\n|\r")
      
      if re.search("_ASMWIN_VER_=",Line):
         ASMWINver = "ASMWIN Version is: " + re.split("_ASMWIN_VER_=",Line)[1]

      if re.search("_C18_VER_=",Line):
         C18Version = "C18 Version is: " + re.split("_C18_VER_=",Line)[1]

      if re.search("_C30_VER_=",Line):
         C30Version = "C30 Version is: " + re.split("_C30_VER_=",Line)[1]         

      if re.search("_C32_VER_=",Line):
         C32Version = "C32 Version is: " + re.split("_C32_VER_=",Line)[1]

      if re.search("_XC8_VER_=",Line):
         XC8Version = "XC8 Version is: " + re.split("_XC8_VER_=",Line)[1]

      if re.search("_XC16_VER_=",Line):
         XC16Version = "XC16 Version is: " + re.split("_XC16_VER_=",Line)[1]         

      if re.search("_XC32_VER_=",Line):
         XC32Version = "XC32 Version is: " + re.split("_XC32_VER_=",Line)[1]         
   
   '''
   ##########################################
   Command = '"' + C18CompExePath + " -v > " + VerFileName + '"'
   os.system(Command)
   
   if os.path.exists(VerFileName):
      Fptr = open(VerFileName,'r')
      for Line in Fptr:
         Line = Line.strip("\n|\r")
         if re.search("MPLAB C18 ",Line):
            C18Version = "C18 Version is: " + re.split(" ",re.split("MPLAB C18 ",Line)[1])[0]
            break
      Fptr.close()
      os.remove(VerFileName)
   ##########################################
   ##########################################
   Command = '"' + C30gccExePath + " --version > " + VerFileName + '"'
   os.system(Command)
   
   if os.path.exists(VerFileName):
      Fptr = open(VerFileName,'r')
      for Line in Fptr:
         Line = Line.strip("\n|\r")
         if re.search("__C30_VERSION__ == ",Line):
            C30Version = "C30 Version is: " + re.split("__C30_VERSION__ == ",Line)[1]
            break
      Fptr.close()
      os.remove(VerFileName)
   ##########################################
   ##########################################
   Command = '"' + C32gccExePath + " --version > " + VerFileName + '"'
   os.system(Command)
   
   if os.path.exists(VerFileName):
      Fptr = open(VerFileName,'r')
      for Line in Fptr:
         Line = Line.strip("\n|\r")
         if re.search("MPLAB C Compiler for PIC32 MCUs ",Line):
            C32Version = "C32 Version is: " + re.split("MPLAB C Compiler for PIC32 MCUs ",Line)[1]
            break      
      Fptr.close()
      os.remove(VerFileName)
   ##########################################
   '''
   ReturnCommand = '\n## Compiler Version Information ##\n'
   
   if CompilerToBeUsed == '' or CompilerToBeUsed == "ALL":
      ReturnCommand = ReturnCommand + InsertLine() + "\n\n" + XC8Version + "\n" + XC16Version + "\n" + XC32Version
      
   elif CompilerToBeUsed == "C18":
      ReturnCommand = ReturnCommand + InsertLine() + "\n\n" + C18Version 
   elif CompilerToBeUsed == "C30":
      ReturnCommand = ReturnCommand + InsertLine() + "\n\n" + C30Version 
   elif CompilerToBeUsed == "C32":
      ReturnCommand = ReturnCommand + InsertLine() + "\n\n" + C32Version 
   elif CompilerToBeUsed == "XC8":
      ReturnCommand = ReturnCommand + InsertLine() + "\n\n" + XC8Version 
   elif CompilerToBeUsed == "XC8-C18":
      ReturnCommand = ReturnCommand + InsertLine() + "\n\n" + XC8Version + " - Executing C18 Drivers from XC8 Compiler"
   elif CompilerToBeUsed == "XC16":
      ReturnCommand = ReturnCommand + InsertLine() + "\n\n" + XC16Version 
   elif CompilerToBeUsed == "XC32":
      ReturnCommand = ReturnCommand + InsertLine() + "\n\n" + XC32Version       
      
   return(ReturnCommand)

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

def log_pre_build_error(message):
   
   ResultSummaryFile = "0_ALL_Mplab8_ResultSummary.html"
   ResultSummaryFilePtr = open(ResultSummaryFile,"w")
   ResultSummaryFilePtr.write("\n<br>" + message)
   #ResultSummaryFilePtr.write("\n<br>" + "[*FAIL*]")
   # Above line commented to make the job green, if there is any failures due to the missing mplab 8 projects in the given directory.
   ResultSummaryFilePtr.close()
   







############ M A I N !!!!!!!!!!!!!#####################

if __name__ == "__main__":

   CompilerToBeUsed = ''
   DirectoryForScan = ''
   CheckoutRevision = ''
   COSVNLink = ''
   ProjectName = ''
   job_name = ''

   if len(sys.argv) <= 1:
      print "\nError ! \nFeed the Project Directory and/or the compiler to be used for build"
      exit()

   if len(sys.argv) >= 10:
      print "\nError ! \n Unknown number of parameters passed"
      exit()   

   PRCount = 0

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
         elif re.search("-pro=",Parameter.lower()):
            Parameter = re.sub("-pro=",'',Parameter)
            ProjectName = Parameter
         elif re.search("-job=",Parameter.lower()):
            Parameter = re.sub("-job=",'',Parameter)
            job_name = Parameter            
            
   StatisticsFileString = "MPLAB_TYPE:8\n"
   StatisticsFileName = CompilerToBeUsed + "_MPLAB8_Statistics.statinfo"

   EmailErrorFileName = CompilerToBeUsed + "_MPLAB8.errinfo"
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
      log_pre_build_error("\nError ! \nNo directory specified")
      exit()
   
   if not (CompilerToBeUsed == "ALL" or CompilerToBeUsed == "C18" or CompilerToBeUsed == "C30" or CompilerToBeUsed == "C32" or CompilerToBeUsed == "XC8" or CompilerToBeUsed == "XC8-C18" or CompilerToBeUsed == "XC16" or CompilerToBeUsed == "XC32" or CompilerToBeUsed == "PICC" or CompilerToBeUsed == "PICC18" or CompilerToBeUsed == ''):
      log_pre_build_error("Unknown Compiler")
      exit()
   
   
   if CompilerToBeUsed == '':
      CompilerToBeUsed = "ALL"
   
  
   if not os.path.exists(DirectoryForScan):
      log_pre_build_error(DirectoryForScan + "<br>\nError ! \nSpecified Directory not found")
      exit()

   
   if not os.path.exists("mcpr_modified.mcpr"):
      if not os.path.exists("C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr"):
         log_pre_build_error("Error !!\nCompiler Paths References File not found")
         exit()


   CompilerLogMessage = os.path.normpath(os.path.join(os.getcwd(),"CompilerLogMessage.txt"))

   #ResultSummaryFile = os.path.join(os.getcwd(), CompilerToBeUsed + "_ResultSummary.txt")

   
   
   if os.path.exists(CompilerLogMessage):
      os.remove(CompilerLogMessage)
   #if os.path.exists(ResultSummaryFile):
   #   os.remove(ResultSummaryFile)

   
   
   
   ExecutionCount = 0

   McpFileNames =  FindMcpFiles(DirectoryForScan, CompilerToBeUsed)

   
   ResultsFinalDirectory = ''
      
   if ProjectName != '':
      ResultsFinalDirectory = ProjectName + "_" + CompilerToBeUsed
      StatisticsFileName = ProjectName + "_" + StatisticsFileName
   else:
      ResultsFinalDirectory = CompilerToBeUsed
   
   StatisticsFileString = StatisticsFileString + "\nPROJECT_NAME:" + ProjectName + "\n"
   StatisticsFileString = StatisticsFileString + "\nCOMPILER_NAME:" + CompilerToBeUsed + "\n"
   
   Temp = "0_" + ResultsFinalDirectory + "_Mplab8_ResultSummary.html"
   
   StatisticsFileString = StatisticsFileString + "\nRESULT_FILE_NAME:" + Temp + "\n"
   
   ResultSummaryFile = os.path.join(os.getcwd(), Temp)
   
   
   if McpFileNames == []:
      #ResultSummaryFilePtr = open(ResultSummaryFile,"w")
      #ResultSummaryFilePtr.write("No Mplab8 Project files (.mcp) Found")
      #ResultSummaryFilePtr.close()
      log_pre_build_error(DirectoryForScan + "<br>\n\nNo Mplab8 Project files (.mcp) Found")
      print "Error !!\nNo .mcp Found for the given compiler"
      exit()
      
   for McpFileWithPath in McpFileNames:

      OtherCommands = ''
      ExecutionCount = ExecutionCount + 1
      ProjectPath = os.path.normpath(os.path.split(McpFileWithPath)[0])
      
      #BatchFileName = os.path.join(ProjectPath,"build.bat")

      #BatFile = open(BatchFileName,"w")
      #OtherCommands = "\n" + ProjectPath[:2]
      #OtherCommands = OtherCommands + "\ncd \\"
      #OtherCommands = OtherCommands + "\ncd " + '"' + ProjectPath + '"'
      
      OtherCommands = OtherCommands + "\n" + str(ExecutionCount) + ". ARBS_Executing - " + ExtractMcpFileNameFromPath(McpFileWithPath) + ".mcp "
      OtherCommands = OtherCommands + "\n" + "Project Location - " + '"' + ProjectPath + '"' + "\n"
      
      AddMessage(OtherCommands,CompilerLogMessage)
      
      #BatFile.write(OtherCommands)
     
      print str(ExecutionCount) + '/' + str(len(McpFileNames)) + " - Building " + McpFileWithPath
      ScriptsPath = os.getcwd()
      os.chdir(ProjectPath)
      BuildIndividualExecutor(McpFileWithPath,CompilerLogMessage,ScriptsPath,CompilerToBeUsed)
      os.chdir(ScriptsPath)
      
      #if not (TemporaryDir == ProjectPath or TemporaryDir == ''):
      #   BatFile.write("\nrm -rf " + '"' + TemporaryDir + '"')
      #   BatFile.write("\nmd " + '"' + TemporaryDir + '"' + "\n")

      #BatFile.write(Command)
      #BatFile.close()

      #os.system('"' + BatchFileName + '"')

      #os.remove(BatchFileName)

      CompilerLogMessagePtr = open(CompilerLogMessage,"a")
      OtherCommand = "ARBS_Execution_End\n"

      for i in range(100):
         OtherCommand = OtherCommand + "#"
      OtherCommand = OtherCommand + "\n\n\n"   
      CompilerLogMessagePtr.write(OtherCommand)

      CompilerLogMessagePtr.close()


   #############################################################
   ####### Framing Result Summary ##############################
   CompilerLogMessagePtr = open(CompilerLogMessage,"r")

   Fail = 0
   Pass = 0
   PassWithWarnings = 0
   
   
   PassCount = 0
   PassWithWarningsCount = 0
   FailCount = 0

   ProjectCount = 0

   StartScan = 0

   McpFileNames = []
   Result = []
   
   CompilerMessagesArray = []
   _LCompilerMessages = ''
   

   #######################################
   ### Determining individual project's result
   #######################################

   for Line in CompilerLogMessagePtr:

      Line = Line.strip("\n|\r")

      if re.search("ARBS_Execution_End",Line):
         StartScan = 0 
         
         CompilerMessagesArray.append(_LCompilerMessages)
         
         if Fail == 1:
            FailCount = FailCount + 1
            Result.append(2)
         
         elif PassWithWarnings == 1:
            PassWithWarningsCount = PassWithWarningsCount + 1
            Result.append(1)
         
         elif Pass == 1:
            PassCount = PassCount + 1
            Result.append(0)         
         
         else:
            FailCount = FailCount + 1
            Result.append(2)         

      if StartScan == 1:
         
         _LCompilerMessages = _LCompilerMessages + Line + "\n"
         
         if not re.search("_EXECUTING_COMMAND_: ",Line):
         
            if re.search("warning",Line,re.IGNORECASE):
               if Fail == 0:
                  PassWithWarnings = 1


            if re.search("ExitStatus: ",Line):

               if re.sub(' ','',re.split("ExitStatus: ",Line)[1]) == "0":
                  if Fail == 0:
                     Pass = 1
               else:
                  Fail = 1
                  Pass = 0
                  PassWithWarnings = 0

      if re.search("ARBS_Executing - ",Line):
         StartScan = 1
         ProjectCount = ProjectCount + 1
         Fail = 0
         Pass = 0  
         PassWithWarnings = 0
         McpFileNames.append(re.split("ARBS_Executing - ",Line)[1])
         _LCompilerMessages = ''

   #######################################

   MaxCharCount = 0
   Offset = 7
   MaxDashes = 0
   Dashes = ''
   for i in range(len(McpFileNames)):

      if len(McpFileNames[i]) > MaxCharCount:
         MaxCharCount = len(McpFileNames[i])

   
   if ProjectCount > 0:
   
      CentPassCount = round((PassCount/ProjectCount),4) * 100
      CentPassWithWarningsCount = round((PassWithWarningsCount/ProjectCount),4) * 100
      CentFailCount = round((FailCount/ProjectCount),4) * 100
   
   svn_rev, svn_link = get_svn_revision()  
   
   ResultsFilePtr = open(ResultSummaryFile,"w")
   
   ResultsFilePtr.write("<html>\n<head>\n<title>Mplab8_ResultSummary</title>\n</head>\n<body>\n<font face=Courier >\n")
   
   
   ResultSummaryToFile = "<b>ARBS_Build_Mechanism_For_MPLAB_8_Projects Rev 0V1</b>\n"
   
   if job_name != '':
      ResultSummaryToFile = ResultSummaryToFile + "<b>Job Name: </b>" + job_name
      
   ResultSummaryToFile = ResultSummaryToFile + "<b>Directory: </b>" + DirectoryForScan
   _date, _time = get_date_time()
   ResultSummaryToFile = ResultSummaryToFile + "\n" + "<b>Time: </b>" + _date + " " + _time
   
   ResultSummaryToFile = ResultSummaryToFile + "\n" + GetCompilerVersions(CompilerToBeUsed,ScriptsPath) + "\n\n" + InsertLine()
   if not CheckoutRevision == '':
      ResultSummaryToFile = ResultSummaryToFile + "\n\n<b>SVN Link: </b>" + "<a href=%s>%s</a>"%(re.sub(" ","%20",COSVNLink),COSVNLink) + "\n<b>Checkout Revision: </b>" + CheckoutRevision + "\n\n" + InsertLine()
   elif svn_link != '':
      ResultSummaryToFile = ResultSummaryToFile + "\n\n<b>SVN Link: </b>" + "<a href=%s>%s</a>"%(re.sub(" ","%20",svn_link),svn_link) + "\n<b>Checkout Revision: </b>" + svn_rev + "\n\n" + InsertLine()
      
   ResultSummaryToFile = ResultSummaryToFile + "\n\n<b>Test Summary:</b>\n-------------"
   Temp = "\nTotal Number of Projects Executed: " + str(ProjectCount)
   ResultSummaryToFile = ResultSummaryToFile + Temp
   StatisticsFileString = StatisticsFileString + "\nTOTAL_NUMBER_OF_PROJECTS:" + str(ProjectCount) + "\n"
   
   ########################################
   # Detect the max no of spaces to be inserted, before displaying the %
   MaxLenSp = 0
   MaxLenSp = len(str(ProjectCount))
   
   if len(str(PassCount)) > MaxLenSp:
      MaxLenSp = len(str(PassCount))
   if len(str(PassWithWarningsCount)) > MaxLenSp:
      MaxLenSp = len(str(PassWithWarningsCount))
   if len(str(FailCount)) > MaxLenSp:
      MaxLenSp = len(str(FailCount))
   
   #########################################
   Temp = "\nPassed                           : " + str(PassCount) + SpaceTobeInserted(MaxLenSp,PassCount) + '(' + str(CentPassCount) + '%)'
   ResultSummaryToFile = ResultSummaryToFile + Temp
   StatisticsFileString = StatisticsFileString + "\nTOTAL_PASS_COUNT:" + str(PassCount) + "\n" + "\nTOTAL_PASS_CENT:" + str(CentPassCount) + "\n"
   
   Temp = "\nPassed with Warnings             : " + str(PassWithWarningsCount) + SpaceTobeInserted(MaxLenSp,PassWithWarningsCount) + '(' + str(CentPassWithWarningsCount) + '%)'
   ResultSummaryToFile = ResultSummaryToFile + Temp
   StatisticsFileString = StatisticsFileString + "\nTOTAL_PASS_WARN_COUNT:" + str(PassWithWarningsCount) + "\n" + "\nTOTAL_PASS_WARN_CENT:" + str(CentPassWithWarningsCount) + "\n"
   
   Temp = "\nFailed                           : " + str(FailCount)  + SpaceTobeInserted(MaxLenSp,FailCount) + '(' + str(CentFailCount) + '%)' + "\n"
   ResultSummaryToFile = ResultSummaryToFile + Temp
   StatisticsFileString = StatisticsFileString + "\nTOTAL_FAIL_COUNT:" + str(FailCount) + "\n" + "\nTOTAL_FAIL_CENT:" + str(CentFailCount) + "\n"
   
   if not CheckoutRevision == '':
      StatisticsFileString = StatisticsFileString + "\nSVN_REPO_LINK:" + str(COSVNLink) + "\n" + "\nCHECKED_OUT_REVISION:" + str(CheckoutRevision) + "\n"
   else:
      StatisticsFileString = StatisticsFileString + "\nSVN_REPO_LINK:" + str(svn_link) + "\n" + "\nCHECKED_OUT_REVISION:" + str(svn_rev) + "\n"
      
   ResultSummaryToFile = ResultSummaryToFile + "\n" + InsertLine() + "\n\n"
   
   ResultSummaryToFile = ResultSummaryToFile + "\n\n<b>Individual Project Execution Result:</b>\n-----------------------------------------\n"
   
   ResultSummaryToFile = ResultSummaryToFile + "<a href=\"Archives/Mplab8/" + ResultsFinalDirectory + "/" + "Results_ALL_PASS.txt\">"
   ResultSummaryToFile = ResultSummaryToFile + "Click here for Pass only messages" 
   ResultSummaryToFile = ResultSummaryToFile + "<br></a>"
   
   ResultSummaryToFile = ResultSummaryToFile + "<a href=\"Archives/Mplab8/" + ResultsFinalDirectory + "/" + "Results_ALL_FAIL.txt\">"
   ResultSummaryToFile = ResultSummaryToFile + "Click here for Fail only messages" 
   ResultSummaryToFile = ResultSummaryToFile + "<br></a>\n"
   
   
   for i in range(len(McpFileNames)):

      MaxDashes = (MaxCharCount - len(McpFileNames[i])) + Offset - len(str(i+1))
      Dashes = ''
      for j in range(MaxDashes): 
         Dashes = Dashes + '-'

      ResultTest = ''
      
      ResultTest = "<a href=\"Archives/Mplab8/" + ResultsFinalDirectory + "/" + str(i+1) + ".txt\">"
      
      if Result[i] == 0:
         ResultTest = ResultTest + "[ PASS ]</a>"
      elif Result[i] == 1:
         ResultTest = ResultTest + "[ PASS with warnings ]</a>"
      else:
         ResultTest = ResultTest + "[*FAIL*]</a>"
         
      ResultSummaryToFile = ResultSummaryToFile + str(i+1) + ". " + McpFileNames[i] + Dashes + ResultTest + "\n"
   
   ResultSummaryToFile = ResultSummaryToFile + "\n\n" + ("+" * 100)
   ResultSummaryToFile = re.sub("\n","<br>\n",ResultSummaryToFile)
   ResultSummaryToFile = re.sub("  ","&nbsp;&nbsp;",ResultSummaryToFile)

   ResultsFilePtr.write(ResultSummaryToFile)
   
   ResultsFilePtr.close()
   
   
   ###################################################################
   # Generating the Results File in the results Directory
   ###################################################################
   ResultsDirectory = os.path.join(os.getcwd(),"Archives")
   ResultsDirectory = os.path.join(ResultsDirectory,"Mplab8")
   ResultsDirectory = os.path.join(ResultsDirectory,ResultsFinalDirectory)
   
   UsageResultsDirectory = '"' + ResultsDirectory + '"'
   
   if os.path.exists(ResultsDirectory):
      RemoveCommand = "rmdir /S /Q " + os.path.normpath(UsageResultsDirectory)
      os.system('"' + RemoveCommand + '"')
      
   CreateResultsDirectoryCommand = "mkdir " + os.path.normpath(UsageResultsDirectory)
   os.system('"' + CreateResultsDirectoryCommand + '"')
   
   CompilerResultMessages = ''   
   
   for i in range(len(McpFileNames)):
   
      ResultFile = os.path.join(ResultsDirectory,str(i+1) + ".txt")
      
      ResultFilePtr = open(ResultFile,"w")
      
      #ResultFilePtr.write(ProjectLocation[i] + "\n\n")
      
      ResultFilePtr.write("Result for Mplab8 ProjectFile: " + McpFileNames[i] + "\n\n")
      
      if Result[i] == 0:
         ResultMessage = "PASS"
      elif Result[i] == 1:
         ResultMessage = "PASS with Warnings" 
      else:
         ResultMessage = "FAIL" 
         
      ResultFilePtr.write("Result: " + ResultMessage + "\n\n" + ('*' * 200) + "\n")
      
      ResultFilePtr.write(CompilerMessagesArray[i] + "\n\n" + ('*' * 200) + "\n")
      
      ResultFilePtr.close()
      
   
   ###########################################################
   # Defining .PASS and .FAIL files
   PassSummary = ''
   PassCompilerMessages = ''
   
   FailSummary = ''
   FailCompilerMessages = ''
   
   for i in range(len(McpFileNames)):
            
      MaxDashes = (MaxCharCount - len(McpFileNames[i])) + Offset - len(str(i+1))
      Dashes = ''
      for j in range(MaxDashes): 
         Dashes = Dashes + '-'
      
      if Result[i] == 0:
         ResultMessage = "PASS"
      elif Result[i] == 1:
         ResultMessage = "PASS with Warnings" 
      else:
         ResultMessage = "FAIL" 
  
      if Result[i] <= 1:
         PassSummary = PassSummary + str(i+1) + ". " + McpFileNames[i] + Dashes + ResultMessage + "\n"
         PassCompilerMessages = PassCompilerMessages + "\n\n" + ('*' * 200) + "\n" + str(i+1) + ". " + McpFileNames[i] + "\n" + CompilerMessagesArray[i] + "\n"
      else:
         FailSummary = FailSummary + str(i+1) + ". " + McpFileNames[i] + Dashes + ResultMessage + "\n"
         FailCompilerMessages = FailCompilerMessages + "\n\n" + ('*' * 200) + "\n" + str(i+1) + ". " + McpFileNames[i] + "\n" + CompilerMessagesArray[i] + "\n"
         
         
   if PassSummary == '':
      PassSummary = "No Projects found Passed"

   if FailSummary == '':
      FailSummary = "No Projects found Failed"      
      
   PassResultFile = os.path.join(ResultsDirectory,"Results_ALL_PASS.txt")
   FailResultFile = os.path.join(ResultsDirectory,"Results_ALL_FAIL.txt")

   PassResultFilePtr = open(PassResultFile,"w")
   FailResultFilePtr = open(FailResultFile,"w")   
   
   PassResultFilePtr.write(PassSummary + PassCompilerMessages)
   FailResultFilePtr.write(FailSummary + FailCompilerMessages)
   
   PassResultFilePtr.close()
   FailResultFilePtr.close()
   
   StatisticsFilePtr = open(StatisticsFileName,"w")
   StatisticsFilePtr.write(StatisticsFileString)
   StatisticsFilePtr.close()
   '''
   ResultSummaryFilePtr.write(ResultSummaryToFile + InsertLine() + "\n\n\n\n\nIndividual Project Execution Messages:\n\n")

   OtherCommand = ''
   for i in range(100):
         OtherCommand = OtherCommand + "#"

   ResultSummaryFilePtr.write(OtherCommand + "\n")

   CompilerLogMessagePtr = open(CompilerLogMessage,'r')

   for LLine in CompilerLogMessagePtr:
      ResultSummaryFilePtr.write(LLine)

   CompilerLogMessagePtr.close()
   ResultSummaryFilePtr.close()
   os.remove(CompilerLogMessage)
   
   ############################################
   # Added by Shankar on 28 NOV to meet Nagesh's Requirements
   ############################################
   
   PassResultSummaryToFile = ''
   FailResultSummaryToFile = ''

   PassResultMessageToFile = ''
   FailResultMessageToFile = ''
   
   FailCount = 0
   PassCount = 0
   
   for i in range(len(McpFileNames)):

      if Result[i] <= 1:
         MaxDashes = (MaxCharCount - len(McpFileNames[i])) + Offset - len(str(FailCount+1))
         Dashes = ''
         for j in range(MaxDashes): 
            Dashes = Dashes + '-'

         FailCount = FailCount + 1

         FailResultSummaryToFile = FailResultSummaryToFile + str(FailCount) + ". " + McpFileNames[i] + Dashes + ' [ ' + Result[i] + ' ]' + "\n"
         
         FailResultMessageToFile = FailResultMessageToFile + "\n***************************************************************************************\n"
         
         FailResultMessageToFile = FailResultMessageToFile + "\n" + str(FailCount) + ". Executing for MCP File: " + McpFileNames[i] + "\n"
         
         FailResultMessageToFile = FailResultMessageToFile + CompilerMessagesArray[i]
         
         
      else:
         MaxDashes = (MaxCharCount - len(McpFileNames[i])) + Offset - len(str(PassCount+1))
         Dashes = ''
         for j in range(MaxDashes): 
            Dashes = Dashes + '-'

         PassCount = PassCount + 1 

         PassResultSummaryToFile = PassResultSummaryToFile + str(PassCount) + ". " + McpFileNames[i] + Dashes + ' [ ' + Result[i] + ' ]' + "\n"

         PassResultMessageToFile = PassResultMessageToFile + "\n***************************************************************************************\n"
         
         PassResultMessageToFile = PassResultMessageToFile + "\n" + str(PassCount) + ". Executing for MCP File: " + McpFileNames[i] + "\n"
         
         PassResultMessageToFile = PassResultMessageToFile + CompilerMessagesArray[i]
                  

         
         
   PASSResultSummaryFilePtr = open(os.path.join(os.getcwd(), CompilerToBeUsed + "_ResultSummary.PASS"),"w")
   FAILResultSummaryFilePtr = open(os.path.join(os.getcwd(), CompilerToBeUsed + "_ResultSummary.FAIL"),"w")
   
   PASSResultSummaryFilePtr.write(PassResultSummaryToFile + "\n\n\n\n")
   PASSResultSummaryFilePtr.write(PassResultMessageToFile)
   
   FAILResultSummaryFilePtr.write(FailResultSummaryToFile + "\n\n\n\n")
   FAILResultSummaryFilePtr.write(FailResultMessageToFile)
   
   PASSResultSummaryFilePtr.close()
   FAILResultSummaryFilePtr.close()
   '''