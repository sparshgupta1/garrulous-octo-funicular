import os

#############################################################
#### Prints the Message into a channel
#### The Channel may be a File
#############################################################

def LogFile(PrintString):                                   # Prints into Log File
   LogFile = os.path.join(os.getcwd(),"LogFile.txt")           
   Log_File = open(LogFile,'a')              
   Log_File.write(PrintString + "\n")                          # For every Line, print a newline character at the end.
   Log_File.close()                                            # So, while calling this Module, donot append this 
                                                               # Do not pass a "\n" character at the end.
def Console(PrintString):                                 # Prints in Console which can be viewed in Hudson's build Console.
   print PrintString



#################################################################
#### Inserts Text needed at the start of Execution of a makefile
################################################################# 

def MakeFileTag(ExecutionCount, MakeFile, Mode):
   LogFile("\n")
   if '' == Mode:                                              # For Non-PICC18 compiler
      LogFile(str(ExecutionCount + 1) + ". Executing for Makefile: " + MakeFile + "\nMessage Log:")
   else:                                                       # For PICC18 compiler, display, in which mode, the build is happening
      LogFile(str(ExecutionCount + 1) + ". Executing for Makefile: " + MakeFile + " (Build Mode - " + Mode + ")\nMessage Log:")
   

#################################################################
#### Inserts Text needed at the end of Execution of a makefile
################################################################# 

def InsertEndOfExecution():
   LogFile(('#' * 65))
   LogFile(('-' * 21) + "End of Make File Messages" + ('-' * 21))
   LogFile(('#' * 65) + "\n")


#################################################################
#### Inserts Text needed at the start of Execution of a makefile
################################################################# 

def InsertStartOfExecution():
   LogFile("\n" + ('#' * 65))
   LogFile(('-' * 23) + "Make File Messages" + ('-' * 23))
   LogFile(('#' * 65))

