import boto3
from botocore.exceptions import ClientError
import logging
import requests
import os
import dotenv
import datetime
import json

dotenv.load_dotenv()
auth_token = "apikey " + os.environ.get("APIKEY", "")
base_url = "https://api.transport.nsw.gov.au/v1/live/hazards/{}/open"
headers = {
    "content-type": "application/json",
    "Authorization": auth_token
}

bucket_name = 'hazards-nsw'

ts = datetime.datetime.now().timestamp()
hazards = ["incident", "majorevent", "roadwork"]
responses = {}
file_name = "hazards_{}_{}.json"

#create function to upload file to S3 bucket
def upload_file(req_data, bucket, object_name):
    s3_client = boto3.client('s3')
    try:
        json_string = json.dumps(req_data)
        s3_client.put_object(Body=json_string, Bucket=bucket, Key=object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

#create handler for Lambda function
def handler(event, context):
    for hazard in hazards:
        response = requests.get(base_url.format(hazard), headers=headers)
        responses[hazard] = response.text
        #print (responses[hazard])

        object_name = file_name.format(hazard, ts)
        if upload_file(responses[hazard], bucket_name, object_name):
            print("Upload successful")
        else:
            print("Upload failed")

        # with open(file_name.format(hazard, ts),"w") as file:
        #     file.write(responses[hazard])