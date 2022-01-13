import cloudinary as cloudinary
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# SQLALCHEMY_DATABASE_URL = "sqlite:///./bike_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://hveqyyyhbigzeo:8781ef75adccf9c5909a907f4ff414fd1b95627b563cb1c90eb2389a8bd7dcee@ec2-99-81-177-233.eu-west-1.compute.amazonaws.com:5432/dao8eqkjta72db"
SQLALCHEMY_DATABASE_URL = "postgresql://pscnzdyneoynet:4e1b483536cb8d35dfe2629fb221f871d9d9ec005999e77aa215987dd77c5530@ec2-63-34-153-52.eu-west-1.compute.amazonaws.com:5432/d4rc3ghqb0ed0t"

cloudinary.config(
    cloud_name="de4x1kbdg",
    api_key="521237727855918",
    api_secret="yEpVH-nvPBWNxmyuZhmo60GJ57E"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
    # , connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
