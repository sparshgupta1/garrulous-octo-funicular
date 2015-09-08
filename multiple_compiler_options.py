import os
import re
import sys
import subprocess
from xml.dom.minidom import parse
import xml.dom.minidom
import shutil

import time



def get_mplabx_and_jdk_path():

   CompilerRevFileLocation = ''
   
   mplabx_path = ''
   jdk_path = ''
   
   if 'win32' == sys.platform:
      CompilerRevFileLocation = "C:/ARBS_SUPPORT/WIN_ToolSuiteLocations.mcpr" 
   elif'linux2' == sys.platform:                                 # Linux
      CompilerRevFileLocation = "/home/ARBS_SUPPORT/LIN_ToolSuiteLocations.mcpr" 
   elif 'darwin' == sys.platform:                                 # MAC 
      CompilerRevFileLocation = "/Users/ARBS_SUPPORT/MAC_ToolSuiteLocations.mcpr"
   
   mcpr_fptr = open(CompilerRevFileLocation,"r")
   for Line in mcpr_fptr:
      Line = re.sub("\n","",Line)
      Line = re.sub("\r","",Line)
      if re.search("^_MPLAB_X_INSTALLATION_PATH_", Line):
         mplabx_path = re.split("=", Line)[1]
      if re.search("^_JDK_PATH_", Line):
         jdk_path = re.split("=", Line)[1]      

   mcpr_fptr.close()
   
   return(mplabx_path, jdk_path)
   

