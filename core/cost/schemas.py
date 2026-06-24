from pydantic import BaseModel, Field


class CostBaseSchema(BaseModel):
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        pattern=r"^[\w\s.,-]+$",
        description="Cost description",
    )
    amount: float = Field(..., gt=0, description="Cost amount")


class CostCreateSchema(CostBaseSchema):
    pass


class CostUpdateSchema(CostBaseSchema):
    pass


class CostResponseSchama(CostBaseSchema):
    id: int

    model_config = {"from_attributes": True}
