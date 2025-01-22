from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger, Column

from sql_requests import create_obj
from base import Base

class Users(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(30))
	gitlabUsername: Mapped[str] = mapped_column(String(30))
	telegramId: Mapped[int] = Column(BigInteger, unique = True)
	gitlabId: Mapped[int] = Column(BigInteger)

	def __repr__(self) -> str:
			return f"Users(id={self.id}, name={self.name}, telegramId={self.telegramId}, gitlabId={self.gitlabId}, gitlabUsername={self.gitlabUsername})"

def create_new_user(Session, request, telegram_id, gitlab_id):
    new_user = Users(
        name="new_user",
        gitlabUsername = "@username",
        telegramId=int(telegram_id),
        gitlabId=int(gitlab_id))
    create_obj(Session, new_user, Users, {'telegramId' : int(telegram_id)})


