from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger, Column

from mysite.src.sql_requests import create_obj
from mysite.src.tables.base import Base

class Labels(Base):
	__tablename__ = "labels"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(30))
	labelId: Mapped[int] = Column(BigInteger, unique = True)

	def __repr__(self) -> str:
			return f"Labels(id={self.id}, name={self.name}, labelId={self.labelId})"

def create_new_label(Session, request, bot = None):
    if request.json["event_type"] == 'issue':
        labels = request.json["labels"]
    else:
        labels = request.json["issue"]["labels"]

    for lbl in labels:
        new_label = Labels(
            name = lbl["title"],
            labelId = lbl["id"]
        )
        create_obj(Session, new_label, Labels, {'labelId' : lbl["id"]}, bot)




