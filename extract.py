import boto3
import requests
import os
import dotenv
import datetime

dotenv.load_dotenv()

base_url = "https://api.transport.nsw.gov.au/v1/live/hazards/{}/open"

auth_token = "apikey " + os.environ.get("APIKEY")
headers = {
    "content-type": "application/json",
    "Authorization": auth_token
}

ts = datetime.datetime.now().timestamp()

events = ["incident", "majorevent", "roadwork"]
responses = {}
file_name = "hazards_{}_{}.json"

for event in events:
    response = requests.get(base_url.format(event), headers=headers)
    responses[event] = response.text
    #print (responses[event])

    with open(file_name.format(event, ts),"w") as file:
        file.write(responses[event])