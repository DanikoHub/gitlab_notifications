from flask import Flask, request
from functools import partial
import telebot
import os
from dotenv import load_dotenv

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from mysite.src.table_record import TableUser, TableIssue, TableCommentBranch, TableLabel, TableLabelTaskLink
from mysite.src.tables.base import Base
from mysite.src.table_record import Record

from mysite.src.log_tools import log_error

# -------------Настройка бота------------

app = Flask(__name__)

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")
secret_bot = os.getenv("BOT_ENDPOINT")
url = os.getenv("BOT_DOMAIN") + secret_bot
postgre_url = os.getenv("POSTGRE_URL")
telegram_id = os.getenv("TELEGRAM_ID")
secret_gitlab = os.getenv("GITLAB_ENDPOINT")

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

engine = create_engine(postgre_url, poolclass=NullPool, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

def create_db_and_tables() -> None:
	Base.metadata.create_all(engine)

try:
    create_db_and_tables()
except Exception as e:
     log_error(e)

# --------------Обработка запроса из Gitlab---------------

@app.route('/'+secret_gitlab, methods = ['POST', 'GET'])
def index():
    if request.headers.get('Content-Type') == 'application/json':
        try:
            record = Record(Session, request, bot)
            record.create_new_record(TableIssue)
            record.create_new_record(TableLabel)
            record.create_new_record(TableLabelTaskLink)
            record.create_new_record(TableCommentBranch)

            record.delete_record(TableLabelTaskLink)

        except Exception as e:
            log_error(e)

    return 'ok', 200

# ---------------Команды Бота-----------------
bot.send_message(telegram_id, "Бот запущен")

@bot.message_handler(commands=['start'])
def start_func(m):
    bot.send_message(m.chat.id, 'Отправьте ваш UserId')
    next_step = partial(get_client_id)
    bot.register_next_step_handler(m, next_step)

def get_client_id(m):
    try:
        record_user = Record(Session)
        record_user.create_new_record(TableUser, telegram_id = m.chat.id, gitlab_id = m.text)
    except Exception as e:
        log_error(e)





