
import json
import time
from common import load_json, get_files, load_all_json, compare_arrow_tables, compare_dataframes
#from python_dbs.clickhouse import ClickhouseProcessor
from python_dbs.sqlite import SQLiteProcessor
from python_dbs.postgres import PostgresProcessor
from python_dbs.clickhouse import ClickhouseProcessor
from python_dbs.duckdb import DuckdbProcessor
from python_dbs.clickhouse_postgresql import ClickhousePostgreProcessor
from collections import defaultdict
import subprocess
from subprocess import PIPE
import os

    
# load from progress report json 
progress_report = []
with open("progress_report.json", "r") as f:
    progress_report = json.load(f)

# reset html file to empty
with open("progress_report.html", "w") as f:
    f.write("")
    
list_of_dbms = []

# get all dbms from the progress report
for report in progress_report:
    source_db = report["source_db"]
    # check if source_db is not in the list_of_dbms
    if source_db not in list_of_dbms:
        list_of_dbms.append(source_db)
        
print(list_of_dbms)
    

# Group progress reports by source_db
grouped_reports = defaultdict(list)
for report in progress_report:
    grouped_reports[report['source_db']].append(report)
html = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
  font-family: Arial, sans-serif;
}


.tab {
  overflow: hidden;
  border: 1px solid #ccc;
  background-color: #f1f1f1;
}

.tab button {
  background-color: inherit;
  float: left;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 14px 16px;
  transition: 0.3s;
}

.tab button:hover {
  background-color: #ddd;
}

.tab button.active {
  background-color: #ccc;
}

.tabcontent {
  display: none;
  padding: 6px 12px;
  border: 1px solid #ccc;
  border-top: none;
}

