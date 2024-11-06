from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from WebApp.models import VehicleInstance

import datetime
import plotly.express as px
import plotly.graph_objects as go
import os

plotlyconfig = {'responsive': True, 'scrollZoom': False, 'staticPlot': True}

def ping(request):
    return HttpResponse("pong")

def save(request):
    if request.method != "POST": return HttpResponse("Please use POST")
    try:
        # \\r\\n seems to work as a divider wehn sending tests from Postman, this might have to change when recieving actual data from the microcontroller
        speed_instances = str(request.body)[2:-1].split('\\r\\n')
        for instance in speed_instances:
            
            date_str = instance.partition(" ")[0].split("-")
            if date_str[0] == '': continue# Last line of the text file tends to cause issues, ignore invalid ones

            V = VehicleInstance(date=datetime.datetime(int(date_str[0]), int(date_str[1]), int(date_str[2]), int(date_str[3]), int(date_str[4]), int(date_str[5])),
                                speeds=instance.partition(" ")[2],
                                direction=request.headers["direction"],
                                custom_text=request.headers["custom-text"])
            # Save it to the table
            V.save()
        # Update the table
        regenerate_analysis()
    
        return HttpResponse("VehicleInstance object has been sucessfully received and saved.")
    except:
        return HttpResponse("There has been an error processing your request")

        
def index(request, resource=None):
    index_template = loader.get_template('WebApp/index.html')
    context={"show_splash": False, "resource": resource, "db_empty": False}
    
    # change context to provide variables to the template
    if not resource:
        context["show_splash"] = True
        return HttpResponse(index_template.render(context, request))
    elif resource=="Analysis":
        # This will generate the analysis graphs and table if there's any data in the ddatabase
        if not regenerate_analysis():
            context["db_empty"] = True

    return HttpResponse(index_template.render(context, request))


def generate_table():
    # format all speed info into values and cells to make table
    sorted_speeds = VehicleInstance.objects.order_by("-id")
    dates, ids, text = zip(*[(s.date, s.id, str(s.custom_text)) for s in sorted_speeds])
    
    speeds = [s.speeds.split(" ") for s in sorted_speeds]
    avg_speeds = [round(sum(float(s) for s in speed)/len(speed), 1) for speed in speeds]
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Instance ID', 'Speed', 'Time Recorded', 'Custom Text']),
        cells=dict(values=[ids, avg_speeds, dates, text]))
    ])
    
    # Sets background to be transparent when loaded in html
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    fig.write_html('WebApp/templates/WebApp/table.html', config=plotlyconfig, full_html=False, include_plotlyjs='cdn')
    return

def generate_frequency_graph():
    freq_by_hour = {"00":0,"01":0,"02":0,"03":0,"04":0,"05":0,"06":0,"07":0,"08":0,"09":0,"10":0,"11":0, 
                    "12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0,"22":0,"23":0}
    
    for instance in VehicleInstance.objects.all():
        hour = str(instance.date.hour)
        if len(hour) == 1:
            hour="0"+hour
        freq_by_hour[hour]+=1
        
    fig = go.Figure(go.Bar(
    x=list(freq_by_hour.keys()),  # Hours as x-axis
    y=list(freq_by_hour.values()),  # Frequency as y-axis
    marker_color= '#0059CB'  # Bar color
    ))

    fig.update_layout(
        title="Vehicle Occurrences by Hour",
        xaxis_title="Time of Day (Hours)",
        yaxis_title="Frequency",
        xaxis=dict(tickmode="array", tickvals=list(freq_by_hour.keys())),
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    fig.write_html('WebApp/templates/WebApp/frequency_graph.html', config=plotlyconfig, full_html=False, include_plotlyjs='cdn')
    return

def regenerate_analysis():
    # If the database is not empty:
    if VehicleInstance.objects.all().count() != 0:
        # Generate table of average speeds w/ date and time
        generate_table()
        # Generate graph of vehicle detection frequencies
        generate_frequency_graph()
        return 1
    else:
        # This makes us not throw an error if we try to open the index page w/ nothing in the DB
        return 0