def extract_compiler_options_file_from_ide():
   
   mplabx_path, jdk_path = get_mplabx_and_jdk_path()
   
   xc8_compiler_jar_file_location = ''
   xc16_compiler_jar_file_location = ''
   xc32_compiler_jar_file_location = ''
   
   cc_xc8 = {"GCC":"", "LD":"","AS":"","jar_location":""}
   cc_xc16 = {"GCC":"", "LD":"","AS":"","jar_location":""}
   cc_xc32 = {"GCC":"", "LD":"","AS":"","jar_location":""}
   
   compiler_options_files = {"XC8":cc_xc8, "XC16":cc_xc16, "XC32":cc_xc32}
      
   jar_paths_file = "compiler_options_file_locations.info"
   
   fptr = open(jar_paths_file,"r")
   
   scan_xc8 = 0
   scan_xc16 = 0
   scan_xc32 = 0
   
   for Line in fptr:
      Line = re.sub("\n","", Line)
      Line = re.sub("\r","", Line)
      
      if re.search("^_END",Line):
         scan_xc8 = 0
         scan_xc16 = 0
         scan_xc32 = 0
   
      if scan_xc8 == 1:
         if re.search("^GCC",Line):
            temp = re.split("#",Line)[0]  # to remove Comments in the line
            temp = temp.strip(" ")
            temp = re.split(":", temp)[1]
            temp = temp.strip(" ")
            compiler_options_files["XC8"]["GCC"] = temp
         if re.search("^LD",Line):
            temp = re.split("#",Line)[0]  # to remove Comments in the line
            temp = temp.strip(" ")
            temp = re.split(":", temp)[1]
            temp = temp.strip(" ")
            compiler_options_files["XC8"]["LD"] = temp
         if re.search("^AS",Line):
            temp = re.split("#",Line)[0]  # to remove Comments in the line
            temp = temp.strip(" ")
            temp = re.split(":", temp)[1]
            temp = temp.strip(" ")
            compiler_options_files["XC8"]["AS"] = temp
            
            
      if scan_xc16 == 1:
         if re.search("^GCC",Line):
            temp = re.split("#",Line)[0]  # to remove Comments in the line
            temp = temp.strip(" ")
            temp = re.split(":", temp)[1]
            temp = temp.strip(" ")
            compiler_options_files["XC16"]["GCC"] = temp
         if re.search("^LD",Line):
            temp = re.split("#",Line)[0]  # to remove Comments in the line
            temp = temp.strip(" ")
            temp = re.split(":", temp)[1]
            temp = temp.strip(" ")
            compiler_options_files["XC16"]["LD"] = temp
         if re.search("^AS",Line):
            temp = re.split("#",Line)[0]  # to remove Comments in the line
            temp = temp.strip(" ")
            temp = re.split(":", temp)[1]
            temp = temp.strip(" ")
            compiler_options_files["XC16"]["AS"] = temp
            
            
      if scan_xc32 == 1:
         if re.search("^GCC",Line):
            temp = re.split("#",Line)[0]  # to remove Comments in the line
            temp = temp.strip(" ")
            temp = re.split(":", temp)[1]
            temp = temp.strip(" ")
            compiler_options_files["XC32"]["GCC"] = temp
         if re.search("^LD",Line):
            temp = re.split("#",Line)[0]  # to remove Comments in the line
            temp = temp.strip(" ")
            temp = re.split(":", temp)[1]
            temp = temp.strip(" ")
            compiler_options_files["XC32"]["LD"] = temp
         if re.search("^AS",Line):
            temp = re.split("#",Line)[0]  # to remove Comments in the line
            temp = temp.strip(" ")
            temp = re.split(":", temp)[1]
            temp = temp.strip(" ")
            compiler_options_files["XC32"]["AS"] = temp
            
         
      if re.search("^_XC8:",Line):
         temp = re.split("#",Line)[0]  # to remove Comments in the line
         temp = temp.strip(" ")
         temp = re.split(":", temp)[1]
         temp = temp.strip(" ")
         temp = os.path.join(mplabx_path, temp)
         compiler_options_files["XC8"]["jar_location"] = os.path.normpath(temp)
         scan_xc8 = 1
         
      if re.search("^_XC16:",Line):
         temp = re.split("#",Line)[0]  # to remove Comments in the line
         temp = temp.strip(" ")
         temp = re.split(":", temp)[1]
         temp = temp.strip(" ")
         temp = os.path.join(mplabx_path, temp)
         compiler_options_files["XC16"]["jar_location"] = os.path.normpath(temp)
         scan_xc16 = 1
         
      if re.search("^_XC32:",Line):
         temp = re.split("#",Line)[0]  # to remove Comments in the line
         temp = temp.strip(" ")
         temp = re.split(":", temp)[1]
         temp = temp.strip(" ")
         temp = os.path.join(mplabx_path, temp)
         compiler_options_files["XC32"]["jar_location"] = os.path.normpath(temp)
         scan_xc32 = 1
         
   fptr.close()
   
   for compiler_key in compiler_options_files.keys():
      

      for options_key in compiler_options_files[compiler_key].keys():
         if compiler_options_files[compiler_key][options_key] != '' and options_key != "jar_location":
            command = []
            jar_path = os.path.join(jdk_path, "bin/jar")
            jar_path = os.path.normpath(jar_path)
            command = [jar_path, "xf", compiler_options_files[compiler_key]["jar_location"], re.sub(r"\\","/",compiler_options_files[compiler_key][options_key])]
            #print "***\n"
            #print command
            if os.path.exists(compiler_options_files[compiler_key][options_key]):
               print "IDE Reference File already exists\nSkipping Extraction"
            else:
               error_code = subprocess.call(command)            
      
   return(compiler_options_files)
   
def extract_xml_option(text):
   
   #extn_found = 0
   
   temp = ''
   
   #if re.search("\(\.\+\)", text):
   #   extn_found = 1   
   
   if re.search("=", text):
      temp1 = re.split("=",text)
      
      if len(temp1) >= 2:
         for i in range(len(temp1)-1):
            temp = temp + temp1[i] + "="
         temp = temp.strip("=") + "="

      else:
         temp = temp1[0] + "="
   else:
      temp = text
   
   temp = re.sub(r"\.","",temp)
   temp = re.sub(r"\+","",temp)
   temp = re.sub(r"\?","",temp)
   temp = re.sub(r"\(","",temp)
   temp = re.sub(r"\)","",temp)
   temp = re.sub(r"\*","",temp)
   temp = re.sub(r"\^","",temp)
   temp = re.sub(r"\!","",temp)
   temp = re.sub(r"\\","",temp)
   temp = re.split(r"\[",temp)[0]
   return(temp)
   
   
