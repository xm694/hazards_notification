import boto3
from botocore.exceptions import ClientError
import logging
import json
import re
import os
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text, Integer

from engine import engine
from create_tables import create_tables
from updateDB import update_events, update_roads


s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
sqlengine = engine()

#get content from s3 bucket file
def get_content(bucket, key):
    s3_obj = s3_client.get_object(
        Bucket = bucket,
        Key = key,
    )
    raw_json = json.loads(s3_obj['Body'].read().decode('utf-8'))
    return raw_json

#match file name to decide which table the properties go to
def matching_file_name(key):
    if re.search(pattern=r".*?majorevent.*?\.json", string=key, flags=re.IGNORECASE):
        return "majorevent"
    if re.search(pattern=r".*?roadwork.*?\.json", string=key, flags=re.IGNORECASE):
        return "roadworks"
    if re.search(pattern=r".*?incident.*?\.json", string=key, flags=re.IGNORECASE):
        return "incident"

#get detail properties from json raw data for database metric
def get_information(raw_json):
    hazard_general={}
    general_info = []
    hazard_road={}
    road_info=[]

    for i in raw_json['features']:
        #properties about general information
        hazard_id = int(i['id'])
        category = i['properties']['CategoryIcon']
        latitude = i['geometry']['coordinates'][0]
        longitude = i['geometry']['coordinates'][1]
        notification = i['properties'].get('otherAdvice', None)
        planed_end_time = i['properties'].get('end',None)

        #collect general infomation
        hazard_general={
            'hazard_id':hazard_id,
            'category':category,
            'latitude':latitude,
            'longitude':longitude,
            'planed_end_time':planed_end_time,
            'notification':notification
        }
        general_info.append(hazard_general)
        
        #properties about roads
        region=[]
        suburb=[]
        mainStreet=[]
        crossStreet=[]
        if not i['properties']['roads']:
            notification = notification + "No area under impact!"
        else:
            for j in i['properties']['roads']:
                region.append(j['region'])
                suburb.append(j['suburb'])
                mainStreet.append(j.get('mainStreet', None))
                crossStreet.append(j.get('crossStreet', None))

        #collect affected roads information
        hazard_road={
            'hazard_id':hazard_id,
            'region':region,
            'suburb':suburb,
            'mainStreet':mainStreet,
            'crossStreet':crossStreet
        }
        road_info.append(hazard_road)

    return general_info, road_info

#save clean data to silver tier bucket
def upload_silver_data(general_info, road_info, key):
    silver_data = {
        "general_info": general_info,
        "road_info":road_info
    }
    silver_bucket = "silver-hazard-nsw"
    file_name = f"silver-{key}"

    try:
        json_string = json.dumps(silver_data)
        s3_client.put_object(Body=json_string, Bucket=silver_bucket, Key=file_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

#function to convert timestamp
def timestamp_conversion(x):
    if pd.isna(x) or x is None:
        return datetime.now() + timedelta(days=365*1000)
    try:
        x = float(x)
        if x > 1e11:
            return datetime.fromtimestamp(x/1000)
        else:
            return datetime.fromtimestamp(x)
    except (ValueError, TypeError):
        return datetime.now() + timedelta(days=365*1000)
    

#function to send sns notification
def sns_notification(TopicArn, IDs_to_notify, general_info):
    #filter new event IDs to notify from bulk information
    events_to_notify = list(filter(lambda event: event["hazard_id"] in IDs_to_notify, general_info))
    messages = [event["notification"] for event in events_to_notify if event.get("notification")]
    message = "\n".join(messages)

    sns_notification = sns_client.publish(TopicArn=TopicArn, Message=message)
    
    return sns_notification


#create lambda function handler
def handler(event, context):
    ##debug
    #query database to confirm records inserted
    if (event.get('requestContext')):
        query = event['queryStringParameters'].get("q", "")
        sqlType = event['queryStringParameters'].get("type", "")

        with sqlengine.begin() as conn:
            if sqlType == "ddl":
                conn.execute(text(query))
                conn.commit()
            else:
                result = conn.execute(text(query)).fetchall()
                for data in result:
                    print(data)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "result": "Ok"
            })
        }
    
    bucket = event['detail']['bucket']['name']
    key = event['detail']['object']['key']
    #get content
    raw_json = get_content(bucket, key)
    ###debug
    if (isinstance(raw_json,str)):
        raw_json = json.loads(raw_json)

    #create tables if not exits
    create_tables()

    #extract important data for tables 
    general_info, road_info = get_information(raw_json)

    #upload silver data to silver bucket
    if upload_silver_data(general_info, road_info, key):
        print("Upload to silver bucket successful.")
    else:
        print("Upload to silver bucket failed.")

    #insert data respectively for each event table
    df_general = pd.DataFrame(general_info)
    df_road = pd.DataFrame(road_info)

    # cast the timestamp numbers to datetime object
    df_general['planed_end_time'] = df_general['planed_end_time'] .apply(timestamp_conversion)
    # df_general['planed_end_time'] = df_general['planed_end_time'].apply(lambda x: x/1000 if len(str(x).strip()) > 10 else x ).apply(datetime.fromtimestamp)
        
    if matching_file_name(key) == 'incident':
        table_name = 'incident'
        # staging_table_name = 'incident_staging'
    elif matching_file_name(key) == 'majorevent':
        table_name = 'majorevent'
        # staging_table_name = 'majorevent_staging'
    elif matching_file_name(key) == 'roadworks':
        table_name = 'roadworks'
        # staging_table_name = 'roadworks_staging'

    # now insert data to database
    # the mechanism of updating data records
    with sqlengine.connect() as conn:
        record_count = conn.execute(text(f'select * from {table_name}')).rowcount

        #if table is empty, insert records straingt
        if record_count==0:
            #insert data for event tables respecitvely
            df_general.to_sql(name=table_name, con=sqlengine, if_exists='append', index=False, method='multi', dtype={'hazard_id':Integer()})
            print(f"insert successful in table {table_name}")
            #insert data for roads table
            df_road.to_sql(name='roads', con=sqlengine, if_exists='append', index=False, method='multi', dtype={'hazard_id':Integer()})
            print("insert successful in table roads.")
        #if table is not empty, upsert records and delete expired records
        else:
            #insert new records, update old records and delete records no longer exists by PK
            IDs_to_notify = update_events(sqlengine=sqlengine, table_name=table_name, df=df_general)
            update_roads(sqlengine=sqlengine, table_name='roads', df=df_road)
            print(IDs_to_notify)
    
    # with sqlengine.connect() as conn:
    #     # Truncate staging table first
    #     # and insert data into staging data first 
    #     # and merge the result into main table
    #     print("truncating staging table !")
    #     conn.execute(text(f"TRUNCATE TABLE {staging_table_name}" ))
    #     print("staging table truncated!")
    #     df_general.to_sql(name=staging_table_name, con=conn, if_exists='append', index=False, dtype={'hazard_id': Integer()})
    #     print(f"insert successful in table {staging_table_name}")

    #     conn.execute(create_merge_stmt(table_name, staging_table_name))
    #     print(f"Merge successful on table {table_name}")

    #     # now truncate staging table again
    #     conn.execute(text(f"TRUNCATE TABLE {staging_table_name}" ))

    #todos: send notification through sns
    TopicArn = os.environ.get("TopicArn", "")
    if len(IDs_to_notify) > 0:
        try: 
            response = sns_notification(TopicArn, IDs_to_notify)
            print(f"Notification sent successfully. Message ID: {response["MessageId"]}")
        except Exception as e:
            print(f"Failed to send notificaiton: {e}")