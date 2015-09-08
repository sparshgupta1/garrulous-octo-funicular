import os
import sys
import re
import stat
import shutil        
import subprocess
import time
import stat
import picc_options_from_csv


def GetCommand(ReceivedCommand, McpfileNativeCompiler):
   
   CompilerDefaultOptionsArray = ''
   LinkerDefaultOptionsArray = ''
   
   if McpfileNativeCompiler == "PICC":
      CompilerDefaultOptions = "C6=31 DB=0 DC=9 DF=0 DD=1 C2=0 C3=0 DE=1 D7=1 11E=0 121=0 122=0 123=0 124=0 125=0 11F=94 C7=1"
      LinkerDefaultOptions = "C9=23,22,21 FE=31 EC=1 F0=0 EF=1 EE=0 104=0 E9= C4=0 F2= F3= F4= F8=1 F5= F9=0 FA=0 FB=0 C0=0 C1=0 BD=0 BC=0 BB=0 BF=0 BE=0 B8= 101=0 103= 102=0 BA= FF=0 100=0 106=0 109=0 10A=1 10B=0 10C=0 10E=0 10F=1 110=0 118=0 116=0 117= 10D=0 114=-1 113=-1 111=0 115=-1"

   elif McpfileNativeCompiler == "PICC18":
      CompilerDefaultOptions = "C6=31 DB=0 DC=9 DF=0 DD=1 C2=0 C3=0 DE=1 D7=1 11E=0 121=0 122=0 123=0 124=0 125=0 11F=94 C7=1"
      LinkerDefaultOptions = "C6=31 DB=0 DC=9 DF=0 DD=1 C2=0 C3=0 DE=1 D7=1 11E=0 121=0 122=0 123=0 124=0 125=0 11F=94 C9=23,22,21 FE=31 EC=1 F0=0 EF=1 EE=0 104=0 E9= C4=0 F2= F3= F4= F8=0 F5= F9=0 FA=0 FB=0 C0=1 C1=0 BD=0 BC=0 BB=0 BF=0 BE=0 B8= 101=0 103= 102=0 BA= FF=0 100=0 106=0 109=0 10A=1 10B=0 10C=0 10E=0 10F=1 110=1 118=0 116=0 117= 10D=0 114=-1 113=-1 111=0 115=-1"

   else:
      CompilerDefaultOptions = "C6=31 DB=0 DC=9 DF=0 DD=1 C2=0 C3=0 DE=1 D7=1 11E=0 121=0 122=0 123=0 124=0 125=0 11F=94 C7=1"
      LinkerDefaultOptions = "C6=31 DB=0 DC=9 DF=0 DD=1 C2=0 C3=0 DE=1 D7=1 11E=0 121=0 122=0 123=0 124=0 125=0 11F=94 C9=24,23,22,21 FE=31 EC=1 F0=0 EF=1 EE=0 104=0 E9= C4=0 F2= F3= F4= F8=1 F5= F9=0 FA=0 FB=0 C0=0 C1=0 BD=0 BC=0 BB=0 BF=0 BE=0 B8= 101=0 103= 102=0 BA= FF=0 100=0 106=0 109=0 10A=1 10B=0 10C=0 10E=1 10F=1 110=1 118=0 116=0 117= 10D=0 114=-1 113=-1 111=0 115=-1"
   
   
   CompilerDefaultOptionsArray = re.split(" ",CompilerDefaultOptions)
   LinkerDefaultOptionsArray = re.split(" ",LinkerDefaultOptions)
   
   DafaultOptionsArray = []
   
   AllDefaultOptionsArray = CompilerDefaultOptionsArray + LinkerDefaultOptionsArray
   
   for i in AllDefaultOptionsArray:
      Found = 0
      i = i.strip(" ")
      i = i.strip("\n")
      DO = re.split("=",i)[0]
      for j in DafaultOptionsArray:
         j = j.strip(" ")
         j = j.strip("\n")
         DO1 = re.split("=",j)[0]
         if DO == DO1:
            Found = 1
            break

      if Found == 0:
         DafaultOptionsArray.append(i)
   
   ReceivedCommandOptionsArray = re.split(" ",ReceivedCommand) 

   for i in ReceivedCommandOptionsArray:
      Found = 0
      i = i.strip(" ")
      i = i.strip("\n")
      DO = re.split("=",i)[0]
      for j in DafaultOptionsArray:
         j = j.strip(" ")
         j = j.strip("\n")
         DO1 = re.split("=",j)[0]
         if DO == DO1:
            if i == j:
               Found = 1
               break
            else:
               DafaultOptionsArray.remove(j)
               break

      if Found == 0:
         if i != '':
            DafaultOptionsArray.append(i)   
   
   return(DafaultOptionsArray)
   
  