def get_string_or_list_option_elements(dom_object):
   
   string_option = []
   string_list_option = []
   
   string_list_option_nodes = dom_object.getElementsByTagName("opt:stringListOption")
   for string_list_option_node in string_list_option_nodes:
      if string_list_option_node.ELEMENT_NODE == string_list_option_node.nodeType:
         
         if string_list_option_node.attributes: 

            for i in range(string_list_option_node.attributes.length): 
               a = string_list_option_node.attributes.item(i)
               if a.name == "opt:id":
                  temp = a.value
                  string_list_option.append(temp)
                  
   string_list_option_nodes = dom_object.getElementsByTagName("opt:stringOption")
   for string_list_option_node in string_list_option_nodes:
      if string_list_option_node.ELEMENT_NODE == string_list_option_node.nodeType:
         
         if string_list_option_node.attributes: 

            for i in range(string_list_option_node.attributes.length): 
               a = string_list_option_node.attributes.item(i)
               if a.name == "opt:id":
                  temp = a.value
                  string_option.append(temp)                  
                  
   return(string_list_option, string_option)
   
                                 
   
   
def get_options_from_xml(xml_file, compiler_key=""):
   
   option_type = []
   expression = []
   idref = []
   match_substitute_for_xml_update = []
   
   #fsecond_exp_found = []
   string_list_option = []
   string_option = []
      
   #print "\n\n"
   if os.path.exists(xml_file):
      dom = parse(xml_file)
      optionLanguageNodes = dom.childNodes 
      
      string_list_option, string_option = get_string_or_list_option_elements(dom)
      for optionLanguageNode in optionLanguageNodes:
         if optionLanguageNode.ELEMENT_NODE == optionLanguageNode.nodeType:
            opt_nodes = optionLanguageNode.childNodes
            for opt_node in opt_nodes:
               if opt_node.ELEMENT_NODE == opt_node.nodeType:
                  
                  opt_nodes_array = []
                  opt_nodes_array.append(opt_node)
                  
                  sub_opt_nodes = opt_node.childNodes
                  for sub_opt_node in sub_opt_nodes:
                     if sub_opt_node.ELEMENT_NODE == sub_opt_node.nodeType:
                        opt_nodes_array.append(sub_opt_node)
                  
                  for temp_opt_node in opt_nodes_array:
                     if temp_opt_node.nodeName == "opt:submatchPattern" or temp_opt_node.nodeName == "opt:enablePattern" or temp_opt_node.nodeName == "opt:disablePattern" or temp_opt_node.nodeName == "opt:modifierPattern":
                        #print temp_opt_node.attributes["opt:expr"].value
                        if temp_opt_node.attributes: 
                           expr_found = 0
                           idref_found = 0
                           #first_second_exp_found = 0

                           expr = ''
                           id_ref = ''
                           match_prefix_substitute_for_xml_update = ''
                           #first_second_exp = ''

                           for i in range(temp_opt_node.attributes.length): 
                              a = temp_opt_node.attributes.item(i)
                              if a.name == "opt:expr":
                                 temp = a.value
                                 
                                 if re.search("\(", temp):
                                    match_prefix_substitute_for_xml_update = re.split("\(", temp)[0]
                                    
                                 temp = extract_xml_option(temp)
                                 expr = temp 
                                 expr_found = 1
                              if a.name == "opt:idref":
                                 temp = a.value
                                 temp = extract_xml_option(temp)
                                 id_ref = temp 
                                 idref_found = 1
                                 
                           if expr_found == 0 and idref_found == 1:
                              for i in range(temp_opt_node.attributes.length): 
                                 a = temp_opt_node.attributes.item(i)
                                 if a.name == "opt:firstexpr":
                                    temp = a.value
                                    temp = extract_xml_option(temp)
                                    expr = temp 
                                    expr_found = 1

                                 
                                 
                              #if a.name == "opt:firstexpr" or a.name == "opt:secondexpr":
                              #   first_second_exp_found = 1 


                           if temp_opt_node.nodeName == "opt:modifierPattern":
                              mod_pattern_child_nodes = temp_opt_node.childNodes
                              for mod_pattern_child_node in mod_pattern_child_nodes:
                                 if mod_pattern_child_node.ELEMENT_NODE == mod_pattern_child_node.nodeType:
                                    for i in range(mod_pattern_child_node.attributes.length): 
                                       a = mod_pattern_child_node.attributes.item(i)
                                       if a.name == "opt:expr":
                                          temp = a.value
                                          temp = extract_xml_option(temp)
                                          expr = temp 
                                          expr_found = 1
                                       if a.name == "opt:idref":
                                          temp = a.value
                                          temp = extract_xml_option(temp)
                                          id_ref = temp 
                                          idref_found = 1  

                                    if expr_found == 0 and idref_found == 1:
                                       for i in range(mod_pattern_child_node.attributes.length): 
                                          a = mod_pattern_child_node.attributes.item(i)
                                          if a.name == "opt:firstexpr":
                                             temp = a.value
                                             temp = extract_xml_option(temp)
                                             expr = temp 
                                             expr_found = 1                                          
                                       #if a.name == "opt:firstexpr" or a.name == "opt:secondexpr":
                                       #  first_second_exp_found = 1                                        



                           
                                 
                           if re.search(r"\|", expr):
                              array = re.split(r"\|", expr)
                              for items in array:
                                 if items != '':
                                    option_type.append(temp_opt_node.nodeName.encode('ascii','ignore'))
                                    expression.append(items.encode('ascii','ignore'))
                                    idref.append(id_ref.encode('ascii','ignore'))
                                    match_substitute_for_xml_update.append(match_prefix_substitute_for_xml_update.encode('ascii','ignore'))
                                    #fsecond_exp_found.append(first_second_exp_found)

                           else:
                              option_type.append(temp_opt_node.nodeName.encode('ascii','ignore'))
                              expression.append(expr.encode('ascii','ignore'))
                              idref.append(id_ref.encode('ascii','ignore'))
                              match_substitute_for_xml_update.append(match_prefix_substitute_for_xml_update.encode('ascii','ignore'))
                              #fsecond_exp_found.append(first_second_exp_found)
                        
                        
                        
         '''
         optionsNode = optionLanguageNode.childNodes
         for job_param_node in job_param_nodes:
            if job_param_node.ELEMENT_NODE == job_param_node.nodeType:
         '''
      
   #print option_type, expression, idref, fsecond_exp_found   
   #return(option_type, expression, idref, fsecond_exp_found)
   return(option_type, expression, idref, match_substitute_for_xml_update, string_list_option, string_option)
   
   
   
   
   
