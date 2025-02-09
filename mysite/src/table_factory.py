from mysite.src.tables import Users, Issues, CommentBranch, Labels, LabelsTaskLink
from mysite.src.sql_requests import SQLRequest


class TableFactory:

    def __init__(self, Session, request):
        self.Session = Session
        self.request = request

    @classmethod
    def create_table(cls, table_name, Session, request, **args):
        return table_name(Session, request).create_table(**args)

    @classmethod
    def delete_record(cls, table_name : LabelsTaskLink, Session, request, **args):
        return table_name(Session, request).delete_record(**args)


class TableUser(TableFactory):

    def __init__(self, Session, request):
        super().__init__(Session, request)

    def create_table(self, telegram_id, gitlab_id):
        new_user = Users(
            name="new_user",
            gitlabUsername = "@username",
            telegramId=int(telegram_id),
            gitlabId=int(gitlab_id))
        
        user_sql_request = SQLRequest(self.Session, Users)
        user_sql_request.create_obj(new_user, {'telegramId' : int(telegram_id)})


class TableIssue(TableFactory):

    def __init__(self, Session, request):
        super().__init__(Session, request)

    def create_table(self):
        if self.request.json["event_type"] == 'issue':
            obj_attr = 'object_attributes'
        else:
            obj_attr = 'issue'

        new_issue = Issues(
            title = self.request.json[obj_attr]["title"],
            description = self.request.json[obj_attr]["description"],
            url = self.request.json[obj_attr]["url"],
            issueId = int(self.request.json[obj_attr]["id"]),
            issueIid = int(self.request.json[obj_attr]["iid"]),
            authorId = int(self.request.json[obj_attr]["author_id"]),
            isClosed = int(self.request.json[obj_attr]["state_id"])
        )

        issue_sql_request = SQLRequest(self.Session, Issues)
        issue_sql_request.create_obj(new_issue, {'issueId' : int(self.request.json[obj_attr]["id"])})

        return new_issue

 
class TableCommentBranch(TableFactory):

    def __init__(self, Session, request):
        super().__init__(Session, request)

    def create_table(self):
        if self.request.json["event_type"] == 'note':
            obj_attrs = self.request.json["object_attributes"]
        
            new_branch = CommentBranch(
                discussionId=obj_attrs["discussion_id"],
                userGitlabId=int(obj_attrs["author_id"])
            )

            combranch_sql_request = SQLRequest(self.Session, CommentBranch)
            combranch_sql_request.create_obj(new_branch,\
                {'discussionId' : obj_attrs["discussion_id"],
                'userGitlabId' : int(obj_attrs["author_id"])})


class TableLabel(TableFactory):

    def __init__(self, Session, request):
        super().__init__(Session, request)

    def create_table(self):
        if self.request.json["event_type"] == 'issue':
            labels = self.request.json["labels"]
        else:
            labels = self.request.json["issue"]["labels"]

        label_sql_request = SQLRequest(self.Session, Labels)
        for lbl in labels:
            new_label = Labels(
                name = lbl["title"],
                labelId = lbl["id"]
            )
            
            label_sql_request.create_obj(new_label, {'labelId' : lbl["id"]})


class TableLabelTaskLink(TableFactory):

    def __init__(self, Session, request):
        super().__init__(Session, request)

    def create_table(self):
        if self.request.json["event_type"] == 'issue':
            labels = self.request.json["labels"]
            obj_attr = 'object_attributes'
        else:
            labels = self.request.json["issue"]["labels"]
            obj_attr = 'issue'

        labeltasklink_sql_request = SQLRequest(self.Session, LabelsTaskLink)

        for lbl in labels:
            new_label_task_link = LabelsTaskLink(
                issueId = int(self.request.json[obj_attr]["id"]),
                labelId = int(lbl["id"])
            )

            labeltasklink_sql_request.create_obj(new_label_task_link,
                {'issueId' : int(self.request.json[obj_attr]["id"]), 'labelId' : int(lbl["id"])})
    
    def delete_record(self):
        if "changes" in self.request.json and 'labels' in self.request.json["changes"].keys():
            obj_attr = 'object_attributes'

            labeltasklink_sql_request = SQLRequest(Session=self.Session, class_name=LabelsTaskLink)
            labels = self.request.json["changes"]["labels"]["current"]
            links_in_db = labeltasklink_sql_request.select_by_field(LabelsTaskLink.issueId, int(self.request.json[obj_attr]["id"]), LabelsTaskLink.labelId)

            if links_in_db is None:
                return

            gitlab_labels = []
            if labels is not None:
                [gitlab_labels.append(l["id"]) for l in labels]

            for lbl_id in links_in_db:
                if lbl_id[0] not in gitlab_labels:
                    labeltasklink_sql_request.delete_obj(filters={'issueId' : int(self.request.json[obj_attr]["id"]), 'labelId' : int(lbl_id[0])})


