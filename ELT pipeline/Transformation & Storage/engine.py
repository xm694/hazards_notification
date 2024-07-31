from sqlalchemy import create_engine
import os

def engine():
    dbname="postgres"
    user="root"
    pwd= os.environ.get("PASSWORD","")
    host= os.environ.get("HOST","")
    port = 5432

    engine = create_engine(f'postgresql://{user}:{pwd}@{host}:{port}/{dbname}')

    return engine
