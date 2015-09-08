import re
import sys
import os
import shutil
import subprocess
import time
import ftplib        # Nalini: 20 Nov 2014 - add support to transfer files via FTP
import threading
import socket
import errno


def get_file_names(file_path, _file_extn_to_be_commited):
   
   _file_extn_to_be_commited = _file_extn_to_be_commited.strip("*")
   
   filename = ''                                               # of Files availbale anf the number of Files.
   FileCount = 0
   FileArray = []
   for filename in os.listdir(file_path):                       # Lists the Files in the given Location
      if filename.upper().endswith(_file_extn_to_be_commited.upper()):                          # If Ends with Make,
         FileArray.append(os.path.join(file_path,filename))                         # Append to the return array List
         FileCount = FileCount + 1                          # Track the Count

   return(FileArray)                                 # Return the found items and the number.
   
   
   
def commit_files(svn_base_path, _files_to_be_commited_svn_dir, available_files_list_array):
   full_svn_path = svn_base_path + "/" + _files_to_be_commited_svn_dir
   
   #full_svn_path = re.sub("//","",full_svn_path)
   
   commit_directory = "commit_directory"
   
   if os.path.exists(commit_directory):
      try:
         shutil.rmtree(commit_directory)
      except:
         print "unable to remove CO Dir"
         
   try:
      os.mkdir(commit_directory)
   except:
      print "unable to mkdir"
      
   co_command = "svn co \"" + full_svn_path + "\" \"" + commit_directory + "\" " + " --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
   os.system(co_command)
   
   if os.path.exists(commit_directory):
      for item in available_files_list_array:
         shutil.copy(item, commit_directory)
         print "*" * 20
         print "Adding File"         
         svn_add_command = "svn add \"" + commit_directory + "/" + os.path.split(item)[1] + "\" --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
         print "Command: " + svn_add_command
         os.system(svn_add_command)
         print "*" * 20
         
         
         build_number = "build_number: " + os.getenv('BUILD_NUMBER', "LOCAL_RUN")
         build_id = "build_date: " + os.getenv('BUILD_ID', "LOCAL_RUN")
         jobname = "Job: " + os.getenv('JOB_NAME', "LOCAL_RUN")
         
         commit_message = jobname + ", " + build_number + ", " + build_id
         
         print "*" * 20
         print "Commiting File"
         svn_add_command = "svn commit \"" + commit_directory + "/" + os.path.split(item)[1] + "\" -m \"" + commit_message + "\" --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
         print "Command: " + svn_add_command
         os.system(svn_add_command)   
         print "*" * 20


def create_commit_dir_in_repo(svn_base_path, files_to_be_commited_svn_dir_array):
   commit_directory = "commit_directory"
   
   if os.path.exists(commit_directory):
      try:
         shutil.rmtree(commit_directory)
      except:
         print "unable to remove CO Dir"
         
   try:
      os.mkdir(commit_directory)
   except:
      print "unable to mkdir"
      
   co_command = "svn co \"" + svn_base_path + "\" \"" + commit_directory + "\" " + " --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
   os.system(co_command)
   
   for i in range(len(files_to_be_commited_svn_dir_array)):
      dpath = os.path.join(commit_directory, files_to_be_commited_svn_dir_array[i])
      if os.path.exists(dpath):
         print "Dir Exists: " + dpath
      else:
         os.makedirs(dpath)
         a = files_to_be_commited_svn_dir_array[i]
         a = re.sub(r"\\","/",a)
         first_dir = re.split("/",a)[0]
         
         svn_dir_to_add = os.path.join(commit_directory, first_dir)
         
         co_command = "svn add \"" + svn_dir_to_add + "\" --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
         print co_command
         os.system(co_command)
         
         co_command = "svn commit \"" + commit_directory + "\" -m \"Creating Directory Structure\" --trust-server-cert --non-interactive --username hudson_arbs --password Microchip"
         print co_command
         os.system(co_command)                
         


