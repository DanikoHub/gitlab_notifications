from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger

from base import Base
from sql_requests import add_composed_obj

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

def create_new_issue(request, Session):
    new_issue = Issues(
        title = request.json["object_attributes"]["title"],
        description = request.json["object_attributes"]["description"],
        url = request.json["object_attributes"]["url"],
        issueId = int(request.json["object_attributes"]["id"]),
        issueIid = int(request.json["object_attributes"]["iid"]),
        authorId = int(request.json["object_attributes"]["author_id"]),
        isClosed = int(request.json["object_attributes"]["state"] != 'opened')
    )
    add_composed_obj(Session, new_issue)
    return new_issue

def issue_change(bot, request, users_to_send):
    if 'description' in request.json["changes"].keys():
        for u in users_to_send:
            bot.send_message(u, "Изменено описание в issue - " + request.json["object_attributes"]["url"])



