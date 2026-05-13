from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

# Repository
from app.repositories.plan_repository import PlanRepository

# Schemas
from app.schemas.plan_schema import PlanCreate, PlanUpdate, PlanResponse

# Exceptions
from app.exceptions.exceptions import (
    ResourceNotFoundException,
    DuplicateErrorException,
    DatabaseErrorException
)


class PlanService:
    def __init__(self, db: Session):
        self.db = db
        self.plan_repo = PlanRepository(db)

    # =========================================================================
    # Logic 1: Create New Plan (Admin)
    # =========================================================================
    def create_plan(self, plan_data: PlanCreate) -> PlanResponse:
        """
        Creates a new subscription plan (e.g., 'Gold Membership').
        Ensures the plan name is unique.
        """
        # 1. Check for duplicates (Name must be unique)
        # We assume the repository has a generic filter or specific get_by_name method
        # If not, we can implement it or iterate (less efficient but works for small tables)

        # Option A: Ideally, PlanRepository has get_by_name
        # existing_plan = self.plan_repo.get_by_name(plan_data.name)

        # Option B: Generic check (assuming name is a field)
        existing_plan = self.db.query(self.plan_repo.model).filter(
            self.plan_repo.model.name == plan_data.name
        ).first()

        if existing_plan:
            raise DuplicateErrorException(f"Plan with name '{plan_data.name}' already exists.")

        # 2. Create via Repository
        try:
            new_plan = self.plan_repo.create(plan_data)
            return new_plan

        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Database error creating plan: {str(e)}")

    # =========================================================================
    # Logic 2: Read Plans (Public/Admin)
    # =========================================================================
    def get_plan_by_id(self, plan_id: int) -> PlanResponse:
        """
        Fetch a single plan details.
        """
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ResourceNotFoundException(f"Plan with ID {plan_id} not found.")
        return plan

    def get_all_plans(self) -> List[PlanResponse]:
        """
        Fetch all available plans.
        Used for the 'Pricing' page on the frontend.
        """
        return self.plan_repo.get_all()

    # =========================================================================
    # Logic 3: Update & Delete (Admin)
    # =========================================================================
    def update_plan(self, plan_id: int, update_data: PlanUpdate) -> PlanResponse:
        """
        Update plan details (e.g., price, duration).
        """
        # 1. Verify existence
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ResourceNotFoundException(f"Plan with ID {plan_id} not found.")

        # 2. Update via Repository
        try:
            updated_plan = self.plan_repo.update(plan, update_data)
            return updated_plan
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseErrorException(f"Failed to update plan: {str(e)}")

    def delete_plan(self, plan_id: int):
        """
        Delete a plan.
        WARNING: This might fail if users are already subscribed to this plan.
        """
        # 1. Verify existence
        self.get_plan_by_id(plan_id)

        try:
            self.plan_repo.delete(plan_id)
            return {"message": "Plan deleted successfully"}

        except SQLAlchemyError as e:
            self.db.rollback()
            # If standard deletion fails (due to Foreign Key constraints), we catch it here
            raise DatabaseErrorException(f"Cannot delete plan (it might be in use by members): {str(e)}")