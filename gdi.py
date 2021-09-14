import boto3
import os
import shutil
import tarfile

s3 =    boto3.client("s3") 
splunk_path = '/opt/splunk/etc/apps/pfc/downloads/'
full_data_path = '/opt/splunk/etc/apps/pfc/downloads/full/'

def sync_s3_folder(bucket_name):
    objects = s3.list_objects(Bucket = bucket_name)["Contents"]
    for s3_object in objects:
        s3_key = s3_object["Key"]
        path, filename = os.path.split(s3_key)
        if len(path) != 0 and not os.path.exists(path):
           os.makedirs(path)
        if not s3_key.endswith("/"):
           download_to = splunk_path + '/' + filename if path else filename
           s3.download_file(bucket_name, s3_key, download_to)
           print("Files Downloaded")
           print(download_to)

def sync_manual_gdi(local_path,fname):
    if fname.endswith(".gz"):
       local_file = local_path + fname
       pfc_path = splunk_path + fname
       shutil.copy(local_file, pfc_path)
       print(local_file)
       print(pfc_path)
               
def untar(fname,splunk_path):
    if fname.endswith(".gz"):
       tar = tarfile.open(fname, "r:gz")
       tar.extractall(full_data_path)
       tar.close()
    elif fname.endswith(".tar"):
       tar = tarfile.open(fname, "r:")
       tar.extractall(full_data_path)
       tar.close()
       print("Files Extracted to PFC downloads/full directory")
       print(fname)

def clean_up(fname,splunk_path):    
    if fname.endswith(".gz"):
       os.remove(fname)
       print("Clean-Up -- Files Deleted")
       print(fname) 


if __name__ == "__main__":
    prompt1=input('Which GDI Method do you want to use - s3 or manual? ').lower()

    if prompt1 == 's3':
       bucket_name = input("Enter your bucket name: ")
       print("Bucket name is: ")
       print(bucket_name)
       sync_s3_folder(bucket_name)
       scandir_iterator = os.scandir(splunk_path)
       for item in scandir_iterator :
           if os.path.isfile(item.path):
              fname = splunk_path+item.name
              untar(fname,splunk_path)
              clean_up(fname,splunk_path)

    elif prompt1 == 'manual':
         local_path = input("Enter your local folder path with the trailing / (e.g. /home/splunker/)  ")

         print("Local path is: ")
         print(os.listdir(local_path))
         scandir_iterator = os.scandir(local_path)
         for item in scandir_iterator :
             if os.path.isfile(item.path):
                fname = item.name
                sync_manual_gdi(local_path,fname)
                print(fname)
                fname = splunk_path+item.name
                untar(fname,splunk_path)
                clean_up(fname,splunk_path)
    else:
        print('Please enter either S3 or Manual to continue') #an answer that wouldn't be yes or no

