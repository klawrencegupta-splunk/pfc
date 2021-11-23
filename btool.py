Kate Lawrence-Gupta - Splunk - Platform Architect
#btool analysis script

#Libraries
import os
import re

pfc_path = "/opt/splunk/etc/apps/pfc/downloads/full"
#conf_files = ['server']
y = "outputs"
count = 0  
# \n is placed to indicate EOL (End of Line)


#Functions
def get_dirs(pfc_path):
    subfolders = [ f.path for f in os.scandir(pfc_path) if f.is_dir() ]
    print(subfolders)
    return subfolders

def splunk_run_btool(x,y):
    payload = str(os.system('/opt/splunk/bin/./splunk btool '+ y +' list --dir='+x +' --debug > btool.tmp'))


def path_parsing_func(pfc_path):
    r  = re.search('diag(.+)\-(202\d.\d{1,2}-\d{1,2}).(\d{1,2}-\d{1,2}-\d{1,2})',pfc_path)
    if r is not None:
       host_short_name = str(r.group(1))
       diag_date = str(r.group(2))
       diag_time = str(r.group(3))
       print(host_short_name)
       print(diag_date)
       print(diag_time)
       return host_short_name, diag_date, diag_time

#formats the output from the btool into a log format
#needs some more format fixing
#uses the same precence from btool to preserve a precedence factor
#will also need logic for identifying '[' as a line breaker


if __name__ == "__main__":
    subfolders = get_dirs(pfc_path)
    for x in subfolders:
        x = x+'/etc'
        host_short_name, diag_date, diag_time = path_parsing_func(x)
        splunk_run_btool(x,y)
        btool_log = open("btool.tmp","r")
        for x in btool_log:
            count +=1
            message = diag_date + " " + diag_time + " " + host_short_name + " " + " precedence_factor=" + str(count)+ "   " + str(x)
            print(message)