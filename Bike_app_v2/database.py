from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#SQLALCHEMY_DATABASE_URL = "sqlite:///./bike_app.db"
SQLALCHEMY_DATABASE_URL = "postgres://hveqyyyhbigzeo:8781ef75adccf9c5909a907f4ff414fd1b95627b563cb1c90eb2389a8bd7dcee@ec2-99-81-177-233.eu-west-1.compute.amazonaws.com:5432/dao8eqkjta72db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()