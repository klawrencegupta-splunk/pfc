import boto3
import os
import tarfile

s3 =    boto3.client("s3") 
bucket_name = "klgpfc"
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
           print(download_to)
        
def untar(fname,splunk_path):
    if fname.endswith(".gz"):
       print(fname) 
       tar = tarfile.open(fname, "r:gz")
       tar.extractall(full_data_path)
       tar.close()
    elif fname.endswith(".tar"):
       tar = tarfile.open(fname, "r:")
       tar.extractall(full_data_path)
       tar.close()


if __name__ == "__main__":
    sync_s3_folder(bucket_name)
    scandir_iterator = os.scandir(splunk_path)
    for item in scandir_iterator :
       if os.path.isfile(item.path):
          print(item.name)
          fname = splunk_path+item.name
          untar(fname,splunk_path)