'''
def extract_compiler_options(compiler_name, compiler_options_files):
   
   for compiler_key in compiler_options_files.keys(): 
      
      if compiler_key == compiler_name:
         for options_key in compiler_options_files[compiler_key].keys():
            if options_key != "jar_location" and compiler_options_files[compiler_key][options_key] != '':
               get_options_from_xml(compiler_options_files[compiler_key][options_key], options_key)
'''

def get_user_options(file):
   
   row_options = []
   col_options = []
   compilers = []
   
   _col_options = []
   _row_options = []
   
   
   if os.path.exists(file):
      fptr = open(file,"r")
      scan = 0
      temp_compiler = ''
      for Line in fptr:
         Line = re.sub("\n","",Line)
         Line = re.sub("\r","",Line)
         Line = re.split(r"\#",Line)[0]
         Line = Line.strip(" ")
         
         
         if (re.search("^:END", Line) or re.search("^:XC", Line)) and scan == 1:
            
            if temp_compiler != '':
            
               compilers.append(temp_compiler)
               row_options.append(_row_options)
               col_options.append(_col_options)
            
            scan = 0
            
         if scan == 1:
            if Line != '':
               if re.search("^ROW:",Line):
                  if (re.split("ROW:",Line)[1]) != "":
                     _row_options.append(re.split("ROW:",Line)[1])
               if re.search("^COL:",Line):
                  if (re.split("COL:",Line)[1]) != "":
                     _col_options.append(re.split("COL:",Line)[1])         
                     
         if re.search("^:XC", Line):
            temp = re.sub(":","",Line)
            temp_compiler = temp
            scan = 1
            _row_options = []
            _col_options = []
            
            
            

      
      fptr.close()
   
   mplabx_path, jdk_path = get_mplabx_and_jdk_path()
   if mplabx_path == '' or jdk_path == '' or (not os.path.exists(jdk_path)) or (not os.path.exists(mplabx_path)):
      print "\n\n***Unable to Get the JDK and/or MPLABX IDE Paths. Please update the IDE and JDK paths in mcpr file***\n\n"
      print "\n\nBypassing Multiple Build Options and enabling regular build mode\n\n"
      compilers = []
      
      
   return(row_options, col_options, compilers)
         
