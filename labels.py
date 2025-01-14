from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger, Column

from base import Base

class Labels(Base):
	__tablename__ = "labels"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(30))
	labelId: Mapped[int] = Column(BigInteger, unique = True)

	def __repr__(self) -> str:
			return f"Labels(id={self.id}, name={self.name}, labelId={self.labelId}"




