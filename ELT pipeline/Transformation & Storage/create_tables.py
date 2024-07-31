from engine import engine
import sqlalchemy
from sqlalchemy import MetaData,Table, Column, Integer, Float, String, VARCHAR, DateTime, text


def create_tables():

    sqlengine = engine()
    metadata = MetaData()

    incident = Table('incident', metadata,
                     Column('hazard_id', Integer, primary_key=True, unique=True),
                     Column('category', String(80)),
                     Column('latitude', Float),
                     Column('longitude', Float),
                     Column('planed_end_time',DateTime),
                     Column('notification', VARCHAR(5000))
                     )

    majorevent = Table('majorevent', metadata,
                     Column('hazard_id', Integer, primary_key=True, unique=True),
                     Column('category', String(80)),
                     Column('latitude', Float),
                     Column('longitude', Float),
                     Column('planed_end_time',DateTime),
                     Column('notification', VARCHAR(5000))
                     )

    roadworks = Table('roadworks', metadata,
                     Column('hazard_id', Integer, primary_key=True, unique=True),
                     Column('category', String(80)),
                     Column('latitude', Float),
                     Column('longitude', Float),
                     Column('planed_end_time',DateTime),
                     Column('notification', VARCHAR(5000))
                     )


    roads =  Table('roads', metadata,
                   Column('hazard_id', Integer, primary_key=True, unique=True),
                   Column('region', VARCHAR(1000)),
                   Column('suburb', VARCHAR(1000)),
                   Column('mainStreet', VARCHAR(1000)),
                   Column('crossStreet', VARCHAR(1000))
                   )

    try:
        metadata.create_all(sqlengine)
        print("Tables has created succesfully.")
    except Exception as error:
        print(error)
 


# def create_merge_stmt(table_name: str, staging_table_name: str):
#     merge_stmt_sql = f"""
# merge into {table_name} target_table 
# using {staging_table_name} source_table
# on target_table.hazard_id = source_table.hazard_id 
# when matched then 
#     update set (
#         category = source_table.category,
#         latitude = source_table.latitude,
#         longitude = source_table.longitude,
#         notification = source_table.notification
#         )
# when not matched then
#     insert (hazard_id, category, latitude, longitude, notification)
#     values (source_table.hazard_id, source_table.category, source_table.latitude, source_table.longitude, source_table.notification)
# """
#     return text(merge_stmt_sql)


