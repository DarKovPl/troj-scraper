from datetime import datetime
from os import path
from sqlalchemy import Column, Integer, String, create_engine, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from unidecode import unidecode
from environs import Env

"""
This module is responsible for create database and for a saving data to a SQLite database. 
Columns are creates from environment variables.  
"""

date_database = str(datetime.today().date()).replace('-', '_')
database_path = f'databases/database_{date_database}.db'

engine = create_engine(f'sqlite:///{database_path}', echo=True)
Base = declarative_base()

Env().read_env('.env')
columns = [column.replace('\n', '') for column in Env().list('COLUMNS_FOR_BASE')]


class ScrapperBase(Base):
    __table__ = Table(
        'data_of_advertises',
        Base.metadata,
        Column('id', Integer, primary_key=True),
        *(Column(unidecode(column_), String) for column_ in columns))


if not path.exists(database_path):
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
