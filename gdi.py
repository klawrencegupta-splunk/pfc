#Kate Lawrence-Gupta - Splunk - Platform Architect
#Splunk Pre-Flight Check GDI Script:
# GDI.py automates the ingest of Splunk diag files from either a pre-configure AWS-S3 Bucket or a path local to the instance running PFC.

#Libraries
import os
import sys
import shutil
import tarfile
import gzip

#Functions

#Checks that gdi.py is being run as root user and exits
def get_user():
    user = str(os.environ.get('USER'))
    if "root" in user:
       pass
    else:
       print(" !! -- Please run the gdi.py script as root to avoid permissions issues  ")
       quit()

#Checks that the diag files available are not corrupted
def check_files(local_path):
    scandir_iterator = os.scandir(local_path)
    for item in scandir_iterator:
        if os.path.isfile(item.path):
            fname = item.name
            if fname.endswith(".gz"):
                fname = local_path + fname
                print("Checking diag files for corruption: ")
                print(fname)
                with gzip.open(fname) as g:
                     try:
                       while g.read(1024 * 1024):
                           pass
                     except IOError as e:
                           print("Corrupted!", e)
                           quit()
#Find all the diag files in the S3 Bucket name (provided by the user) and downloads them to the PFC staging directory
def sync_s3_folder(bucket_name):
    s3 =    boto3.client("s3")
    objects = s3.list_objects(Bucket = bucket_name)["Contents"]
    for s3_object in objects:
        s3_key = s3_object["Key"]
        path, filename = os.path.split(s3_key)
        if len(path) != 0 and not os.path.exists(path):
           os.makedirs(path)
        if not s3_key.endswith("/"):
           download_to = splunk_path + '/' + filename if path else filename
           s3.download_file(bucket_name, s3_key, download_to)
           print("Files Downloaded\n")
           print(download_to)

def sync_manual_gdi(local_path, splunk_path, fname):
    local_files = local_path + fname
    print("Synced files from:   " + local_files)
    pfc_path = splunk_path + fname
    print("to: " + pfc_path)
    shutil.copy(local_files, pfc_path)
    print(local_files)
    print(pfc_path)
    
#untar function
def untar(fname,splunk_path,full_data_path):
    if fname.endswith(".gz"):
       fname = splunk_path + fname
       tar = tarfile.open(fname, "r:gz")
       tar.extractall(full_data_path)
       tar.close()
    elif fname.endswith(".tar"):
       fname = splunk_path + fname
       tar = tarfile.open(fname, "r:")
       tar.extractall(full_data_path)
       tar.close()
       print("Files Extracted to PFC downloads/full directory")
       print(fname)

#After the diags are extracted to the ingest directory they can be deleted to clean up space
def clean_up(fname,splunk_path):
    fname = splunk_path + fname
    os.remove(fname)
    print("Clean-Up -- Files Deleted\n")
    print(fname)

def print_message():
    print("####")
    print("####")
    print("####")
    print("---------")
    print("This is the Splunk Pre-Flight Check GDI Script ####\n")
    print("There 2 available Getting Data In (GDI) options - both take the diags in their native .tar.gz format and automatically extract to the correct folders for indexing\n")
    print("s3: Download diag files from an S3 Bucket (requires boto3 + awscli configured along with correct AWS secret/access keys. User provides the bucket name of the source diags\n")
    print("manual: Diag files are in a local path on the same instance where Splunk PFC is installed & running. User provides the local directory path of the source diags\n")

def splunk_restart():
    os.system('/opt/splunk/bin/./splunk restart')

def get_env_info():
    SPLUNK_HOME = os.environ.get('SPLUNK_HOME')
    if SPLUNK_HOME is None:
       SPLUNK_HOME = "/opt/splunk/"
    splunk_path = SPLUNK_HOME + "/etc/apps/pfc/downloads/"
    full_data_path = SPLUNK_HOME + "/etc/apps/pfc/downloads/full/"
    print("Diag Download staging directory is set:   " + splunk_path)
    print("Diag Download ingest direcotry is set:   " + full_data_path)
    return splunk_path, full_data_path

## Main Functions

if __name__ == "__main__":
    get_user()
    splunk_path, full_data_path = get_env_info()
    if len(sys.argv) < 2:
       print_message()
       prompt1=input('Which GDI Method do you want to use - s3 or manual? ').lower()
       local_path = None
    else:
      prompt1 = sys.argv[1]
      local_path = sys.argv[2]
      if local_path[-1] == '/':
          pass
      else:
          local_path=local_path+"/"
          print("Local path is:" + local_path)
          print(prompt1)

## S3 - checks for boto3 and then prompts for bucket name *assuming it's already been configured with the awscli ./configure command.
    if prompt1 == 's3':
       try:
         import boto3
         print('\n boto3 is installed')
       except ImportError:
         print('\n The boto3 module not installed - please install boto3 & awscli via pip3 to enable s3 gdi option')
         sys.exit()
       bucket_name = input("Enter your bucket name: ")
       print("Bucket name is: ")
       print(bucket_name)
       sync_s3_folder(bucket_name)
       scandir_iterator = os.scandir(splunk_path)
       for item in scandir_iterator :
           if os.path.isfile(item.path):
              fname = splunk_path+item.name
              check_files(splunk_path,fname)
              untar(fname,splunk_path,full_data_path)
              clean_up(fname,splunk_path)
              splunk_restart()

    elif prompt1 == 'manual':
         if local_path is None:
            local_path = input("Diags need to be copied to the Linux instance running Splunk Pre-Flight Check. At the prompt enter the path (e.g. /home/splunker/) to the diags:")
            print("Local path is:" + local_path)
            if local_path[-1] == '/':
               pass
            else:
               local_path=local_path+"/"
               print("Local path is:" + local_path)
         scandir_iterator = os.scandir(local_path)
         for item in scandir_iterator:
             if os.path.isfile(item.path):
                fname = item.name
                if fname.endswith(".gz"):
                   print("Files found: " + local_path + fname)
                   check_files(local_path)
                   sync_manual_gdi(local_path, splunk_path, fname)
                   untar(fname,splunk_path,full_data_path)
                   clean_up(fname,splunk_path)
                   splunk_restart()

    else:
        print('Please enter either s3 or manual to continue') #an answer that wouldn't be yes or no