def get_files_and_commit_dir(svn_commit_info_csv_file, project_dir):
   
   report_files_array = []
   
   svn_link_array, files_to_be_commited, local_dir = [],[],[]
   
   _files_to_be_commited = []
   _files_to_be_commited_local_dir = []
   _files_to_be_commited_svn_dir = []
   
   svn_base_path = ''
   
   #csv_file_full_path = os.path.join(project_dir, svn_commit_info_csv_file)
   ##csv_file_full_path = "csv_file\\ARBS_JOB_DESCRIPTION.CSV"
   
   csv_file_full_path = svn_commit_info_csv_file
   
   
   if os.path.exists(csv_file_full_path):
      fptr = open(csv_file_full_path)
      
      for line in fptr:
         line = line.strip("\n")
         line = re.sub("\"","",line)
         line = re.sub("\n","",line)
         line = re.sub("\t","",line)
         line = re.sub("\r","",line)
         #line = re.sub(" ","",line)         
         
         
         array = re.split(",",line)
         
         if re.search("^BUILD_ARTIFACT_SOURCE_FOLDER", line):
            
            report_path_first_link = re.split(";",array[1])[0].strip(" ")
            
            report_paths = project_dir + "/" + report_path_first_link.strip("/")
            
            
            if report_path_first_link == '':
               file_name = "NA"
               file_name_path = "NA"  
            elif report_path_first_link == "." or report_path_first_link == "*.*" or report_path_first_link == "*":
               file_name = ""
               file_name_path = project_dir 
            elif os.path.isdir(report_paths):
               file_name = ""
               file_name_path = report_paths.strip("/")
            else:
               file_name = os.path.split(report_paths)[1]
               file_name_path = os.path.split(report_paths)[0]
            
            if os.path.exists(file_name_path):
            
               all_files_dirs = os.listdir(file_name_path)
               
               for f in all_files_dirs:
               
                  if os.path.isfile(file_name_path + "/" + f):   ## Scan only for files, not for directories
                  
                     if re.search("\*\.\*", file_name):  # This is *.*
                        report_files_array.append(file_name_path + "/" + f)
                        
                     elif re.search("\*\.", file_name): # This must be a file type like *.html
                        file_type = re.split("\.",file_name)[1]
                        if f.endswith(file_type):
                           report_files_array.append(file_name_path + "/" + f)
                           
                     elif re.search("\.", file_name): # This must be a file name
                        if f.lower() == file_name.lower():
                           report_files_array.append(file_name_path + "/" + f)
                           
                     else: # This must be a folder, put all the files under report
                        report_files_array.append(file_name_path + "/" + f)
                        
                        
                        
         if re.search("^COMMIT_BASE_PATH", line):
            
            svn_base_path = array[1]
       
         if re.search("^COMMIT_FILE",line):
            _files_to_be_commited.append(array[1].strip("/|\\").strip(" "))
            _files_to_be_commited_local_dir.append(array[2].strip("/|\\").strip(" "))
            _files_to_be_commited_svn_dir.append(array[3].strip("/|\\").strip(" "))
            
      
      fptr.close()  
   
   create_commit_dir_in_repo(svn_base_path, _files_to_be_commited_svn_dir)
   
   for i in range(len(_files_to_be_commited)):
      file_path = os.path.join(project_dir, _files_to_be_commited_local_dir[i])
            
      if os.path.exists(file_path):
         available_files_list = get_file_names(file_path, _files_to_be_commited[i])
         
         
         commit_files(svn_base_path, _files_to_be_commited_svn_dir[i], available_files_list)
         
   return(report_files_array)
   
   
def get_svn_revision(project_dir):
   svn_rev, svn_link = '',''
   
   if os.path.exists(project_dir):
      command = "svn info " + project_dir + " > svn_log.txt" 
      
      if 'win32' == sys.platform:
         command = "svn info -r BASE Project > svn_log.txt 2>&1" 
         os.system('"' + command + '"')
      else:
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
   
def inject_env_variables():   
   # Read the mcpr file and create the required environment variables needed.
   a = 0


