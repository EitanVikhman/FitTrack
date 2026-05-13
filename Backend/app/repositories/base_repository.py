from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.exceptions.exceptions import DuplicateErrorException, DatabaseErrorException

class BaseRepository:
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model

    # --- Read ---
    def get_by_id(self, id: int):
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(self.model).offset(skip).limit(limit).all()

    # --- Create ---
    def create(self, obj_in):
        # Convert Pydantic model to a standard dictionary
        if hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump()
        else:
            obj_data = obj_in

        db_obj = self.model(**obj_data)
        self.db.add(db_obj)

        try:
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj

        except IntegrityError as e:
            self.db.rollback()  # Vital: Reset the failed transaction
            # Raises a clean error that maps to HTTP 400/409
            raise DuplicateErrorException(f"Resource already exists. Details: {str(e.orig)}")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Database error: {str(e)}")

    # --- Update ---
    def update(self, db_obj, obj_in):
        # Convert to dict, excluding fields that were not sent (exclude_unset=True)
        # This prevents overwriting existing data with None
        if hasattr(obj_in, 'model_dump'):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        # Update attributes on the existing DB object
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)

        try:
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj

        except IntegrityError as e:
            self.db.rollback()
            raise DuplicateErrorException(f"Update failed due to conflict. Details: {str(e.orig)}")

        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Database update error: {str(e)}")

    # --- Delete ---
    def delete(self, id: int):
        obj = self.get_by_id(id)
        if obj:
            try:
                self.db.delete(obj)
                self.db.commit()
                return True

            except IntegrityError:
                self.db.rollback()
                # Happens if trying to delete a parent record linked to children (Foreign Key constraint)
                raise DatabaseErrorException("Cannot delete because this resource is in use.")

            except SQLAlchemyError:
                self.db.rollback()
                raise DatabaseErrorException("Delete failed due to database error.")

        return False