from django.db import models

class State(models.Model):
    state = models.CharField(max_length=100)
    state_code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.state

class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.CharField(max_length=100)
    district_code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.state.state_code} {self.district}"

class Taluka(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    taluka = models.CharField(max_length=100)
    taluka_code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.district.state.state_code} {self.district.district_code} {self.taluka}"

class Junction(models.Model):
    taluka = models.ForeignKey(Taluka, on_delete=models.CASCADE)
    junction = models.CharField(max_length=100)
    junction_code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.taluka} {self.junction}"

class Lane(models.Model):
    junction = models.ForeignKey(Junction, on_delete=models.CASCADE)
    lane = models.CharField(max_length=100)
    lane_slug=models.SlugField(max_length=100,null=True,blank=True)
    green_on_url = models.CharField(max_length=120)  # URL to turn on the green light
    green_off_url = models.CharField(max_length=120)  # URL to turn off the green light
    red_switch_on_url = models.CharField(max_length=120)  # URL to turn on the red light
    red_switch_off_url = models.CharField(max_length=120)  # URL to turn off the red light
    current_status = models.CharField(max_length=10, default='red')  # 'green' or 'red'
    green_triggered_by = models.CharField(max_length=20, null=True, blank=True)  # 'ambulance' or 'timer'

    def __str__(self):
        return f"{self.junction.junction} - {self.lane}"

    class Meta:
        verbose_name_plural = "Lanes"

class Coordinates(models.Model):
    lane = models.ForeignKey(Lane, on_delete=models.CASCADE)
    upper_left_x = models.DecimalField(max_digits=20, decimal_places=10)
    upper_left_y = models.DecimalField(max_digits=20, decimal_places=10)
    upper_right_x = models.DecimalField(max_digits=20, decimal_places=10)
    upper_right_y = models.DecimalField(max_digits=20, decimal_places=10)
    lower_left_x = models.DecimalField(max_digits=20, decimal_places=10)
    lower_left_y = models.DecimalField(max_digits=20, decimal_places=10)
    lower_right_x = models.DecimalField(max_digits=20, decimal_places=10)
    lower_right_y = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return f"Coordinates for {self.lane.lane}"

class OffSwitch(models.Model):
    onswitch = models.ForeignKey(Coordinates, on_delete=models.CASCADE)
    offswitch = models.ForeignKey(Lane, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.offswitch.lane} - {self.onswitch.lane.lane}"

class OffTable(models.Model):
    lane = models.ForeignKey(Lane, on_delete=models.CASCADE)
    offURL = models.CharField(max_length=500)
    offtime = models.DateTimeField()



class M(models.Model):
    id1 = models.AutoField(primary_key=True)
    s = models.CharField(max_length=100)
    s2 = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.s} {self.s2}"
