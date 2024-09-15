import threading
from datetime import datetime, timedelta
import pytz
import requests
from django.http import HttpResponse
from django.shortcuts import render
from .models import M, Coordinates, OffSwitch, OffTable, Lane, Junction, JunctionLaneState,CurrentJunctionState
import time as t
IST = pytz.timezone('Asia/Kolkata')


def home(request):
    m = M.objects.values().all()
    return render(request, template_name="index.html", context={"m": m})


def getJunctionState(request):
    junctionId=int(request.GET['junctionid'])
    #print(junctionId)
    junctions=CurrentJunctionState.objects.filter(junction=junctionId)
    if(len(junctions)==0):
        return -1
    for junction in junctions:
        return HttpResponse(int(junction.lane.id))

def getdata(request):
    lat = request.GET['lat']
    lng = request.GET['lng']

    # Save incoming coordinates
    m = M(s=lat, s2=lng)
    m.save()

    coords = Coordinates.objects.all()
    ambulance_detected = False

    for coor in coords:
        if is_point_inside_rectangle(float(coor.upper_left_x), float(coor.upper_left_y), float(coor.lower_right_x),
                                     float(coor.lower_right_y), float(lat), float(lng)):
            ambulance_detected = True
            lane = coor.lane
            lanes_to_be_stored = [lane]
            # Check if the lane is already in the OffTable
            if not OffTable.objects.filter(lane=lane).exists():
                lane1_on_url = lane.green_on_url
                lane1_off_url = lane.green_off_url
                junction=lane.junction
                current_junction_state=CurrentJunctionState.objects.filter(junction=junction)
                #print(current_junction_state)
                # Turn on the green light for the ambulance lane
                lane.current_status = 'green'
                lane.green_triggered_by = 'ambulance'
                lane.save()
                if len(current_junction_state)>0:
                    for obj in current_junction_state:
                        obj.lane=lane
                        obj.save()
                        #print(obj.lane)
                else:
                    CurrentJunctionState.objects.create(junction=junction,lane=lane)
                temp = OffSwitch.objects.filter(onswitch=coor)

                url_list = [lane1_off_url]
                for i in temp:
                    obj = Lane.objects.get(id=i.offswitch.id)
                    obj.green_triggered_by = 'ambulance'
                    obj.current_status = 'red'
                    obj.save()
                    url_list.append(i.offswitch.red_switch_off_url)
                    lanes_to_be_stored.append(obj)

                off_time = datetime.now(IST) + timedelta(minutes=2)
                junc = lanes_to_be_stored[0].junction

                for i in range(len(url_list)):
                    OffTable.objects.create(lane=lanes_to_be_stored[i], offURL=url_list[i], offtime=off_time, junction=junc)
            else:
                # Extend the off time if the lane is already in OffTable
                for obj in OffTable.objects.filter(lane=lane):
                    obj.offtime += timedelta(minutes=2)
                    obj.save()

            break

    if not ambulance_detected:
        return HttpResponse("<h1>No ambulance detected within the defined zones</h1>")

    return HttpResponse(f"<h1>Ambulance detected at coordinates: {lat}, {lng}</h1>")




def is_point_inside_rectangle(x1, y1, x2, y2, x, y):
    return x1 <= x <= x2 and y1 <= y <= y2


def traffic_light_queue_system():
    """
    This function controls the traffic light queue system, ensuring that each lane in every junction gets a green light for 30 seconds.
    If an ambulance is detected in a lane, that lane's light stays green until the ambulance passes.
    """
    #print("Running traffic_light_queue_system...")
    junctions = Junction.objects.all()

    for junction in junctions:
        lanes = Lane.objects.filter(junction=junction).order_by('id')
        lanes_as_list = list(lanes)
        lane_count = len(lanes)

        try:
            lane_state = JunctionLaneState.objects.get(junction=junction)
        except JunctionLaneState.DoesNotExist:
            lane_state = JunctionLaneState.objects.create(junction=junction, next_lane=lanes.first())

        current_lane = lane_state.next_lane
        if current_lane.green_triggered_by == 'ambulance':
            continue

        lanes_to_turn_green = []
        amb = False
        lanes_to_turn_red = []

        for lane in lanes:
            if lane.green_triggered_by == 'ambulance':
                amb = True
                break
            elif lane == current_lane:
                if lane.current_status == 'red':
                    lanes_to_turn_green.append(lane)
            else:
                lanes_to_turn_red.append(lane)

        if amb:
            continue
        current_junction_state=CurrentJunctionState.objects.filter(junction=junction)
        for lane in lanes_to_turn_green:
            lane.current_status = 'green'
            lane.green_triggered_by = 'timer'
            #print("Green ",lane.lane)
            lane.save()

            if len(current_junction_state)>0:
                for obj in current_junction_state:
                    obj.lane=lane
                    obj.save()
                    #print(obj.lane)
            else:
                CurrentJunctionState.objects.create(junction=junction,lane=lane)
            

        for lane in lanes_to_turn_red:
            lane.current_status = 'red'
            #print("Red ",lane.lane)
            lane.green_triggered_by = 'timer'
            lane.save()

        next_lane_index = (lanes_as_list.index(current_lane) + 1) % lane_count
        lane_state.next_lane = lanes[next_lane_index]
        lane_state.save()


def sayHi():
    """
    This function checks if the ambulance has left the zone and handles the transition of lanes based on the timer.
    """
    d1 = datetime.now(IST)
    offtable_data = OffTable.objects.all()
    #print("Ambulance position checker")
    #print(d1)
    #print("-"*100)
    for obj in offtable_data:
        if obj.offtime <= d1:
            junc = obj.lane.junction
            #print(junc.junction)
            next_junc = JunctionLaneState.objects.get(junction=junc).next_lane
            all_lanes_from_junction = Lane.objects.filter(junction=junc)
            current_junction_state=CurrentJunctionState.objects.filter(junction=junc)
            #print(current_junction_state)
            for lane in all_lanes_from_junction:
                if lane == next_junc:
                    #print("Green ",lane.lane)
                    lane.green_triggered_by = "timer"
                    lane.current_status = "green"
                    lane.save()
                    if len(current_junction_state)>0:
                        for obj in current_junction_state:
                            obj.lane=lane
                            obj.save()
                            #print(obj.lane)
                    else:
                        CurrentJunctionState.objects.create(junction=junc,lane=lane)
                else:
                    #print("Red ",lane.lane)
                    lane.green_triggered_by = "timer"
                    lane.current_status = "red"
                    lane.save()

            delete_lanes_from_offtable = OffTable.objects.filter(junction=junc)
            for lane in delete_lanes_from_offtable:
                lane.delete()
                
        
    #print('-'*100)


# Function to run both tasks every 30 seconds
def run_every_30_seconds():
    traffic_light_queue_system()
    sayHi()
    # Schedule the next run in 30 seconds
    threading.Timer(30, run_every_30_seconds).start()


# Call the function to start the recurring process
run_every_30_seconds()