from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Column, select, delete, Table, MetaData
import logging
import traceback

def update_events(sqlengine, table_name, df):
    try:
        #create table object from database
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=sqlengine)
        #update and insert records
        records = df.to_dict(orient="records")
        upsert_stmt = insert(table).values(records)

        upsert_stmt = upsert_stmt.on_conflict_do_update(
            index_elements=[table.c.hazard_id],
            set_={
                "category":upsert_stmt.excluded.category,
                "latitude":upsert_stmt.excluded.latitude,
                "longitude":upsert_stmt.excluded.longitude,
                "planed_end_time":upsert_stmt.excluded.planed_end_time,
                "notification":upsert_stmt.excluded.notification
            }
        )
        with sqlengine.connect() as conn:
            conn.execute(upsert_stmt)

            #delete records no longer exist
            #select IDs from the database that are not in the new data
            current_ids = df["hazard_id"].tolist()
            select_stmt = select(table.c.hazard_id)
            existing_ids = [row[0] for row in conn.execute(select_stmt)]
            #the IDs in the database but not in the new data
            IDs_to_delete = set(existing_ids) - set(current_ids)
            #the IDs in the new data but not in the database
            IDs_to_notify = set(current_ids) - set(existing_ids)

            if IDs_to_delete:
                delete_stmt = table.delete().where(table.c.hazard_id.in_(IDs_to_delete))
                result = conn.execute(delete_stmt)
                deleted_count = result.rowcount
                logging.info(f"Deleted {deleted_count} records.")
            else:
                logging.info("No records to delete.")
            
            return IDs_to_notify

    except Exception as error:
        logging.error(f"An error occurred: {error}")
        traceback.print_exc()
        return set()


def update_roads(sqlengine, table_name, df):
    try:
        #update and insert records
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=sqlengine)

        records = df.to_dict(orient="records")
        upsert_stmt = insert(table).values(records)

        upsert_stmt = upsert_stmt.on_conflict_do_update(
            index_elements=[table.c.hazard_id],
            set_={
                "region":upsert_stmt.excluded.region,
                "suburb":upsert_stmt.excluded.suburb,
                "mainStreet":upsert_stmt.excluded.mainStreet,
                "crossStreet":upsert_stmt.excluded.crossStreet,
            }
        )

        with sqlengine.connect() as conn:
            conn.execute(upsert_stmt)

            #delete records no longer exist
            #select IDs from the database that are not in the new data
            current_ids = df["hazard_id"].tolist()
            select_stmt = select(table.c.hazard_id)
            existing_ids = [row[0] for row in conn.execute(select_stmt)]
            #the IDs in the database but not in the new data
            IDs_to_delete = set(existing_ids) - set(current_ids)

            if IDs_to_delete:
                delete_stmt = table.delete().where(table.c.hazard_id.in_(IDs_to_delete))
                result = conn.execute(delete_stmt)
                deleted_count = result.rowcount
                logging.info(f"Deleted {deleted_count} records.")
            else:
                logging.info("No records to delete.")
        
    except Exception as error:
        logging.error(f"An error occurred: {error}")
        traceback.print_exc()