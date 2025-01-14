from flask import Flask, request
import telebot
from functools import partial
import os
import json

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from users import Users
from issues import Issues
from comment_branch import CommentBranch
from labels import Labels
from labels_task_link import LabelsTaskLink

from sql_requests import get_all_objs, add_composed_obj, select_by_field
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
                res = select_by_field(Session(), Issues, Issues.issueId, int(request.json["object_attributes"]["id"]))
                if len(res) == 0:
                    bot.send_message(secret_var["telegram_id"], "Новый issue - " + request.json["object_attributes"]["url"])
                    new_issue = Issues(
                        title = request.json["object_attributes"]["title"],
                        description = request.json["object_attributes"]["description"],
                        url = request.json["object_attributes"]["url"],
                        issueId = int(request.json["object_attributes"]["id"]),
                        issueIid = int(request.json["object_attributes"]["iid"]),
                        authorId = int(request.json["object_attributes"]["author_id"]),
                        isClosed = int(request.json["object_attributes"]["state"] != 'opened')
                    )
                    add_composed_obj(Session, new_issue)
                else:
                    if 'labels' in request.json["changes"].keys():
                        lbl_list = ''

                        for lbl in request.json["changes"]["labels"]["current"]:
                            lbl_list += lbl["title"] + ", "

                        lbl_list = lbl_list[:-2]
                        bot.send_message(secret_var["telegram_id"],
                        "Были изменены лейблы в issue - " +
                        request.json["object_attributes"]["url"] +
                        "\nАкутальные лейблы - " + lbl_list
                        )

                for lbl in request.json["labels"]:
                    new_label = Labels(
                        name = lbl["title"],
                        labelId = lbl["id"]
                    )
                    add_composed_obj(Session, new_label)

                    new_label_task_link = LabelsTaskLink(
                        issueId = request.json["object_attributes"]["id"],
                        labelId = lbl["id"]
                    )
                    add_composed_obj(Session, new_label_task_link)

            if request.json["event_type"] == 'note':
                bot.send_message(secret_var["telegram_id"], "Новый комментарий в - " + request.json["object_attributes"]["url"])

                new_branch = CommentBranch(
                    discussionId=request.json["object_attributes"]["discussion_id"],
                    userId=int(request.json["object_attributes"]["author_id"])
                )
                add_composed_obj(Session, new_branch)

                for lbl in request.json["issue"]["labels"]:
                    new_label = Labels(
                        name = lbl["title"],
                        labelId = lbl["id"]
                    )
                    add_composed_obj(Session, new_label)

                    new_label_task_link = LabelsTaskLink(
                        issueId = request.json["issue"]["id"],
                        labelId = lbl["id"]
                    )
                    add_composed_obj(Session, new_label_task_link)
        except Exception as e:
            bot.send_message(secret_var["telegram_id"], e)
    return 'ok', 200

# ---------------Команды Бота-----------------

@bot.message_handler(commands=['start'])
def start_func(m):
    bot.send_message(secret_var["telegram_id"], 'Отправьте ваш ClientId')
    next_step = partial(get_client_id)
    bot.register_next_step_handler(m, next_step)

def get_client_id(m):
    bot.send_message(secret_var["telegram_id"], str(m.chat.id))
    telegram_id = m.chat.id
    gitlab_id = m.text
    try:
        new_user = Users(name="new_user", telegramId=int(telegram_id), gitlabId=int(gitlab_id))
        add_composed_obj(Session, new_user)
    except Exception as e:
        bot.send_message(secret_var["telegram_id"], e)

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




