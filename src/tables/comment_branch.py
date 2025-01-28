from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Index

from mysite.src.sql_requests import create_obj
from mysite.src.tables.base import Base

class CommentBranch(Base):
	__tablename__ = "comment_branch"

	id: Mapped[int] = mapped_column(primary_key=True)
	discussionId: Mapped[str] = mapped_column(String(50))
	userGitlabId: Mapped[int] = mapped_column()

	__table_args__ = (Index('idx_discussionId_userId', 'discussionId', 'userGitlabId', unique=True),)

	def __repr__(self) -> str:
			return f"CommentBranch(id={self.id},\n\tdiscussionId={self.discussionId},\n\tuserGitlabId={self.userGitlabId})\n\n"

def create_new_commentbranch(Session, request):
    new_branch = CommentBranch(
        discussionId=request.json["object_attributes"]["discussion_id"],
        userGitlabId=int(request.json["object_attributes"]["author_id"])
    )
    create_obj(Session, new_branch, CommentBranch,
        {'discussionId' : request.json["object_attributes"]["discussion_id"],
        'userGitlabId' : int(request.json["object_attributes"]["author_id"])})


