from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger

from mysite.src.tables.base import Base

class Issues(Base):
	__tablename__ = "issues"

	id: Mapped[int] = mapped_column(primary_key=True)
	title: Mapped[str] = mapped_column(String(100))
	description: Mapped[str] = mapped_column(String(100))
	url: Mapped[str] = mapped_column(String(100))
	issueId: Mapped[int] = mapped_column(BigInteger, unique = True)
	issueIid: Mapped[int] = mapped_column(BigInteger)
	authorId: Mapped[int] = mapped_column(BigInteger)
	isClosed: Mapped[int] = mapped_column()

	def __repr__(self) -> str:
			return f"Issues(id={self.id}\n\ttitle={self.title}\n\tdescription={self.description}\n\turl={self.url}\n\tissueIid={self.issueIid}\n\tissueId={self.issueId}\n\tauthorId={self.authorId}\n\tisClosed={self.isClosed})\n\n"



