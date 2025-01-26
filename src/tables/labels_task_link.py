from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import BigInteger, Column, Index
import json

from mysite.src.tables.base import Base
from mysite.src.sql_requests import create_obj, select_by_field, select_filtered_rows

class LabelsTaskLink(Base):
	__tablename__ = "labels_task_link"

	id: Mapped[int] = mapped_column(primary_key=True)
	issueId: Mapped[int] = Column(BigInteger)
	labelId: Mapped[int] = Column(BigInteger)

	__table_args__ = (Index('idx_taskId_labelId', 'issueId', 'labelId', unique=True),)

	def __repr__(self) -> str:
			return f"LabelsTaskLink(id={self.id}, issueId={self.issueId}, labelId={self.labelId})"

def create_new_labeltasklink(Session, request, bot = None):
    if request.json["event_type"] == 'issue':
        labels = request.json["labels"]
        obj_attr = 'object_attributes'
    else:
        labels = request.json["issue"]["labels"]
        obj_attr = 'issue'

    for lbl in labels:
        new_label_task_link = LabelsTaskLink(
            issueId = int(request.json[obj_attr]["id"]),
            labelId = int(lbl["id"])
        )
        create_obj(Session,
            new_label_task_link,
            LabelsTaskLink,
            {'issueId' : int(request.json[obj_attr]["id"]), 'labelId' : int(lbl["id"])}, bot = bot)

with open('./mysite/secret_var.json', 'r') as file:
    secret_var = json.load(file)

def delete_labeltasklink(Session, request, bot):
    if 'labels' in request.json["changes"].keys():
        labels = request.json["labels"]
        links_in_db = select_by_field(Session, LabelsTaskLink, LabelsTaskLink.issueId, int(request.json["object_attributes"]["id"]), LabelsTaskLink.labelId)

        gitlab_labels = []
        if labels is not None:
            for l in  labels:
                gitlab_labels.append(l["id"])


        if links_in_db is None:
            return

        for lbl_id in links_in_db:
            if lbl_id in gitlab_labels:
                continue

            with Session() as session:
                try:
                    obj = select_filtered_rows(Session, LabelsTaskLink, {'issueId' : int(request.json["object_attributes"]["id"]), 'labelId' : int(lbl_id)})
                    if len(obj) != 0:
                        session.delete(obj[0])
                except:
                    session.rollback()
                else:
                    session.commit()



