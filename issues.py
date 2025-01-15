from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger

from base import Base

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

def issue_change(bot, request, secret_var):
    if 'description' in request.json["changes"].keys():
        bot.send_message("Изменено описание в issue - " + request.json["object_attributes"]["url"])



