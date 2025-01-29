from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Index

from mysite.src.sql_requests import SQLRequest
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
    obj_attrs = request.json["object_attributes"]
    new_branch = CommentBranch(
        discussionId=obj_attrs["discussion_id"],
        userGitlabId=int(obj_attrs["author_id"])
    )
    combranch_sql_request = SQLRequest(Session, CommentBranch)
    combranch_sql_request.create_obj(new_branch,\
        {'discussionId' : obj_attrs["discussion_id"],
        'userGitlabId' : int(obj_attrs["author_id"])})





