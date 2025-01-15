from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String

from sql_requests import add_composed_obj
from base import Base

class CommentBranch(Base):
	__tablename__ = "comment_branch"

	id: Mapped[int] = mapped_column(primary_key=True)
	discussionId: Mapped[str] = mapped_column(String(30))
	userId: Mapped[int] = mapped_column()

	def __repr__(self) -> str:
			return f"CommentBranch(id={self.id}, discussionId={self.discussionId}, userId={self.userId}"

def create_new_commentbranch(request, Session):
    new_branch = CommentBranch(
        discussionId=request.json["object_attributes"]["discussion_id"],
        userId=int(request.json["object_attributes"]["author_id"])
    )
    add_composed_obj(Session, new_branch)


