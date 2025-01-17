from flask import Flask, request
import telebot
from functools import partial
import os
import json
import re

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from users import Users
from issues import Issues, issue_change, create_new_issue
from comment_branch import CommentBranch, create_new_commentbranch
from labels import Labels, labels_change, create_new_label
from labels_task_link import LabelsTaskLink, delete_link, create_new_labeltasklink

from sql_requests import get_all_objs, add_composed_obj, select_by_field
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

engine = create_engine(secret_var["mysql_url"])
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
            if request.json["event_type"] == 'issue':
                users_to_send = get_users_for_notification(request)
                res = select_by_field(Session(), Issues, Issues.issueId, int(request.json["object_attributes"]["id"]))
                if len(res) == 0:
                    for u in users_to_send:
                        bot.send_message(u, "Новая issue - " + request.json["object_attributes"]["url"])
                    create_new_issue(request, Session)
                else:
                    if 'assignees' in request.json["changes"].keys():
                        for u in users_to_send:
                            bot.send_message(u, "Изменены ответсвенные в issue - " + request.json["object_attributes"]["url"])

                    labels_change(bot, request, users_to_send)
                    issue_change(bot, request, users_to_send)

                create_new_label(request, Session)
                create_new_labeltasklink(request, Session)
                delete_link(request.json["object_attributes"]["id"], request.json["labels"], Session)

            if request.json["event_type"] == 'note':
                create_new_commentbranch(request, Session)
                users_to_send = get_users_for_notification(request)
                for u in users_to_send:
                    bot.send_message(u, "Новый комментарий в - " + request.json["object_attributes"]["url"])


        except Exception as e:
            bot.send_message(secret_var["telegram_id"], e)
    return 'ok', 200

def get_users_for_notification(request):
    users_to_send = set()
    initiator_giltab_id = int(request.json["user"]["id"])

    if request.json["event_type"] == 'issue':
        author = select_by_field(Session(), Users, Users.gitlabId, int(request.json["object_attributes"]["author_id"]))

        users_to_send.add(author[0].telegramId)
        for a in request.json["object_attributes"]["assignee_ids"]:
            assignee = select_by_field(Session(), Users, Users.gitlabId, int(a))
            users_to_send.add(assignee[0].telegramId)

    if request.json["event_type"] == 'note':
        try:
            comment = request.json["object_attributes"]["description"]
            mentions = re.findall(r"@\w+", comment)

            for m in mentions:
                user_mentioned = select_by_field(Session(), Users, Users.gitlabUsername, m)
                users_to_send.add(user_mentioned[0].telegramId)

            branche_comments = select_by_field(Session(), CommentBranch, CommentBranch.discussionId, request.json["object_attributes"]["discussion_id"])
            for b in branche_comments:
                if b.userGitlabId != initiator_giltab_id:
                    branch_participant = select_by_field(Session(), Users, Users.gitlabId, b.userGitlabId)
                    users_to_send.add(branch_participant[0].telegramId)
        except Exception as e:
            bot.send_message(secret_var["telegram_id"], "Error = " + str(e))
    return users_to_send

# ---------------Команды Бота-----------------

@bot.message_handler(commands=['start'])
def start_func(m):
    bot.send_message(m.chat.id, 'Отправьте ваш ClientId')
    next_step = partial(get_client_id)
    bot.register_next_step_handler(m, next_step)

def get_client_id(m):
    bot.send_message(secret_var["telegram_id"], str(m.chat.id))
    telegram_id = m.chat.id
    gitlab_id = m.text
    try:
        new_user = Users(name="new_user", gitlabUsername = "@username", telegramId=int(telegram_id), gitlabId=int(gitlab_id))
        add_composed_obj(Session, new_user)
    except Exception as e:
        bot.send_message(secret_var["telegram_id"], e)

# -------------Технические функции, не будут использоваться позже--------------
def get_all(m, Classname):
    with Session() as session:
        try:
            res = get_all_objs(session, Classname)
            bot.send_message(secret_var["telegram_id"], str(res))
        except Exception as e:
            bot.send_message(secret_var["telegram_id"], e)

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




