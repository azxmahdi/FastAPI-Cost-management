from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from config.database import Base


class CostModel(Base):
    __tablename__ = "costs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=True)
    amount = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel", back_populates="costs", uselist=False)
