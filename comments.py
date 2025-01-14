from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker
from sqlalchemy import String, create_engine
from sqlalchemy import select, TIMESTAMP, Column

from base import Base
from sql_requests import add_composed_obj

class Comments(Base):
	__tablename__ = "comments"

	id: Mapped[int] = mapped_column(primary_key=True)
	text: Mapped[str] = mapped_column(String(1000))
	url: Mapped[str] = mapped_column(String(100))
	authorId: Mapped[int] = mapped_column()
	branchId: Mapped[str] = mapped_column(String(100))
	is_responce: Mapped[int] = mapped_column()


	def __repr__(self) -> str:
			return f"Comments(id={self.id}, text={self.text}, url={self.url}, authorId={self.authorId}, branchId={self.branchId}, is_responce={self.is_responce})"

# def create_comment(comment, session) -> None:
# 	session.add(comment)

# def get_all_comments(session, class_name):
# 	statement = select(class_name)
# 	db_object = session.scalars(statement).all()
# 	return db_object

# def update_comment(new_object: Comments, session) -> None:
# 	session.merge(new_object)

def add_comment(bot, request, Session):
    comment_url = '_'
    try:
        new_comment = Comments(
            text = request.json["object_attributes"]["note"],
            url = request.json["object_attributes"]["url"],
            authorId = int(request.json["object_attributes"]["author_id"]),
            branchId = request.json["object_attributes"]["discussion_id"],
            is_responce = int(request.json["object_attributes"]["type"] == 'DiscussionNote')
        )
        comment_url = request.json["object_attributes"]["url"]

        add_composed_obj(Session, new_comment, comment_url)

    except Exception as e:
        bot.send_message(5892105841, e)
    try:
        bot.send_message(5892105841, f"Новый комментарий в issue - {comment_url}")
    except Exception as e:
        bot.send_message(5892105841, e)


