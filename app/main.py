import os

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.functions import current_timestamp

app = FastAPI()

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URI,
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# class CustomBase:
#     # Generate __tablename__ automatically
#     @declared_attr
#     def __tablename__(cls):
#         return cls.__name__.lower()


# Base = declarative_base(cls=CustomBase)
# Base.metadata.create_all(bind=engine)

# db_session = SessionLocal()


# class Log(Base):
#     __tablename__ = "log_test"

#     #     __tablename__ = 'inhouse.log'
#     log_id = Column(Integer, primary_key=True, nullable=False, index=True)
#     community_id = Column(Integer, unique=True, nullable=False, index=True)
#     message = Column(String, unique=False, nullable=False, index=True)
#     created = Column(DateTime, nullable=True, server_default=current_timestamp())

#     def to_json(self):
#         result = self.__dict__.copy()
#         if "_sa_instance_state" in result:
#             del result["_sa_instance_state"]
#         return result


# @app.post("/log")
# def insert_log():
#     last_id = db_session.query(Log).order_by(Log.log_id.desc()).first().log_id
#     # community_id = request.args.get("limit", default=-1, type=int)
#     db_session.execute(
#         Log.__table__.insert(
#             [
#                 last_id + 1,
#             ]
#         )
#     )
#     db_session.commit()


class RequestItem(BaseModel):
    community_id: int
    message: str = ""


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None


@app.get("/")
def read_root():
    return {"Hello": "World", "URI": SQLALCHEMY_DATABASE_URI}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.post("/items/")
def post_item(item: Item):
    return {"item_name": item.name, "item_price": item.price}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}
