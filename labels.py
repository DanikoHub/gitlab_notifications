from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, BigInteger, Column

from base import Base

class Labels(Base):
	__tablename__ = "labels"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(30))
	labelId: Mapped[int] = Column(BigInteger, unique = True)

	def __repr__(self) -> str:
			return f"Labels(id={self.id}, name={self.name}, labelId={self.labelId}"

def labels_change(bot, request, secret_var):
    if 'labels' in request.json["changes"].keys():
        lbl_list = ''

        for lbl in request.json["changes"]["labels"]["current"]:
            lbl_list += lbl["title"] + ", "

        lbl_list = lbl_list[:-2]
        bot.send_message(secret_var["telegram_id"],
        "Были изменены лейблы в issue - " +
        request.json["object_attributes"]["url"] +
        "\nАкутальные лейблы - " + lbl_list
        )