def connect_to_FTP_send_files(svn_commit_info_csv_file, project_dir):
    # Nalini: 20 Nov 2014 - add support to transfer files via FTP
    ftp_host_name = ['']
    ftp_username = ['']
    ftp_password = [''] 
    files_to_transfer = []
    files_to_transfer_local_dir = []
    files_to_transfer_remote_dir = [] 
    ftp_num = 0
    Num_of_files = [0,0,0,0,0,0,0,0,0,0,0,0]
    local_file_path = ''
    remote_dir_path = ''
    remote_dir_path_array = []
    remote_pwd = ''
    remote_dir_path_exists = 0
    dir_exists = 0
    BLOCKSIZE = 8192  # chunk size to read and transmit: 8 kB
    
    
    # csv_file_full_path = os.path.join(project_dir, svn_commit_info_csv_file)    # comment this in final
    ##csv_file_full_path = "csv_file\\ARBS_JOB_DESCRIPTION.CSV"
   
    csv_file_full_path = svn_commit_info_csv_file    # retain this in final
    
    
    if os.path.exists(csv_file_full_path):
        fptr = open(csv_file_full_path)
        
        for line in fptr:
            line = line.strip("\n")
            line = re.sub("\"","",line)
            line = re.sub("\n","",line)
            line = re.sub("\t","",line)
            line = re.sub("\r","",line)
            #line = re.sub(" ","",line)         
            
            
            array = re.split(",",line)
            
            if re.search("^FTP_HOST_NAME", line):
                ftp_num += 1
                ftp_host_name[ftp_num-1] = array[1]
                ftp_username[ftp_num-1] = array[2]
                ftp_password[ftp_num-1] = array[3]
            
            if re.search("^TRANSFER_FILE",line):
                files_to_transfer.append(array[1].strip("/|\\").strip(" "))
                files_to_transfer_local_dir.append(array[2].strip("/|\\").strip(" "))
                files_to_transfer_remote_dir.append(array[3])           #.strip("/|\\").strip(" "))
                Num_of_files[ftp_num-1] += 1
            
        fptr.close()

    if (ftp_host_name != ''):
          
        for i in range(ftp_num):                          
            try:
                # In case the ftp base path contains ftp:// at the beginning, remove it. 
                # The ftp:// is only mandatory for a URL but the ftplib library expects only the hostname of the FTP server. 
                ftp_host_name[i] = re.sub('^ftp://', '', ftp_host_name[i])
                # establish FTP connection to the server using the login credentials provided       
                session = ftplib.FTP(ftp_host_name[i], ftp_username[i], ftp_password[i])
                session.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                session.set_debuglevel(2)
                session.voidcmd("TYPE I")
            except ftplib.all_errors, e:
                print e
            else:
                for j in range(Num_of_files[i]):
                    # reset values
                    remote_dir_path_exists = 0
                    dir_exists = 0
                    # get the present working directory on the ftp server
                    remote_pwd = session.pwd()
                    
                    # get the remote directory path to which the file has to be transferred
                    remote_dir_path = files_to_transfer_remote_dir[j]
                    # replace backward slashes in the path with forward slash
                    remote_dir_path = re.sub(r"\\", "/", remote_dir_path)
                    
                    if ((remote_dir_path == '/') or (remote_dir_path == '')):        
                        # remote dir is root folder
                        # set the current working directory as root and go to file transfer
                        session.cwd('/') 
                    
                    else:
                        # check if remote_dir_path and the remote_pwd are same; if yes, go ahead with the FTP transfer
                        # if not, first check whether the remote directory path exists or needs to be created
                        if (remote_dir_path != remote_pwd):
                            remote_dir_path = remote_dir_path.strip('/')
                            remote_dir_path_array = re.split("/", remote_dir_path)
                            # set the current working directory as root
                            session.cwd('/')
                            for d in range(len(remote_dir_path_array)):
                                filelist1 = []
                                session.retrlines('LIST', filelist1.append)
                                for f1 in filelist1:
                                    if re.search("<DIR>", f1):
                                        if re.search(remote_dir_path_array[d] + '$', f1):
                                            dir_exists = 1
                                            session.cwd(remote_dir_path_array[d])
                                            if (d == len(remote_dir_path_array)-1):
                                                remote_dir_path_exists = 1
                                            break
                                        else:
                                            # sub-directory needs to be created
                                            dir_exists = 0
                                if (dir_exists != 1):
                                    break
                            
                            # check the value of d here. That should tell us what directories already exist and what needs to be created, at what level
                            # store the value of d in another variable
                            d_val = d
                                                    
                            if (remote_dir_path_exists == 0):
                                for c in range(d_val, len(remote_dir_path_array)):
                                    # print remote_dir_path_array[c]
                                    session.mkd(remote_dir_path_array[c])
                                    session.cwd(remote_dir_path_array[c])
                                
                                        
         
                    local_file_path = os.path.join(project_dir, files_to_transfer_local_dir[j])
            
                    if os.path.exists(local_file_path):
                        available_files_list = get_file_names(local_file_path, files_to_transfer[j])
                        # open each file in the available_files_list, and then send it via ftp and close the file
                        for upfile in available_files_list:
                            # name for the file when stored on the FTP server. The local file will be stored on the FTP server by this name    
                            Remote_FileName = os.path.basename(upfile)

                            # Store command, consisting of STOR followed by the remote file name (name of the file on the FTP server)        
                            datasock, esize = session.ntransfercmd('STOR %s' % Remote_FileName)
                            size = os.stat(upfile)[6]  
                            # send the file
                            try:   
                                def background():
                                    # file to send will be opened in order to be able to read it
                                    fd = open(upfile, 'rb')
                                    bytes_so_far = 0
                                    
                                    while 1:
                                        buf = fd.read(BLOCKSIZE)
                                        if not buf:
                                            break
                                        try:
                                            datasock.sendall(buf)
                                        except socket.error as error:
                                            if error.errno == errno.WSAECONNRESET:
                                                print error
                                        
                                        bytes_so_far += len(buf)
                                        print("\rFile:", Remote_FileName, "Sent", bytes_so_far, "of", size, "bytes", \
                                              "(%.1f%%)\r" % (100 * bytes_so_far / float(size)))
                                        sys.stdout.flush()
                                    
                                    datasock.close()
                                    fd.close()

                                t = threading.Thread(target=background)
                                t.start()
                                while t.is_alive():
                                    # t.join(2)                                    
                                    session.voidcmd('NOOP')
                                    t.join(2)
                                   # time.sleep(5)                   
                                
                                
                                
                            except ftplib.all_errors, e:
                                print e

                            
                # quit FTP session                              
                session.quit()
                # close the Connection
                session.close()

                    
