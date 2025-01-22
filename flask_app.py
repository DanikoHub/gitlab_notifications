from flask import Flask, request
import telebot
from functools import partial
import os
import json

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from users import Users, create_new_user
from issues import Issues, create_new_issue
from comment_branch import CommentBranch, create_new_commentbranch
from labels import Labels, create_new_label
from labels_task_link import LabelsTaskLink, create_new_labeltasklink, delete_labeltasklink

from sql_requests import select_all
from notifications import get_users_for_notification, issue_change, labels_change, new_comment
from fetch_users_from_gitlab import fetch_users
from base import Base

# -------------Настройка бота------------

app = Flask(__name__)
with open('./mysite/secret_var.json', 'r') as file:
    secret_var = json.load(file)

token = secret_var["telegram_token"]
secret_bot = secret_var["bot_endpoint"]
url = 'https://GitlabWebHook.pythonanywhere.com/' + secret_bot

bot = telebot.TeleBot(token, threaded = False)
bot.remove_webhook()
bot.set_webhook(url)

@app.route('/'+secret_bot, methods = ['POST', 'GET'])
def index_bot():
    if request.headers.get('Content-Type') == 'application/json':
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return 'ok', 200

# -----------Подключение к БД----------------

engine = create_engine(secret_var["mysql_url"], poolclass=NullPool)
Session = sessionmaker(engine)

def create_db_and_tables() -> None:
	Base.metadata.create_all(engine)

try:
    create_db_and_tables()
except Exception as e:
     bot.send_message(secret_var["telegram_id"], e)

# --------------Обработка запроса из Gitlab---------------

secret = secret_var["gitlab_endpoint"]

@app.route('/'+secret, methods = ['POST', 'GET'])
def index():
    if request.headers.get('Content-Type') == 'application/json':
        try:
            create_new_issue(Session, request, bot)
            create_new_label(Session, request, bot)
            create_new_labeltasklink(Session, request, bot)

            if request.json["event_type"] == 'issue':

                users_to_send = get_users_for_notification(Session, request, bot)

                labels_change(bot, request, users_to_send)
                issue_change(bot, request, users_to_send)

                delete_labeltasklink(Session, request, bot)

            if request.json["event_type"] == 'note':

                create_new_commentbranch(Session, request)

                users_to_send = get_users_for_notification(Session, request, bot)

                new_comment(bot, request, users_to_send)


        except Exception as e:
            bot.send_message(secret_var["telegram_id"], e)
    return 'ok', 200

# ---------------Команды Бота-----------------

@bot.message_handler(commands=['start'])
def start_func(m):
    bot.send_message(m.chat.id, 'Отправьте ваш UserId')
    next_step = partial(get_client_id)
    bot.register_next_step_handler(m, next_step)

def get_client_id(m):
    try:
        create_new_user(Session, request, m.chat.id, m.text)
    except Exception as e:
        bot.send_message(secret_var["telegram_id"], e)

# -------------Технические функции, не будут использоваться позже--------------
def get_all(m, Classname):
    res = select_all(Session, Classname)
    bot.send_message(secret_var["telegram_id"], str(res))

@bot.message_handler(commands=['get_all_users'])
def get_users(m):
    get_all(m, Users)

@bot.message_handler(commands=['get_all_issues'])
def get_issues(m):
    get_all(m, Issues)

@bot.message_handler(commands=['get_all_branches'])
def get_branches(m):
    get_all(m, CommentBranch)

@bot.message_handler(commands=['get_all_labels'])
def get_labels(m):
    get_all(m, Labels)

@bot.message_handler(commands=['get_all_links'])
def get_links(m):
    get_all(m, LabelsTaskLink)

@bot.message_handler(commands=['fetch_users'])
def get_fetched_users(m):
    r = fetch_users()
    res_id = ''
    for i in r["users"]["nodes"]:
        res_id += i["id"] + '\n'
    bot.send_message(secret_var["telegram_id"], res_id)

@bot.message_handler(commands=['backup'])
def backup(m):
    try:
        directory_path = secret_var["directory_path"]
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                try:
                    file = open(file_path, "rb")
                    bot.send_document(secret_var["telegram_id"], file)
                    file.close()
                except:
                    pass
    except Exception as e:
        bot.send_message(5892105841, e)




