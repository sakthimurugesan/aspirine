from django.http import HttpResponse
from django.shortcuts import render
from .models import M,Coordinates,OffSwitch,OffTable
import schedule
import time as t
from datetime import *
import requests
import threading
import pytz



def home(request):
    m=M.objects.values().all()
    d=datetime.now()
    t2=timedelta(minutes=2)
    print(type(d-t2))
    return render(request,template_name="index.html",context={"m":m})

def getdata(request):
    lat=request.GET['lat']
    lng=request.GET['lng']
    m=M(s=lat,s2=lng)
    m.save()
    
    coords=Coordinates.objects.all()
    for coor in coords:
        a=(float(coor.upper_left_x),float(coor.upper_left_y))
        b=(float(coor.upper_right_x),float(coor.upper_right_y))
        d=(float(coor.lower_right_x),float(coor.lower_right_y))
        c=(float(coor.lower_left_x),float(coor.lower_left_y))
        x1=a[0]
        y1=a[1]
        x2=d[0]
        y2=d[1]
        x=float(lat)
        y=float(lng)
        if(is_point_inside_rectangle(x1,y1,x2,y2,x,y)):
            laneId=coor.lane.id
            lane1_on_url=coor.lane.green_on_url #green on url
            requests.get(url=lane1_on_url)
            print(lane1_on_url)
            lane1_off_url=coor.lane.green_off_url # green off url 
            check_lane_exist_in_offtable=OffTable.objects.filter(lane=coor.lane)
            if(len(check_lane_exist_in_offtable)==0):
                temp=OffSwitch.objects.filter(onswitch=laneId)
                
                url_list=[lane1_off_url]

                for i in temp:
                    print(i.offswitch.red_switch_on_url) # red on url
                    url_list.append(i.offswitch.red_switch_off_url)
                d1=datetime.now()
                d=datetime(d1.year,d1.month,d1.day,d1.hour,d1.minute)+timedelta(minutes=2)

                print("ON TIME ",datetime.now())
                print("OFF TIME",d)

                for i in url_list:
                    offTableObj=OffTable(lane=coor.lane,offURL=i,offtime=d)
                    offTableObj.save()
            else:
                for obj in check_lane_exist_in_offtable:
                    obj.offtime+=timedelta(minutes=2)
                    obj.save()
        else:
            pass
    return HttpResponse("<h1>"+lat+" "+lng+"</h1>")

def is_point_inside_rectangle(x1, y1, x2, y2, x, y):
    
    return x1 <= x <= x2 and y1 <= y <= y2


def sayHi():
    k=1
    while True:
        print("inside function")
        d1=datetime.now()
        d=datetime(d1.year,d1.month,d1.day,d1.hour,d1.minute,0)
        offtable_data=OffTable.objects.all()

        for obj in offtable_data:
            temp_date=datetime(obj.offtime.year,obj.offtime.month,obj.offtime.day,obj.offtime.hour,obj.offtime.minute,0)
            if(temp_date<=d):
                try:
                    requests.get(obj.offURL)
                except:
                    pass

                obj.delete()       
        t.sleep(60)



my_thread = threading.Thread(target=sayHi)
my_thread.start()