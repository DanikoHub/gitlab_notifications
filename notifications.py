import re
import json

with open('./mysite/secret_var.json', 'r') as file:
    secret_var = json.load(file)

from mysite.tables.users import Users
from mysite.tables.comment_branch import CommentBranch

from sql_requests import select_by_field, select_all_from_list

def new_comment(bot, request, users_to_send):
    for u in users_to_send:
        bot.send_message(u, "Новый комментарий в - " + request.json["object_attributes"]["url"])

def issue_change(bot, request, users_to_send):
    if 'id' in request.json["changes"].keys():
        for u in users_to_send:
            bot.send_message(u, "Новая issue - " + request.json["object_attributes"]["url"])

    elif 'description' in request.json["changes"].keys():
        for u in users_to_send:
            bot.send_message(u, "Изменено описание в issue - " + request.json["object_attributes"]["url"])

    elif 'assignees' in request.json["changes"].keys():
        for u in users_to_send:
            bot.send_message(u, "Изменены ответственные в issue - " + request.json["object_attributes"]["url"])

def labels_change(bot, request, users_to_send):
    if 'labels' in request.json["changes"].keys() and users_to_send is not None:
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

def get_users_for_notification(Session, request, bot = None):
    users_to_send = set()
    initiator_giltab_id = int(request.json["user"]["id"])

    if request.json["event_type"] == 'issue':
        author = select_by_field(Session, Users, Users.gitlabId, int(request.json["object_attributes"]["author_id"]))

        if author is not None:
            users_to_send.add(author[0].telegramId)

        if request.json["object_attributes"]["assignee_ids"] is not None:

            int_assignee_ids = [int(i) for i in request.json["object_attributes"]["assignee_ids"]]

            if len(int_assignee_ids) > 0:
                assignees = select_all_from_list(Session, Users, Users.gitlabId, int_assignee_ids, Users.telegramId)

                if assignees is not None:
                    users_to_send.update(assignees)



    if request.json["event_type"] == 'note':
        try:
            comment = request.json["object_attributes"]["description"]
            mentions = re.findall(r"@\w+", comment)

            mentioned = select_all_from_list(Session, Users, class_field = Users.gitlabUsername, list_vals = mentions, return_field = Users.telegramId)
            if mentioned is not None:
                users_to_send.update(mentioned)

            branche_comments = select_by_field(Session, CommentBranch, CommentBranch.discussionId, request.json["object_attributes"]["discussion_id"])

            if branche_comments is None:
                return users_to_send

            for b in branche_comments:
                if b.userGitlabId != initiator_giltab_id:
                    branch_participant = select_by_field(Session, Users, Users.gitlabId, b.userGitlabId)
                    users_to_send.add(branch_participant[0].telegramId)

        except Exception as e:
            if bot is not None:
                bot.send_message(secret_var["telegram_id"], 'not89 ' + str(e))

    return users_to_send


