import re

from users import Users
from comment_branch import CommentBranch

from sql_requests import select_by_field, select_all_from_list

def get_users_for_notification(request, Session, bot):
    users_to_send = set()
    initiator_giltab_id = int(request.json["user"]["id"])

    if request.json["event_type"] == 'issue':
        author = select_by_field(Session(), Users, Users.gitlabId, int(request.json["object_attributes"]["author_id"]))
        users_to_send.add(author[0].telegramId)

        int_assignee_ids = [int(i) for i in request.json["object_attributes"]["assignee_ids"]]
        assignees = select_all_from_list(Session(), Users, class_field = Users.gitlabId, list_vals = int_assignee_ids, return_field = Users.telegramId)
        users_to_send.update(assignees)

    if request.json["event_type"] == 'note':
        try:
            comment = request.json["object_attributes"]["description"]
            mentions = re.findall(r"@\w+", comment)

            mentioned = select_all_from_list(Session(), Users, class_field = Users.gitlabUsername, list_vals = mentions, return_field = Users.telegramId)
            users_to_send.update(mentioned)

            branche_comments = select_by_field(Session(), CommentBranch, CommentBranch.discussionId, request.json["object_attributes"]["discussion_id"])
            for b in branche_comments:
                if b.userGitlabId != initiator_giltab_id:
                    branch_participant = select_by_field(Session(), Users, Users.gitlabId, b.userGitlabId)
                    users_to_send.add(branch_participant[0].telegramId)

        except Exception as e:
            print("===========ERROR========\n" + str(e) + "\n======================")
    return users_to_send


