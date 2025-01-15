from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger, Column

from sql_requests import add_composed_obj
from base import Base

class Labels(Base):
	__tablename__ = "labels"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(30))
	labelId: Mapped[int] = Column(BigInteger, unique = True)

	def __repr__(self) -> str:
			return f"Labels(id={self.id}, name={self.name}, labelId={self.labelId}"

def create_new_label(request, Session):
    for lbl in request.json["labels"]:
        new_label = Labels(
            name = lbl["title"],
            labelId = lbl["id"]
        )
        add_composed_obj(Session, new_label)

def labels_change(bot, request, users_to_send):
    if 'labels' in request.json["changes"].keys():
        lbl_list = ''

        for lbl in request.json["changes"]["labels"]["current"]:
            lbl_list += lbl["title"] + ", "

        lbl_list = lbl_list[:-2]
        for u in users_to_send:
            bot.send_message(u,
            "Были изменены лейблы в issue - " +
            request.json["object_attributes"]["url"] +
            "\nАкутальные лейблы - " + lbl_list
            )




