import os
import sys
import re
import stat
import shutil        
import subprocess
import time
import stat


def GetValueReplacement(RCA1, CommaSeparated, EquivalentCompilerCommand):
   Command = ''
   Array = re.split(",",RCA1)
   
   for Elements in Array:
   
      if Elements != '':
         if CommaSeparated.upper() == "Y":
            Command = Command + ","
         else:
            Command = Command + " "

         Command = Command + EquivalentCompilerCommand + Elements
         
   return(Command)




def GetValueBasedReplacement(RCA1, ValueBase, CommaSeparated, EquivalentCompilerCommand):
   Command = ''
   
   if RCA1 == ValueBase:

      if CommaSeparated.upper() == "Y":
         Command = Command + ","
      else:
         Command = Command + " "
      
      Command = Command + EquivalentCompilerCommand
   
   return(Command)
   
   

def GetPlusMinusReplacement(RCA1, CommaSeparatedCommand, EquivalentCompilerCommand):
   
   Command = ''
   Invert = 0
   
   EquivalentCompilerCommand = re.sub(" ","",EquivalentCompilerCommand)
   
   Array = re.split(",",EquivalentCompilerCommand)
   for Elements in Array:
      
      Invert = 0
      
      if CommaSeparatedCommand.upper() == "Y":
         Command = Command + ","
      else:
         Command = Command + " "         
      
      if re.search("^!",Elements):
         Elements = re.sub("!","",Elements)
         Invert = 1
      
      if RCA1 == "0":
         if Invert == 0:
            Command = Command + "-" + Elements
         else:
            Command = Command + "+" + Elements
      else:
         if Invert == 0:
            Command = Command + "+" + Elements
         else:
            Command = Command + "-" + Elements

   return(Command)



def GetConditionalValueReplacement(ReceivedCommandArray, ReplacementCondition, CommaSeparatedCommand, EquivalentCompilerCommand, RCA1):
   
   Command = ''
   
   Found = 0
   
   ReplacementCondition = re.sub(" ","",ReplacementCondition)
   
   for Element in ReceivedCommandArray:
      if Element == ReplacementCondition:
         Found = 1
   
   if Found == 1:
      if CommaSeparatedCommand == "Y":
         Command = Command + ","
      else:
         Command = Command + " "
      
      Command = Command + EquivalentCompilerCommand + RCA1
 
   return(Command)



