import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASSWORD")
db_name = os.environ.get("DB_NAME")
db_instance_ip = os.environ.get("DB_INSTANCE_IP")
database_uri = os.environ.get("SQLALCHEMY_DATABASE_URI")
database_connection_uri = ("mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4"%(db_user, db_pass, db_instance_ip,db_name))
engine = create_engine(database_connection_uri, pool_size=20, max_overflow=0, pool_timeout=30, pool_recycle=1800, pool_pre_ping=True)
Connection = scoped_session(sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine))
Base = declarative_base()
Base.query = Connection.query_property()


def init_db():
    import webapp.models
    Base.metadata.create_all(bind=engine)