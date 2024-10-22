from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from WebApp.models import VehicleInstance

import plotly.express as px
import plotly.graph_objects as go
import os

def ping(request):
    return HttpResponse("pong")

def save(request):
    if request.method != "POST": return HttpResponse("Please use POST")
    try:
        V = VehicleInstance(date="Not Yet Implemented",
                            speed=request.headers["captured-speed"],
                            direction=request.headers["direction"],
                            custom_text=request.headers["custom-text"])
        # Save it to the table
        V.save()
        # Update the table
        generate_table()
    
        return HttpResponse("VehicleInstance object has been sucessfully received and saved.")
    except:
        return HttpResponse("There has been an error processing your request")

        
def index(request):
    index_template = loader.get_template('WebApp/index.html')
    # change context to provide variables to the template
    context = {}
    if not os.path.exists("listen/table.html"):
        generate_table()
    return HttpResponse(index_template.render(context, request ))

def generate_table():
    # If the database is not empty:
    if VehicleInstance.objects.all().count() != 0:
        # format all speed info into values and cells to make table
        sorted_speeds = VehicleInstance.objects.order_by("-id")
        speeds, dates, ids, text = zip(*[(float(s.speed), s.date, s.id, str(s.custom_text)) for s in sorted_speeds])
        
        fig = go.Figure(data=[go.Table(header=dict(values=['Instance ID', 'Speed', 'Time Recorded', 'Custom Text']),
                        cells=dict(values=[ids, speeds, dates, text]))
                        ])
        fig.write_html('WebApp/templates/WebApp/table.html', full_html=False, include_plotlyjs='cdn')
    else:
        # This makes us not throw an error if we try to open the index page w/ nothing in the DB
        with open('WebApp/templates/WebApp/table.html', "w") as f:
            f.close()
    return

def logo(request):
    logopage = loader.get_template('WebApp/logopage.html')
    # change context to provide variables to the template
    context = {}
    return HttpResponse(logopage.render(context, request))