def FrameCompilerCommand(ReceivedCommandFromMcpFile, MCPFileCommands, ValueBase, CompilerLinkerOption, CommaSeparatedCommand, CommandReplacementNature, ReplacementCondition, EquivalentCompilerCommand, PICCAvailability, PICC18Availability, XC8Availability, McpfileNativeCompiler):
   
   ReceivedCommandFromMcpFile = ReceivedCommandFromMcpFile.strip(" ")
   ReceivedCommandFromMcpFile = ReceivedCommandFromMcpFile.strip("\n")
   
   ReceivedCommandArray = re.split(" ",ReceivedCommandFromMcpFile)
   
   CompilerCommand = ''
   LinkerCommand = ''
   
   GroupCommand = 0
   SkipThisLine = 0
   
   for i in range(len(MCPFileCommands)):
      
      Command = ''
      Found = 0

      if re.search("__GROUP_APPEND_START__",MCPFileCommands[i]):
         GroupCommand = 1
         SkipThisLine = 1
         
         if CommaSeparatedCommand[i].upper() == "Y":
            Command = Command + "," + (re.split(":",MCPFileCommands[i])[1]).strip(" ")
         else:
            Command = Command + " " + (re.split(":",MCPFileCommands[i])[1]).strip(" ")
         
      if re.search("__GROUP_APPEND_END__",MCPFileCommands[i]):
         GroupCommand = 0
         SkipThisLine = 1
         
      if SkipThisLine == 0:
      
         for j in range(len(ReceivedCommandArray)):

            if re.search("=",ReceivedCommandArray[j]):
               Array = re.split("=",ReceivedCommandArray[j])
               RCA1 = ''
               for k in range(len(Array)):
                  if k == 0:
                     RCA0 = Array[k]
                  elif k == 1:
                     RCA1 = RCA1 + Array[k]
                  else:
                     RCA1 = RCA1 + "=" + Array[k]
                  
               if RCA0 == MCPFileCommands[i]:
                  Found = 1
                  break

         if Found == 1:
            if CommandReplacementNature[i] == "__VALUE_REPLACEMENT__":
               Command = Command + GetValueReplacement(RCA1,CommaSeparatedCommand[i],EquivalentCompilerCommand[i])  
            
            elif CommandReplacementNature[i] == "__VALUE_BASED_REPLACEMENT__":
               Command = Command + GetValueBasedReplacement(RCA1, ValueBase[i], CommaSeparatedCommand[i], EquivalentCompilerCommand[i])
            
            elif CommandReplacementNature[i] == "__PLUS_MINUS__":
               Command = Command + GetPlusMinusReplacement(RCA1, CommaSeparatedCommand[i], EquivalentCompilerCommand[i])
            
            elif CommandReplacementNature[i] == "__CONDITIONAL_VALUE_REPLACEMENT__":
               Command = Command + GetConditionalValueReplacement(ReceivedCommandArray, ReplacementCondition[i], CommaSeparatedCommand[i], EquivalentCompilerCommand[i], RCA1)
            
            Command = re.sub("%2C",",",Command)
      else:
         
         SkipThisLine = 0
      
      AvailabilityOptionForCompiler = ''
      
      McpfileNativeCompiler = McpfileNativeCompiler.upper()
      
      if McpfileNativeCompiler == "PICC":
         AvailabilityOptionForCompiler = PICCAvailability[i]
      elif McpfileNativeCompiler == "PICC18":
         AvailabilityOptionForCompiler = PICC18Availability[i]
      elif McpfileNativeCompiler == "XC8":
         AvailabilityOptionForCompiler = XC8Availability[i]
      
      
      if AvailabilityOptionForCompiler.upper() != "N":
         if re.search("C",CompilerLinkerOption[i].upper()):
            CompilerCommand = CompilerCommand + Command

         if re.search("L",CompilerLinkerOption[i].upper()):
            LinkerCommand = LinkerCommand + Command

   return(CompilerCommand, LinkerCommand)
   
   
   

def Get(Command, McpfileNativeCompiler, OptionsCSVfile):

   MCPFileCommands = []
   ValueBase = []
   CompilerLinkerOption = []
   CommaSeparatedCommand = []
   CommandReplacementNature = []
   ReplacementCondition = []
   EquivalentCompilerCommand = []
   PICCAvailability = []
   PICC18Availability = []
   XC8Availability = []
   
   
   CsvFilePtr = open(OptionsCSVfile,"r")
   for Line in CsvFilePtr:
      Line = Line.strip("\n")
      if not re.search("^#",Line):
         Array = re.split(",",Line)
         if len(Array) >= 7:
            MCPFileCommands.append(Array[0].strip(" "))
            ValueBase.append(Array[1].strip(" "))
            CompilerLinkerOption.append(Array[2].strip(" "))
            CommaSeparatedCommand.append(Array[3].strip(" "))
            CommandReplacementNature.append(Array[4].strip(" "))
            ReplacementCondition.append(Array[5].strip(" "))
            EquivalentCompilerCommand.append(Array[6].strip(" "))
            PICCAvailability.append(Array[7].strip(" "))
            PICC18Availability.append(Array[8].strip(" "))
            XC8Availability.append(Array[9].strip(" "))
            
   CsvFilePtr.close()
   
   compiler_options,linker_options = FrameCompilerCommand(Command, MCPFileCommands, ValueBase, CompilerLinkerOption, CommaSeparatedCommand, CommandReplacementNature, ReplacementCondition, EquivalentCompilerCommand, PICCAvailability, PICC18Availability, XC8Availability, McpfileNativeCompiler)
   
   compiler_options = compiler_options + " -D__DEBUG=1 -g --asmlist"
   linker_options = linker_options + " -D__DEBUG=1 -g --asmlist"
   
   return(compiler_options,linker_options)      
      
      
      
      
      
      
      
      
      
      
      
      
      