def get_attach_files_info(svn_commit_info_csv_file, project_dir):
    # Nalini: 16 Feb 2015 - add support to attach files/reports in email

    files_to_attach = []
    files_to_attach_local_dir = []
    Num_of_files = 0
    local_path = ''
    file_name_path = ''
    attach_files_array = []
    
    
    #csv_file_full_path = os.path.join(project_dir, svn_commit_info_csv_file)    # comment this in final
    ##csv_file_full_path = "csv_file\\ARBS_JOB_DESCRIPTION.CSV"
   
    csv_file_full_path = svn_commit_info_csv_file    # retain this in final
    
    
    if os.path.exists(csv_file_full_path):
        fptr = open(csv_file_full_path)
        
        for line in fptr:
            line = line.strip("\n")
            line = re.sub("\"","",line)
            line = re.sub("\n","",line)
            line = re.sub("\t","",line)
            line = re.sub("\r","",line)
            #line = re.sub(" ","",line)         
            
            
            array = re.split(",",line)

            
            if re.search("^ATTACH_FILE",line):
                Num_of_files += 1
                files_to_attach.append(array[1].strip("/|\\").strip(" "))
                files_to_attach_local_dir.append(array[2].strip("/|\\").strip(" "))
                
            
        fptr.close()
    
    if (Num_of_files > 0):
        for i in range(Num_of_files):
            local_path = os.path.join(project_dir, files_to_attach_local_dir[i])
            file_name_path = local_path + "/" + files_to_attach[i]
            attach_files_array.append(file_name_path)
            
    return (attach_files_array)     
            
            

   
