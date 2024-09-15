from django.http import HttpResponse
from django.shortcuts import render
from .models import M, Coordinates, OffSwitch, OffTable, Lane, Junction
from datetime import datetime, timedelta
import requests
import threading
import time as t

# Function to check if a point is inside a rectangle
def is_point_inside_rectangle(x1, y1, x2, y2, x, y):
    return x1 <= x <= x2 and y1 <= y <= y2

# Function to handle the queuing system for a junction
def queue_system(junction):
    lanes = Lane.objects.filter(junction=junction)
    while True:
        for lane in lanes:
            # Turn green light on for the current lane
            requests.get(lane.green_on_url)
            print(f"Green light on for {lane}")

            # Turn red light on for all other lanes
            for other_lane in lanes.exclude(id=lane.id):
                requests.get(other_lane.red_switch_on_url)
                print(f"Red light on for {other_lane}")

            # Wait for 30 seconds
            t.sleep(30)

            # Turn green light off for the current lane
            requests.get(lane.green_off_url)
            print(f"Green light off for {lane}")

            # Turn red light off for all other lanes
            for other_lane in lanes.exclude(id=lane.id):
                requests.get(other_lane.red_switch_off_url)
                print(f"Red light off for {other_lane}")

# Function to handle ambulance detection and modify the queuing system
def getdata(request):
    lat = request.GET['lat']
    lng = request.GET['lng']
    coords = Coordinates.objects.all()
    ambulance_detected = False

    for coor in coords:
        if is_point_inside_rectangle(float(coor.upper_left_x), float(coor.upper_left_y), float(coor.lower_right_x), float(coor.lower_right_y), float(lat), float(lng)):
            if OffTable.objects.filter(lane=coor.lane).exists():
                continue  # Skip if the lane is already occupied by another ambulance
            ambulance_detected = True
            lane = coor.lane
            lane1_on_url = lane.green_on_url
            lane1_off_url = lane.green_off_url
            requests.get(url=lane1_on_url)
            OffTable.objects.filter(lane=lane).delete()  # Remove any pending off actions
            OffTable(lane=lane, offURL=lane1_off_url, offtime=datetime.now() + timedelta(minutes=2)).save()
            # Turn all other lanes red
            Lane.objects.filter(junction=lane.junction).exclude(id=lane.id).update(green_on_url=None)
            break

    if not ambulance_detected:
        return HttpResponse("<h1>No ambulance detected</h1>")

    return HttpResponse("<h1>Ambulance detected and handled</h1>")

# Function to resume the queuing system after an ambulance has left the zone
def resume_queue_system(junction):
    queue_thread = threading.Thread(target=queue_system, args=(junction,))
    queue_thread.start()

# Background function to check if the ambulance has left and resume the queue system
def sayHi():
    while True:
        print("Checking if the ambulance has left...")
        d1 = datetime.now()
        d = datetime(d1.year, d1.month, d1.day, d1.hour, d1.minute, 0)
        offtable_data = OffTable.objects.all()

        for obj in offtable_data:
            temp_date = datetime(obj.offtime.year, obj.offtime.month, obj.offtime.day, obj.offtime.hour, obj.offtime.minute, 0)
            if temp_date <= d:
                try:
                    requests.get(obj.offURL)
                except:
                    pass
                obj.delete()  # Delete the entry after the light is turned off
        t.sleep(60)

# Start the background thread to monitor ambulance status
my_thread = threading.Thread(target=sayHi)
my_thread.start()

# Sample view for testing
def home(request):
    m = M.objects.values().all()
    d = datetime.now()
    t2 = timedelta(minutes=2)
    print(type(d-t2))
    return render(request, template_name="index.html", context={"m": m})
