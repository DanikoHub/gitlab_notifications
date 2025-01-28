import re
import json

with open('./mysite/secret_var.json', 'r') as file:
	secret_var = json.load(file)

from mysite.src.tables.users import Users
from mysite.src.tables.issues import Issues
from mysite.src.tables.comment_branch import CommentBranch

from mysite.src.sql_requests import select_by_field, select_all_from_list, update_obj

def send_to_users(bot, users_to_send, text):
	send = lambda user, text : bot.send_message(user, text)
	[send(u, text) for u in users_to_send]

def new_comment_notify(Session, request, bot):
	users_to_send = get_users_for_notification(Session, request, bot)
	send_to_users(bot, users_to_send, "Новый комментарий в issue - " + request.json["object_attributes"]["url"])

def issue_change_notify(Session, request, bot):

	users_to_send = get_users_for_notification(Session, request, bot)

	if request.json["event_type"] == 'issue' and users_to_send is not None:

		obj_attrs = request.json["object_attributes"]

		issue = select_by_field(Session, Issues, Issues.issueId, int(obj_attrs["id"]))

		match request.json["changes"]:

			case {'id' : id}:
				send_to_users(bot, users_to_send, "Новая issue - " + obj_attrs["url"])

			case {'description' : description}:
				send_to_users(bot, users_to_send, "Изменено описание в issue - " + obj_attrs["url"])

			case {'assignees' : assignees}:
				send_to_users(bot, users_to_send, "Изменены ответственные в issue - " + obj_attrs["url"])

			case {'state_id' : state_id}:
				try:
					update_obj(Session, Issues, Issues.issueId, int(obj_attrs["id"]), {'isClosed' : int(request.json["changes"]["state_id"]["current"])}, bot)

					if issue[0].isClosed != int(request.json["changes"]["state_id"]["current"]):
						send_to_users(bot, users_to_send, "Issue была переоткрыта - " + obj_attrs["url"] \
						if request.json["changes"]["state_id"]["current"] == 1 \
						else "Issue была закрыта - " + request.json["object_attributes"]["url"])

				except Exception as e:
					if bot is not None:
						bot.send_message(secret_var["telegram_id"], 'not44 ' + str(e))


def labels_change_notify(Session, request, bot):
	users_to_send = get_users_for_notification(Session, request, bot)

	if 'labels' in request.json["changes"].keys() and users_to_send is not None:

		send_to_users(bot, users_to_send, "Были изменены лейблы в issue - " + request.json["object_attributes"]["url"] + \
		"\nАкутальные лейблы - " + ', '.join([lbl["title"] for lbl in request.json["changes"]["labels"]["current"]]))


def get_users_for_notification(Session, request, bot = None):
	users_to_send = set()
	initiator_giltab_id = int(request.json["user"]["id"])

	if request.json["event_type"] == 'issue':
		author = select_by_field(Session, Users, Users.gitlabId, int(request.json["object_attributes"]["author_id"]))

		if author is not None:
			users_to_send.add(author[0].telegramId)

		if request.json["object_attributes"]["assignee_ids"] is None:
			return users_to_send

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


