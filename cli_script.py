import os
import requests
import sys
import json
from dotenv import load_dotenv
from datetime import datetime
import argparse

from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer, DateTime, literal  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker


def get_from_airtable(endpoint):
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    r = requests.get(endpoint, headers=headers)
    return r.text


def parse_env_variables():
    parser = argparse.ArgumentParser()
    parser.add_argument("AIRTABLE_BASE_ID", help="Enter AIRTABLE_BASE_ID of the table you are going to use",\
                        type=str)
    parser.add_argument("AIRTABLE_API_KEY", help="Enter AIRTABLE_BASE_ID of the table you are going to use",\
                        type=str)
    parser.add_argument("AIRTABLE_TABLE_NAME", help="Enter AIRTABLE_TABLE_NAME of the table you are going to use",\
                        type=str)
    parser.add_argument("POSTGRES_PASSWORD", help="Enter POSTGRES_PASSWORD of the table you are going to use",\
                        type=str)
    
    return parser.parse_args()


if __name__ == '__main__':
    # Parsing .env variables from user input
    args = parse_env_variables()

    # Writing .env variables into .env file
    with open('.env', 'w') as env_file:
        env_file.write(f'AIRTABLE_BASE_ID={args.AIRTABLE_BASE_ID}\n')
        env_file.write(f'AIRTABLE_API_KEY={args.AIRTABLE_API_KEY}\n')
        env_file.write(f'AIRTABLE_TABLE_NAME={args.AIRTABLE_TABLE_NAME}\n')
        env_file.write(f'POSTGRES_PASSWORD={args.POSTGRES_PASSWORD}\n')

    # Loading .env variables from the environment
    load_dotenv('.env')
    AIRTABLE_BASE_ID=os.environ.get("AIRTABLE_BASE_ID")
    AIRTABLE_API_KEY=os.environ.get("AIRTABLE_API_KEY")
    AIRTABLE_TABLE_NAME=os.environ.get("AIRTABLE_TABLE_NAME")
    POSTGRES_PASSWORD=os.environ.get("POSTGRES_PASSWORD")

    # Fetching data from Airtable as json
    endpoint=f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}'
    data = get_from_airtable(endpoint)

    # Writing raw json line and cli_script launch datetime into raw_data_storage
    db_string = f'postgresql://postgres:{POSTGRES_PASSWORD}@localhost:5432/raw_data_storage'
    db = create_engine(db_string)  
    base = declarative_base()   

    class RawData(base):  
        __tablename__ = 'raw_data_storage'

        id_number = Column(Integer, primary_key=True, autoincrement=True)
        data = Column(String)
        script_launch_datetime = Column(DateTime)


    Session = sessionmaker(db)  
    session = Session()

    base.metadata.create_all(db)

    new_row = RawData(data=data, script_launch_datetime=datetime.utcnow())  
    session.add(new_row)  
    session.commit()

    # Parsing json into python object
    data = json.loads(data)
    # Get a list of unique ids of current therapists in Airtable
    current_therapists = [row['id'] for row in data['records']]
    
    # Run add, update and delete commands on main_data_storage
    db_string = f'postgresql://postgres:{POSTGRES_PASSWORD}@localhost:5432/main_data_storage'
    db = create_engine(db_string)  
    base = declarative_base()   

    class MainData(base):  
        __tablename__ = 'main_data_storage'

        id_number = Column(Integer, primary_key=True, autoincrement=True)
        person_id = Column(String, unique=True)
        person_name = Column(String)
        methods = Column(String)
        main_photo = Column(String)
        thumbnail = Column(String)


    Session = sessionmaker(db)  
    session = Session()

    base.metadata.create_all(db)

    # Deleting rows from main_data_storage which were removed from Airtable
    q = session.query(MainData.person_id)
    # Recent therapists from main_data_storage
    recent_therapists = [therapist.person_id for therapist in q]
    # Therapists to delete from main_data_storage
    therapists_to_delete = [x for x in recent_therapists if x not in current_therapists]

    # Deleting therapists
    for therapist in therapists_to_delete:
        q = session.query(MainData).filter(MainData.person_id == therapist)
        session.delete(q.one()) 

    # Updating/adding new therapists
    for row in data['records']:
        q = session.query(MainData).filter(MainData.person_id == f'{row["id"]}')
        print(q.one().person_id)
        if session.query(literal(True)).filter(q.exists()).scalar():
            # Updating current row in main_data_table
            q.one().person_name = row['fields']['Имя']
            q.one().methods = str(row['fields']['Методы'])
            q.one().main_photo = row['fields']['Фотография'][0]['url']
            q.one().thumbnail = row['fields']['Фотография'][0]['thumbnails']['small']['url']
        else:
            # Adding new row to main_data_table
            person_id = row['id']
            person_name = row['fields']['Имя']
            methods = str(row['fields']['Методы'])
            main_photo = row['fields']['Фотография'][0]['url']
            thumbnail = row['fields']['Фотография'][0]['thumbnails']['small']['url']
            session.add(MainData(person_id=person_id, person_name=person_name, methods=methods, main_photo=main_photo, thumbnail=thumbnail))  

    session.commit()