#def get_updated_node(





def update_node(node, compiler_options_files, row_options, col_options):
   
   #print node, compiler_options_files, row_options, col_options
   
   tgt_device = ''
   tgt_compiler = ''
   
   gcc_node_name = ""
   ld_node_name = ""
   as_node_name = ""
   update_done = 0
   
   
   toolsSetNode = node.getElementsByTagName("toolsSet")[0]
   tgt_device_node = toolsSetNode.getElementsByTagName("targetDevice")[0]
   tgt_compiler_node = toolsSetNode.getElementsByTagName("languageToolchain")[0]
   
   if len(tgt_device_node.childNodes) >= 1:
      tgt_device = tgt_device_node.childNodes[0].data.encode('ascii','ignore')   
   if len(tgt_compiler_node.childNodes) >= 1:
      tgt_compiler = tgt_compiler_node.childNodes[0].data.encode('ascii','ignore')   
   
   
   if tgt_compiler == "XC8":
      gcc_node_name = "HI-TECH-COMP"
      ld_node_name = "HI-TECH-LINK"
      as_node_name = ""
   if tgt_compiler == "XC16":
      gcc_node_name = "C30"
      ld_node_name = "C30-LD"
      as_node_name = "C30-AS"
   if tgt_compiler == "XC32":
      gcc_node_name = "C32"
      ld_node_name = "C32-LD"
      as_node_name = "C32-AS"
   user_defined_all_options = row_options + col_options
   
   

   search_element_name = ''
   for compiler_elements in compiler_options_files[tgt_compiler].keys():
      if compiler_elements != '' and compiler_elements != "jar_location":
         if compiler_elements == "GCC":
            search_element_name = gcc_node_name
         elif compiler_elements == "LD":
            search_element_name = ld_node_name
         elif compiler_elements == "AS":
            search_element_name = as_node_name
         
         if search_element_name != '' and compiler_elements != '' and len(node.getElementsByTagName(search_element_name)) > 0:
            #print search_element_name
            #print node.getElementsByTagName(search_element_name)


            gcc_nodes = node.getElementsByTagName(search_element_name)
            for gcc_node in gcc_nodes:

               '''
               if gcc_node == '':
                  compiler_child_nodes = node.childNodes
                  for compiler_child_node in compiler_child_nodes:
                     if compiler_child_node.ELEMENT_NODE == compiler_child_node.nodeType:
                        if compiler_child_node.nodeName == search_element_name:
                           gcc_node = compiler_child_node

               if gcc_node == '':
                  continue
               '''   

               #option_type, expression, idref, fsecond_exp_found = get_options_from_xml(compiler_options_files[tgt_compiler][compiler_elements])

               option_type, expression, idref, match_substitute_for_xml_update, string_list_option, string_option = get_options_from_xml(compiler_options_files[tgt_compiler][compiler_elements])

               #print option_type, expression, idref, string_list_option, string_option
               loaded_option_type = []
               loaded_idref = []
               #loaded_fsecond_exp_found = []
               expression_to_be_updated = []
               expression_update_type = []   # 0 for append, 1 for replace, Applicable only for SubmatchPattern
               remove_expresson = []
               #print user_defined_all_options
               #print expression
               for option in user_defined_all_options:

                  if re.search("\[COMPILER\]",option):
                     if compiler_elements != "GCC":
                        continue

                  if re.search("\[LINKER\]",option):
                     if compiler_elements != "LD":
                        continue                  

                  if re.search("--chip=", option) or re.search("-mcpu=", option) or re.search("-mprocessor=", option):
                     new_device = re.split("=",option)[1]
                     new_device = new_device.strip(" ")
                     if new_device != "":
                        new_device = new_device.upper().strip("DSPIC")
                        new_device = new_device.strip("PIC")
                        if re.search("^30", new_device) or re.search("^33", new_device):
                           new_device = "dsPIC" + new_device
                        else:
                           new_device = "PIC" + new_device

                        if tgt_device != "":
                           tgt_device_node.childNodes[0].data = new_device

                     continue

                  if re.search("\[ADDITIONAL_OPTION\]", option):
                     temp = option.strip("\[REM\]|[\EN\]|[\DIS\]|\[LINKER\]|\[COMPILER\]|\[ADDITIONAL_OPTION\]")

                     document_node = gcc_node

                     while document_node.parentNode != None:
                        document_node = document_node.parentNode

                     additional_option_node = document_node.createElement("appendMe")
                     additional_option_node.setAttribute("value", temp)

                     #additional_option_node = gcc_node.createElement("appendMe")

                     #additional_option_node = xml.dom.minidom.parseString("<appendMe value=\"" + temp + "\"/>").toxml()
                     gcc_node.appendChild(additional_option_node)


                     #document_node = document_node.toprettyxml() 

                     continue

                  for i in range(len(expression)):
                     #print option
                     #print expression[i]
                     #if re.search("y",expression[i]):
                     #   print expression[i]
                     
                     found = 0
                     _t_options = option.strip("\[REM\]|[\EN\]|[\DIS\]|\[LINKER\]|\[COMPILER\]|\[ADDITIONAL_OPTION\]")
                     
                     if re.search(r"\|", option):
                        temp_array = re.split(r"\|",option)
                        for _t_opt in temp_array:
                           if len(_t_opt) >= len(expression[i]):
                              if expression[i] == _t_opt[:len(expression[i])]:
                                 found = 1
                           
                        
                     elif _t_options == expression[i]:
                        found = 1
                     
                     else:
                        if len(_t_options) >= len(expression[i]):
                           if expression[i] == _t_options[:len(expression[i])]:
                              found = 1
                           
                           
                     if found == 1 and expression[i] != '':
                     
                        #print "sadfkjnafv"
                        loaded_option_type.append(option_type[i])
                        loaded_idref.append(idref[i])
                        #loaded_fsecond_exp_found.append(fsecond_exp_found[i])

                        force_false = 0
                        remove_exp = 0
                        exp_upd_type = 1

                        if re.search(r"\|", option):
                           temp_array = re.split(r"\|",option)
                           for temp in temp_array:
                              if re.search(expression[i], temp):
                                 mcu = re.split("MCU:",temp.upper())[1].strip(r"\}")
                                 mcu = re.sub("DSPIC","",mcu.upper())
                                 mcu = re.sub("PIC","",mcu)
                                 tgt_xml_mcu = re.sub("DSPIC", "", tgt_device.upper())
                                 tgt_xml_mcu = re.sub("PIC","",tgt_xml_mcu)
                                 if mcu != tgt_xml_mcu[:len(mcu)]:
                                    force_false = 1

                        if option_type[i] == "opt:enablePattern":
                           if force_false == 1:
                              expression_to_be_updated.append("false")
                           elif re.search("REM|DIS", option):
                              expression_to_be_updated.append("false")
                           else:
                              expression_to_be_updated.append("true")

                        if option_type[i] == "opt:disablePattern":
                           expression_to_be_updated.append("false")

                        if option_type[i] == "opt:submatchPattern":


                           remove_prefix_option = 0



                           for item in string_option:
                              if item == idref[i]:
                                 remove_prefix_option = 1
                                 break

                           for item in string_list_option:
                              if item == idref[i]:
                                 remove_prefix_option = 1
                                 exp_upd_type = 0
                                 break



                           if re.search("REM|DIS", option):
                              remove_exp = 1


                           temp = ''
                           if remove_prefix_option == 0:
                              temp = option
                           else:
                              temp = option.strip("\[REM\]|[\EN\]|[\DIS\]|\[LINKER\]|\[COMPILER\]")
                              temp = re.sub(expression[i],"",temp)
                              temp = temp.strip(" ")
                              temp = temp.strip("\"")

                           if match_substitute_for_xml_update[i] != '':
                              temp = re.sub("^" + match_substitute_for_xml_update[i], "", temp)
                              
                           expression_to_be_updated.append(temp)

                        expression_update_type.append(exp_upd_type) 
                        remove_expresson.append(remove_exp)

                        #break
               #print tgt_device
               #print loaded_option_type, loaded_idref, loaded_fsecond_exp_found, expression_to_be_updated
               #print gcc_node.nodeName
               child_nodes = gcc_node.childNodes
               for child_node in child_nodes:
                  if child_node.ELEMENT_NODE == child_node.nodeType:
                     #print child_node.nodeName
                     for i in range(child_node.attributes.length): 
                        a = child_node.attributes.item(i)
                        if a.name == "key":
                           for i in range(len(loaded_idref)):
                              if a.value == loaded_idref[i]:
                                 if loaded_option_type[i] == "opt:submatchPattern":
                                    if expression_update_type[i] == 1:
                                       child_node.attributes["value"].value = expression_to_be_updated[i]
                                       update_done = 1
                                    elif expression_update_type[i] == 0:
                                       if child_node.attributes["value"].value == '':
                                          child_node.attributes["value"].value = expression_to_be_updated[i]
                                          update_done = 1
                                       else:
                                          child_node.attributes["value"].value = child_node.attributes["value"].value + ";" + expression_to_be_updated[i]
                                          temp = re.split(";", child_node.attributes["value"].value.encode('ascii','ignore'))
                                          temp_array = []
                                          temp1 = ''
                                          for item in temp:
                                             found = 0
                                             for item1 in temp_array:
                                                if item == item1:
                                                   found = 1
                                             if found == 0:
                                                temp1 = temp1 + item + ";"
                                                temp_array.append(item)

                                          temp1 = temp1.strip(";")
                                          child_node.attributes["value"].value = temp1  
                                          update_done = 1

                                    if remove_expresson[i] == 1:
                                       temp = re.split(";", child_node.attributes["value"].value)
                                       temp1 = ''
                                       for item in temp:
                                          if item.encode('ascii','ignore') == expression_to_be_updated[i]:
                                             continue
                                          else:
                                             temp1 = temp1 + item + ";"
                                       temp1 = temp1.strip(";")
                                       child_node.attributes["value"].value = temp1
                                       update_done = 1

                                 else:
                                    child_node.attributes["value"].value = expression_to_be_updated[i]
                                    update_done = 1
                                 #print child_node.attributes["value"].value                        
                     
   #node = node.toprettyxml()
   return(node, tgt_compiler, update_done)   
   
