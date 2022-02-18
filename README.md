Development Release -- 1.3.1 version release notes
+ Landing Page Bugs Fixed
+ New Splunk Operations Dashboard
+ Temp Bug (Create Lookup Macro) *to be fixed in v1.4.0
+ Eventtypes added for CM/SHC replication failures


Pre-Production Release -- 1.3.0 version release notes
+ Admin page added 
+ Data Model Status
+ PFC Data Available by Time Frame & size on disk (MB)
+ Sum (GB) by sourcetype

+ |rest /servicesNS/nobody/-/admin/summarization/tstats:DM_pfc_DM_deploymentInfo | table eai:acl.app title summary.complete summary.size 
| append [|rest /servicesNS/nobody/-/admin/summarization/tstats:DM_pfc_DM_resourcelogdata | table eai:acl.app title summary.complete summary.size ] 
| append [rest /servicesNS/nobody/-/admin/summarization/tstats:DM_pfc_DM_searchdata | table eai:acl.app title summary.complete summary.size ]
| append [|rest /servicesNS/nobody/-/admin/summarization/tstats:DM_pfc_DM_splunkops | table eai:acl.app title summary.complete summary.size ]

+ Landing Page Host Table - add flag for 99% utilization of any host volume & improve search performance
done - index=pfc (sourcetype="resource_usage_log" component=Hostwide) OR (sourcetype=systeminfo_txt AND ("**********" "/dev" NOT ("summary" OR "datamodel" OR hot))) |  rex field=_raw "(?<fs>.\\w+[\\s|\\W\\w]\\w+[\\s|\\W\\w+])\\s+(?<onekblks>\\d+)\\s+(?<used>\\d+)\\s+(?<avail>\\d+)\\s+(?<use_perc>\\d+)\\W\\s(?<path>.+)" max_match=200  
 | stats max(use_perc) AS use_perc max(data.cpu_count) AS phys_cpu max(data.virtual_cpu_count) AS vcpu max(data.mem) AS mem_kb max(data.splunk_version) AS splunk_version by host_short_name host | eval vcpu=tonumber(vcpu) | eval phys_cpu=tonumber(phys_cpu) | eval ht_status=if(vcpu>phys_cpu,"HT enabled", "HT NOT Enabled") | lookup host_role.csv host_short_name OUTPUT role | eval "Memory GB"=mem_kb/1024  | table host host_short_name role splunk_version ht_status phys_cpu vcpu "Memory GB" splunk_version use_perc | rename host AS "Diag File Path" | rename role AS Role | rename splunk_version AS "Splunk Version" | rename ht_status AS "Hyper-Threading Status" | rename phys_cpu AS "Physical CPUs" | rename vcpu AS "vCPU" | eval disk_alert=if(searchmatch("use_perc>99"), "Disk Utilization Over 99%", null)

+ done - Role Identification includes conditions for universal_fowarder when SWAP AND CPU information isn't available (no resource_usage.log for a UF in a diag)

+ Landing Page vCPU estimate
done -- validate it is role conditional in the calc - heavy fwd are clocking in 

+ Resource Usage - added SWAP flag
done - | tstats prestats=true summariesonly=false allow_old_summaries=false max(DM_resourcelogdata.data.swap_used) AS data.swap_used values("DM_resourcelogdata.data.cpu_idle_pct") as "values of data.cpu_idle_pct", values("DM_resourcelogdata.data.avg_total_ms") as "values of data.avg_total_ms", values("DM_resourcelogdata.data.mem_perc_used") as "values of Memory % used" FROM datamodel=DM_resourcelogdata.DM_resourcelogdata WHERE (nodename=DM_resourcelogdata "DM_resourcelogdata.host_short_name"="*") BY "DM_resourcelogdata.host_short_name" 
| stats values(data.swap_used) AS SWAP values(DM_resourcelogdata.data.cpu_idle_pct) AS CPU values(DM_resourcelogdata.data.avg_total_ms) AS STORAGE values(DM_resourcelogdata.data.mem_perc_used) AS MEM by DM_resourcelogdata.host_short_name 
| stats max(SWAP) AS SWAP perc25(CPU) AS CPU perc25(MEM) AS MEM perc75(STORAGE) AS STORAGE by DM_resourcelogdata.host_short_name
| eval "CPU Status"=if(CPU>45.00, "✅", "❌") 
| eval "Memory Status"=if(MEM<35.00, "✅", "❌")
| eval "Storage Status"=if(STORAGE<10.00, "✅", "❌")
| eval "Swap Status"=if(isnull(SWAP),"❌","✅")
| rename DM_resourcelogdata.host_short_name AS host_short_name | lookup host_role.csv host_short_name OUTPUT role
| table host_short_name role *Status CPU MEM STORAGE SWAP
