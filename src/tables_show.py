import json
from sqlalchemy import select

# from mysite.src.sql_requests import select_all
from mysite.src.fetch_users_from_gitlab import fetch_users

from mysite.src.tables.users import Users
from mysite.src.tables.issues import Issues
from mysite.src.tables.comment_branch import CommentBranch
from mysite.src.tables.labels import Labels
from mysite.src.tables.labels_task_link import LabelsTaskLink

with open('./mysite/secret_var.json', 'r') as file:
	secret_var = json.load(file)

def get_all(Session, bot, m, Classname):
	statement = select(Classname)
	with Session() as session:
		db_object = session.scalars(statement).all()
	res = db_object
	bot.send_message(secret_var["telegram_id"], str(res)[:2000])

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

	@bot.message_handler(commands=['fetch_users'])
	def get_fetched_users(m):
		r = fetch_users()
		res_id = '\n'.join([i["id"] for i in r["users"]["nodes"]])
		bot.send_message(secret_var["telegram_id"], "Fetched users - " + res_id[:2000])

