1.0.9 release notes

* added lookup for Eventtypes extended explanations
* fixed HT/NoHT logic on Landing Page & normalized Column names
* added new panel to Splunk Search Analysis for more context on skipped searches eligible/dispatched averages
* added new Summary PDF Report

#eventtypes.csv

eventtype_desc_name, eventtype
"Incomplete Search Results - search requests from indexers were incomplete", incomplete_search_results
"Searches were skipped - 1 more more scheduled jobs were skipped", searches_skipped_true
"Splunk REST API - the /server/info is taking a long time to respond", server_info_long_response_time
"Splunk Broken Pipes - the TcpInput processor is reporting TCP ingest problems", tcpinputproc_broken_pipes
"Splunk Time Skew Found - the NTP timingis out of sync between the search and indexer tier", time_skew_found

Summary Report Contents

#SH/Peers/Forwarders/Indexes

index=pfc (sourcetype=splunkd_log AND site) OR (sourcetype=metrics_log sourceHost OR Peer_Count) OR (sourcetype="peers_csv") OR (sourcetype=audit_log action=search "search/jobs/" NOT "search/jobs/16*") 
| rex field=_raw "remote.(?<origin_sh>.{1,25})_subsearch" 
| eval index_count=mvcount(split(searchable_indexes,","))-1 
| stats dc(origin_sh) AS "# of SH" max(Peer_Count) AS "# of IDX" dc(sourceHost) AS "Forwarder count" max(index_count) AS "Index Count" | table "# of SH"

#Host Table Info

index=pfc sourcetype="resource_usage_log" OR (sourcetype=systeminfo_txt AND build) | stats max(data.cpu_count) AS phys_cpu max(data.virtual_cpu_count) AS vcpu max(data.mem) AS mem_kb max(data.splunk_version) AS  splunk_version by host_short_name host | eval ht_status=if(searchmatch("vcpu!=phys_cpu"),"HT enabled", "HT NOT Enabled") | lookup host_role.csv host_short_name OUTPUT role | eval "Memory GB"=mem_kb/1024  | table host host_short_name role splunk_version ht_status phys_cpu vcpu "Memory GB" splunk_version | rename host AS "Diag File Path" | rename role AS Role | rename splunk_version AS "Splunk Version" | rename ht_status AS "Hyper-Threading Status" | rename phys_cpu AS "Physical CPUs" | rename vcpu AS "vCPU"

#Searches per Day

| tstats prestats=true summariesonly=false allow_old_summaries=false dc("DM_searchdata.data.search_props.sid") as "Distinct Count of data.search_props.sid" FROM datamodel=DM_searchdata.DM_searchdata WHERE nodename=DM_searchdata BY _time span=1d DM_searchdata.host_short_name | eval "DM_searchdata.data.search_props.app"='DM_searchdata.data.search_props.app', host_short_name='DM_searchdata.host_short_name' | eval _time='_time' | timechart dedup_splitvals=t dc(DM_searchdata.data.search_props.sid) AS dc_sids span=1d  | sort limit=0 _time | fields + _time, dc_sids | eval dc_sids=tonumber(dc_sids) | where dc_sids>0

#Total Apps Count
| tstats prestats=true summariesonly=false allow_old_summaries=false count as "Count of DM_searchdata" FROM datamodel=DM_searchdata.DM_searchdata WHERE nodename=DM_searchdata BY "DM_searchdata.data.search_props.app" | stats dedup_splitvals=t count AS "Count of DM_searchdata" by DM_searchdata.data.search_props.app | sort limit=10000 "Count of DM_searchdata" | fields - _span | rename "DM_searchdata.data.search_props.app" as "data.search_props.app" | fillnull "Count of DM_searchdata" | fields + "data.search_props.app" | sort +"data.search_props.app" | stats dc("data.search_props.app") AS "App Count"

#Total Apps Count/List
| tstats prestats=true summariesonly=false allow_old_summaries=false dc("DM_searchdata.data.search_props.sid") as "search count" FROM datamodel=DM_searchdata.DM_searchdata WHERE nodename=DM_searchdata BY "DM_searchdata.data.search_props.app" | stats dedup_splitvals=t dc(DM_searchdata.data.search_props.sid) AS "search count" by DM_searchdata.data.search_props.app | sort limit=100 DM_searchdata.data.search_props.app | fields - _span | rename "DM_searchdata.data.search_props.app" as "data.search_props.app" | fillnull "search count" | fields + "data.search_props.app", "search count" | sort - "search count"

#Resource Usage Summary

| tstats prestats=true summariesonly=false allow_old_summaries=false values("DM_resourcelogdata.data.cpu_idle_pct") as "values of data.cpu_idle_pct", values("DM_resourcelogdata.data.avg_total_ms") as "values of data.avg_total_ms", values("DM_resourcelogdata.data.mem_perc_used") as "values of Memory % used" FROM datamodel=DM_resourcelogdata.DM_resourcelogdata WHERE (nodename=DM_resourcelogdata "DM_resourcelogdata.host_short_name"="*") BY "DM_resourcelogdata.host_short_name" | stats dedup_splitvals=t values(DM_resourcelogdata.data.cpu_idle_pct) AS CPU values(DM_resourcelogdata.data.avg_total_ms) AS STORAGE values(DM_resourcelogdata.data.mem_perc_used) AS MEM by DM_resourcelogdata.host_short_name | stats perc25(CPU) AS CPU perc25(MEM) AS MEM perc75(STORAGE) AS STORAGE by DM_resourcelogdata.host_short_name | eval cpu_exhaustion_status=if(searchmatch("CPU<45.00"),"CPU Exhaustion Found", "CPU OK") 
| eval high_memutil_status=if(searchmatch("MEM>90.00"),"High Memory Utilization Found", "Memory OK") 
| eval storage_contention_status=if(searchmatch("STORAGE>10.00"),"Storage Contention Found", "Storage OK") | rename DM_resourcelogdata.host_short_name AS host_short_name | lookup host_role.csv host_short_name OUTPUT role

#Queue Blocks by host

| tstats prestats=true summariesonly=false allow_old_summaries=false values("DM_splunkops.blocked") as "Distinct Values of blocked", count("DM_splunkops.blocked") as "Count of blocked" FROM datamodel=DM_splunkops.DM_splunkops WHERE (nodename=DM_splunkops "DM_splunkops.host_short_name"="*") BY "DM_splunkops.host_short_name" | stats dedup_splitvals=t count(DM_splunkops.blocked) AS block_count by DM_splunkops.host_short_name | eval "Blocked Status"=if(searchmatch("block_count>0"), "Blocked Queues", "No Blocks") | table DM_splunkops.host_short_name block_count | rename DM_splunkops.host_short_name AS host_short_name | sort -block_count

#Problem Events

index=pfc eventtype=incomplete_search_results OR eventtype=tcpinputproc_broken_pipes OR eventtype=server_info_long_response_time OR eventtype=searches_skipped_true OR eventtype=time_skew_found | stats count by eventtype host_short_name | lookup host_role.csv host_short_name OUTPUT role | sort -count | lookup eventtypes.csv eventtype OUTPUT eventtype_desc_name | table eventtype_desc_name host_short_name count