table {
  font-family: Arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

.expandable-content {
  display: none;
  padding-left: 20px;
}

.expandable-row {
  cursor: pointer;
}
</style>
<script>
function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

function toggleContent(header) {
  var content = header.nextElementSibling;
  if (content.style.display === "none" || content.style.display === "") {
    content.style.display = "block";
  } else {
    content.style.display = "none";
  }
}

function toggleExpandableContent(row) {
  var nextRow = row.nextElementSibling;
  if (nextRow.style.display === "table-row") {
    nextRow.style.display = "none";
  } else {
    nextRow.style.display = "table-row";
  }
}
</script>
</head>
<body>

<div class="tab">
"""

# Create tab buttons for each source_db
for i, source_db in enumerate(grouped_reports):
    active_class = " active" if i == 0 else ""
    html += f'<button class="tablinks{active_class}" onclick="openTab(event, \'tab{source_db}\')">{source_db}</button>'

html += "</div>"

# append current html to the file
with open("progress_report.html", "a") as f:
    f.write(html)
    html = ""
    
    
def color_for_percentage(percentage):
    # for 100 do dark green
    # between 80 and 100 do green
    # between 50 and 80 do yellow
    # between 20 and 50 do orange
    # between 0 and 20 do red
    
    if percentage == 100:
        return "darkgreen"
    elif percentage >= 80:
        return "green"
    elif percentage >= 50:
        return "yellow"
    elif percentage >= 20:
        return "orange"
    else:
        return "red"

# Create tab content for each source_db
for i, (source_db, reports) in enumerate(grouped_reports.items()):
    display_style = "block" if i == 0 else "none"
    html += f'<div id="tab{source_db}" class="tabcontent" style="display: {display_style};">'
    
    # create a table for each test_report create a row and then add columns name, success count source and then success count for each target db
    
    html += "<h1>Report for " + source_db + "</h1>"
    
    html += "<table style='width:1200px'>"
    html += "<tr>"
    html += "<th>Test Name</th>"
    html += "<th>Queries</th>"
    html += "<th>Source Success</th>"
    for db in list_of_dbms:
        if db == source_db:
            continue
        
        html += f"<th>{db} Success</th>"
    html += "</tr>"
    
    for test_report in reports:
        total_queries = len(test_report["queries"])
        source_success_count = sum([1 for query_report in test_report["queries"] if query_report["source_success"]])
        source_success_percentage = source_success_count / total_queries * 100
        html += "<tr>"
        # make the name a link which is an anchor to the detailed information
        target_id = (source_db + "_" + test_report['test_name']).replace(" ", "_")
        # on click also auto expand the detailed information
        
        js_open = f"""
        console.log("Opening element with id", "{target_id}");
        var element = document.getElementById(\"{target_id}\");
        console.log(element);
        toggleContent(element);
        """
        
        html += f"<td><a href='#{target_id}' onclick='{js_open}'>{test_report['test_name']}</a></td>"
        html += f"<td>{len(test_report['queries'])}</td>"
        html += f"<td style='background-color: {color_for_percentage(source_success_percentage)}'>{source_success_count} ({source_success_percentage:.2f}%)</td>"
        
        for db in list_of_dbms:
            if db == source_db:
                continue
            
            target_success_count = sum([1 for query_report in test_report["queries"] for target_report in query_report["target_dbs"] if target_report["db"] == db and target_report["success"]])
            target_success_count_percentage = target_success_count / total_queries * 100
            html += f"<td style='background-color: {color_for_percentage(target_success_count_percentage)}'>{target_success_count} ({target_success_count_percentage:.2f}%)</td>"
        
        html += "</tr>"
        
    html += "</table>"
    
    for test_report in reports:
        source_success_count = sum([1 for query_report in test_report["queries"] if query_report["source_success"]])
        element_id = (source_db + "_" + test_report['test_name']).replace(" ", "_")
        html += f"<h2 onclick='toggleContent(this)' style='cursor: pointer;' id='{element_id}'>{test_report['test_name']} ({len(test_report['queries'])}) Success: {source_success_count}</h2>"
        
        html += "<div style='display: none;'>"
        html += "<table>"
        html += "<tr>"
        html += "<th>Nr</th>"
        html += "<th>Query</th>"
        html += "<th>Source Shape</th>"
        html += "<th>Source Result</th>"
        html += "<th>Source Exception</th>"
        html += "<th>Source Success</th>"
        for db in list_of_dbms:
            if db == test_report["source_db"]:
                continue
            
            html += f"<th>{db} Success</th>"
        html += "</tr>"
        
        query_count = 0
        for query_report in test_report["queries"]:
            query_count += 1
            html += "<tr class='expandable-row' onclick='toggleExpandableContent(this)'>"
            html += f"<td>{query_count}</td>"
            html += f"<td><span style=\"white-space: pre-line\">{query_report['query']}</span></td>"
            html += f"<td>{query_report['source_shape']}</td>"
            html += f"<td>{query_report['source_result_html']}</td>"
            html += f"<td>{query_report['source_exception']}</td>"
            html += f"<td style='background-color: {'green' if query_report['source_success'] else 'red'}'>{query_report['source_success']}</td>"
            
            for target_report in query_report["target_dbs"]:
                if target_report["db"] == test_report["source_db"]:
                    continue
                
                html += f"<td style='background-color: {'green' if target_report['success'] else 'red'}'>{target_report['success']}</td>"
            
            html += "</tr>"
            
            # Add hidden expandable content
            html += "<tr class='expandable-content'>"
            html += f"<td colspan='100%'>"  # Spanning all columns for the detailed information
            html += "<div>"
            # make table row with the details
            html += "<table>"
            
            first = True
            for target_report in query_report["target_dbs"]:

                if first:
                    html += "<tr>"
                    html += f"<th>DB</th>"
                    html += f"<th>Success</th>"
                    html += f"<th>Error</th>"
                    html += f"<th>Result</th>"
                    html += f"<th>Shape</th>"
                    html += f"<th>Shape Equal</th>"
                    html += f"<th>Columns Equal</th>"
                    html += f"<th>Dtypes Equal</th>"
                    html += f"<th>Values Equal</th>"
                    html += f"<th>Full Match</th>"
                    html += "</tr>"
                    
                first = False
                
                html += "<tr>"
                html += f"<td>{target_report['db']}</td>"
                html += f"<td style='background-color: {'green' if target_report['success'] else 'red'}'>{target_report['success']}</td>"
                html += f"<td>{target_report['error']}</td>"
                html += f"<td>{target_report['result_html']}</td>"
                html += f"<td>{target_report['shape']}</td>"
                html += f"<td>{target_report['shape_equal']}</td>"
                html += f"<td>{target_report['columns_equal']}</td>"
                html += f"<td>{target_report['dtypes_equal']}</td>"
                html += f"<td>{target_report['values_equal']}</td>"
                html += f"<td>{target_report['full_match']}</td>"
                html += "</tr>"
                
            html += "</table>"
            html += "</div>"
            html += "</td>"
            html += "</tr>"
        
        html += "</table>"
        html += "</div>"
        
        # append current html to the file
        with open("progress_report.html", "a") as f:
            f.write(html)
            html = ""
            
    
    html += "</div>"

html += """
</body>
</html>
"""



with open("progress_report.html", "a") as f:
    f.write(html)
    html = ""