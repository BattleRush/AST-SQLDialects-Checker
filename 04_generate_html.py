
import json
import time

import numpy as np
from collections import defaultdict
from subprocess import PIPE
import os

for root, dirs, files in os.walk("output"):
    for file in files:
        if file.endswith(".json"):

            # get just the file name without the extension
            file_name = file.split(".")[0]
            html_file = file_name + ".html"
            
            # if the html file exists do not process the json file
            if os.path.exists(os.path.join("output", html_file)):
                # if the file is not older than 1h then regenerate it
                if time.time() - os.path.getmtime(os.path.join("output", html_file)) > 3600:
                  print("Skipping", file)
                  continue
            
            print("Processing", file)

            # load from progress report json 
            progress_report = []
            with open(os.path.join("output", file), "r") as f:
                progress_report = json.load(f)

            # reset html file to empty
            with open(os.path.join("output", html_file), "w") as f:
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


            /* Apply styles to all tables with class 'dataframe' */
            table.dataframe {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                font-size: 16px;
                font-family: Arial, sans-serif;
            }

            table.dataframe th, table.dataframe td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }

            table.dataframe th {
                background-color: #f2f2f2;
                font-weight: bold;
            }

            table.dataframe tbody tr:nth-child(even) {
                background-color: #f9f9f9;
            }

            table.dataframe tbody tr:hover {
                background-color: #f1f1f1;
            }

            table.dataframe th:first-child, 
            table.dataframe td:first-child {
                width: 50px; /* Adjust width of the index column */
            }

            table.dataframe th:first-child {
                background-color: #f2f2f2;
                font-weight: bold;
            }

            /* Apply this CSS only to the table with class 'summary' */
            table.summary th:nth-child(4n+3) {
                border-right: 4px solid d3d3d3; /* thicker red border on the right for header */
            }

            table.summary th:nth-child(4n+4) {
                border-left: 4px solid d3d3d3; /* thicker red border on the left for header */
            }

            table.summary td:nth-child(4n+3) {
                border-right: 4px solid #fff; /* thicker and grayish border on the right for body */
            }

            table.summary td:nth-child(4n+4) {
                border-left: 4px solid #fff; /* thicker and grayish border on the left for body */
            }
            
            /* Apply this CSS only to the table with class 'detailed' */
            table.detailed th:nth-child(2n+6) {
                border-right: 4px solid d3d3d3; /* thicker red border on the right for header */
            }

            table.detailed td:nth-child(2n+6) {
                border-right: 4px solid #fff; /* thicker and grayish border on the right for body */
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
            with open(os.path.join("output", html_file), "a") as f:
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
                # make the first line stickly but only until we scrolled to the end of this table
                html += "<table style='width:1200px' class='summary'>"
                html += "<tr style='position: sticky; top: 0; background-color: white;'>"
                html += "<th>Test Name</th>"
                html += "<th>Queries</th>"
                html += "<th>Source Success</th>"
                for db in list_of_dbms:
                    if db == source_db:
                        continue
                    
                    html += f"<th>{db} Success</th>"
                    html += f"<th>{db} Success Match</th>"
                    html += f"<th>{db} Shape Match</th>"
                    html += f"<th>{db} Result Match</th>"
                html += "</tr>"
                
                success_info = []
                
                all_total_queries = sum([len(test_report["queries"]) for test_report in reports])
                
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
                    html += f"<td style='background-color: {color_for_percentage(source_success_percentage)}'>{source_success_count}/{total_queries} ({source_success_percentage:.2f}%)</td>"
                    
                    for db in list_of_dbms:
                        if db == source_db:
                            continue
                        
                        target_success_count = sum([1 for query_report in test_report["queries"] for target_report in query_report["target_dbs"] if target_report["db"] == db and target_report["success"]])
                        target_success_count_percentage = target_success_count / total_queries * 100
                        html += f"<td style='background-color: {color_for_percentage(target_success_count_percentage)}'>{target_success_count}/{total_queries} ({target_success_count_percentage:.2f}%)</td>"
                    
                        count_success_match = sum([1 for query_report in test_report["queries"] for target_report in query_report["target_dbs"] if target_report["db"] == db and query_report["source_success"] == target_report["success"]])
                        # count shape match only where success matches
                        count_shape_match = sum([1 for query_report in test_report["queries"] for target_report in query_report["target_dbs"] if target_report["db"] == db and target_report["shape_equal"] and query_report["source_success"] == target_report["success"]])
                        count_result_match = sum([1 for query_report in test_report["queries"] for target_report in query_report["target_dbs"] if target_report["db"] == db and target_report["values_equal"] and target_report["success"] == query_report["source_success"]])
                        
                        if count_success_match == 0:
                            count_success_match_percentage = 0
                            count_shape_match_percentage = 0
                            count_result_match_percentage = 0
                        else:
                            count_success_match_percentage = count_success_match / total_queries * 100
                            count_shape_match_percentage = count_shape_match / total_queries * 100
                            count_result_match_percentage = count_result_match / count_success_match * 100
                        
                        # display achieved count/total count (percentage)
                        html += f"<td style='background-color: {color_for_percentage(count_success_match_percentage)}'>{count_success_match}/{total_queries} ({count_success_match_percentage:.2f}%)</td>"
                        html += f"<td style='background-color: {color_for_percentage(count_shape_match_percentage)}'>{count_shape_match}/{total_queries} ({count_shape_match_percentage:.2f}%)</td>"
                        html += f"<td style='background-color: {color_for_percentage(count_result_match_percentage)}'>{count_result_match}/{count_success_match} ({count_result_match_percentage:.2f}%)</td>"
                    
                    
                        success_info.append({
                          "db": db,
                          "total_queries": total_queries,
                          "source_success_count": source_success_count,
                          "source_success_percentage": source_success_percentage,
                          "target_success_count": target_success_count,
                          "target_success_count_percentage": target_success_count_percentage,
                          "count_success_match": count_success_match,
                          "count_success_match_percentage": count_success_match_percentage,
                          "count_shape_match": count_shape_match,
                          "count_shape_match_percentage": count_shape_match_percentage,
                          "count_result_match": count_result_match,
                          "count_result_match_percentage": count_result_match_percentage
                        })
                        
                    html += "</tr>"
                    
                # total row
                html += "<tr>"
                html += "<td><b>Total</b></td>"
                html += f"<td><b>{sum([len(test_report['queries']) for test_report in reports])}</b></td>"
                total_percentage = sum([sum([1 for query_report in test_report['queries'] if query_report['source_success']]) for test_report in reports]) / all_total_queries * 100
                html += f"<td style='background-color: {color_for_percentage(total_percentage)}'><b>{sum([sum([1 for query_report in test_report['queries'] if query_report['source_success']]) for test_report in reports])}/{all_total_queries} ({total_percentage:.2f}%)</b></td>"
                
                for db in list_of_dbms:
                    if db == source_db:
                        continue
                    
                    # sum over success_info
                    total_success_count = sum([x["target_success_count"] for x in success_info if x["db"] == db])
                    total_success_count_percentage = total_success_count / all_total_queries * 100
                    
                    total_count_success_match = sum([x["count_success_match"] for x in success_info if x["db"] == db])
                    total_count_success_match_percentage = total_count_success_match / all_total_queries * 100
                    
                    total_count_shape_match = sum([x["count_shape_match"] for x in success_info if x["db"] == db])
                    total_count_shape_match_percentage = total_count_shape_match / total_count_success_match * 100
                    
                    total_count_result_match = sum([x["count_result_match"] for x in success_info if x["db"] == db])
                    total_count_result_match_percentage = total_count_result_match / total_count_success_match * 100
                    
                    html += f"<td style='background-color: {color_for_percentage(total_success_count_percentage)}'><b>{total_success_count}/{all_total_queries} ({total_success_count_percentage:.2f}%)</b></td>"
                    html += f"<td style='background-color: {color_for_percentage(total_count_success_match_percentage)}'><b>{total_count_success_match}/{all_total_queries} ({total_count_success_match_percentage:.2f}%)</b></td>"
                    html += f"<td style='background-color: {color_for_percentage(total_count_shape_match_percentage)}'><b>{total_count_shape_match}/{total_count_success_match} ({total_count_shape_match_percentage:.2f}%)</b></td>"
                    html += f"<td style='background-color: {color_for_percentage(total_count_result_match_percentage)}'><b>{total_count_result_match}/{total_count_success_match} ({total_count_result_match_percentage:.2f}%)</b></td>"
                
                
                html += "</table>"
                
                for test_report in reports:
                    source_success_count = sum([1 for query_report in test_report["queries"] if query_report["source_success"]])
                    element_id = (source_db + "_" + test_report['test_name']).replace(" ", "_")
                    html += f"<h2 onclick='toggleContent(this)' style='cursor: pointer;' id='{element_id}'>{test_report['test_name']} ({len(test_report['queries'])}) Success: {source_success_count}</h2>"
                    
                    html += "<div style='display: none;'>"
                    html += "<table class='detailed'>"
                    # make the first line stickly but only until we scrolled to the end of this table
                    html += "<tr style='position: sticky; top: 0; background-color: white;'>" 
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
                        html += f"<th>{db} Values Equal</th>"
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
                            value_equal = target_report["values_equal"] and target_report["success"] == query_report["source_success"]
                            html += f"<td style='background-color: {'green' if value_equal else 'red'}'>{value_equal}</td>"
                        
                        html += "</tr>"
                        
                        # Add hidden expandable content
                        html += "<tr class='expandable-content'>"
                        html += f"<td colspan='100%'>"  # Spanning all columns for the detailed information
                        html += "<div>"
                        # make table row with the details
                        
                        html += "<table class='query_detailed'>"
                        
                        first = True
                        for target_report in query_report["target_dbs"]:

                            if first:
                                html += "<tr>"
                                html += f"<th>DB</th>"
                                html += f"<th>Success</th>"
                                html += f"<th>Error</th>"
                                html += f"<th>Result</th>"
                                html += f"<th>Shape</th>"
                                html += f"<th>Data types</th>"
                                html += f"<th>Shape Equal</th>"
                                html += f"<th>Columns Equal</th>"
                                html += f"<th>Dtypes Equal</th>"
                                html += f"<th>Values Equal</th>"
                                html += "</tr>"
                                
                                # add row of source
                                html += "<tr>"
                                html += f"<td><b>{test_report['source_db']}</b></td>"
                                html += f"<td style='background-color: {'green' if query_report['source_success'] else 'red'}'>{query_report['source_success']}</td>"
                                html += f"<td>{query_report['source_exception']}</td>"
                                html += f"<td>{query_report['source_result_html']}</td>"
                                html += f"<td>{query_report['source_shape']}</td>"
                                html += f"<td style='border: 1px solid #dddddd;'>{query_report['source_datatypes']}</td>"
                                html += f"<td style='border: 1px solid #dddddd;'></td>"
                                html += f"<td style='border: 1px solid #dddddd;'></td>"
                                html += f"<td></td>"
                                html += f"<td></td>"
                                html += "</tr>"
                                
                            first = False
                            
                            html += "<tr>"
                            html += f"<td>{target_report['db']}</td>"
                            html += f"<td style='background-color: {'green' if target_report['success'] else 'red'}'>{target_report['success']}</td>"
                            html += f"<td>{target_report['error']}</td>"
                            html += f"<td>{target_report['result_html']}</td>"
                            html += f"<td>{target_report['shape']}</td>"
                            html += f"<td style='border: 1px solid #dddddd;'>{target_report['data_types']}</td>"
                            html += f"<td style='border: 1px solid #dddddd;'>{target_report['shape_equal']}</td>"
                            html += f"<td style='border: 1px solid #dddddd;'>{target_report['columns_equal']}</td>"
                            html += f"<td>{target_report['dtypes_equal']}</td>"
                            html += f"<td>{target_report['values_equal']}</td>"
                            html += "</tr>"
                            
                        html += "</table>"
                        html += "</div>"
                        html += "</td>"
                        html += "</tr>"
                        
                        with open(os.path.join("output", html_file), "a") as f:
                            f.write(html)
                            html = ""
                    
                    html += "</table>"
                    html += "</div>"
                    
                    # append current html to the file
                    with open(os.path.join("output", html_file), "a") as f:
                        f.write(html)
                        html = ""
                        
                
                html += "</div>"

            html += """
            </body>
            </html>
            """



            with open(os.path.join("output", html_file), "a") as f:
                f.write(html)
                html = ""