def update_config_xml(project_location, project_configuration, compiler_options_files, row_options, col_options):
   tgt_compiler, update_done = '',0
   if os.path.exists(project_location):
      config_xml_path = os.path.join(project_location, "nbproject/configurations.xml")
      config_xml_path = os.path.normpath(config_xml_path)
      original_file_path = config_xml_path + ".original"
      #updated_conf = ""
      if os.path.exists(original_file_path):
         dom = parse(original_file_path)
         all_confs = dom.getElementsByTagName("conf")
         for all_conf in all_confs:
            if all_conf.ELEMENT_NODE == all_conf.nodeType:
               if all_conf.attributes: 
                  for i in range(all_conf.attributes.length): 
                     a = all_conf.attributes.item(i)
                     if a.name == "name":
                        if a.value == project_configuration:
                           all_conf, tgt_compiler, update_done = update_node(all_conf, compiler_options_files, row_options, col_options)
                           updated_conf = all_conf
                           #all_confs = []
                           #all_confs.append(all_conf)
                           
         #print all_confs
         if update_done == 1:
            for _all_confs in all_confs:
               if updated_conf.attributes["name"].value.encode('ascii','ignore') != _all_confs.attributes["name"].value.encode('ascii','ignore'):
                  _all_confs.parentNode.removeChild(_all_confs)
                  print "\n\n\nremoving " + _all_confs.attributes["name"].value
                  
         time.sleep(0.5)
         file_handle = open(config_xml_path,"wb")
         time.sleep(0.5)
         dom.writexml(file_handle)
         time.sleep(0.5)
         file_handle.close()            
         time.sleep(0.5)           
         
         
         
   return(tgt_compiler, update_done)   
   
   