def InScriptsExtract(command, McpfileNativeCompiler):
   
   command_list = GetCommand(command, McpfileNativeCompiler)
   
   # command_list = re.split(" ",command)
   # build_options = build_options + command_list[i] + " "

   preprocessasm = ""
   runtimeoptions = ""
   optimisationsettings = ""
   messages = ""
   idlength = ""
   codeanddatamodel = ""
   addrqualifiers = ""
   reportoptions = ""
   inhx032 = ""
   definedmacros = ""
   undefinedmacros = ""
   linkoptions = "" 
   htmloption = ""
   compiler_options = ""
   linker_options = ""

   DD_Value = ''
   DC_Value = ''

   for i in range(len(command_list)):
      
      ###################### COMPILER OPTIONS #############################
      ######### Defined Macros and Undefined macros ######################
      
      if re.search("D1=",command_list[i]):
         command_list[i] = re.sub("D1=",'',command_list[i])
         if command_list[i] == '':
            command_list[i] = '';
         elif re.search(",",command_list[i]):
            Array = re.split(",",command_list[i])
            command_list[i] = ''
            for j in Array:
               command_list[i] = command_list[i] + "-D" + j + " "
         else:
            command_list[i] = " -D" + command_list[i]
         definedmacros = definedmacros + command_list[i] + " "

      elif re.search("D5=",command_list[i]):
         command_list[i] = re.sub("D5=",'',command_list[i])
         if command_list[i] == '':
            command_list[i] = '';
         elif re.search(",",command_list[i]):
            Array = re.split(",",command_list[i])
            command_list[i] = ''
            for j in Array:
               command_list[i] = command_list[i] + "-U" + j + " "
         else:
            command_list[i] = "-U" + command_list[i]
         undefinedmacros = undefinedmacros + command_list[i] + " "
         
      ######### Pre processor assembler -P ######################
         
      elif(command_list[i] == "D7=0"):
         command_list[i] = ""
         preprocessasm = preprocessasm + command_list[i]
      
      
      elif(command_list[i] == "D7=1"):
         command_list[i] = "-P"
         preprocessasm = preprocessasm + command_list[i]
         
         
      ######## Identifier Length -N ##############################
      
      elif re.search("C6=",command_list[i]):
         command_list[i] = re.sub("C6=","-N",command_list[i])
         idlength = command_list[i]
         
      ####### Optimization settings asm, speed, space, debug, global #######
      
      elif(command_list[i] == "DE=0"):
         command_list[i] = ",-asm"
         optimisationsettings = optimisationsettings + command_list[i]
      
      elif(command_list[i] == "DE=1"):
         command_list[i] = ",+asm"
         optimisationsettings = optimisationsettings + command_list[i]
         
      elif(command_list[i] == "C2=0"):
         command_list[i] = ",-speed" + ",+space"
         optimisationsettings = optimisationsettings + command_list[i]
         
      elif(command_list[i] == "C2=1"):
         command_list[i] = ",+speed" + ",-space"
         optimisationsettings = optimisationsettings + command_list[i]
         
      elif(command_list[i] == "C3=0"):
         command_list[i] = ",-debug"
         optimisationsettings = optimisationsettings + command_list[i]
         
      elif(command_list[i] == "C3=1"):
         command_list[i] = ",+debug"
         optimisationsettings = optimisationsettings + command_list[i]
         
      elif re.search("DD=",command_list[i]):
         DD_Value = re.split("DD=",command_list[i])[1]
         command_list[i] = ''
         
      elif re.search("DC=",command_list[i]):
         DC_Value = re.split("DC=",command_list[i])[1]
         command_list[i] = ''
      ########## Messages Verbose, warning levels #######################################
      
      elif(command_list[i] == "DF=0"):
         command_list[i] = ""
         messages = messages + command_list[i]
         
      elif(command_list[i] == "DF=1"):
         command_list[i] = " -v"
         messages = messages + command_list[i]
         
      elif re.search("DB",command_list[i]):
         command_list[i] = re.sub("DB","--warn",command_list[i])
         messages = messages + command_list[i]
         
      ########### Operation Mode Pro or lite #############################################
      
      elif(command_list[i] == "11F=96"):
         command_list[i] = "--mode=lite"
         
         
      elif(command_list[i] == "11F=94"):
         command_list[i] = ""
         
         
      ############ Address Qualifiers ignore, request, require, reject ######################################################
      
      elif(command_list[i] == "11E=0"):
         command_list[i] = "--addrqual=ignore"
         addrqualifiers = addrqualifiers + command_list[i] + " "
         
      elif(command_list[i] == "11E=1"):
         command_list[i] = "--addrqual=request"  
         addrqualifiers = addrqualifiers + command_list[i] + " "
         
      elif(command_list[i] == "11E=2"):
         command_list[i] = "--addrqual=require"  
         addrqualifiers = addrqualifiers + command_list[i] + " "
         
      elif(command_list[i] == "11E=3"):
         command_list[i] = "--addrqual=reject"
         addrqualifiers = addrqualifiers + command_list[i] + " "
         
      ############################## LINKER OPTIONS ##################################################################
      
      ############################## Run Time Options - clear,init,keep,download,stackwarn,config,clib,plib ##########

      elif(command_list[i] == "EC=0"):
         command_list[i] = ",-clear"
         runtimeoptions = runtimeoptions + command_list[i]
         
      elif(command_list[i] == "EC=1"):
         command_list[i] = ",+clear"
         runtimeoptions = runtimeoptions + command_list[i]
         
         
      elif(command_list[i] == "EF=0"):
         command_list[i] = ",-init"
         runtimeoptions = runtimeoptions + command_list[i]
         
      
      elif(command_list[i] == "EF=1"):
         command_list[i] = ",+init"
         runtimeoptions = runtimeoptions + command_list[i]
         
         
      elif(command_list[i] == "F0=0"):
         command_list[i] = ",-keep"
         runtimeoptions = runtimeoptions + command_list[i]
         

      elif(command_list[i] == "F0=1"):
         command_list[i] = ",+keep"
         runtimeoptions = runtimeoptions + command_list[i]
         
         
      elif(command_list[i] == "FA=0"):
         command_list[i] = ",-download"
         runtimeoptions = runtimeoptions + command_list[i]
         
         
      elif(command_list[i] == "FA=1"):
         command_list[i] = ",+download"
         runtimeoptions = runtimeoptions + command_list[i]
         
         
      elif(command_list[i] == "10F=0"):
         command_list[i] = ",-clib"
         runtimeoptions = runtimeoptions + command_list[i]
         
         
      elif(command_list[i] == "10F=1"):
         command_list[i] = ",+clib"
         runtimeoptions = runtimeoptions + command_list[i]
         
      if(McpfileNativeCompiler == "PICC"):
      
         if(command_list[i] == "F9=1"):
            command_list[i] = ",+resetbits"
            runtimeoptions = runtimeoptions + command_list[i]

         elif(command_list[i] == "F9=0"):
            command_list[i] = ",-resetbits"
            runtimeoptions = runtimeoptions + command_list[i]          

         elif(command_list[i] == "F8=1"):
            command_list[i] = ",+osccal"
            runtimeoptions = runtimeoptions + command_list[i]

         elif(command_list[i] == "F8=0"):
            command_list[i] = ",-osccal"
            runtimeoptions = runtimeoptions + command_list[i] 
            
         elif re.search("F5=",command_list[i]):
            Temp = re.split("F5=",command_list[i])[1]
            if Temp != '':
               runtimeoptions = runtimeoptions + ",+oscval:" + Temp
            
         elif(command_list[i] == "C1=1"):
            command_list[i] = ",+stackcall"
            runtimeoptions = runtimeoptions + command_list[i]

         elif(command_list[i] == "C1=0"):
            command_list[i] = ",-stackcall"
            runtimeoptions = runtimeoptions + command_list[i] 
      
      else:
      
         if(command_list[i] == "C0=0"):
            command_list[i] = ",-stackwarn"
            runtimeoptions = runtimeoptions + command_list[i]


         elif(command_list[i] == "C0=1"):
            command_list[i] = ",+stackwarn"
            runtimeoptions = runtimeoptions + command_list[i]


         elif(command_list[i] == "10E=0"):
            command_list[i] = ",-config"
            runtimeoptions = runtimeoptions + command_list[i]


         elif(command_list[i] == "10E=1"):
            command_list[i] = ",+config"
            runtimeoptions = runtimeoptions + command_list[i]  

         elif(command_list[i] == "110=0"):
            command_list[i] = ",-plib"
            runtimeoptions = runtimeoptions + command_list[i]


         elif(command_list[i] == "110=1"):
            command_list[i] = ",+plib"
            runtimeoptions = runtimeoptions + command_list[i]            
      
      ######## Linker Options - fill,codeoffset,checksum,errata,debugger,inhx032 ##########################################
      
      if re.search("F2=",command_list[i]):
         command_list[i] = re.sub("F2=",'',command_list[i])
         if command_list[i] == '':
            command_list[i] = '';      
         else:
            command_list[i] = " --fill=" + command_list[i]
         linkoptions = linkoptions + command_list[i]
         
      elif re.search("E9=",command_list[i]):
         command_list[i] = re.sub("E9=",'',command_list[i])
         if command_list[i] == '':
            command_list[i] = '';      
         else:
            command_list[i] = " --codeoffset=" + command_list[i]
         linkoptions = linkoptions + command_list[i]
         
      elif re.search("F3=",command_list[i]):
         command_list[i] = re.sub("F3=",'',command_list[i])
         if command_list[i] == '':
            command_list[i] = '';      
         else:
            command_list[i] = " --checksum=" + command_list[i]
         linkoptions = linkoptions + command_list[i]
         
      elif re.search("F4=",command_list[i]):
         command_list[i] = re.sub("F4=",'',command_list[i])
         if command_list[i] == '':
            command_list[i] = '';      
         else:
            command_list[i] = " --errata=" + command_list[i]
         linkoptions = linkoptions + command_list[i]
         
      elif(command_list[i] == "FE=31"):
         command_list[i] = ""
         linkoptions = linkoptions + command_list[i]
         
      elif(command_list[i] == "FE=32"):
         command_list[i] = ""
         linkoptions = linkoptions + command_list[i]
         
      elif(command_list[i] == "FE=33"):
         command_list[i] = " --debugger=icd2"
         linkoptions = linkoptions + command_list[i]
         
      elif(command_list[i] == "FE=34"):
         command_list[i] = " --debugger=icd3"
         linkoptions = linkoptions + command_list[i]
         
      elif(command_list[i] == "FE=35"):
         command_list[i] = " --debugger=realice"
         linkoptions = linkoptions + command_list[i]
         
      elif(command_list[i] == "FE=38"):
         command_list[i] = " --debugger=pickit2"
         linkoptions = linkoptions + command_list[i]
         
      elif(command_list[i] == "FE=39"):
         command_list[i] = " --debugger=pickit3"
         linkoptions = linkoptions + command_list[i]
         
      elif(command_list[i] == "10D=0"):
         command_list[i] = ",-inhx032"
         inhx032 = inhx032 + command_list[i]
         
      elif(command_list[i] == "10D=1"):
         command_list[i] = ",+inhx032"
         inhx032 = inhx032 + command_list[i]
         
      ########### Report options - psect,class,mem,hex,html #############################

      elif(command_list[i] == "106=0"):
         command_list[i] = ",-psect"
         reportoptions = reportoptions + command_list[i]
         
      elif(command_list[i] == "106=1"):
         command_list[i] = ",+psect"
         reportoptions = reportoptions + command_list[i]
         
      elif(command_list[i] == "109=0"):
         command_list[i] = ",-class"
         reportoptions = reportoptions + command_list[i]
         
      elif(command_list[i] == "109=1"):
         command_list[i] = ",+class"
         reportoptions = reportoptions + command_list[i]
         
      elif(command_list[i] == "10A=0"):
         command_list[i] = ",-mem"
         reportoptions = reportoptions + command_list[i]
         
      elif(command_list[i] == "10A=1"):
         command_list[i] = ",+mem"
         reportoptions = reportoptions + command_list[i]
         
      elif(command_list[i] == "10B=0"):
         command_list[i] = ",-hex"
         reportoptions = reportoptions + command_list[i]
         
      elif(command_list[i] == "10B=1"):
         command_list[i] = ",+hex"
         reportoptions = reportoptions + command_list[i]
         
      elif(command_list[i] == "10C=0"):
         command_list[i] = ""
         reportoptions = reportoptions + command_list[i]
         
      elif(command_list[i] == "10C=1"):
         command_list[i] = "--html"
         htmloption = command_list[i]
         
      ############ Global Options - mem model,double,float,pointer size,emi,ram ranges,rom ranges ########################
      
      if(McpfileNativeCompiler != "PICC"):
      
         if(command_list[i] == "E5=0"):
            command_list[i] = "-Bsmall"
            codeanddatamodel = codeanddatamodel + command_list[i] + " "

         elif(command_list[i] == "E5=1"):
            command_list[i] = "-Blarge"
            codeanddatamodel = codeanddatamodel + command_list[i] + " "

         elif(command_list[i] == "E7=0"):
            command_list[i] = "--cp=16"
            codeanddatamodel = codeanddatamodel + command_list[i] + " "

         elif(command_list[i] == "E7=1"):
            command_list[i] = "--cp=24"
            codeanddatamodel = codeanddatamodel + command_list[i] + " "

         elif(command_list[i] == "F1=1"):
            command_list[i] = "--emi=bytewrite"
            codeanddatamodel = codeanddatamodel + command_list[i] + " "

         elif(command_list[i] == "F1=2"):
            command_list[i] = "--emi=byteselect"
            codeanddatamodel = codeanddatamodel + command_list[i] + " "
         
      if(command_list[i] == "E8=0"):
         command_list[i] = "--double=24"
         codeanddatamodel = codeanddatamodel + command_list[i] + " "
         
      elif(command_list[i] == "E8=1"):
         command_list[i] = "--double=32"
         codeanddatamodel = codeanddatamodel + command_list[i] + " "
         
      elif(command_list[i] == "126=0"):
         command_list[i] = "--float=24"
         codeanddatamodel = codeanddatamodel + command_list[i] + " "
         
      elif(command_list[i] == "126=1"):
         command_list[i] = "--float=32" 
         codeanddatamodel = codeanddatamodel + command_list[i] + " "
         
      elif(command_list[i] == "F1=0"):
         command_list[i] = ""
         codeanddatamodel = codeanddatamodel + command_list[i] + " "
         
      elif re.search("F6=",command_list[i]):
         command_list[i] = re.sub("F6=",'',command_list[i])
         if command_list[i] == '':
            command_list[i] = '';      
         else:
            command_list[i] = "--ram=" + command_list[i]
         codeanddatamodel = codeanddatamodel + command_list[i] + " "
         
      elif re.search("F7=",command_list[i]):
         command_list[i] = re.sub("F7=",'',command_list[i])
         if command_list[i] == '':
            command_list[i] = '';      
         else:
            command_list[i] = "--rom=" + command_list[i]
         codeanddatamodel = codeanddatamodel + command_list[i] + " "
         

   if DD_Value == "0":
      optimisationsettings = optimisationsettings + ",-9"
   else:
      optimisationsettings = optimisationsettings + "," + DC_Value

   
   compiler_options = preprocessasm + " --runtime=default" + " " + definedmacros + " " + undefinedmacros + runtimeoptions + " " + htmloption + " --opt=default" + optimisationsettings + " " + messages + " " + idlength + " -D__DEBUG=1" + linkoptions + " " + codeanddatamodel + addrqualifiers + "-g --asmlist" #+ " \"--errformat=Error [%n] %f; %l.%c %s\"" + " \"--msgformat=Advisory[%n] %s\"" + " \"--warnformat=Warning [%n] %f; %l.%c %s\""

        
   linker_options = " --summary=default" + " " + definedmacros + " " + undefinedmacros + reportoptions + " --output=default" + inhx032 + " " + preprocessasm + " --runtime=default" + runtimeoptions + " " + htmloption  + " --opt=default" + optimisationsettings + " " + messages + " " + idlength + " -D__DEBUG=1 " + linkoptions + " " + codeanddatamodel + addrqualifiers + "-g --asmlist" #+ " \"--errformat=Error [%n] %f; %l.%c %s\"" + " \"--msgformat=Advisory[%n] %s\"" + " \"--warnformat=Warning [%n] %f; %l.%c %s\""
   
   return(compiler_options,linker_options)

    
      
def Extract(command, McpfileNativeCompiler, ScriptDir):

   compiler_options,linker_options = '',''
   
   OptionsCSVfile = os.path.join(ScriptDir, "picc_options.csv")
   
   if os.path.exists(OptionsCSVfile):
   
      CommandToExtract = ''
      command_list = GetCommand(command, McpfileNativeCompiler)
      for i in command_list:
         CommandToExtract = CommandToExtract + " " + i
      
      CommandToExtract = CommandToExtract.strip(" ")
      
      compiler_options,linker_options = picc_options_from_csv.Get(CommandToExtract, McpfileNativeCompiler, OptionsCSVfile)
      
   else:
      compiler_options,linker_options = InScriptsExtract(command, McpfileNativeCompiler)
   
   return(compiler_options,linker_options)
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      