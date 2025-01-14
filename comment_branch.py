from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String

from base import Base

class CommentBranch(Base):
	__tablename__ = "comment_branch"

	id: Mapped[int] = mapped_column(primary_key=True)
	discussionId: Mapped[str] = mapped_column(String(30))
	userId: Mapped[int] = mapped_column()

	def __repr__(self) -> str:
			return f"CommentBranch(id={self.id}, discussionId={self.discussionId}, userId={self.userId}"




