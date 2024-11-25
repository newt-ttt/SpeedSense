from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from WebApp.models import VehicleInstance

import datetime
import plotly.express as px
import plotly.graph_objects as go
import os

speed_limit = 25 # Set this value to the speed limit in the zone
speed_margin = 1 # Increase this value if you want to give some leeway in the visual representation of data i.e. at 0, 25.1mph is considered speeding and at 5, 30 is not considered speeding


def ping(request):
    return HttpResponse("pong")

def save(request):
    if request.method != "POST": return HttpResponse("Please use POST")
    try:
        # \\r\\n seems to work as a divider when sending tests from Postman, this might have to change when recieving actual data from the microcontroller
        # \\n works with the String in the arduino code since it's sending the "\n" as a literal
        # Change it to "\n" once it's sending "\n" as new line
        
        try:
            if request.headers['Postman-Token']:
                split_on = '\\r\\n'
        except:
            split_on = '\\n'
            
        speed_instances = str(request.body)[2:-1].split(split_on)
        for instance in speed_instances:
            #print(instance)
            date_str = instance.partition(" ")[0].split("-")
            if date_str[0] == '': continue# Last line of the text file tends to cause issues, ignore invalid ones

            V = VehicleInstance(date=datetime.datetime(int(date_str[0]), int(date_str[1]), int(date_str[2]), int(date_str[3]), int(date_str[4]), int(date_str[5])),
                                speeds=instance.partition(" ")[2],
                                direction=request.headers["direction"],
                                custom_text=request.headers["custom-text"])
            # Save it to the table
            V.save()
        # Update the table
        try:
            regenerate_analysis()
        except:
            print("Error generating analysis")
            return HttpResponse("VehicleInstance objects have been successfully saved, but we ran into an error generating the analysis data.")
            
        return HttpResponse("VehicleInstance objects have been sucessfully received and saved.")
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
    plotlyconfig = {'responsive': True, 'scrollZoom': False, 'staticPlot': False}
    # format all speed info into values and cells to make table
    sorted_speeds = VehicleInstance.objects.order_by("-date")[:100]
    dates, ids, text = zip(*[(format_date(s.date), s.id, str(s.custom_text)) for s in sorted_speeds])
    
    speeds = [s.speeds.split(" ") for s in sorted_speeds]
    avg_speeds = [round(sum(float(s) for s in speed)/len(speed), 1) for speed in speeds]
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Instance ID', 'Speed', 'Time Recorded', 'Custom Text']),
        cells=dict(values=[ids, avg_speeds, dates, text]))
    ])
    
    # Sets background to be transparent when loaded in html
    fig.update_layout(
        font_family="Poppins",
        title=dict(text="All Recently Recorded Vehicles, sorted by date", font=dict(size=28), automargin=True, yref='container', x=0.5, y=0.9, yanchor='top'),
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgb(25, 42, 66, 0.2)'
    )

    fig.write_html('WebApp/templates/WebApp/table.html', config=plotlyconfig, full_html=False, include_plotlyjs='cdn')
    return

def generate_frequency_graph():
    plotlyconfig = {'responsive': True, 'scrollZoom': False, 'staticPlot': False}
    freq_by_hour = {"00":0,"01":0,"02":0,"03":0,"04":0,"05":0,"06":0,"07":0,"08":0,"09":0,"10":0,"11":0, 
                    "12":0,"13":0,"14":0,"15":0,"16":0,"17":0,"18":0,"19":0,"20":0,"21":0,"22":0,"23":0}
    
    for instance in VehicleInstance.objects.order_by("-date")[:100]:
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
        font_family="Poppins",
        title=dict(text="Vehicle Occurrences by Hour", font=dict(size=28), automargin=True, yref='container', x=0.5, y=0.9, yanchor='top'),
        xaxis_title="Time of Day (Hours)",
        xaxis_title_font_size=20,
        yaxis_title="# of Vehicles",
        yaxis_title_font_size=20,
        xaxis=dict(tickmode="array", tickvals=list(freq_by_hour.keys())),
        yaxis=dict(tickmode="array", tickvals=[5*n for n in range(0, 2+max([n for n in freq_by_hour.values()])//5)]),
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(25, 42, 66, 0.2)'
    )

    fig.write_html('WebApp/templates/WebApp/frequency_graph.html', config=plotlyconfig, full_html=False, include_plotlyjs='cdn')
    return

def generate_delta_speed_graph():
    plotlyconfig = {'responsive': True, 'scrollZoom': False, 'staticPlot': False}
    
    sorted_speeds = VehicleInstance.objects.order_by("-date")[:100]
    speeds = [s.speeds.split(" ") for s in sorted_speeds]
    speeds = [[float(s) for s in speed] for speed in speeds]
    max_speeds = [round(max(speed), 1) for speed in speeds]
    delta_speeds = [round(max(speed)-min(speed), 1) for speed in speeds]
    
    speeders_x=[]
    speeders_y=[]
    non_speeders_x=[]
    non_speeders_y=[]
    
    for ms, ds in zip(max_speeds, delta_speeds):
        if ms-ds > speed_limit+speed_margin:
            speeders_y.append(ds)
            speeders_x.append(ms)
        else:
            non_speeders_y.append(ds)
            non_speeders_x.append(ms)

    # Red dots for speeders, blue dots for non-speeders
    fig = go.Figure(go.Scatter(
    name="Non-Speeding Vehicle",
    x=non_speeders_x,
    y=non_speeders_y,
    marker_color= '#0059CB',  # Bar color
    mode="markers"
    ))

    fig.add_trace(go.Scatter(
    name="Speeding Vehicle",
    x=speeders_x,
    y=speeders_y,
    marker_color= '#C22222',  # Bar color
    mode="markers"
    ))
    
    fig.update_layout(
    font_family="Poppins",
    title=dict(text="Vehicle Changes in Speed", font=dict(size=28), automargin=True, yref='container', x=0.5, y=0.9, yanchor='top'),
    xaxis_title="Maximum Speed",
    xaxis_title_font_size=20,
    yaxis_title="Change in speed",
    yaxis_title_font_size=20,
    xaxis=dict(tickmode="array", tickvals=[2.5*n for n in range(0,2+int(max(max_speeds)/2.5))]),
    template='plotly_dark',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(25, 42, 66, 0.2)',
    showlegend=True
    )
        
    fig.write_html('WebApp/templates/WebApp/delta_speed_graph.html', config=plotlyconfig, full_html=False, include_plotlyjs='cdn')
    return

def regenerate_analysis():
    # If the database is not empty:
    if VehicleInstance.objects.all().count() != 0:
        # Generate table of average speeds w/ date and time
        generate_table()
        # Generate graph of vehicle detection frequencies
        generate_frequency_graph()
        # Generate graph of vehicle changes in speed
        generate_delta_speed_graph()
        return 1
    else:
        # This makes us not throw an error if we try to open the index page w/ nothing in the DB
        return 0

def format_date(date: datetime.datetime):
    ampm = "PM" if date.hour//12 else "AM"
    if date.hour%12 ==0:
        hour=12
    else:
        hour=date.hour%12
        
    if len(str(date.minute)) == 1:
        minute = "0"+str(date.minute)
    else:
        minute=date.minute
        
    if len(str(date.second)) == 1:
        second = "0"+str(date.second)
    else:
        second=date.second
    return f'{date.month}-{date.day}-{date.year} {hour}:{minute}:{second} {ampm}'