def update_configuration(project_location, project_configuration, ind_row_options, ind_col_options):
   
   config_xml_path = os.path.join(project_location, "nbproject/configurations.xml")
   config_xml_path = os.path.normpath(config_xml_path)
   original_file_path = config_xml_path + ".original"
   
   
   if not os.path.exists(original_file_path):
      shutil.copy(config_xml_path, original_file_path)   
   
   time.sleep(0.5)
   
   #remove the existing Configuration
   if os.path.exists(config_xml_path):
      os.remove(config_xml_path)
      
   time.sleep(0.5)
   
   # Recreate the configuration
   shutil.copy(original_file_path, config_xml_path)
   
   compiler_options_files = extract_compiler_options_file_from_ide()
   
   tgt_compiler, update_done = update_config_xml(project_location, project_configuration, compiler_options_files, ind_row_options, ind_col_options)
   return(tgt_compiler, update_done)



def revert_configuration(project_location):
   config_xml_path = os.path.join(project_location, "nbproject/configurations.xml")
   config_xml_path = os.path.normpath(config_xml_path)
   original_file_path = config_xml_path + ".original"
   
   if os.path.exists(original_file_path):
      if os.path.exists(config_xml_path):
         os.remove(config_xml_path)
      
      shutil.copy(original_file_path, config_xml_path)
      time.sleep(0.1)
      os.remove(original_file_path)
      time.sleep(0.1)




'''
project_location = "C:/Users/i14304/Desktop/mplabx_testing/282/Test_ICD3/Test_ICD3.X"
config = "32MX795F512L_C32_WLM"

config_xml_path = os.path.join(project_location, "nbproject/configurations.xml")
config_xml_path = os.path.normpath(config_xml_path)
original_file_path = config_xml_path + ".original"

if not os.path.exists(original_file_path):
   shutil.copy(config_xml_path, original_file_path)
   



compiler_options_files = extract_compiler_options_file_from_ide()

row_options, col_options = get_user_options("example_options/compiler_options_input.txt")
print row_options, col_options
for col_item in col_options:
   ind_col_options = re.split(",",col_item)
   for row_item in row_options:
      ind_row_options = re.split(",",row_item)
      update_config_xml(project_location, config, compiler_options_files, ind_row_options, ind_col_options)

#revert_configuration(project_location)
'''