if __name__ == "__main__":

   current_file_path = sys.argv[0]

   new_path = os.path.split(current_file_path)[0]

   if new_path != '':
      os.chdir(new_path)
   
   project_dir = ""
   script_to_be_executed = ""
   svn_commit_info_csv_file = ""
   
   script_type = ''
   
   for arg in sys.argv:                                           # Iterate and receive the parameters from command line.

      if re.search("-project_dir=",arg):
         project_dir = re.split("=",arg)[1]
      if re.search("-script=",arg):
         script_to_be_executed = re.split("=",arg)[1]
      if re.search("-svn_commit_info_file=",arg):
         svn_commit_info_csv_file = re.split("=",arg)[1]         
   
   
   if script_to_be_executed != '':
   
      if re.search("\.", script_to_be_executed):
         if script_to_be_executed.lower().endswith("bat"):
            print "Batch file execution"
            script_type = "bat"
         elif script_to_be_executed.lower().endswith("sh"):
            print "Shell file execution"
            script_type = "sh"
         elif script_to_be_executed.lower().endswith("py"):
            print "Python File execution, executable to be identified from given environment path"
            script_type = "python"     
         elif script_to_be_executed.lower().endswith("pl"):
            print "Perl File execution, executable to be identified from given environment path"
            script_type = "perl"                
      else:
         print "Generic Shell/Batch File Execution"
         script_type = "generic_bat_shell"
         
   else:
   
      print "Empty Script cannot be executed"
      sys.exit()
   
   inject_env_variables()
   
   
   command_for_exec = []
   
   if script_type == "bat":
      command_for_exec.append(script_to_be_executed)
      
   elif script_type == "sh":
      command_for_exec.append("sh")
      command_for_exec.append(script_to_be_executed)
      
   elif script_type == "generic_bat_shell":
   
      if 'win32' == sys.platform:
         command_for_exec.append(script_to_be_executed)
      else:
         command_for_exec.append("sh")
         command_for_exec.append(script_to_be_executed)      
         
   #################################################
   # Change of CWD to Project Working Directory
   cwd = os.getcwd()
   os.chdir(os.path.join(cwd, project_dir))
   ##################################################
   # Execute the script file
   Process1 = subprocess.Popen(command_for_exec)
   
   TimeOut = 0
   
   while(None == Process1.poll()):                 # Check for the existance of the process
      time.sleep(1)
      TimeOut = TimeOut + 1   
   
   print "Took " + str(TimeOut) + " Seconds"
   # Execution complete
   ##################################################
   os.chdir(cwd)

   if Process1.returncode == 0:  # If no error, Success
      print "Build Success, Error Code is 0"
   else:
      print "*FAIL*"
      print "Making this build unstable"
  
   report_files_array = []
   attach_files_array = []
   
   if svn_commit_info_csv_file != '':
      
      report_files_array = get_files_and_commit_dir(svn_commit_info_csv_file, project_dir)

   if (svn_commit_info_csv_file != ''):
       connect_to_FTP_send_files(svn_commit_info_csv_file, project_dir)   
   
   
   
   if svn_commit_info_csv_file != '':
      
      attach_files_array = get_attach_files_info(svn_commit_info_csv_file, project_dir)
   
   stat_info_file = "lib_build_statistics.statinfo"
   
   fptr = open(stat_info_file,"w")
   
   fptr.write("MPLAB_TYPE:SRC_BUILD\n")
   
   if Process1.returncode == 0:
      fptr.write("MESSAGE:EXECUTION_RESULT - SUCCESS\n")   
   else:
      fptr.write("MESSAGE:EXECUTION_RESULT - FAILURE\n")   
      
   svn_rev, svn_link = get_svn_revision(project_dir) 
   
   fptr.write("\nSVN_REPO_LINK:" + str(svn_link) + "\n" + "\nCHECKED_OUT_REVISION:" + str(svn_rev) + "\n")
   
   for file in report_files_array:
      fptr.write("\nRESULT_FILE_NAME:" + file + "\n")
   
   if (attach_files_array != []):
       for afile in attach_files_array:
           fptr.write("\nATTACH_FILE:" + afile + "\n")
           
   fptr.close()
   
   
   
   
   
            