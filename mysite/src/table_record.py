from mysite.src.tables import Users, Issues, CommentBranch, Labels, LabelsTaskLink
from mysite.src.sql_requests import SQLRequest
from mysite.src.notifications import Notification, NotificationIssue, NotificationComment
from mysite.src.fetch_users_from_gitlab import fetch_users

class Record:

    def __init__(self, Session, request = "", bot = None):
        self.Session = Session
        self.request = request
        self.bot = bot

    def create_new_record(self, class_name, **args):
        RecordFactory.create_record(class_name, self.Session, self.request, **args)
        if self.bot is not None:
            RecordFactory.notify(class_name, self.Session, self.request, self.bot)

    def delete_record(self, class_name):
        RecordFactory.delete_record(class_name, self.Session, self.request)


class RecordFactory:

    def __init__(self, Session, request):
        self.Session = Session
        self.request = request

    @classmethod
    def create_record(cls, table_name, Session, request, **args):
        return table_name(Session, request).create_table(**args)

    @classmethod
    def delete_record(cls, table_name : LabelsTaskLink, Session, request, **args):
        return table_name(Session, request).delete_record(**args)
    
    @classmethod
    def notify(cls, table_name, Session, request, bot):
        return table_name(Session, request).notify(bot)


class TableUser(RecordFactory):

    def __init__(self, Session, request):
        super().__init__(Session, request)

    def create_record(self, telegram_id, gitlab_id):
        gl_fetch = fetch_users(gitlab_id)
        name_fetch = gl_fetch["user"]["name"]
        username_fetch = "@" + gl_fetch["user"]["username"]


        new_user = Users(
            name=name_fetch,
            gitlabUsername = username_fetch,
            telegramId=int(telegram_id),
            gitlabId=int(gitlab_id))
        
        user_sql_request = SQLRequest(self.Session, Users)
        user_sql_request.create_obj(new_user, {'telegramId' : int(telegram_id)})
    
    def notify(self, bot):
        pass


class TableIssue(RecordFactory):

    def __init__(self, Session, request):
        super().__init__(Session, request)

    def create_record(self):
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
    
    def notify(self, bot):
        notification = NotificationIssue(self.Session, self.request, bot)
        notification.notify()

 
class TableCommentBranch(RecordFactory):

    def __init__(self, Session, request):
        super().__init__(Session, request)

    def create_record(self):
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
    
    def notify(self, bot):            
        notification = NotificationComment(self.Session, self.request, bot)
        notification.notify()


class TableLabel(RecordFactory):

    def __init__(self, Session, request):
        super().__init__(Session, request)

    def create_record(self):
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
    
    def notify(self, bot):
        pass


class TableLabelTaskLink(RecordFactory):

    def __init__(self, Session, request):
        super().__init__(Session, request)

    def create_record(self):
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

    def notify(self, bot):
        pass


