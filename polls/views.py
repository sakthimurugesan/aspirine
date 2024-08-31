import threading
import time as t
from datetime import datetime, timedelta
import pytz
import requests
from django.http import HttpResponse
from django.shortcuts import render
from .models import M, Coordinates, OffSwitch, OffTable, Lane, Junction

IST = pytz.timezone('Asia/Kolkata')


def home(request):
    m = M.objects.values().all()
    return render(request, template_name="index.html", context={"m": m})


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
            lanes_to_be_stored=[lane]
            # Check if the lane is already in the OffTable
            if not OffTable.objects.filter(lane=lane).exists():
                lane1_on_url = lane.green_on_url
                lane1_off_url = lane.green_off_url

                # Turn on the green light for the ambulance lane
                # requests.get(url=lane1_on_url)
                """
                red off green on
                """
                print(f"Turning red off for lane: {lane.lane} (URL: {lane.red_switch_off_url})")
                print(f"Turning green for lane: {lane.lane} (URL: {lane1_on_url})")
                lane.current_status = 'green'
                lane.green_triggered_by = 'ambulance'
                lane.save()

                temp = OffSwitch.objects.filter(onswitch=coor)

                url_list = [lane1_off_url]
                for i in temp:
                    # requests.get(url=i.offswitch.red_switch_on_url)
                    # print('-' * 100)
                    # print(f"Turning red on for lane: {i.offswitch.lane} (URL: {i.offswitch.red_switch_on_url})")
                    # print('-' * 100)
                    """
                    red on green off
                    """
                    obj=Lane.objects.get(id=i.offswitch.id)
                    print('-' * 100)
                    print(obj.lane)
                    print('-' * 100)

                    obj.green_triggered_by = 'ambulance'
                    obj.current_status = 'red'
                    obj.save()
                    url_list.append(i.offswitch.red_switch_off_url)
                    lanes_to_be_stored.append(obj)

                for url in url_list:
                    print(f"URL to be saved in OffTable: {url}")

                off_time = datetime.now(IST) + timedelta(minutes=2)


                for i in range(len(url_list)):
                    OffTable.objects.create(lane=lanes_to_be_stored[i], offURL=url_list[i], offtime=off_time)
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
    while True:
        print("Running traffic_light_queue_system...")
        junctions = Junction.objects.all()

        for junction in junctions:
            lanes = Lane.objects.filter(junction=junction)
            lanes_to_turn_green = []
            amb = False
            lanes_to_turn_red = []
            for lane in lanes:
                if lane.green_triggered_by == 'ambulance':
                    amb = True
                    break
                else:
                    if lane.current_status == 'red':
                        lanes_to_turn_green.append(lane)
                    else:
                        lanes_to_turn_red.append(lane)
            if amb:
                continue

            # Turn lanes to green as necessary
            for lane in lanes_to_turn_green:
                # Turn the lane green
                # requests.get(url=lane.green_on_url)
                lane.current_status = 'green'
                lane.green_triggered_by = 'timer'
                lane.save()
                print(f"QUEUE Lane {lane.lane} is turned green (triggered by timer).")

            for lane in lanes_to_turn_red:
                # Turn the lane red
                # requests.get(url=lane.red_on_url)
                lane.current_status = 'red'
                lane.green_triggered_by = 'timer'
                lane.save()
                print(f"QUEUE Lane {lane.lane} is turned red (triggered by timer).")

        t.sleep(60)  # Sleep to prevent overwhelming the server


def sayHi():
    """
    This function checks every minute if the ambulance has left the zone.
    If the ambulance has left, it will turn off the lights and update the lane statuses.
    Additionally, it will handle the transition of lanes based on the timer.
    """
    while True:
        d1 = datetime.now(IST).replace(second=0, microsecond=0)
        offtable_data = OffTable.objects.all()

        for obj in offtable_data:
            if obj.offtime <= d1:
                lane = obj.lane
                print(lane.lane)
                # Turn off the light using the offURL
                try:
                    print(f"SAYHI Turning off light for lane: {lane.lane} (URL: {obj.offURL})")
                    # requests.get(obj.offURL)
                except requests.RequestException as e:
                    print(f"SAYHI Failed to send request: {e}")

                # Update lane status based on the previous status and trigger
                if lane.current_status == 'green':
                    lane.current_status = 'red'

                else:
                    lane.current_status = 'green'
                lane.green_triggered_by = 'timer'
                lane.save()

                # Remove the entry from OffTable after turning off the lights
                obj.delete()

        t.sleep(60)


# Start the background threads
queue_thread = threading.Thread(target=traffic_light_queue_system)
queue_thread.daemon = True
queue_thread.start()

say_hi_thread = threading.Thread(target=sayHi)
say_hi_thread.daemon = True
say_hi_thread.start()