from flask import Flask, request
import telebot
from functools import partial
import json

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from mysite.src.tables.users import create_new_user
from mysite.src.tables.issues import create_new_issue
from mysite.src.tables.comment_branch import create_new_commentbranch
from mysite.src.tables.labels import create_new_label
from mysite.src.tables.labels_task_link import create_new_labeltasklink, delete_labeltasklink
from mysite.src.tables.base import Base

from mysite.src.debug_tools import send_e
from mysite.src.tables_show import setup_handlers
from mysite.src.notifications import issue_change_notify, labels_change_notify, new_comment_notify

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
     send_e(bot, e, line = 'flask52 ')

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

                labels_change_notify(Session, request, bot)
                issue_change_notify(Session, request, bot)

                delete_labeltasklink(Session, request, bot)

            if request.json["event_type"] == 'note':

                create_new_commentbranch(Session, request)

                new_comment_notify(Session, request, bot)

        except Exception as e:
            send_e(bot, e, line = 'flask80 ')

    return 'ok', 200

# ---------------Команды Бота-----------------
bot.send_message(secret_var["telegram_id"], "Бот запущен")

@bot.message_handler(commands=['start'])
def start_func(m):
    bot.send_message(m.chat.id, 'Отправьте ваш UserId')
    next_step = partial(get_client_id)
    bot.register_next_step_handler(m, next_step)

def get_client_id(m):
    try:
        create_new_user(Session, request, m.chat.id, m.text)
    except Exception as e:
        send_e(bot, e, line = 'flask97 ')

# -------------Технические функции, не будут использоваться позже--------------
setup_handlers(Session, bot)





