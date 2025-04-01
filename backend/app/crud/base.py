import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from app.db.base_class import Base
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        logger.debug(f"Getting {self.model.__name__} with id: {id}")
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        logger.debug(
            f"Getting multiple {self.model.__name__}s with skip: {skip}, limit: {limit}"
        )
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        logger.debug(f"Creating new {self.model.__name__}")
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Created {self.model.__name__} with id: {db_obj.id}")
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        logger.debug(f"Updating {self.model.__name__} with id: {db_obj.id}")
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(
                exclude_unset=True
            )  # Use model_dump for Pydantic v2
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Updated {self.model.__name__} with id: {db_obj.id}")
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        logger.debug(f"Removing {self.model.__name__} with id: {id}")
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
            logger.info(f"Removed {self.model.__name__} with id: {id}")
        else:
            logger.warning(
                f"Attempted to remove non-existent {self.model.__name__} with id: {id}"
            )
        return obj
