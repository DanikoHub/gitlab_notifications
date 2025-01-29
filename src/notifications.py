import re

from mysite.src.tables.users import Users
from mysite.src.tables.issues import Issues
from mysite.src.tables.comment_branch import CommentBranch

from mysite.src.sql_requests import select_by_field, select_from_list, update_obj
from mysite.src.debug_tools import send_e

def send_to_users(bot, users_to_send, text):
	send = lambda user, text : bot.send_message(user, text)
	[send(u, text) for u in users_to_send]

def new_comment_notify(Session, request, bot):
	users_to_send = get_users_for_notification(Session, request, bot)
	send_to_users(bot, users_to_send, "💬Новый комментарий в issue - " + request.json["object_attributes"]["url"])

def get_message_text_issue_change(Session, request, bot):
	obj_attrs = request.json["object_attributes"]
	issue = select_by_field(Session, Issues, Issues.issueId, int(obj_attrs["id"]))

	match request.json["changes"]:
		case {'id' : id}:
			return "🆕Новая issue - " + obj_attrs["url"]
		case {'description' : description}:
			return "🧷Изменено описание в issue - " + obj_attrs["url"]
		case {'assignees' : assignees}:
			return "👤Изменены ответственные в issue - " + obj_attrs["url"]
		case {'state_id' : state_id}:
			try:
				update_obj(Session, Issues, Issues.issueId, int(obj_attrs["id"]), {'isClosed' : int(request.json["changes"]["state_id"]["current"])}, bot)

				if issue[0].isClosed != int(request.json["changes"]["state_id"]["current"]):
					return "🔔Issue была открыта - " + obj_attrs["url"] if request.json["changes"]["state_id"]["current"] == 1 \
					else "🔕Issue была закрыта - " + obj_attrs["url"]

			except Exception as e:
					send_e(e)

def issue_change_notify(Session, request, bot):

	users_to_send = get_users_for_notification(Session, request, bot)
	mes_text = get_message_text_issue_change(Session, request, bot)

	if request.json["event_type"] == 'issue' and users_to_send is not None and mes_text is not None:
		send_to_users(bot, users_to_send, mes_text)


def labels_change_notify(Session, request, bot):
	users_to_send = get_users_for_notification(Session, request, bot)

	if 'labels' in request.json["changes"].keys() and users_to_send is not None:

		send_to_users(bot, users_to_send, "❗️Были изменены лейблы в issue - " + request.json["object_attributes"]["url"] + \
		"\nАкутальные лейблы - " + ', '.join([lbl["title"] for lbl in request.json["changes"]["labels"]["current"]]))


def get_users_for_notification(Session, request, bot = None):
	users_to_send = set()
	initiator_giltab_id = int(request.json["user"]["id"])
	obj_attrs = request.json["object_attributes"]

	if request.json["event_type"] == 'issue':
		author = select_by_field(Session, Users, Users.gitlabId, int(obj_attrs["author_id"]))

		if author is not None:
			users_to_send.add(author[0].telegramId)

		if obj_attrs["assignee_ids"] is None:
			return users_to_send

		assign_list = [int(i) for i in obj_attrs["assignee_ids"]]
		assignees = select_from_list(Session, Users, Users.gitlabId, assign_list, Users.telegramId) if len(assign_list) > 0 else None

		if assignees is not None:
			users_to_send.update(assignees)

	if request.json["event_type"] == 'note':
		try:
			comment = obj_attrs["description"]
			mentions = re.findall(r"@\w+", comment)

			mentioned = select_from_list(Session, Users, class_field = Users.gitlabUsername, list_vals = mentions, return_field = Users.telegramId)
			if mentioned is not None:
				users_to_send.update(mentioned)

			branche_comments = select_by_field(Session, CommentBranch, CommentBranch.discussionId, obj_attrs["discussion_id"])

			if branche_comments is None:
				return users_to_send

			add_branch_users = [b.userGitlabId for b in branche_comments if b.userGitlabId != initiator_giltab_id]
			branch_participants = select_from_list(Session, Users, Users.gitlabId, add_branch_users, return_field = Users.telegramId)
			users_to_send.update(branch_participants)

		except Exception as e:
			send_e(e)

	return users_to_send


