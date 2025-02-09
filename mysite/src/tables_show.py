from sqlalchemy import select
import os

from mysite.src.fetch_users_from_gitlab import fetch_users

from mysite.src.tables.users import Users
from mysite.src.tables.issues import Issues
from mysite.src.tables.comment_branch import CommentBranch
from mysite.src.tables.labels import Labels
from mysite.src.tables.labels_task_link import LabelsTaskLink

telegram_id = os.getenv("TELEGRAM_ID")


def get_all(Session, bot, m, Classname):
	statement = select(Classname)
	with Session() as session:
		db_object = session.scalars(statement).all()
	res = db_object
	bot.send_message(telegram_id, "Res = " + (str(res)[:-2000] if len(res) > 2000 else str(res)))

def setup_handlers(Session, bot):
	@bot.message_handler(commands=['get_all_users'])
	def get_users(m):
		get_all(Session, bot, m, Users)

	@bot.message_handler(commands=['get_all_issues'])
	def get_issues(m):
		get_all(Session, bot, m, Issues)

	@bot.message_handler(commands=['get_all_branches'])
	def get_branches(m):
		get_all(Session, bot, m, CommentBranch)

	@bot.message_handler(commands=['get_all_labels'])
	def get_labels(m):
		get_all(Session, bot, m, Labels)

	@bot.message_handler(commands=['get_all_links'])
	def get_links(m):
		get_all(Session, bot, m, LabelsTaskLink)

