import os
import re
import csv


def GetEWarningFromFile(EWarningFilesLocation,EWarningFile,CSVFileLocation):
   
   EErrorFromFile = []
   EWarningFromFile = []
   ErrorInfoFileExistingError = 0
   
   if not '' == EWarningFile:
      
      FilePresentInDirectory = os.path.split(CSVFileLocation)[0]

      FileLocation = ''

      Count = 0

      for i in range(100):
         if re.search("^./",EWarningFilesLocation):
            Count = Count + 1
            EWarningFilesLocation = re.sub("^./",'',EWarningFilesLocation)

      if Count >= 1:
         Count = Count - 1

      for i in range(Count):
         FilePresentInDirectory = os.path.split(FilePresentInDirectory)[0]

      FileLocation = os.path.normpath(os.path.join(FilePresentInDirectory, EWarningFilesLocation))
      FileLocation = os.path.normpath(os.path.join(FileLocation, EWarningFile))

      if os.path.exists(FileLocation):
         EWarningFilePtr = open(FileLocation,'r')
         
         for Line in EWarningFilePtr:
            Line = re.sub("\n|\r",'',Line)
            if re.search('^#warning',Line):          
               EWarningFromFile.append(re.sub("^ | $",'',re.sub('^#warning ','',Line)))
            if re.search('^#error',Line):          
               EErrorFromFile.append(re.sub("^ | $",'',re.sub('^#error ','',Line)))
      else:
         ErrorInfoFileExistingError = 1
         
   return(EErrorFromFile, EWarningFromFile, ErrorInfoFileExistingError)
   
   


def GetAPIList(CSVFile,GivenDevice):

   #CSVFile = "api_table2.csv"

   CSVFilePtr = reader = csv.reader(open(CSVFile, "rb"), delimiter=',', quoting=csv.QUOTE_NONE)

   LineCount = 0

   DeviceList = []
   SupportInfo = []

   EWarningFilesLocation = ''
   EWarningFile = []

   ErrorInfoFileExistingError = 0

   SupportedAPIList = []
   UnSupportedAPIList = []

   EErrorFromFile = []
   EWarningFromFile = []
   
   #GivenDevice = "PIC24FJ256GB110"

   GivenDevice = GivenDevice.upper()
   GivenDevice = re.sub("DSPIC|PIC",'',GivenDevice)

   RowIndex = 0
   for Line in CSVFilePtr:
      if not [] == Line:
         DeviceList.append(re.sub(" ",'',Line[0]))
         Line.remove(Line[0])
         
         if 0 == RowIndex:
            EWarningFilesLocation = re.sub(" ",'',Line[0])
         
         EWarningFile.append(re.sub(" ",'',Line[0]))      
         
         Line.remove(Line[0])
         
         SupportInfo.append(Line)
         RowIndex = RowIndex + 1

   RowIndex = 0
   for DeviceName in DeviceList:   

      DeviceName = DeviceName.upper()
      DeviceName = re.sub("PIC|DSPIC",'',DeviceName) 
      # DeviceName = re.sub(" ",'',DeviceName)

      if GivenDevice == DeviceName:
         EErrorFromFile,EWarningFromFile,ErrorInfoFileExistingError = GetEWarningFromFile(EWarningFilesLocation,EWarningFile[RowIndex],CSVFile)
        
         for ColNumber in range(len(SupportInfo[RowIndex])):
            if "Y" == SupportInfo[RowIndex][ColNumber]:
               SupportedAPIList.append(re.sub(" ",'',SupportInfo[0][ColNumber]))
            if "N" == SupportInfo[RowIndex][ColNumber]:
               UnSupportedAPIList.append(re.sub(" ",'',SupportInfo[0][ColNumber]))
         break
         
      RowIndex = RowIndex + 1


   return (SupportedAPIList,UnSupportedAPIList, EErrorFromFile, EWarningFromFile, ErrorInfoFileExistingError)