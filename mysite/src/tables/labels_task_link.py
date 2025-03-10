from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import BigInteger, Column, Index
import json

from mysite.src.tables.base import Base

class LabelsTaskLink(Base):
	__tablename__ = "labels_task_link"

	id: Mapped[int] = mapped_column(primary_key=True)
	issueId: Mapped[int] = Column(BigInteger)
	labelId: Mapped[int] = Column(BigInteger)

	__table_args__ = (Index('idx_taskId_labelId', 'issueId', 'labelId', unique=True),)

	def __repr__(self) -> str:
			return f"LabelsTaskLink(id={self.id},\n\tissueId={self.issueId},\n\tlabelId={self.labelId})\n\n"



