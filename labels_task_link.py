from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import BigInteger, Column, Index, select

from base import Base
from sql_requests import add_composed_obj, select_by_field

class LabelsTaskLink(Base):
	__tablename__ = "labels_task_link"

	id: Mapped[int] = mapped_column(primary_key=True)
	issueId: Mapped[int] = Column(BigInteger)
	labelId: Mapped[int] = Column(BigInteger)

	__table_args__ = (Index('idx_taskId_labelId', 'issueId', 'labelId', unique=True),)

	def __repr__(self) -> str:
			return f"LabelsTaskLink(id={self.id}, issueId={self.issueId}, labelId={self.labelId}"

def create_new_labeltasklink(request, Session):
    for lbl in request.json["labels"]:
        # select_by_field(Session(), LabelsTaskLink, LabelsTaskLink., value)
        new_label_task_link = LabelsTaskLink(
            issueId = request.json["object_attributes"]["id"],
            labelId = lbl["id"]
        )
        add_composed_obj(Session, new_label_task_link)

def delete_link(issue_id, labels, Session):
    gitlab_labels = []
    for l in labels:
        gitlab_labels.append(l["id"])

    with Session() as session:
        try:
            statement = select(LabelsTaskLink).where(LabelsTaskLink.issueId == issue_id)
            links_in_db = session.scalars(statement).all()
        except:
            pass

    for el in links_in_db:
        if el.labelId not in gitlab_labels:
            try:
                with Session() as session:
                    try:
                        obj=session.query(LabelsTaskLink).filter(LabelsTaskLink.issueId==issue_id and LabelsTaskLink.labelId==el.labelId).first()
                        session.delete(obj)
                    except:
                        session.rollback()
                    else:
                        session.commit()
            except:
                pass



