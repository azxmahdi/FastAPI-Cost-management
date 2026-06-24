from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
from fastapi_cache.decorator import cache

from dependencies.database import get_db
from cost.schemas import CostCreateSchema, CostUpdateSchema, CostResponseSchama
from cost.models import CostModel
from account.models import UserModel
from dependencies.auth import get_current_user_from_cookie

router = APIRouter(tags=["cost"])


@router.get(
    "/costs",
    response_model=List[CostResponseSchama],
    status_code=status.HTTP_200_OK,
)
@cache(expire=600)
def cost_list(
    auth_user: UserModel = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    statement = select(CostModel).where(CostModel.user_id == auth_user.id)
    costs = db.execute(statement).scalars()
    return costs


@router.get(
    "/costs/{cost_id}",
    response_model=CostResponseSchama,
    status_code=status.HTTP_200_OK,
)
@cache(expire=600)
def cost_detail(
    cost_id: int = Path(ge=1),
    auth_user: UserModel = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    statement = select(CostModel).where(
        CostModel.id == cost_id, CostModel.user_id == auth_user.id
    )
    cost_db = db.execute(statement).scalar_one_or_none()
    if not cost_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cost not found"
        )
    return cost_db


@router.post(
    "/costs",
    response_model=CostResponseSchama,
    status_code=status.HTTP_201_CREATED,
)
def cost_create(
    cost: CostCreateSchema,
    auth_user: UserModel = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    cost_db = CostModel(
        description=cost.description, amount=cost.amount, user_id=auth_user.id
    )
    db.add(cost_db)
    db.commit()
    db.refresh(cost_db)
    return cost_db


@router.put(
    "/costs/{cost_id}",
    response_model=CostResponseSchama,
    status_code=status.HTTP_200_OK,
)
def cost_update(
    cost: CostUpdateSchema,
    cost_id: int = Path(ge=1),
    auth_user: UserModel = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    statement = select(CostModel).where(
        CostModel.id == cost_id, CostModel.user_id == auth_user.id
    )
    cost_db = db.execute(statement).scalar_one_or_none()
    if not cost_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cost not found"
        )
    cost_db.description = cost.description
    cost_db.amount = cost.amount
    db.commit()
    db.refresh(cost_db)
    return cost_db


@router.delete("/costs/{cost_id}", status_code=status.HTTP_204_NO_CONTENT)
def cost_delete(
    cost_id: int = Path(ge=1),
    auth_user: UserModel = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    statement = select(CostModel).where(
        CostModel.id == cost_id, CostModel.user_id == auth_user.id
    )
    cost_db = db.execute(statement).scalar_one_or_none()
    if not cost_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cost not found"
        )
    db.delete(cost_db)
    db.commit()
    return
