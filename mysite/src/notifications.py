import re

from mysite.src.tables import Users, Issues, CommentBranch
from mysite.src.table_factory import TableIssue, TableCommentBranch

from mysite.src.sql_requests import SQLRequest
from mysite.src.log_tools import log_error

class NotificationFactory:

	def __init__(self, Session, request, bot):
		self.Session = Session
		self.request = request
		self.bot = bot

	def send_to_users(self, users_to_send, text):
		send = lambda user, text : self.bot.send_message(user, text)
		[send(u, text) for u in users_to_send]
	
	def get_users_for_notification(self):
		pass

	@classmethod
	def notify(cls, table_name, Session, request, bot):
		if table_name == TableIssue:
			NotificationIssue(Session, request, bot).notify()
		if table_name == TableCommentBranch:
			NotificationComment(Session, request, bot).notify()


class NotificationIssue(NotificationFactory):
	
	def __init__(self, Session, request, bot):
		super().__init__(Session, request, bot)

	def get_message_text_issue_change(self):
		obj_attrs = self.request.json["object_attributes"]

		if "changes" in self.request.json:
			obj_changes = self.request.json["changes"]
			issues_sql_request = SQLRequest(self.Session, Issues)
			issue = issues_sql_request.select_by_field(Issues.issueId, int(obj_attrs["id"]))

			match obj_changes:
				case {'id' : id}:
					return "🆕Новая issue - " + obj_attrs["url"]
				case {'description' : description}:
					return "🧷Изменено описание в issue - " + obj_attrs["url"]
				case {'assignees' : assignees}:
					return "👤Изменены ответственные в issue - " + obj_attrs["url"]
				case {'labels' : labels}:
					return "❗️Были изменены лейблы в issue - " + obj_attrs["url"] + "\nАкутальные лейблы - " + ', '.join([lbl["title"] for lbl in obj_changes["labels"]["current"]])
				case {'state_id' : state_id}:
					try:
						issues_sql_request.update_obj(Issues.issueId, int(obj_attrs["id"]), {'isClosed' : int(obj_changes["state_id"]["current"])})

						if issue[0].isClosed != int(obj_changes["state_id"]["current"]):
							return "🔔Issue была открыта - " + obj_attrs["url"] if obj_changes["state_id"]["current"] == 1 \
							else "🔕Issue была закрыта - " + obj_attrs["url"]

					except Exception as e:
							log_error(e)

	def get_users_for_notification(self):
		users_to_send = set()

		if self.request.json["event_type"] == 'issue':
			obj_attrs = self.request.json["object_attributes"]

			users_sql_request = SQLRequest(self.Session, Users)

			author = users_sql_request.select_by_field(Users.gitlabId, int(obj_attrs["author_id"]))

			if author is not None and author != []:
				users_to_send.add(author[0].telegramId)

			if obj_attrs["assignee_ids"] is None:
				return users_to_send

			assign_list = [int(i) for i in obj_attrs["assignee_ids"]]
			assignees = users_sql_request.select_from_list(Users.gitlabId, assign_list, Users.telegramId) if len(assign_list) > 0 else None

			if assignees is not None and assignees != []:
				users_to_send.update([assignees[i][0] for i in range(len(assignees))])
		
		return users_to_send

	def notify(self):
		users_to_send = self.get_users_for_notification()
		mes_text = self.get_message_text_issue_change()

		if self.request.json["event_type"] == 'issue' and users_to_send is not None and mes_text is not None:
			self.send_to_users(users_to_send, mes_text)


class NotificationComment(NotificationFactory):
	
	def __init__(self, Session, request, bot):
		super().__init__(Session, request, bot)
	
	def get_users_for_notification(self):
		users_to_send = set()

		if self.request.json["event_type"] == 'note':
			initiator_giltab_id = int(self.request.json["user"]["id"])
			obj_attrs = self.request.json["object_attributes"]
			users_sql_request = SQLRequest(self.Session, Users)
			
			try:
				comment = obj_attrs["description"]
				mentions = re.findall(r"@\w+", comment)

				mentioned = users_sql_request.select_from_list(filter_class_field = Users.gitlabUsername, filter_list_values = mentions, return_field = Users.telegramId)
				if mentioned is not None:
					users_to_send.update([mentioned[i][0] for i in range(len(mentioned))])

				combranch_sql_request = SQLRequest(self.Session, CommentBranch)

				branche_comments = combranch_sql_request.select_by_field(CommentBranch.discussionId, obj_attrs["discussion_id"])

				if branche_comments is None and branche_comments != []:
					return users_to_send

				add_branch_users = [b.userGitlabId for b in branche_comments if b.userGitlabId != initiator_giltab_id]
				branch_participants = users_sql_request.select_from_list(Users.gitlabId, add_branch_users, return_field = Users.telegramId)

				users_to_send.update([branch_participants[i][0] for i in range(len(branch_participants))])

			except Exception as e:
				log_error(e)

		return users_to_send

	def notify(self):
		users_to_send = self.get_users_for_notification()
		self.send_to_users(users_to_send, "💬Новый комментарий в issue - " + self.request.json["object_attributes"]["url"])