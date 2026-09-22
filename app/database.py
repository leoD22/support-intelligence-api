import os

from dotenv import load_dotenv

from sqlalchemy import (
    JSON,
    MetaData,
    Table,
    Column,
    Integer,
    Text,
    ForeignKey,
    String,
    create_engine
)
from sqlalchemy.engine import URL


load_dotenv()

# Database configuration

db_username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = int(os.getenv("DB_PORT"))
db_name = os.getenv("DB_NAME")

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=db_username,
    password=db_password,
    host=db_host,
    port=db_port,
    database=db_name
)

# Engine

engine = create_engine(database_url)

# Metadata and tables

metadata = MetaData()

tickets = Table(
    'tickets', metadata,
    Column('id', Integer(), primary_key=True),
    Column('text', Text(), nullable=False)
    )

predictions = Table(
    'predictions', metadata,
    Column('id', Integer(), primary_key=True),
    Column('ticket_id', Integer(), ForeignKey('tickets.id'), nullable=False),
    Column('category', String(255), nullable=False),
    Column('priority', Integer(), nullable=False),
    Column('summary', Text(), nullable=False),
    Column('entities', JSON, nullable=False)
    )
