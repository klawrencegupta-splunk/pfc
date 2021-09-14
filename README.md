1.1.6 notes

**Fixed css for hover over to be readable instead of black on black**

<style>
 .table th {
          background-image: linear-gradient(to bottom, #34495E, #34495E) !important;
          text-shadow: none !important;
       }
 .table th a{
          color: white !important;
       }
  table tr.odd td{
        background: #F8F9F9 !important;
      }
  table tr.even td{
        background: #CACFD2 !important;
      }
  table tr td{
        color: #00000 !important;
      }
</style>

<p>

**s3.py**
* added prompt for bucket name
* addedd clean_up function to remove gzip files from downloads directory
* cleaned up print statements


**Summary Report**
* added
** skipped searches
** dm count
** size of lookups

1.1.5  notes

* CSS style & color is now consistent across all tables & all views
* additional documentation for GDI added
* UF distribution by major version + bar chart
* resource usage table uses icons green checkbox/red X for status instead of conditional cell color
* splunk queue blocks drilldown uses a column chart + overlay 
* search analysis view restructured & drilldown for table view fixed + search count added

1.1.1 notes

added the following as alignment from SplunkCloud Global Monitoring Console

Landing Page
* of Users found total & per day
	| tstats prestats=true summariesonly=false allow_old_summaries=false dc("DM_searchdata.user") as "Distinct Count of user" FROM datamodel=DM_searchdata.DM_searchdata WHERE nodename=DM_searchdata | stats dedup_splitvals=t dc(DM_searchdata.user) AS "Distinct Count of user" | fillnull "Distinct Count of user" | fields + "#Users Found"
       
* UF versions - pie chart
    index=pfc  "uf" OR "fwd" OR "universal" NOT sourcetype=XML* fwdType=uf | stats count by version

Search Activity
* of DM by app, user
    index=pfc sourcetype="audit_log" savedsearch_name="_ACCELERATE_DM*" | stats dc(savedsearch_name)

Splunk Operations
* index activity in terms of sizes (metrics.log)
    index=pfc sourcetype="metrics_log" group=per_index_thruput | eval gb=round(kb/1024/1024,2) | stats sum(gb) AS gb by series | where gb>0

1.1.0_version notes

* Added tabs.css 
--> for formatting only to _self panes
* Added splunkbase_app_stats_small.csv from Splunkbase pull of apps/versions and support status
--> Gives a detailed table now of all apps their installed version vs the latest splunk version and the last know support status
* Added app.conf ingest stanzas for installed app version and for comparison to Splunkbase

* #Create Lookup JS fix
Add the following the create lookup button to also reload the dashboard after the creations of the lookup is clicked.

require([
    'jquery',
    'splunkjs/mvc/simplexml/ready!'
], function($){
        $('#refresh').on("click",function(){
                setTimeout("location.reload();", 0);
        });
});


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



