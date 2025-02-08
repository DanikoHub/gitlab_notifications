from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import BigInteger, Column, Index
import json

from mysite.src.tables.base import Base
from mysite.src.sql_requests import SQLRequest

class LabelsTaskLink(Base):
	__tablename__ = "labels_task_link"

	id: Mapped[int] = mapped_column(primary_key=True)
	issueId: Mapped[int] = Column(BigInteger)
	labelId: Mapped[int] = Column(BigInteger)

	__table_args__ = (Index('idx_taskId_labelId', 'issueId', 'labelId', unique=True),)

	def __repr__(self) -> str:
			return f"LabelsTaskLink(id={self.id},\n\tissueId={self.issueId},\n\tlabelId={self.labelId})\n\n"

def create_new_labeltasklink(Session, request):
    if request.json["event_type"] == 'issue':
        labels = request.json["labels"]
        obj_attr = 'object_attributes'
    else:
        labels = request.json["issue"]["labels"]
        obj_attr = 'issue'

    labeltasklink_sql_request = SQLRequest(Session, LabelsTaskLink)
    for lbl in labels:
        new_label_task_link = LabelsTaskLink(
            issueId = int(request.json[obj_attr]["id"]),
            labelId = int(lbl["id"])
        )
        labeltasklink_sql_request.create_obj(new_label_task_link,
            {'issueId' : int(request.json[obj_attr]["id"]), 'labelId' : int(lbl["id"])})

def delete_labeltasklink(Session, request):
    if 'labels' in request.json["changes"].keys():
        labeltasklink_sql_request = SQLRequest(Session, LabelsTaskLink)
        labels = request.json["labels"]
        links_in_db = labeltasklink_sql_request.select_by_field(LabelsTaskLink.issueId, int(request.json["object_attributes"]["id"]), LabelsTaskLink.labelId)

        if links_in_db is None:
            return

        gitlab_labels = []
        if labels is not None:
            [gitlab_labels.append(l["id"]) for l in labels]

        for lbl_id in links_in_db:
            if lbl_id not in gitlab_labels:
                labeltasklink_sql_request.delete_obj({'issueId' : int(request.json["object_attributes"]["id"]), 'labelId' : int(lbl_id)})



