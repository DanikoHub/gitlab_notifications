from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger

from mysite.src.tables.base import Base
from mysite.src.sql_requests import create_obj

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
			return f"Issues(id={self.id}, title={self.title}, description={self.description}, url={self.url} issueIid={self.issueIid} issueId={self.issueId} authorId={self.authorId} isClosed={self.isClosed})"

def create_new_issue(Session, request, bot = None):
    if request.json["event_type"] == 'issue':
        obj_attr = 'object_attributes'
    else:
        obj_attr = 'issue'

    new_issue = Issues(
        title = request.json[obj_attr]["title"],
        description = request.json[obj_attr]["description"],
        url = request.json[obj_attr]["url"],
        issueId = int(request.json[obj_attr]["id"]),
        issueIid = int(request.json[obj_attr]["iid"]),
        authorId = int(request.json[obj_attr]["author_id"]),
        isClosed = int(request.json[obj_attr]["state_id"])
    )
    create_obj(Session, new_issue, Issues, {'issueId' : int(request.json[obj_attr]["id"])}, bot)
    return new_issue




