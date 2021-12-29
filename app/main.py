import logging
import os
import traceback

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import current_timestamp

app = FastAPI()
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# DTO親クラス作成
class CustomBase:
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=CustomBase)
Base.metadata.create_all(bind=engine)

db_session = SessionLocal()


# DTO Logクラス作成
class Log(Base):
    __tablename__ = "log_test"

    #     __tablename__ = 'inhouse.log'
    log_id = Column(Integer, primary_key=True, nullable=False, index=True)
    community_id = Column(Integer, unique=True, nullable=False, index=True)
    message = Column(String, unique=False, nullable=False, index=True)
    created = Column(DateTime, nullable=True, server_default=current_timestamp())

    def to_json(self):
        result = self.__dict__.copy()
        if "_sa_instance_state" in result:
            del result["_sa_instance_state"]
        return result


# リクエストパラメータクラス作成
class RequestItem(BaseModel):
    communityId: int = None
    message: str = None


# リクエストパラメータの型不一致対応
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.error(jsonable_encoder({"detail": exc.errors(), "body": exc.body}))
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Bad Request"},
    )


# Log　API POST 作成
# https://co-in-house.github.io/doc-spec/#_log_api
@app.post("/log/")
def insert_log(item: RequestItem):
    # Null チェック
    if (item.communityId is None) or (item.message is None):
        logging.error(
            jsonable_encoder({"detail": "required parameter missing ", "body": item})
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request"
        )
    # DB アクセス
    try:
        last_id = db_session.query(Log).order_by(Log.log_id.desc()).first().log_id
        db_session.execute(
            Log.__table__.insert([last_id + 1, item.communityId, item.message])
        )
        db_session.commit()
    except Exception as e:
        logging.error(
            jsonable_encoder(
                {"detail": "Internal Server Error", "body": item, "err": e}
            )
        )
        logging.error(jsonable_encoder({"traceback": traceback.print_exc()}))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )

    return JSONResponse(content={})


# Log　API GET 作成
# https://co-in-house.github.io/doc-spec/#_log_api
@app.get("/log/{community_id}")
def get_logs(community_id: int):
    # DBアクセス
    try:
        records_obj = db_session.query(Log).filter_by(community_id=community_id).all()
    except Exception as e:
        logging.error(
            jsonable_encoder(
                {"detail": "Internal Server Error", "body": community_id, "err": e}
            )
        )
        logging.error(jsonable_encoder({"traceback": traceback.print_exc()}))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
    records = [r.to_json() for r in records_obj]
    json_item = jsonable_encoder({"list": records})
    return JSONResponse(content=json_item)
