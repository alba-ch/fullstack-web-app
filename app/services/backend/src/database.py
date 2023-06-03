from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
import src.utils
# from dotenv import load_dotenv

# docker_compose_path = os.path.abspath("../../docker_compose.yml")
# load_dotenv(docker_compose_path)

if src.utils.is_production():
    # SQLALCHEMY_DATABASE_URL = "sqlite:///./data.db"
    #SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/appdb"
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./app/data.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL) # "check_same_thread": False
# check_same_thread...is needed only for SQLite. It's not needed for other databases.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
