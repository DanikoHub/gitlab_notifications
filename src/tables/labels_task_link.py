from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import BigInteger, Column, Index
import json

from mysite.src.tables.base import Base
from mysite.src.sql_requests import create_obj, select_by_field, delete_obj

class LabelsTaskLink(Base):
	__tablename__ = "labels_task_link"

	id: Mapped[int] = mapped_column(primary_key=True)
	issueId: Mapped[int] = Column(BigInteger)
	labelId: Mapped[int] = Column(BigInteger)

	__table_args__ = (Index('idx_taskId_labelId', 'issueId', 'labelId', unique=True),)

	def __repr__(self) -> str:
			return f"LabelsTaskLink(id={self.id},\n\tissueId={self.issueId},\n\tlabelId={self.labelId})\n\n"

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

def delete_labeltasklink(Session, request, bot):
    if 'labels' in request.json["changes"].keys():
        labels = request.json["labels"]
        links_in_db = select_by_field(Session, LabelsTaskLink, LabelsTaskLink.issueId, int(request.json["object_attributes"]["id"]), LabelsTaskLink.labelId)

        if links_in_db is None:
            return

        gitlab_labels = []
        if labels is not None:
            [gitlab_labels.append(l["id"]) for l in labels]

        for lbl_id in links_in_db:
            if lbl_id not in gitlab_labels:
                delete_obj(Session, LabelsTaskLink, {'issueId' : int(request.json["object_attributes"]["id"]), 'labelId' : int(lbl_id)})



