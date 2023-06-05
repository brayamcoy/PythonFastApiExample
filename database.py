from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

database_url = "postgresql://developer:qS*7Pjs3v0kw@db.g97.io:5432/data_analyst"
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
Base.metadata.create_all(bind=engine)


class ApiCall(Base):
    __tablename__ = 'api_calls'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    endpoint = Column(String)
    parameters = Column(String)
    result = Column(String)