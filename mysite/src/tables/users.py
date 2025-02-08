from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger, Column

from mysite.src.sql_requests import SQLRequest
from mysite.src.tables.base import Base

class Users(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(30))
	gitlabUsername: Mapped[str] = mapped_column(String(30))
	telegramId: Mapped[int] = Column(BigInteger, unique = True)
	gitlabId: Mapped[int] = Column(BigInteger)

	def __repr__(self) -> str:
			return f"Users(id={self.id},\n\tname={self.name},\n\ttelegramId={self.telegramId},\n\tgitlabId={self.gitlabId},\n\tgitlabUsername={self.gitlabUsername})\n\n"

def create_new_user(Session, request, telegram_id, gitlab_id):
    new_user = Users(
        name="new_user",
        gitlabUsername = "@username",
        telegramId=int(telegram_id),
        gitlabId=int(gitlab_id))
    user_sql_request = SQLRequest(Session, Users)
    user_sql_request.create_obj(new_user, {'telegramId' : int(telegram_id)})


