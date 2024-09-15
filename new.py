import requests
from time import sleep
# The API endpoint
url = "https://blynk.cloud/external/api/update?token=bFlEdoa-cnTzZdiP8cnoefGjhi_pFe5y&v1=0"

# A GET request to the API
response = requests.get(url)
url1="http://103.168.18.181/getdata?lat=123&lng=456"
# Print the response

for i in range(500):
    print(requests.get("http://localhost:8000/junction?junctionid=1").content)
    sleep(5)