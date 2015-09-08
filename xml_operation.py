import os
import re

from xml.dom.minidom import parse


def ExtractLinker(ProjectLocation,MakeFileName):

   XmlFileName = os.path.join(os.path.join(ProjectLocation,"nbproject"),"configurations.xml")

   ScanforLkrFile = 0
   LinkerName = ''

   AllLinkerList = []

   Configuration = MakeFileName[9: -3]


   XmlFilePtr = open(XmlFileName,'r')

   for Line in XmlFilePtr:
      Line = Line.strip("\n|\r")
      Line = Line.strip(" ")
      if re.search("</logicalFolder>",Line):
         ScanforLkrFile = 0

      if 1 == ScanforLkrFile:
         if re.search("<itemPath>",Line):
            #Line = re.sub(" ",'',Line)
            LinkerName = re.sub("<itemPath>|</itemPath>",'',Line)
            AllLinkerList.append(LinkerName)

      if re.search("\<logicalFolder name=\"LinkerScript\"",Line):
         ScanforLkrFile = 1
   XmlFilePtr.close()
      
   ########################################
   ########################################

   XmlFilePtr = open(XmlFileName,'r')
   StartLog = 0
   LineLog = ''
   for Line in XmlFilePtr:
      Line = Line.strip("\n|\r")
      Line = Line.strip(" ")

      if re.search("</conf>",Line):
         ScanforLkrFile = 0

      if 1 == ScanforLkrFile:
                  
         if re.search(">",Line) and 1 == StartLog: 
            StartLog = 0
            for i in AllLinkerList:
               if re.search(i,LineLog):
                  if re.search("ex=\"true\"",LineLog):
                     AllLinkerList.remove(i)
                     break    
                     
         if 1 == StartLog: 
            LineLog = LineLog + Line
         
         if re.search("<item path=",Line):
            
            LineLog = Line
            
            if re.search(">",Line):    ## if the item ends in the same line, then, look for the existance to EX=TRUE
               StartLog = 0
               for i in AllLinkerList:
                  if re.search(i,LineLog):
                     if re.search("ex=\"true\"",LineLog):
                        AllLinkerList.remove(i)
                        break
            else:                      ## Else, log the line, till the end of the item path.
               StartLog = 1

      ConfName = "<conf name=\"" + Configuration + '"'

      if re.search(ConfName,Line):
         ScanforLkrFile = 1
         StartLog = 0
   
   return(AllLinkerList)



def get_all_project_config(project_location):
   all_config = []
   all_compiler = []
   
   config_xml_path = os.path.join(project_location, "nbproject/configurations.xml")
   config_xml_path = os.path.normpath(config_xml_path)
   
   if os.path.exists(config_xml_path):
      try:
         dom = parse(config_xml_path)
         all_confs = dom.getElementsByTagName("conf")
         for all_conf in all_confs:
            if all_conf.ELEMENT_NODE == all_conf.nodeType:
               if all_conf.attributes: 
                  for i in range(all_conf.attributes.length): 
                     a = all_conf.attributes.item(i)
                     if a.name == "name":         
                        all_config.append(a.value.encode('ascii','ignore'))
                        tgt_compiler = ''
                        tgt_compiler_node = all_conf.getElementsByTagName("languageToolchain")[0]
                        if len(tgt_compiler_node.childNodes) >= 1:
                           tgt_compiler = tgt_compiler_node.childNodes[0].data.encode('ascii','ignore') 
                        all_compiler.append(tgt_compiler)
      except:
         print "corrupted project_files"
         
   return(all_config, all_compiler)
            
   
def get_compiler(project_location, configuration):
   rtn_comp = ""
   all_config, all_compiler = get_all_project_config(project_location)
   for i in range(len(all_config)):
      if all_config[i] == configuration:
         rtn_comp = all_compiler[i]
         break
   return(rtn_comp)
         
      
def find_valid_xml(xml_file_name):
   error = 1
   if os.path.exists(xml_file_name):   
      try:
         dom = parse(xml_file_name)
         error = 0
      except:
         print "XML file Error"
   
   return(error)      