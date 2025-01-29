from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger

from mysite.src.tables.base import Base
from mysite.src.sql_requests import SQLRequest

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

def create_new_issue(Session, request):
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
    issue_sql_request = SQLRequest(Session, Issues)
    issue_sql_request.create_obj(new_issue, {'issueId' : int(request.json[obj_attr]["id"])})
    return new_issue




